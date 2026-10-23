"""
Tests for CampusPilot FastAPI REST Endpoints.
Verifies health, overview, courses, assignments, exams, sessions, reminders, timetable, and alexa routes.
"""

import pytest
import asyncio
import httpx
from backend.main import app
from backend.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    asyncio.run(init_db())

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert data["service"] == "campuspilot-api"

@pytest.mark.asyncio
async def test_overview_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/overview")
        assert res.status_code == 200
        data = res.json()
        assert "student_name" in data
        assert "metrics" in data
        assert "recent_assignments" in data
        assert "upcoming_exams" in data
        assert "today_sessions" in data

@pytest.mark.asyncio
async def test_profile_endpoints():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # GET profile
        res = await client.get("/api/profile")
        assert res.status_code == 200
        profile = res.json()
        assert "full_name" in profile
        assert "current_gpa" in profile

        # PUT profile update
        update_data = {
            "full_name": "Kishor Developer",
            "weekly_target_hours": 26.5
        }
        update_res = await client.put("/api/profile", json=update_data)
        assert update_res.status_code == 200
        updated = update_res.json()
        assert updated["full_name"] == "Kishor Developer"
        assert updated["weekly_target_hours"] == 26.5

@pytest.mark.asyncio
async def test_courses_endpoints():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # GET courses
        res = await client.get("/api/courses")
        assert res.status_code == 200
        courses = res.json()
        assert len(courses) >= 1
        assert any(c["code"] == "CS301" for c in courses)

@pytest.mark.asyncio
async def test_assignments_crud():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create
        new_assn = {
            "title": "Automated Unit Test Assignment",
            "description": "Testing CRUD flow",
            "due_date": "2026-11-20T23:59:00Z",
            "status": "pending",
            "priority": "urgent",
            "weight_percentage": 15.0
        }
        res = await client.post("/api/assignments", json=new_assn)
        assert res.status_code == 200
        created = res.json()
        assn_id = created["id"]
        assert created["title"] == new_assn["title"]

        # 2. List with filter
        list_res = await client.get(f"/api/assignments?status=pending")
        assert list_res.status_code == 200
        assert any(a["id"] == assn_id for a in list_res.json())

        # 3. Update
        patch_res = await client.patch(f"/api/assignments/{assn_id}", json={"status": "completed"})
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "completed"
        assert patch_res.json()["completed_at"] is not None

        # 4. Delete
        del_res = await client.delete(f"/api/assignments/{assn_id}")
        assert del_res.status_code == 200
        assert del_res.json()["success"] is True

        # 5. Verify deleted 404
        patch_404 = await client.patch(f"/api/assignments/{assn_id}", json={"title": "Should fail"})
        assert patch_404.status_code == 404

@pytest.mark.asyncio
async def test_reminders_crud():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create reminder
        new_rem = {
            "title": "Study Cryptography for Midterm",
            "priority": "urgent",
            "status": "pending"
        }
        res = await client.post("/api/reminders", json=new_rem)
        assert res.status_code == 200
        created = res.json()
        rem_id = created["id"]
        assert created["title"] == new_rem["title"]

        # List reminders
        list_res = await client.get("/api/reminders")
        assert list_res.status_code == 200
        assert any(r["id"] == rem_id for r in list_res.json())

        # Update reminder
        up_res = await client.patch(f"/api/reminders/{rem_id}", json={"status": "completed"})
        assert up_res.status_code == 200
        assert up_res.json()["status"] == "completed"

        # Delete reminder
        del_res = await client.delete(f"/api/reminders/{rem_id}")
        assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_timetable_and_resources():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Timetable
        tt_res = await client.get("/api/timetable")
        assert tt_res.status_code == 200
        assert isinstance(tt_res.json(), list)

        # Resources
        res_res = await client.get("/api/resources?query=Zero+Trust")
        assert res_res.status_code == 200
        assert len(res_res.json()) >= 1
        assert "Zero Trust" in res_res.json()[0]["title"]

@pytest.mark.asyncio
async def test_alexa_sync_plan():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/alexa/sync-plan", json={"routine_name": "Test Routine"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "announcement_text" in data
