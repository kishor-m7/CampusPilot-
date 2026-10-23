from fastapi import APIRouter, Query
from typing import List, Optional
from backend.models import LearningResource
from backend.services import search_learning_resources_service

router = APIRouter(prefix="/api/resources", tags=["Learning Resources"])

@router.get("", response_model=List[LearningResource])
async def search_resources(
    query: Optional[str] = Query(None),
    course_code: Optional[str] = Query(None),
    topic: Optional[str] = Query(None)
):
    items = await search_learning_resources_service(query=query, course_code=course_code, topic=topic)
    return [LearningResource(**i) for i in items]
