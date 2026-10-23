from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.auth import get_current_user_id
from backend.models import StudySession, StudySessionCreate, StudySessionUpdate
from backend.services import (
    create_study_session_service,
    fetch_all, fetch_one, execute
)
from datetime import datetime, timezone

router = APIRouter(prefix="/api/study-sessions", tags=["Study Sessions"])

@router.get("", response_model=List[StudySession])
async def list_study_sessions(user_id: str = Depends(get_current_user_id)):
    rows = await fetch_all("""
    SELECT s.*, c.code as course_code
    FROM study_sessions s
    LEFT JOIN courses c ON s.course_id = c.id
    WHERE s.user_id = ?
    ORDER BY s.start_time ASC
    """, (user_id,))
    
    return [
        StudySession(
            id=r["id"],
            user_id=r["user_id"],
            course_id=r["course_id"],
            title=r["title"],
            session_type=r["session_type"],
            start_time=r["start_time"],
            end_time=r["end_time"],
            duration_minutes=int(r["duration_minutes"] or 60),
            completed=bool(r["completed"]),
            alexa_synced=bool(r["alexa_synced"]),
            created_at=r["created_at"],
            course_code=r["course_code"]
        ) for r in rows
    ]

@router.post("", response_model=StudySession)
async def create_study_session(data: StudySessionCreate, user_id: str = Depends(get_current_user_id)):
    item = await create_study_session_service(user_id=user_id, data=data.model_dump())
    return StudySession(**item)

@router.patch("/{session_id}", response_model=StudySession)
async def update_study_session(session_id: str, updates: StudySessionUpdate, user_id: str = Depends(get_current_user_id)):
    existing = await fetch_one("SELECT * FROM study_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
    if not existing:
        raise HTTPException(status_code=404, detail="Study session not found")
        
    now = datetime.now(timezone.utc).isoformat()
    title = updates.title if updates.title is not None else existing["title"]
    session_type = updates.session_type if updates.session_type is not None else existing["session_type"]
    start_time = updates.start_time if updates.start_time is not None else existing["start_time"]
    end_time = updates.end_time if updates.end_time is not None else existing["end_time"]
    duration_minutes = updates.duration_minutes if updates.duration_minutes is not None else existing["duration_minutes"]
    completed = int(updates.completed) if updates.completed is not None else existing["completed"]
    alexa_synced = int(updates.alexa_synced) if updates.alexa_synced is not None else existing["alexa_synced"]

    await execute("""
    UPDATE study_sessions
    SET title = ?, session_type = ?, start_time = ?, end_time = ?, duration_minutes = ?, completed = ?, alexa_synced = ?, updated_at = ?
    WHERE id = ? AND user_id = ?
    """, (title, session_type, start_time, end_time, duration_minutes, completed, alexa_synced, now, session_id, user_id))
    
    row = await fetch_one("""
    SELECT s.*, c.code as course_code
    FROM study_sessions s
    LEFT JOIN courses c ON s.course_id = c.id
    WHERE s.id = ?
    """, (session_id,))
    
    return StudySession(
        id=row["id"],
        user_id=row["user_id"],
        course_id=row["course_id"],
        title=row["title"],
        session_type=row["session_type"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        duration_minutes=int(row["duration_minutes"] or 60),
        completed=bool(row["completed"]),
        alexa_synced=bool(row["alexa_synced"]),
        created_at=row["created_at"],
        course_code=row["course_code"]
    )
