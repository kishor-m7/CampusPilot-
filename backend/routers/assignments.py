from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from backend.auth import get_current_user_id
from backend.models import Assignment, AssignmentCreate, AssignmentUpdate
from backend.services import (
    get_assignments_service,
    create_assignment_service,
    update_assignment_service,
    delete_assignment_service
)

router = APIRouter(prefix="/api/assignments", tags=["Assignments"])

@router.get("", response_model=List[Assignment])
async def list_assignments(
    status: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    rows = await get_assignments_service(user_id=user_id, status=status, course_id=course_id)
    return [Assignment(**r) for r in rows]

@router.post("", response_model=Assignment)
async def create_assignment(
    data: AssignmentCreate,
    user_id: str = Depends(get_current_user_id)
):
    item = await create_assignment_service(user_id=user_id, data=data.model_dump())
    return Assignment(**item)

@router.patch("/{assignment_id}", response_model=Assignment)
async def update_assignment(
    assignment_id: str,
    updates: AssignmentUpdate,
    user_id: str = Depends(get_current_user_id)
):
    item = await update_assignment_service(
        user_id=user_id,
        assignment_id=assignment_id,
        updates=updates.model_dump(exclude_unset=True)
    )
    if not item:
        raise HTTPException(status_code=404, detail="Assignment not found or unauthorized")
    return Assignment(**item)

@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: str,
    user_id: str = Depends(get_current_user_id)
):
    success = await delete_assignment_service(user_id=user_id, assignment_id=assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"success": True, "deleted_id": assignment_id}
