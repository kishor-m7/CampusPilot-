from fastapi import APIRouter, Depends
from typing import List, Optional
import uuid
import json
from datetime import datetime, timezone
from backend.auth import get_current_user_id
from backend.database import fetch_all, execute
from backend.models import ChatMessageRequest, ChatMessageResponse
from backend.agent import default_agent

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])

@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(user_id: str = Depends(get_current_user_id)):
    rows = await fetch_all("""
    SELECT * FROM assistant_messages 
    WHERE user_id = ? 
    ORDER BY created_at ASC
    """, (user_id,))
    
    return [
        ChatMessageResponse(
            id=r["id"],
            role=r["role"],
            content=r["content"],
            action_type=r["action_type"],
            metadata=json.loads(r["metadata"]) if isinstance(r["metadata"], str) else (r["metadata"] or {}),
            created_at=r["created_at"]
        ) for r in rows
    ]

@router.post("/chat", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest, user_id: str = Depends(get_current_user_id)):
    now = datetime.now(timezone.utc).isoformat()
    user_msg_id = str(uuid.uuid4())
    assistant_msg_id = str(uuid.uuid4())

    # 1. Save user message to database
    await execute("""
    INSERT INTO assistant_messages (id, user_id, role, content, action_type, metadata, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_msg_id, user_id, "user", request.message, request.action_type, json.dumps({}), now))

    # 2. Retrieve recent chat history for conversational context
    history_rows = await fetch_all("""
    SELECT role, content FROM assistant_messages
    WHERE user_id = ?
    ORDER BY created_at DESC LIMIT 8
    """, (user_id,))
    conversation_history = [{"role": r["role"], "content": r["content"]} for r in reversed(history_rows)]

    # 3. Execute Gemini Agent with MCP tool calling
    agent_result = await default_agent.run(
        prompt=request.message,
        user_id=user_id,
        conversation_history=conversation_history
    )

    metadata = {
        "tools_executed": agent_result.tools_executed,
        "citations": agent_result.citations,
        "status": agent_result.status
    }
    if agent_result.action_type:
        metadata["action_label"] = (
            "Sync Plan to Alexa" if agent_result.action_type == "plan_day" else
            ("Start Oral Drill" if agent_result.action_type == "practice_quiz" else "View Syllabus Breakdown")
        )

    # 4. Save assistant response to database
    await execute("""
    INSERT INTO assistant_messages (id, user_id, role, content, action_type, metadata, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (assistant_msg_id, user_id, "assistant", agent_result.response, agent_result.action_type, json.dumps(metadata), now))

    return ChatMessageResponse(
        id=assistant_msg_id,
        role="assistant",
        content=agent_result.response,
        action_type=agent_result.action_type,
        metadata=metadata,
        created_at=now
    )
