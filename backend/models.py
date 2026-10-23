from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

# ---------------------------------------------------------------------------
# Base Response Wrappers
# ---------------------------------------------------------------------------
class SuccessResponse(BaseModel):
    data: Any

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

# ---------------------------------------------------------------------------
# User Profile Models
# ---------------------------------------------------------------------------
class AIPreferences(BaseModel):
    response_style: str = "concise"
    syllabus_parsing: bool = True
    voice_confirmations: bool = True

class UserProfileBase(BaseModel):
    full_name: str = "Kishor"
    email: Optional[str] = "student@university.edu"
    major: str = "B.Tech Computer Science"
    semester: str = "Sem 6"
    current_gpa: float = 3.78
    target_gpa: float = 3.90
    weekly_target_hours: float = 24.0
    ai_preferences: AIPreferences = Field(default_factory=AIPreferences)
    alexa_sync_enabled: bool = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    major: Optional[str] = None
    semester: Optional[str] = None
    current_gpa: Optional[float] = None
    target_gpa: Optional[float] = None
    weekly_target_hours: Optional[float] = None
    ai_preferences: Optional[AIPreferences] = None
    alexa_sync_enabled: Optional[bool] = None

class UserProfile(UserProfileBase):
    id: str
    created_at: str
    updated_at: str

# ---------------------------------------------------------------------------
# Course Models
# ---------------------------------------------------------------------------
class CourseBase(BaseModel):
    code: str
    name: str
    credits: int = 3
    color: str = "#4338ca"
    grade: str = "A"

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: str
    user_id: str
    created_at: str

# ---------------------------------------------------------------------------
# Assignment Models
# ---------------------------------------------------------------------------
class AssignmentBase(BaseModel):
    course_id: Optional[str] = None
    title: str
    description: str = ""
    due_date: str
    status: str = "pending"  # pending, in_progress, completed, overdue
    priority: str = "medium" # low, medium, urgent
    weight_percentage: float = 10.0

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    weight_percentage: Optional[float] = None
    course_id: Optional[str] = None

class Assignment(AssignmentBase):
    id: str
    user_id: str
    completed_at: Optional[str] = None
    created_at: str
    course_code: Optional[str] = None
    course_name: Optional[str] = None

# ---------------------------------------------------------------------------
# Exam Models
# ---------------------------------------------------------------------------
class SyllabusUnit(BaseModel):
    name: str
    covered: bool = False

class ExamBase(BaseModel):
    course_id: Optional[str] = None
    title: str
    exam_date: str
    location: str = ""
    target_score: float = 90.0
    syllabus_units: List[SyllabusUnit] = Field(default_factory=list)
    notes: str = ""

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    exam_date: Optional[str] = None
    location: Optional[str] = None
    target_score: Optional[float] = None
    syllabus_units: Optional[List[SyllabusUnit]] = None
    notes: Optional[str] = None
    course_id: Optional[str] = None

class Exam(ExamBase):
    id: str
    user_id: str
    created_at: str
    course_code: Optional[str] = None
    days_left: Optional[int] = None

# ---------------------------------------------------------------------------
# Study Session Models
# ---------------------------------------------------------------------------
class StudySessionBase(BaseModel):
    course_id: Optional[str] = None
    title: str
    session_type: str = "deep_work" # lecture, deep_work, revision, group_study, lab
    start_time: str
    end_time: str
    duration_minutes: int = 60
    completed: bool = False
    alexa_synced: bool = False

class StudySessionCreate(StudySessionBase):
    pass

class StudySessionUpdate(BaseModel):
    title: Optional[str] = None
    session_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    completed: Optional[bool] = None
    alexa_synced: Optional[bool] = None

class StudySession(StudySessionBase):
    id: str
    user_id: str
    created_at: str
    course_code: Optional[str] = None

# ---------------------------------------------------------------------------
# Overview Aggregate Models
# ---------------------------------------------------------------------------
class OverviewMetrics(BaseModel):
    pending_assignments_count: int
    urgent_assignments_count: int
    upcoming_exams_count: int
    next_exam_title: Optional[str] = None
    next_exam_days_left: Optional[int] = None
    weekly_study_hours: float
    weekly_target_hours: float
    study_target_percentage: int
    tasks_completed_count: int

class OverviewData(BaseModel):
    student_name: str
    semester: str
    metrics: OverviewMetrics
    recent_assignments: List[Assignment]
    upcoming_exams: List[Exam]
    today_sessions: List[StudySession]

# ---------------------------------------------------------------------------
# AI Assistant & Chat Models
# ---------------------------------------------------------------------------
class ChatMessageRequest(BaseModel):
    message: str
    action_type: Optional[str] = None # plan_day, summarize_syllabus, practice_quiz

class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    action_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str

# ---------------------------------------------------------------------------
# Alexa Action Models
# ---------------------------------------------------------------------------
class AlexaSyncPlanRequest(BaseModel):
    schedule_date: Optional[str] = None
    routine_name: str = "Morning Briefing"

class AlexaSyncPlanResponse(BaseModel):
    success: bool
    synced_items_count: int
    announcement_text: str
    alexa_routine: str

# ---------------------------------------------------------------------------
# Reminder Models
# ---------------------------------------------------------------------------
class ReminderBase(BaseModel):
    course_id: Optional[str] = None
    title: str
    due_date: Optional[str] = None
    priority: str = "medium"  # low, medium, urgent
    status: str = "pending"   # pending, completed

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    course_id: Optional[str] = None

class Reminder(ReminderBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str
    course_code: Optional[str] = None

# ---------------------------------------------------------------------------
# Learning Resource Models
# ---------------------------------------------------------------------------
class LearningResourceBase(BaseModel):
    course_id: Optional[str] = None
    title: str
    topic: str
    url: str = ""
    resource_type: str = "notes" # notes, article, video, practice_quiz, official_docs
    summary: str = ""

class LearningResourceCreate(LearningResourceBase):
    pass

class LearningResource(LearningResourceBase):
    id: str
    created_at: str
    course_code: Optional[str] = None

# ---------------------------------------------------------------------------
# Timetable Entry Models
# ---------------------------------------------------------------------------
class TimetableEntry(BaseModel):
    id: str
    title: str
    session_type: str
    start_time: str
    end_time: str
    duration_minutes: int
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    location: Optional[str] = None
    day_of_week: Optional[str] = None

