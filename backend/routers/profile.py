from fastapi import APIRouter, Depends, HTTPException
import json
from datetime import datetime, timezone
from backend.auth import get_current_user_id
from backend.database import fetch_one, execute
from backend.models import UserProfile, UserProfileUpdate, AIPreferences

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_current_user_id)):
    row = await fetch_one("SELECT * FROM user_profiles WHERE id = ?", (user_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Student profile not found")
        
    ai_prefs = json.loads(row["ai_preferences"]) if isinstance(row["ai_preferences"], str) else (row["ai_preferences"] or {})
    return UserProfile(
        id=row["id"],
        full_name=row["full_name"],
        email=row["email"],
        major=row["major"] or "Computer Science",
        semester=row["semester"] or "Sem 1",
        current_gpa=float(row["current_gpa"] or 3.75),
        target_gpa=float(row["target_gpa"] or 3.90),
        weekly_target_hours=float(row["weekly_target_hours"] or 24.0),
        ai_preferences=AIPreferences(**ai_prefs),
        alexa_sync_enabled=bool(row["alexa_sync_enabled"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

@router.put("", response_model=UserProfile)
async def update_profile(updates: UserProfileUpdate, user_id: str = Depends(get_current_user_id)):
    existing = await fetch_one("SELECT * FROM user_profiles WHERE id = ?", (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found")

    now = datetime.now(timezone.utc).isoformat()
    
    full_name = updates.full_name if updates.full_name is not None else existing["full_name"]
    email = updates.email if updates.email is not None else existing["email"]
    major = updates.major if updates.major is not None else existing["major"]
    semester = updates.semester if updates.semester is not None else existing["semester"]
    current_gpa = updates.current_gpa if updates.current_gpa is not None else existing["current_gpa"]
    target_gpa = updates.target_gpa if updates.target_gpa is not None else existing["target_gpa"]
    weekly_target = updates.weekly_target_hours if updates.weekly_target_hours is not None else existing["weekly_target_hours"]
    
    if updates.ai_preferences is not None:
        ai_prefs_str = json.dumps(updates.ai_preferences.model_dump())
    else:
        ai_prefs_str = existing["ai_preferences"]
        
    alexa_sync = updates.alexa_sync_enabled if updates.alexa_sync_enabled is not None else existing["alexa_sync_enabled"]

    await execute("""
    UPDATE user_profiles 
    SET full_name = ?, email = ?, major = ?, semester = ?, current_gpa = ?, target_gpa = ?, weekly_target_hours = ?, ai_preferences = ?, alexa_sync_enabled = ?, updated_at = ?
    WHERE id = ?
    """, (full_name, email, major, semester, current_gpa, target_gpa, weekly_target, ai_prefs_str, int(alexa_sync), now, user_id))

    return await get_profile(user_id=user_id)
