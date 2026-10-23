from fastapi import APIRouter, Depends
from backend.auth import get_current_user_id
from backend.database import fetch_all, execute
from backend.models import AlexaSyncPlanRequest, AlexaSyncPlanResponse

router = APIRouter(prefix="/api/alexa", tags=["Alexa Integration"])

@router.post("/sync-plan", response_model=AlexaSyncPlanResponse)
async def sync_plan_to_alexa(request: AlexaSyncPlanRequest, user_id: str = Depends(get_current_user_id)):
    # 1. Fetch upcoming sessions for today
    sessions = await fetch_all("""
    SELECT s.title, s.start_time, s.duration_minutes, c.code as course_code
    FROM study_sessions s
    LEFT JOIN courses c ON s.course_id = c.id
    WHERE s.user_id = ? AND s.completed = 0
    ORDER BY s.start_time ASC
    """, (user_id,))

    # 2. Mark sessions as alexa_synced
    await execute("UPDATE study_sessions SET alexa_synced = 1 WHERE user_id = ?", (user_id,))

    count = len(sessions)
    if count > 0:
        first_task = sessions[0]["title"]
        announcement = (
            f"Good morning! CampusPilot has synced {count} study sessions for your {request.routine_name}. "
            f"Your first focus block is {first_task}. Say 'Alexa, start study timer' when you are ready."
        )
    else:
        announcement = "CampusPilot: Your study schedule is currently clear for today. Great job staying ahead!"

    return AlexaSyncPlanResponse(
        success=True,
        synced_items_count=count,
        announcement_text=announcement,
        alexa_routine=request.routine_name
    )

@router.get("/oral-drill")
async def get_oral_drill(user_id: str = Depends(get_current_user_id)):
    return {
        "topic": "Public Key Cryptography & Zero Trust",
        "drill_prompt": "Alexa will ask scenario-based questions on Public Key Cryptography and evaluate your spoken answers in real-time.",
        "questions": [
            "What mathematical problem forms the basis for RSA encryption?",
            "Explain the difference between symmetric and asymmetric cipher performance.",
            "Why is certificate revocation checking critical in TLS handshakes?"
        ],
        "alexa_command": "Alexa, open CampusPilot oral drill"
    }
