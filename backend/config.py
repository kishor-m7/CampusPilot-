import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.CORS_ORIGINS: str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
        )
        
        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")
        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        
        # Auth
        self.DEFAULT_DEV_USER_ID: str = os.getenv(
            "DEFAULT_DEV_USER_ID", "00000000-0000-0000-0000-000000000001"
        )
        self.JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
        
        # LLM & Agent
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        raw_model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        # Handle deprecated model names automatically
        if raw_model in ("gemini-2.5-flash", "gemini-1.5-flash"):
            self.GEMINI_MODEL = "gemini-3-flash-preview"
        else:
            self.GEMINI_MODEL = raw_model
        self.MAX_TOOL_ITERATIONS: int = int(os.getenv("MAX_TOOL_ITERATIONS", "5"))


        self.MCP_TIMEOUT_SECONDS: float = float(os.getenv("MCP_TIMEOUT_SECONDS", "15.0"))
        self.MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")
        
        # Alexa MCP Integration
        self.ALEXA_MCP_SERVER_PORT: int = int(os.getenv("ALEXA_MCP_SERVER_PORT", "8001"))


    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
