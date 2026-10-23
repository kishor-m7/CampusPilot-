# CampusPilot API Contract & Data Model Specification

## 1. Domain Entities & Database Schema

All entities belong to an authenticated user (`user_id`). In production with Supabase, `user_id` maps to `auth.users.id`.

### 1.1 `user_profiles`
Stores student academic metadata and co-pilot settings.
```json
{
  "id": "uuid",
  "email": "student@university.edu",
  "full_name": "Kishor",
  "major": "B.Tech CS",
  "semester": "Sem 6",
  "current_gpa": 3.78,
  "target_gpa": 3.90,
  "weekly_target_hours": 24.0,
  "ai_preferences": {
    "response_style": "concise",
    "syllabus_parsing": true,
    "voice_confirmations": true
  },
  "alexa_sync_enabled": true,
  "created_at": "2026-10-23T12:00:00Z",
  "updated_at": "2026-10-23T12:00:00Z"
}
```

### 1.2 `courses`
Academic courses currently enrolled in.
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "code": "CS301",
  "name": "Operating Systems",
  "credits": 4,
  "color": "#4338ca",
  "grade": "3.8",
  "created_at": "2026-10-23T12:00:00Z"
}
```

### 1.3 `assignments`
Coursework deliverables with urgency tracking.
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "course_id": "uuid",
  "title": "Kernel Memory Allocator Lab",
  "description": "Implement buddy memory allocator in C",
  "due_date": "2026-10-27T23:59:00Z",
  "status": "pending | in_progress | completed | overdue",
  "priority": "low | medium | urgent",
  "weight_percentage": 15.0,
  "completed_at": null,
  "created_at": "2026-10-23T12:00:00Z"
}
```

### 1.4 `exams`
Upcoming examination dates and syllabus checklists.
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "course_id": "uuid",
  "title": "Midterm: System Security & Cryptography",
  "exam_date": "2026-10-28T09:00:00Z",
  "location": "Auditorium Hall B",
  "target_score": 90.0,
  "syllabus_units": [
    { "name": "Public Key Cryptography", "covered": true },
    { "name": "Buffer Overflows & ROP", "covered": false }
  ],
  "notes": "Bring calculator and photo ID",
  "created_at": "2026-10-23T12:00:00Z"
}
```

### 1.5 `study_sessions`
Scheduled calendar slots and time-blocking records.
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "course_id": "uuid",
  "title": "Deep Work: Memory Management",
  "session_type": "lecture | deep_work | revision | lab",
  "start_time": "2026-10-24T14:00:00Z",
  "end_time": "2026-10-24T16:00:00Z",
  "duration_minutes": 120,
  "completed": false,
  "alexa_synced": true,
  "created_at": "2026-10-23T12:00:00Z"
}
```

### 1.6 `assistant_messages`
Co-pilot chat interactions.
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "role": "user | assistant",
  "content": "Can you draft a 3-day revision plan for Cybersecurity?",
  "action_type": "plan_day | summarize_syllabus | practice_quiz | null",
  "metadata": {},
  "created_at": "2026-10-23T12:00:00Z"
}
```

---

## 2. Standard API Response Formats

### 2.1 Success Response
Single entity:
```json
{ "data": { ... } }
```
List of entities:
```json
{ "data": [ ... ], "count": 4 }
```

### 2.2 Error Conventions
```json
{
  "error": {
    "code": "NOT_FOUND | VALIDATION_ERROR | UNAUTHORIZED | INTERNAL_ERROR",
    "message": "Human-readable description",
    "details": {}
  }
}
```

---

## 3. Endpoints Matrix

| Method | Path | Description | Used By |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Health check & DB connectivity status | All / Monitor |
| `GET` | `/api/overview` | Aggregated metrics for home dashboard | Overview, Alexa MCP |
| `GET` | `/api/profile` | Read user profile and academic preferences | Settings, Header |
| `PUT` | `/api/profile` | Update profile / preferences | Settings |
| `GET` | `/api/courses` | List all user courses | All screens |
| `POST` | `/api/courses` | Create a new course | Settings / Planner |
| `GET` | `/api/assignments` | List assignments (filterable by status) | Assignments, Overview, Alexa |
| `POST` | `/api/assignments` | Create a new assignment | Assignments, Alexa MCP |
| `PATCH` | `/api/assignments/{id}` | Update assignment / mark complete | Assignments, Alexa MCP |
| `DELETE`| `/api/assignments/{id}` | Delete assignment | Assignments |
| `GET` | `/api/exams` | List upcoming exams | Exams, Overview, Alexa MCP |
| `POST` | `/api/exams` | Create an exam | Exams |
| `PATCH` | `/api/exams/{id}` | Update exam or syllabus unit completion | Exams |
| `GET` | `/api/study-sessions` | List calendar sessions | Study Planner, Overview |
| `POST` | `/api/study-sessions` | Schedule a study session | Study Planner, Alexa MCP |
| `PATCH` | `/api/study-sessions/{id}` | Mark session completed / update time | Study Planner, Alexa MCP |
| `POST` | `/api/assistant/chat` | Send prompt to Academic Assistant | AI Assistant, Overview Quick Ask |
| `POST` | `/api/alexa/sync-plan` | Push active study plan to Alexa | AI Assistant, Planner, Alexa MCP |
