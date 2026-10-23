from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from backend.auth import get_current_user_id
from backend.models import TimetableEntry
from backend.services import get_timetable_service

router = APIRouter(prefix="/api/timetable", tags=["Timetable"])

@router.get("", response_model=List[TimetableEntry])
async def get_timetable(
    date: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    entries = await get_timetable_service(user_id=user_id, date=date, day_of_week=day_of_week)
    return [TimetableEntry(**e) for e in entries]
