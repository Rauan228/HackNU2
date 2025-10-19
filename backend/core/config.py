import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except Exception:
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = None
ENV_PATH = find_dotenv()
if ENV_PATH:
    load_dotenv(ENV_PATH)
else:
    ROOT_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@localhost:5432/hacknu_job_portal')
    jwt_secret: str = os.getenv('SECRET_KEY', 'devsecret')
    jwt_algorithm: str = os.getenv('ALGORITHM', 'HS256')
    jwt_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', str(60 * 24 * 7)))
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
    cors_origins: list = ['http://localhost:3000', 'http://localhost:5173']
    if 'SettingsConfigDict' in globals() and SettingsConfigDict is not None:
        model_config = SettingsConfigDict(env_file=str(Path(ENV_PATH) if ENV_PATH else Path(__file__).resolve().parents[2] / '.env'), extra='ignore')
    else:

        class Config:
            env_file = str(Path(ENV_PATH) if ENV_PATH else Path(__file__).resolve().parents[2] / '.env')
            extra = 'ignore'
settings = Settings()
