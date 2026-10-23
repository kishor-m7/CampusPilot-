from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
from datetime import datetime, timezone
from backend.auth import get_current_user_id
from backend.database import fetch_all, fetch_one, execute
from backend.models import Course, CourseCreate

router = APIRouter(prefix="/api/courses", tags=["Courses"])

@router.get("", response_model=List[Course])
async def list_courses(user_id: str = Depends(get_current_user_id)):
    rows = await fetch_all("SELECT * FROM courses WHERE user_id = ? ORDER BY code ASC", (user_id,))
    return [
        Course(
            id=r["id"],
            user_id=r["user_id"],
            code=r["code"],
            name=r["name"],
            credits=r["credits"] or 3,
            color=r["color"] or "#4338ca",
            grade=r["grade"] or "A",
            created_at=r["created_at"]
        ) for r in rows
    ]

@router.post("", response_model=Course)
async def create_course(course: CourseCreate, user_id: str = Depends(get_current_user_id)):
    course_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    await execute("""
    INSERT INTO courses (id, user_id, code, name, credits, color, grade, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (course_id, user_id, course.code, course.name, course.credits, course.color, course.grade, now, now))
    
    return Course(
        id=course_id,
        user_id=user_id,
        code=course.code,
        name=course.name,
        credits=course.credits,
        color=course.color,
        grade=course.grade,
        created_at=now
    )
