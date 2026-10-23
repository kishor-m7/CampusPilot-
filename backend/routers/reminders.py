from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from backend.auth import get_current_user_id
from backend.models import Reminder, ReminderCreate, ReminderUpdate
from backend.services import (
    get_reminders_service,
    create_reminder_service,
    update_reminder_service,
    delete_reminder_service
)

router = APIRouter(prefix="/api/reminders", tags=["Reminders"])

@router.get("", response_model=List[Reminder])
async def list_reminders(
    status: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    items = await get_reminders_service(user_id=user_id, status=status)
    return [Reminder(**item) for item in items]

@router.post("", response_model=Reminder)
async def create_reminder(
    data: ReminderCreate,
    user_id: str = Depends(get_current_user_id)
):
    item = await create_reminder_service(
        user_id=user_id,
        title=data.title,
        due_date=data.due_date,
        course_id=data.course_id,
        priority=data.priority
    )
    return Reminder(**item)

@router.patch("/{reminder_id}", response_model=Reminder)
async def update_reminder(
    reminder_id: str,
    updates: ReminderUpdate,
    user_id: str = Depends(get_current_user_id)
):
    item = await update_reminder_service(
        user_id=user_id,
        reminder_id=reminder_id,
        updates=updates.model_dump(exclude_unset=True)
    )
    if not item:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return Reminder(**item)

@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id)
):
    success = await delete_reminder_service(user_id=user_id, reminder_id=reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"success": True, "deleted_id": reminder_id}
