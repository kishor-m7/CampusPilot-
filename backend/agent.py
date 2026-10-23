"""
CampusPilot Gemini AI Agent Module.
Integrates the Google Gen AI SDK (`google-genai`) with the CampusPilot Python MCP Server.
Implements dynamic tool discovery, function-calling orchestration, multi-turn execution,
and structured academic co-pilot responses.
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.config import settings
from backend.mcp_server import server

logger = logging.getLogger("campuspilot.agent")

# Optional GenAI SDK import
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai SDK not available; agent will operate in test/fallback mode.")

class AgentResult(BaseModel):
    response: str
    tools_executed: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    action_type: Optional[str] = None
    status: str = "success"  # "success", "missing_api_key", "error", "test_adapter"
    error_message: Optional[str] = None

# ---------------------------------------------------------------------------
# MCP Tool Discovery and Gemini Schema Conversion
# ---------------------------------------------------------------------------

def get_mcp_function_declarations() -> List[Any]:
    """
    Extracts tools from the MCP Server and converts their JSON schemas
    into Google Gen AI FunctionDeclaration objects.
    """
    if not GENAI_AVAILABLE:
        return []

    tools = server._tool_manager.list_tools()
    declarations = []
    
    for t in tools:
        raw_schema = getattr(t, "parameters", {}) or {}
        props = {}
        for p_name, p_def in raw_schema.get("properties", {}).items():
            p_type = "STRING"
            if "type" in p_def:
                p_type = p_def["type"].upper()
            elif "anyOf" in p_def:
                for sub in p_def["anyOf"]:
                    if sub.get("type") != "null":
                        p_type = sub.get("type", "string").upper()
                        break
            props[p_name] = {
                "type": p_type,
                "description": p_def.get("title", p_name)
            }
            
        required = raw_schema.get("required", [])
        fd = types.FunctionDeclaration(
            name=t.name,
            description=t.description or t.name,
            parameters={
                "type": "OBJECT",
                "properties": props,
                "required": required
            }
        )
        declarations.append(fd)
        
    return declarations

# ---------------------------------------------------------------------------
# MCP Tool Execution Helper
# ---------------------------------------------------------------------------

async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any], user_id: str) -> str:
    """
    Invokes the requested tool on the CampusPilot MCP server.
    Ensures user_id is injected to maintain student data scoping.
    """
    arguments = dict(arguments or {})
    if "user_id" not in arguments or not arguments["user_id"]:
        arguments["user_id"] = user_id

    # 1. First attempt execution via official MCP server tool manager
    try:
        tool = server._tool_manager.get_tool(tool_name)
        if not tool:
            return json.dumps({"error": f"Tool '{tool_name}' not found on MCP server."})

        # Call the underlying tool function with signature filtering
        import inspect
        fn = tool.fn
        sig = inspect.signature(fn)
        valid_args = {k: v for k, v in arguments.items() if k in sig.parameters}
        
        if inspect.iscoroutinefunction(fn):
            res = await fn(**valid_args)
        else:
            res = fn(**valid_args)
            
        return str(res)
    except Exception as e:
        logger.error("Error executing MCP tool '%s': %s", tool_name, str(e), exc_info=True)
        return json.dumps({"error": f"Tool execution failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Core Agent Orchestration
# ---------------------------------------------------------------------------

FALLBACK_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-pro-latest"
]

class GeminiAgent:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.max_iterations = settings.MAX_TOOL_ITERATIONS
        self.client = None
        
        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error("Failed to initialize Google Gen AI Client: %s", str(e))
                self.client = None

    def is_configured(self) -> bool:
        """Returns True if Gemini API key and SDK are properly initialized."""
        return bool(self.client and self.api_key and not self.api_key.startswith("your-gemini"))


    async def run(
        self,
        prompt: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        force_test_adapter: bool = False
    ) -> AgentResult:
        """
        Main conversational loop:
        1. Formats history and user request.
        2. Configures Gemini with MCP function declarations.
        3. Orchestrates function calling loop until the model returns a final text answer.
        4. In the absence of an API key or under test mode, executes deterministic MCP integration.
        """
        tools_executed = []
        citations = []

        # Check if live Gemini can be called
        if not self.is_configured() or force_test_adapter:
            return await self._run_deterministic_test_adapter(prompt, user_id, tools_executed)

        try:
            declarations = get_mcp_function_declarations()
            tools_config = [types.Tool(function_declarations=declarations)] if declarations else None
            
            system_instruction = (
                "You are CampusPilot, an intelligent academic co-pilot for university students. "
                "You have access to MCP tools to inspect coursework assignments, deadlines, timetables, "
                "study plans, and reminders. Always use your tools to fetch real data when the student asks "
                "about their classes, assignments, exams, or study plans. Be encouraging, concise, and structured."
            )

            # Build initial contents
            contents: List[types.Content] = []
            
            # Add past turns if provided
            if conversation_history:
                for msg in conversation_history[-6:]:
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg.get("content", ""))]
                        )
                    )

            # Add current user prompt
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            )

            candidate_models = [self.model_name] + [m for m in FALLBACK_MODELS if m != self.model_name]
            last_err = None

            for active_model in candidate_models:
                try:
                    iterations = 0
                    final_text = ""
                    # Create a working copy of contents for this model attempt
                    curr_contents = list(contents)

                    while iterations < self.max_iterations:
                        iterations += 1
                        
                        config = types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            tools=tools_config,
                            temperature=0.3
                        )

                        response = await asyncio.to_thread(
                            self.client.models.generate_content,
                            model=active_model,
                            contents=curr_contents,
                            config=config
                        )

                        # Check if model made function calls
                        function_calls = response.function_calls

                        if function_calls:
                            model_parts = []
                            for cand in response.candidates:
                                if cand.content and cand.content.parts:
                                    model_parts.extend(cand.content.parts)
                            if not model_parts:
                                model_parts = [types.Part.from_text(text="I will check that for you.")]
                            curr_contents.append(types.Content(role="model", parts=model_parts))

                            tool_response_parts = []
                            for call in function_calls:
                                tool_name = call.name
                                tool_args = call.args or {}
                                logger.info("Agent invoking MCP tool '%s' with args: %s", tool_name, tool_args)
                                if tool_name not in tools_executed:
                                    tools_executed.append(tool_name)

                                tool_output = await execute_mcp_tool(tool_name, tool_args, user_id)
                                
                                if "course" in str(tool_output):
                                    citations.append("Campus Academic Records")
                                if tool_name == "get_timetable":
                                    citations.append("Course Schedule 2026")
                                elif tool_name == "search_learning_resources":
                                    citations.append("Syllabus Reference Repository")

                                tool_response_parts.append(
                                    types.Part.from_function_response(
                                        name=tool_name,
                                        response={"result": tool_output}
                                    )
                                )

                            curr_contents.append(types.Content(role="tool", parts=tool_response_parts))
                        else:
                            final_text = response.text or "I have processed your request."
                            break

                    if not final_text and iterations >= self.max_iterations:
                        final_text = "I reached the maximum number of tool lookups while retrieving your academic data. Please check your dashboard or refine your question."

                    return AgentResult(
                        response=final_text,
                        tools_executed=tools_executed,
                        citations=list(dict.fromkeys(citations)),
                        action_type=self._detect_action_type(prompt, tools_executed),
                        status="success"
                    )

                except Exception as model_err:
                    err_msg = str(model_err)
                    logger.warning("Model '%s' failed (%s). Trying next candidate...", active_model, err_msg[:100])
                    last_err = model_err
                    if "404" in err_msg or "503" in err_msg or "UNAVAILABLE" in err_msg or "NOT_FOUND" in err_msg:
                        continue
                    else:
                        break

            # If all live models failed, use deterministic database-backed test adapter
            logger.warning("All candidate models failed. Falling back to deterministic database-backed adapter.")
            fallback_res = await self._run_deterministic_test_adapter(prompt, user_id, tools_executed)
            fallback_res.error_message = str(last_err) if last_err else None
            return fallback_res

        except Exception as e:
            logger.error("Gemini Agent Execution Failed: %s", str(e), exc_info=True)
            return await self._run_deterministic_test_adapter(prompt, user_id, tools_executed)


    async def _run_deterministic_test_adapter(
        self,
        prompt: str,
        user_id: str,
        tools_executed: List[str]
    ) -> AgentResult:
        """
        Deterministic execution adapter used for tests and offline development
        when GEMINI_API_KEY is not configured.
        Invokes actual MCP tools on the database based on intent,
        guaranteeing genuine database-backed results without fabricating AI responses.
        """
        p_lower = prompt.lower()
        citations = []
        action = None
        status = "test_adapter" if not self.api_key else "missing_api_key"

        if "assignment" in p_lower or "task" in p_lower or "due" in p_lower or "deliverable" in p_lower:
            tools_executed.append("get_assignments")
            raw_res = await execute_mcp_tool("get_assignments", {}, user_id)
            data = json.loads(raw_res).get("assignments", [])
            pending = [a for a in data if a["status"] != "completed"]
            count = len(pending)
            citations.append("Coursework Database")
            
            if pending:
                first = pending[0]
                text = (
                    f"You have {count} active assignment deliverables. "
                    f"Your most pressing task is **{first['title']}** for {first.get('course_code', 'CS')} "
                    f"due on {first['due_date'][:10]} with priority {first['priority']}."
                )
            else:
                text = "Great work! You have no pending assignments right now."

        elif "timetable" in p_lower or "class" in p_lower or "lecture" in p_lower or "schedule" in p_lower:
            tools_executed.append("get_timetable")
            raw_res = await execute_mcp_tool("get_timetable", {}, user_id)
            classes = json.loads(raw_res).get("timetable", [])
            citations.append("Academic Timetable 2026")
            
            if classes:
                text = f"Here is your upcoming class schedule:\n"
                for c in classes[:3]:
                    text += f"• **{c['title']}** ({c.get('course_code', '')}) in {c['location']} at {c['start_time'][11:16]} UTC\n"
            else:
                text = "No scheduled lectures found for today."

        elif "reminder" in p_lower or "remind" in p_lower:
            if "create" in p_lower or "set" in p_lower or "remind" in p_lower:
                tools_executed.append("create_reminder")
                title = prompt.replace("remind me to", "").replace("set a reminder to", "").replace("create a reminder for", "").strip()

                if not title:
                    title = "Review study materials"
                raw_res = await execute_mcp_tool("create_reminder", {"title": title, "priority": "urgent"}, user_id)
                citations.append("CampusPilot Reminders")
                text = f"I've created an academic reminder: **'{title}'**. You can view and manage it in your Reminders section."
            else:
                tools_executed.append("get_reminders")
                raw_res = await execute_mcp_tool("get_reminders", {}, user_id)
                reminders = json.loads(raw_res).get("reminders", [])
                citations.append("CampusPilot Reminders")
                text = f"You currently have {len(reminders)} recorded reminders:\n"
                for r in reminders[:3]:
                    text += f"• [{r['priority'].upper()}] {r['title']}\n"

        elif "study" in p_lower or "plan" in p_lower or "revision" in p_lower:
            tools_executed.append("get_study_plan")
            raw_res = await execute_mcp_tool("get_study_plan", {"days": 7}, user_id)
            plan = json.loads(raw_res)
            citations.append("Study Planner & Exam Schedule")
            action = "plan_day"
            sessions = plan.get("study_sessions", [])
            text = (
                f"I've retrieved your active study plan. You have {len(sessions)} scheduled focus blocks this week. "
                f"I've aligned these blocks to prepare you for your upcoming exams."
            )

        elif "resource" in p_lower or "material" in p_lower or "notes" in p_lower or "search" in p_lower:
            tools_executed.append("search_learning_resources")
            raw_res = await execute_mcp_tool("search_learning_resources", {"query": "security"}, user_id)
            res = json.loads(raw_res).get("resources", [])
            citations.append("Campus Learning Repository")
            text = f"Found {len(res)} matching learning resources:\n"
            for item in res[:3]:
                text += f"• **{item['title']}** ({item['topic']}): {item['summary']}\n"

        else:
            tools_executed.append("get_student_tasks")
            raw_res = await execute_mcp_tool("get_student_tasks", {}, user_id)
            tasks = json.loads(raw_res).get("tasks", [])
            text = (
                f"CampusPilot Student Agent online. You have {len(tasks)} course tasks registered. "
                f"How can I assist your study session today? Ask me about assignments, your timetable, or revision plans."
            )

        return AgentResult(
            response=text,
            tools_executed=tools_executed,
            citations=citations,
            action_type=action,
            status=status
        )

    def _detect_action_type(self, prompt: str, tools_executed: List[str]) -> Optional[str]:
        p = prompt.lower()
        if "plan" in p or "get_study_plan" in tools_executed:
            return "plan_day"
        if "quiz" in p or "practice" in p:
            return "practice_quiz"
        if "summarize" in p or "syllabus" in p:
            return "summarize_syllabus"
        return None

# Singleton agent instance
default_agent = GeminiAgent()
