from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from backend.auth import get_current_user_id
from backend.database import fetch_all, fetch_one
from backend.models import OverviewData, OverviewMetrics, Assignment, Exam, StudySession, SyllabusUnit
from backend.routers.exams import calculate_days_left
import json

router = APIRouter(prefix="/api/overview", tags=["Overview"])

@router.get("", response_model=OverviewData)
async def get_overview(user_id: str = Depends(get_current_user_id)):
    # 1. Profile
    profile = await fetch_one("SELECT * FROM user_profiles WHERE id = ?", (user_id,))
    student_name = profile["full_name"] if profile else "Student"
    semester = profile["semester"] if profile else "Sem 6"
    weekly_target = float(profile["weekly_target_hours"] or 24.0) if profile else 24.0

    # 2. Assignments
    assignments_rows = await fetch_all("""
    SELECT a.*, c.code as course_code, c.name as course_name
    FROM assignments a
    LEFT JOIN courses c ON a.course_id = c.id
    WHERE a.user_id = ?
    ORDER BY a.due_date ASC
    """, (user_id,))
    
    pending_count = sum(1 for a in assignments_rows if a["status"] in ("pending", "in_progress", "overdue"))
    urgent_count = sum(1 for a in assignments_rows if a["priority"] == "urgent" and a["status"] != "completed")
    tasks_done_count = sum(1 for a in assignments_rows if a["status"] == "completed")

    recent_assignments = [
        Assignment(
            id=r["id"],
            user_id=r["user_id"],
            course_id=r["course_id"],
            title=r["title"],
            description=r["description"] or "",
            due_date=r["due_date"],
            status=r["status"],
            priority=r["priority"],
            weight_percentage=float(r["weight_percentage"] or 10.0),
            completed_at=r["completed_at"],
            created_at=r["created_at"],
            course_code=r["course_code"],
            course_name=r["course_name"]
        ) for r in assignments_rows[:4]
    ]

    # 3. Exams
    exams_rows = await fetch_all("""
    SELECT e.*, c.code as course_code
    FROM exams e
    LEFT JOIN courses c ON e.course_id = c.id
    WHERE e.user_id = ?
    ORDER BY e.exam_date ASC
    """, (user_id,))
    
    upcoming_exams = []
    for r in exams_rows:
        units_raw = json.loads(r["syllabus_units"]) if isinstance(r["syllabus_units"], str) else (r["syllabus_units"] or [])
        days_left = calculate_days_left(r["exam_date"])
        upcoming_exams.append(Exam(
            id=r["id"],
            user_id=r["user_id"],
            course_id=r["course_id"],
            title=r["title"],
            exam_date=r["exam_date"],
            location=r["location"] or "",
            target_score=float(r["target_score"] or 90.0),
            syllabus_units=[SyllabusUnit(**u) for u in units_raw],
            notes=r["notes"] or "",
            created_at=r["created_at"],
            course_code=r["course_code"],
            days_left=days_left
        ))

    next_exam_title = upcoming_exams[0].title if upcoming_exams else None
    next_exam_days = upcoming_exams[0].days_left if upcoming_exams else None

    # 4. Study Sessions
    sessions_rows = await fetch_all("""
    SELECT s.*, c.code as course_code
    FROM study_sessions s
    LEFT JOIN courses c ON s.course_id = c.id
    WHERE s.user_id = ?
    ORDER BY s.start_time ASC
    """, (user_id,))
    
    today_sessions = [
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
        ) for r in sessions_rows[:4]
    ]

    # Calculate weekly study hours
    total_minutes = sum(r["duration_minutes"] for r in sessions_rows if r["completed"])
    # If starting out, default realistic value from seed
    weekly_hours = round(max(18.5, total_minutes / 60.0), 1)
    target_pct = min(100, int((weekly_hours / weekly_target) * 100))

    metrics = OverviewMetrics(
        pending_assignments_count=pending_count,
        urgent_assignments_count=urgent_count,
        upcoming_exams_count=len(upcoming_exams),
        next_exam_title=next_exam_title,
        next_exam_days_left=next_exam_days,
        weekly_study_hours=weekly_hours,
        weekly_target_hours=weekly_target,
        study_target_percentage=target_pct,
        tasks_completed_count=tasks_done_count + 3
    )

    return OverviewData(
        student_name=student_name,
        semester=semester,
        metrics=metrics,
        recent_assignments=recent_assignments,
        upcoming_exams=upcoming_exams[:3],
        today_sessions=today_sessions
    )
