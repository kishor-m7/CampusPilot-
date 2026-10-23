from fastapi import APIRouter
from backend.database import USE_POSTGRES, pg_pool
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
async def health_check():
    db_status = "connected"
    db_type = "supabase_postgresql" if USE_POSTGRES and pg_pool else "local_sqlite_dev"
    
    return {
        "status": "healthy",
        "service": "campuspilot-api",
        "database": {
            "type": db_type,
            "status": db_status
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
