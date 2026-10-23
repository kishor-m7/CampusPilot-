"""
Tests for CampusPilot Gemini Agent.
Verifies function selection, MCP tool invocation, deterministic adapter, and structured agent results.
"""

import pytest
import asyncio
from backend.agent import GeminiAgent, default_agent
from backend.database import init_db

DEV_USER = "00000000-0000-0000-0000-000000000001"

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    asyncio.run(init_db())

@pytest.mark.asyncio
async def test_agent_deterministic_test_adapter():
    """Verify that deterministic test adapter correctly executes real database tools."""
    agent = GeminiAgent(api_key=None)
    result = await agent.run("What are my pending assignments?", user_id=DEV_USER, force_test_adapter=True)
    assert result.status in ("test_adapter", "missing_api_key")
    assert "get_assignments" in result.tools_executed
    assert len(result.response) > 10
    assert "Coursework Database" in result.citations

@pytest.mark.asyncio
async def test_agent_timetable_intent():
    agent = GeminiAgent(api_key=None)
    result = await agent.run("What is on my timetable for today?", user_id=DEV_USER, force_test_adapter=True)
    assert "get_timetable" in result.tools_executed
    assert len(result.response) > 10

@pytest.mark.asyncio
async def test_agent_reminder_intent():
    agent = GeminiAgent(api_key=None)
    result = await agent.run("Remind me to study Linear Algebra problem set tonight", user_id=DEV_USER, force_test_adapter=True)
    assert "create_reminder" in result.tools_executed
    assert "Linear Algebra" in result.response

@pytest.mark.asyncio
async def test_agent_live_or_fallback():
    """Tests the agent's main execution loop."""
    result = await default_agent.run("What assignments do I have coming up?", user_id=DEV_USER)
    assert result.status in ("success", "test_adapter", "missing_api_key")
    assert len(result.response) > 10
    # Must have executed an MCP tool
    assert len(result.tools_executed) >= 1
