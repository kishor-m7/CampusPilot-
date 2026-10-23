from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
import json
from datetime import datetime, timezone
from backend.auth import get_current_user_id
from backend.database import fetch_all, fetch_one, execute
from backend.models import Exam, ExamCreate, ExamUpdate, SyllabusUnit

router = APIRouter(prefix="/api/exams", tags=["Exams"])

def calculate_days_left(date_str: str) -> int:
    try:
        # Normalize ISO string
        clean_str = date_str.replace("Z", "+00:00")
        target = datetime.fromisoformat(clean_str)
        now = datetime.now(timezone.utc)
        diff = (target - now).days
        return max(0, diff)
    except Exception:
        return 0

@router.get("", response_model=List[Exam])
async def list_exams(user_id: str = Depends(get_current_user_id)):
    rows = await fetch_all("""
    SELECT e.*, c.code as course_code
    FROM exams e
    LEFT JOIN courses c ON e.course_id = c.id
    WHERE e.user_id = ?
    ORDER BY e.exam_date ASC
    """, (user_id,))
    
    result = []
    for r in rows:
        units_raw = json.loads(r["syllabus_units"]) if isinstance(r["syllabus_units"], str) else (r["syllabus_units"] or [])
        units = [SyllabusUnit(**u) for u in units_raw]
        days_left = calculate_days_left(r["exam_date"])
        
        result.append(Exam(
            id=r["id"],
            user_id=r["user_id"],
            course_id=r["course_id"],
            title=r["title"],
            exam_date=r["exam_date"],
            location=r["location"] or "",
            target_score=float(r["target_score"] or 90.0),
            syllabus_units=units,
            notes=r["notes"] or "",
            created_at=r["created_at"],
            course_code=r["course_code"],
            days_left=days_left
        ))
    return result

@router.post("", response_model=Exam)
async def create_exam(data: ExamCreate, user_id: str = Depends(get_current_user_id)):
    exam_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    units_json = json.dumps([u.model_dump() for u in data.syllabus_units])
    
    await execute("""
    INSERT INTO exams (id, user_id, course_id, title, exam_date, location, target_score, syllabus_units, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (exam_id, user_id, data.course_id, data.title, data.exam_date, data.location, data.target_score, units_json, data.notes, now, now))
    
    course_code = None
    if data.course_id:
        c = await fetch_one("SELECT code FROM courses WHERE id = ?", (data.course_id,))
        if c:
            course_code = c["code"]
            
    return Exam(
        id=exam_id,
        user_id=user_id,
        course_id=data.course_id,
        title=data.title,
        exam_date=data.exam_date,
        location=data.location,
        target_score=data.target_score,
        syllabus_units=data.syllabus_units,
        notes=data.notes,
        created_at=now,
        course_code=course_code,
        days_left=calculate_days_left(data.exam_date)
    )

@router.patch("/{exam_id}", response_model=Exam)
async def update_exam(exam_id: str, updates: ExamUpdate, user_id: str = Depends(get_current_user_id)):
    existing = await fetch_one("SELECT * FROM exams WHERE id = ? AND user_id = ?", (exam_id, user_id))
    if not existing:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    now = datetime.now(timezone.utc).isoformat()
    title = updates.title if updates.title is not None else existing["title"]
    exam_date = updates.exam_date if updates.exam_date is not None else existing["exam_date"]
    location = updates.location if updates.location is not None else existing["location"]
    target_score = updates.target_score if updates.target_score is not None else existing["target_score"]
    notes = updates.notes if updates.notes is not None else existing["notes"]
    course_id = updates.course_id if updates.course_id is not None else existing["course_id"]
    
    if updates.syllabus_units is not None:
        units_json = json.dumps([u.model_dump() for u in updates.syllabus_units])
    else:
        units_json = existing["syllabus_units"]

    await execute("""
    UPDATE exams
    SET title = ?, exam_date = ?, location = ?, target_score = ?, syllabus_units = ?, notes = ?, course_id = ?, updated_at = ?
    WHERE id = ? AND user_id = ?
    """, (title, exam_date, location, target_score, units_json, notes, course_id, now, exam_id, user_id))
    
    row = await fetch_one("""
    SELECT e.*, c.code as course_code
    FROM exams e
    LEFT JOIN courses c ON e.course_id = c.id
    WHERE e.id = ?
    """, (exam_id,))
    
    units_raw = json.loads(row["syllabus_units"]) if isinstance(row["syllabus_units"], str) else (row["syllabus_units"] or [])
    return Exam(
        id=row["id"],
        user_id=row["user_id"],
        course_id=row["course_id"],
        title=row["title"],
        exam_date=row["exam_date"],
        location=row["location"] or "",
        target_score=float(row["target_score"] or 90.0),
        syllabus_units=[SyllabusUnit(**u) for u in units_raw],
        notes=row["notes"] or "",
        created_at=row["created_at"],
        course_code=row["course_code"],
        days_left=calculate_days_left(row["exam_date"])
    )
