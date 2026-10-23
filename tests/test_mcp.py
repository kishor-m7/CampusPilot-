"""
Tests for CampusPilot Model Context Protocol (MCP) Server.
Verifies server initialization, tool discovery, and database-backed tool execution for all 7 tools.
"""

import pytest
import json
import asyncio
from backend.mcp_server import server
from backend.database import init_db
from backend.agent import execute_mcp_tool, get_mcp_function_declarations

DEV_USER = "00000000-0000-0000-0000-000000000001"

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    asyncio.run(init_db())

def test_mcp_tool_registration():
    """Verify that all 7 required CampusPilot tools are registered on the MCP server."""
    tools = [t.name for t in server._tool_manager.list_tools()]
    expected = [
        "get_student_tasks",
        "get_assignments",
        "get_timetable",
        "get_study_plan",
        "create_reminder",
        "get_reminders",
        "search_learning_resources"
    ]
    for exp in expected:
        assert exp in tools, f"Expected tool '{exp}' not found in MCP server tool registry."

def test_gemini_function_declarations_conversion():
    """Verify that MCP tool schemas cleanly convert into Gemini FunctionDeclaration format."""
    declarations = get_mcp_function_declarations()
    assert len(declarations) == 7
    dec_names = [d.name for d in declarations]
    assert "get_assignments" in dec_names
    assert "create_reminder" in dec_names
    assert "get_timetable" in dec_names

@pytest.mark.asyncio
async def test_mcp_get_student_tasks():
    raw = await execute_mcp_tool("get_student_tasks", {"status": "pending"}, DEV_USER)
    data = json.loads(raw)
    assert "tasks" in data
    assert "count" in data
    assert isinstance(data["tasks"], list)

@pytest.mark.asyncio
async def test_mcp_get_assignments():
    raw = await execute_mcp_tool("get_assignments", {}, DEV_USER)
    data = json.loads(raw)
    assert "assignments" in data
    assert data["count"] >= 1
    first = data["assignments"][0]
    assert "title" in first
    assert "due_date" in first
    assert "priority" in first

@pytest.mark.asyncio
async def test_mcp_get_timetable():
    raw = await execute_mcp_tool("get_timetable", {}, DEV_USER)
    data = json.loads(raw)
    assert "timetable" in data
    assert isinstance(data["timetable"], list)

@pytest.mark.asyncio
async def test_mcp_get_study_plan():
    raw = await execute_mcp_tool("get_study_plan", {"days": 7}, DEV_USER)
    data = json.loads(raw)
    assert "study_sessions" in data
    assert "upcoming_exams" in data
    assert "active_assignments" in data

@pytest.mark.asyncio
async def test_mcp_reminders_tools():
    # 1. Create reminder via tool
    create_raw = await execute_mcp_tool(
        "create_reminder",
        {"title": "Review Distributed Computing Paxos lecture", "priority": "urgent"},
        DEV_USER
    )
    res = json.loads(create_raw)
    assert res.get("success") is True
    assert res["reminder"]["title"] == "Review Distributed Computing Paxos lecture"

    # 2. Get reminders via tool
    get_raw = await execute_mcp_tool("get_reminders", {}, DEV_USER)
    get_data = json.loads(get_raw)
    assert "reminders" in get_data
    assert any(r["title"] == "Review Distributed Computing Paxos lecture" for r in get_data["reminders"])

@pytest.mark.asyncio
async def test_mcp_search_learning_resources():
    raw = await execute_mcp_tool("search_learning_resources", {"query": "Buddy Allocator"}, DEV_USER)
    data = json.loads(raw)
    assert "resources" in data
    assert len(data["resources"]) >= 1
    assert "Buddy Allocator" in data["resources"][0]["title"]
