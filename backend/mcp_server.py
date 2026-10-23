"""
CampusPilot MCP Server.
Implements the Model Context Protocol (MCP) using the official Python MCP SDK with Streamable HTTP transport.
Exposes academic productivity tools for Gemini Agent and Alexa Assistant integrations.
"""

import json
import logging
from typing import Optional
from mcp.server.mcpserver import MCPServer
from backend.config import settings
from backend.services import (
    get_student_tasks_service,
    get_assignments_service,
    get_timetable_service,
    get_study_plan_service,
    create_reminder_service,
    get_reminders_service,
    search_learning_resources_service
)

logger = logging.getLogger("campuspilot.mcp")

# Initialize official MCP server
server = MCPServer(
    name="campuspilot-mcp",
    version="2.4.0",
    description="CampusPilot Academic Assistant & Alexa Productivity MCP Server"
)

def _resolve_user(user_id: Optional[str] = None) -> str:
    return user_id.strip() if (user_id and user_id.strip()) else settings.DEFAULT_DEV_USER_ID

@server.tool(
    name="get_student_tasks",
    description="Retrieve the student's active coursework tasks, deadlines, and urgency statuses."
)
async def get_student_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user_id: Optional[str] = None
) -> str:
    """Retrieves student tasks and coursework deliverables."""
    uid = _resolve_user(user_id)
    tasks = await get_student_tasks_service(user_id=uid, status=status or None, priority=priority or None)
    return json.dumps({"tasks": tasks, "count": len(tasks)}, indent=2)

@server.tool(
    name="get_assignments",
    description="Retrieve detailed assignments for a course with weights, due dates, and completion status."
)
async def get_assignments(
    status: Optional[str] = None,
    course_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> str:
    """Retrieves assignments for the authenticated student."""
    uid = _resolve_user(user_id)
    assignments = await get_assignments_service(user_id=uid, status=status or None, course_id=course_id or None)
    return json.dumps({"assignments": assignments, "count": len(assignments)}, indent=2)

@server.tool(
    name="get_timetable",
    description="Retrieve the student's weekly academic class schedule, lecture rooms, and lab sessions."
)
async def get_timetable(
    date: Optional[str] = None,
    day_of_week: Optional[str] = None,
    user_id: Optional[str] = None
) -> str:
    """Retrieves academic timetable and class entries."""
    uid = _resolve_user(user_id)
    classes = await get_timetable_service(user_id=uid, date=date or None, day_of_week=day_of_week or None)
    return json.dumps({"timetable": classes, "count": len(classes)}, indent=2)

@server.tool(
    name="get_study_plan",
    description="Retrieve the student's revision schedule, upcoming exams, and scheduled deep work study blocks."
)
async def get_study_plan(
    start_date: Optional[str] = None,
    days: int = 7,
    user_id: Optional[str] = None
) -> str:
    """Retrieves active study plan and focus blocks."""
    uid = _resolve_user(user_id)
    plan = await get_study_plan_service(user_id=uid, start_date=start_date or None, days=days)
    return json.dumps(plan, indent=2)

@server.tool(
    name="create_reminder",
    description="Create an academic reminder or alert for an assignment, lecture, or study goal."
)
async def create_reminder(
    title: str,
    due_date: Optional[str] = None,
    course_id: Optional[str] = None,
    priority: str = "medium",
    user_id: Optional[str] = None
) -> str:
    """Creates a new reminder."""
    uid = _resolve_user(user_id)
    res = await create_reminder_service(
        user_id=uid,
        title=title,
        due_date=due_date or None,
        course_id=course_id or None,
        priority=priority
    )
    return json.dumps({"success": True, "reminder": res}, indent=2)

@server.tool(
    name="get_reminders",
    description="Retrieve student reminders filtered by status (pending or completed)."
)
async def get_reminders(
    status: Optional[str] = None,
    user_id: Optional[str] = None
) -> str:
    """Retrieves student reminders."""
    uid = _resolve_user(user_id)
    reminders = await get_reminders_service(user_id=uid, status=status or None)
    return json.dumps({"reminders": reminders, "count": len(reminders)}, indent=2)

@server.tool(
    name="search_learning_resources",
    description="Search study guides, lecture summaries, notes, and references by subject or query."
)
async def search_learning_resources(
    query: Optional[str] = None,
    course_code: Optional[str] = None,
    topic: Optional[str] = None
) -> str:
    """Searches learning resources and syllabus notes."""
    resources = await search_learning_resources_service(query=query or None, course_code=course_code or None, topic=topic or None)
    return json.dumps({"resources": resources, "count": len(resources)}, indent=2)

# Expose Streamable HTTP ASGI app
mcp_app = server.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    from backend.database import init_db
    import asyncio
    asyncio.run(init_db())
    logger.info("Starting CampusPilot Standalone MCP Server on port %d...", settings.ALEXA_MCP_SERVER_PORT)
    uvicorn.run(mcp_app, host=settings.HOST, port=settings.ALEXA_MCP_SERVER_PORT)
