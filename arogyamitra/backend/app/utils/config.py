from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./arogyamitra.db"
    SECRET_KEY: str = "arogyamitra-super-secret-key-2024-fitness-ai"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["*"]
        # AI Services
    GROQ_API_KEY: str = "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"
    OPENAI_API_KEY: str = "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"
    GEMINI_API_KEY: str = "AIzaSyBGJycryxrnh0Ejdn-1dmYC3Jfe_Q2DTiQ"

    # Google Services
    GOOGLE_CALENDAR_CLIENT_ID: str = ""
    GOOGLE_CALENDAR_CLIENT_SECRET: str = ""
    GOOGLE_CALENDAR_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    YOUTUBE_API_KEY: str = ""

    # Spoonacular
    SPOONACULAR_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
