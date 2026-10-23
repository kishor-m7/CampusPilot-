"""
CampusPilot Core Business Logic Services.
Shared between FastAPI REST endpoints and Python MCP server tools to eliminate duplicate logic.
"""

from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime, timezone, timedelta
from backend.database import fetch_all, fetch_one, execute
from backend.models import (
    Assignment, AssignmentCreate, AssignmentUpdate,
    StudySession, StudySessionCreate, StudySessionUpdate,
    Reminder, ReminderCreate, ReminderUpdate,
    LearningResource, TimetableEntry
)

# ---------------------------------------------------------------------------
# Student Tasks & Assignments Services
# ---------------------------------------------------------------------------

async def get_assignments_service(
    user_id: str,
    status: Optional[str] = None,
    course_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    query = """
    SELECT a.*, c.code as course_code, c.name as course_name
    FROM assignments a
    LEFT JOIN courses c ON a.course_id = c.id
    WHERE a.user_id = ?
    """
    params = [user_id]
    if status:
        query += " AND a.status = ?"
        params.append(status)
    if course_id:
        query += " AND a.course_id = ?"
        params.append(course_id)
        
    query += " ORDER BY a.due_date ASC"
    rows = await fetch_all(query, tuple(params))
    
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "course_id": r["course_id"],
            "title": r["title"],
            "description": r["description"] or "",
            "due_date": r["due_date"],
            "status": r["status"],
            "priority": r["priority"],
            "weight_percentage": float(r["weight_percentage"] or 10.0),
            "completed_at": r["completed_at"],
            "created_at": r["created_at"],
            "course_code": r["course_code"],
            "course_name": r["course_name"]
        }
        for r in rows
    ]

async def get_student_tasks_service(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Aggregates coursework assignments and tasks."""
    query = """
    SELECT a.*, c.code as course_code, c.name as course_name
    FROM assignments a
    LEFT JOIN courses c ON a.course_id = c.id
    WHERE a.user_id = ?
    """
    params = [user_id]
    if status:
        query += " AND a.status = ?"
        params.append(status)
    if priority:
        query += " AND a.priority = ?"
        params.append(priority)
        
    query += " ORDER BY a.due_date ASC"
    rows = await fetch_all(query, tuple(params))
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "course": r["course_code"] or "General",
            "due_date": r["due_date"],
            "status": r["status"],
            "priority": r["priority"],
            "weight": float(r["weight_percentage"] or 10.0),
            "description": r["description"] or ""
        }
        for r in rows
    ]

async def create_assignment_service(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    assignment_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    course_id = data.get("course_id")
    title = data["title"]
    description = data.get("description", "")
    due_date = data["due_date"]
    status = data.get("status", "pending")
    priority = data.get("priority", "medium")
    weight = float(data.get("weight_percentage", 10.0))
    
    await execute("""
    INSERT INTO assignments (id, user_id, course_id, title, description, due_date, status, priority, weight_percentage, completed_at, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (assignment_id, user_id, course_id, title, description, due_date, status, priority, weight, None, now, now))
    
    row = await fetch_one("""
    SELECT a.*, c.code as course_code, c.name as course_name
    FROM assignments a
    LEFT JOIN courses c ON a.course_id = c.id
    WHERE a.id = ?
    """, (assignment_id,))
    
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "course_id": row["course_id"],
        "title": row["title"],
        "description": row["description"] or "",
        "due_date": row["due_date"],
        "status": row["status"],
        "priority": row["priority"],
        "weight_percentage": float(row["weight_percentage"] or 10.0),
        "completed_at": row["completed_at"],
        "created_at": row["created_at"],
        "course_code": row["course_code"],
        "course_name": row["course_name"]
    }

async def update_assignment_service(user_id: str, assignment_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    existing = await fetch_one("SELECT * FROM assignments WHERE id = ? AND user_id = ?", (assignment_id, user_id))
    if not existing:
        return None
        
    now = datetime.now(timezone.utc).isoformat()
    title = updates.get("title") if updates.get("title") is not None else existing["title"]
    description = updates.get("description") if updates.get("description") is not None else existing["description"]
    due_date = updates.get("due_date") if updates.get("due_date") is not None else existing["due_date"]
    status = updates.get("status") if updates.get("status") is not None else existing["status"]
    priority = updates.get("priority") if updates.get("priority") is not None else existing["priority"]
    weight = updates.get("weight_percentage") if updates.get("weight_percentage") is not None else existing["weight_percentage"]
    course_id = updates.get("course_id") if updates.get("course_id") is not None else existing["course_id"]
    
    completed_at = existing["completed_at"]
    if status == "completed" and existing["status"] != "completed":
        completed_at = now
    elif status != "completed":
        completed_at = None

    await execute("""
    UPDATE assignments
    SET title = ?, description = ?, due_date = ?, status = ?, priority = ?, weight_percentage = ?, course_id = ?, completed_at = ?, updated_at = ?
    WHERE id = ? AND user_id = ?
    """, (title, description, due_date, status, priority, weight, course_id, completed_at, now, assignment_id, user_id))
    
    row = await fetch_one("""
    SELECT a.*, c.code as course_code, c.name as course_name
    FROM assignments a
    LEFT JOIN courses c ON a.course_id = c.id
    WHERE a.id = ?
    """, (assignment_id,))
    
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "course_id": row["course_id"],
        "title": row["title"],
        "description": row["description"] or "",
        "due_date": row["due_date"],
        "status": row["status"],
        "priority": row["priority"],
        "weight_percentage": float(row["weight_percentage"] or 10.0),
        "completed_at": row["completed_at"],
        "created_at": row["created_at"],
        "course_code": row["course_code"],
        "course_name": row["course_name"]
    }

async def delete_assignment_service(user_id: str, assignment_id: str) -> bool:
    existing = await fetch_one("SELECT id FROM assignments WHERE id = ? AND user_id = ?", (assignment_id, user_id))
    if not existing:
        return False
    await execute("DELETE FROM assignments WHERE id = ? AND user_id = ?", (assignment_id, user_id))
    return True

# ---------------------------------------------------------------------------
# Timetable & Study Plan Services
# ---------------------------------------------------------------------------

async def get_timetable_service(
    user_id: str,
    date: Optional[str] = None,
    day_of_week: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetches upcoming academic classes, lectures, and lab blocks."""
    rows = await fetch_all("""
    SELECT s.*, c.code as course_code, c.name as course_name
    FROM study_sessions s
    LEFT JOIN courses c ON s.course_id = c.id
    WHERE s.user_id = ?
    ORDER BY s.start_time ASC
    """, (user_id,))
    
    timetable = []
    for r in rows:
        st = r["start_time"]
        dow = None
        try:
            clean_st = st.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_st)
            dow = dt.strftime("%A")
        except Exception:
            pass
            
        if date and not st.startswith(date):
            continue
        if day_of_week and dow and dow.lower() != day_of_week.lower():
            continue

        location = "CS Building Room 204" if r["course_code"] == "CS301" else (
            "Auditorium Hall B" if r["course_code"] == "CS304" else "Science Block 3"
        )
        timetable.append({
            "id": r["id"],
            "title": r["title"],
            "session_type": r["session_type"],
            "start_time": r["start_time"],
            "end_time": r["end_time"],
            "duration_minutes": int(r["duration_minutes"] or 60),
            "course_code": r["course_code"],
            "course_name": r["course_name"],
            "location": location,
            "day_of_week": dow
        })
    return timetable

async def get_study_plan_service(
    user_id: str,
    start_date: Optional[str] = None,
    days: int = 7
) -> Dict[str, Any]:
    """Fetches time-blocked study sessions, exams, and target deadlines."""
    sessions = await fetch_all("""
    SELECT s.*, c.code as course_code, c.name as course_name
    FROM study_sessions s
    LEFT JOIN courses c ON s.course_id = c.id
    WHERE s.user_id = ?
    ORDER BY s.start_time ASC
    """, (user_id,))
    
    exams = await fetch_all("""
    SELECT e.*, c.code as course_code
    FROM exams e
    LEFT JOIN courses c ON e.course_id = c.id
    WHERE e.user_id = ?
    ORDER BY e.exam_date ASC
    """, (user_id,))
    
    assignments = await fetch_all("""
    SELECT a.*, c.code as course_code
    FROM assignments a
    LEFT JOIN courses c ON a.course_id = c.id
    WHERE a.user_id = ? AND a.status != 'completed'
    ORDER BY a.due_date ASC
    """, (user_id,))
    
    return {
        "study_sessions": [
            {
                "id": s["id"],
                "title": s["title"],
                "course": s["course_code"],
                "start": s["start_time"],
                "end": s["end_time"],
                "type": s["session_type"],
                "duration_minutes": s["duration_minutes"],
                "completed": bool(s["completed"]),
                "alexa_synced": bool(s["alexa_synced"])
            }
            for s in sessions
        ],
        "upcoming_exams": [
            {
                "id": e["id"],
                "title": e["title"],
                "date": e["exam_date"],
                "course": e["course_code"]
            }
            for e in exams
        ],
        "active_assignments": [
            {
                "id": a["id"],
                "title": a["title"],
                "due": a["due_date"],
                "priority": a["priority"]
            }
            for a in assignments
        ]
    }

async def create_study_session_service(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    course_id = data.get("course_id")
    title = data["title"]
    session_type = data.get("session_type", "deep_work")
    start_time = data["start_time"]
    end_time = data["end_time"]
    duration_minutes = int(data.get("duration_minutes", 60))
    completed = int(bool(data.get("completed", False)))
    alexa_synced = int(bool(data.get("alexa_synced", False)))
    
    await execute("""
    INSERT INTO study_sessions (id, user_id, course_id, title, session_type, start_time, end_time, duration_minutes, completed, alexa_synced, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, user_id, course_id, title, session_type, start_time, end_time, duration_minutes, completed, alexa_synced, now, now))
    
    row = await fetch_one("""
    SELECT s.*, c.code as course_code
    FROM study_sessions s
    LEFT JOIN courses c ON s.course_id = c.id
    WHERE s.id = ?
    """, (session_id,))
    
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "course_id": row["course_id"],
        "title": row["title"],
        "session_type": row["session_type"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "duration_minutes": int(row["duration_minutes"] or 60),
        "completed": bool(row["completed"]),
        "alexa_synced": bool(row["alexa_synced"]),
        "created_at": row["created_at"],
        "course_code": row["course_code"]
    }

# ---------------------------------------------------------------------------
# Reminders Services
# ---------------------------------------------------------------------------

async def get_reminders_service(user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    query = """
    SELECT r.*, c.code as course_code
    FROM reminders r
    LEFT JOIN courses c ON r.course_id = c.id
    WHERE r.user_id = ?
    """
    params = [user_id]
    if status:
        query += " AND r.status = ?"
        params.append(status)
    query += " ORDER BY r.due_date ASC"
    
    rows = await fetch_all(query, tuple(params))
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "course_id": r["course_id"],
            "title": r["title"],
            "due_date": r["due_date"],
            "priority": r["priority"],
            "status": r["status"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "course_code": r["course_code"]
        }
        for r in rows
    ]

async def create_reminder_service(
    user_id: str,
    title: str,
    due_date: Optional[str] = None,
    course_id: Optional[str] = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    reminder_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    if not due_date:
        # Default to 24 hours from now
        due_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
    await execute("""
    INSERT INTO reminders (id, user_id, course_id, title, due_date, priority, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (reminder_id, user_id, course_id, title, due_date, priority, "pending", now, now))
    
    row = await fetch_one("""
    SELECT r.*, c.code as course_code
    FROM reminders r
    LEFT JOIN courses c ON r.course_id = c.id
    WHERE r.id = ?
    """, (reminder_id,))
    
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "course_id": row["course_id"],
        "title": row["title"],
        "due_date": row["due_date"],
        "priority": row["priority"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "course_code": row["course_code"]
    }

async def update_reminder_service(user_id: str, reminder_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    existing = await fetch_one("SELECT * FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    if not existing:
        return None
        
    now = datetime.now(timezone.utc).isoformat()
    title = updates.get("title") if updates.get("title") is not None else existing["title"]
    due_date = updates.get("due_date") if updates.get("due_date") is not None else existing["due_date"]
    priority = updates.get("priority") if updates.get("priority") is not None else existing["priority"]
    status = updates.get("status") if updates.get("status") is not None else existing["status"]
    course_id = updates.get("course_id") if updates.get("course_id") is not None else existing["course_id"]
    
    await execute("""
    UPDATE reminders
    SET title = ?, due_date = ?, priority = ?, status = ?, course_id = ?, updated_at = ?
    WHERE id = ? AND user_id = ?
    """, (title, due_date, priority, status, course_id, now, reminder_id, user_id))
    
    row = await fetch_one("""
    SELECT r.*, c.code as course_code
    FROM reminders r
    LEFT JOIN courses c ON r.course_id = c.id
    WHERE r.id = ?
    """, (reminder_id,))
    
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "course_id": row["course_id"],
        "title": row["title"],
        "due_date": row["due_date"],
        "priority": row["priority"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "course_code": row["course_code"]
    }

async def delete_reminder_service(user_id: str, reminder_id: str) -> bool:
    existing = await fetch_one("SELECT id FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    if not existing:
        return False
    await execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    return True

# ---------------------------------------------------------------------------
# Learning Resources Services
# ---------------------------------------------------------------------------

async def search_learning_resources_service(
    query: Optional[str] = None,
    course_code: Optional[str] = None,
    topic: Optional[str] = None
) -> List[Dict[str, Any]]:
    sql = """
    SELECT lr.*, c.code as course_code
    FROM learning_resources lr
    LEFT JOIN courses c ON lr.course_id = c.id
    WHERE 1=1
    """
    params = []
    if course_code:
        sql += " AND c.code LIKE ?"
        params.append(f"%{course_code}%")
    if topic:
        sql += " AND (lr.topic LIKE ? OR lr.title LIKE ?)"
        params.append(f"%{topic}%")
        params.append(f"%{topic}%")
    if query:
        sql += " AND (lr.title LIKE ? OR lr.summary LIKE ? OR lr.topic LIKE ?)"
        params.append(f"%{query}%")
        params.append(f"%{query}%")
        params.append(f"%{query}%")
        
    rows = await fetch_all(sql, tuple(params))
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "topic": r["topic"],
            "url": r["url"],
            "resource_type": r["resource_type"],
            "summary": r["summary"],
            "course_code": r["course_code"],
            "created_at": r["created_at"]
        }
        for r in rows
    ]
