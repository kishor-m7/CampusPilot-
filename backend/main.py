from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

from backend.config import settings
from backend.database import init_db, close_db
from backend.routers import (
    health, profile, courses, assignments, exams,
    study_sessions, overview, assistant, alexa,
    reminders, timetable, resources
)
from backend.mcp_server import mcp_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("campuspilot")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CampusPilot Python Backend (%s mode)...", settings.ENVIRONMENT)
    await init_db()
    yield
    logger.info("Shutting down CampusPilot Python Backend...")
    await close_db()

app = FastAPI(
    title="CampusPilot Academic API & MCP Service",
    description="Backend API and MCP service for CampusPilot — AI Student Assistant & Alexa Copilot.",
    version="2.4.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(health.router)
app.include_router(overview.router)
app.include_router(profile.router)
app.include_router(courses.router)
app.include_router(assignments.router)
app.include_router(exams.router)
app.include_router(study_sessions.router)
app.include_router(reminders.router)
app.include_router(timetable.router)
app.include_router(resources.router)
app.include_router(assistant.router)
app.include_router(alexa.router)

# Mount MCP Streamable HTTP transport app at /mcp
app.mount("/mcp", mcp_app)

@app.get("/")
async def root():
    return {
        "message": "CampusPilot API is active. Navigate to /docs for interactive API documentation.",
        "version": "2.4.0",
        "health": "/api/health",
        "mcp_endpoint": "/mcp"
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
