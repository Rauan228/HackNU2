import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/hacknu_job_portal"
    
    # JWT
    jwt_secret: str = "devsecret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Игнорируем дополнительные поля из .env


settings = Settings()