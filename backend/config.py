import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory two levels up (ml_gurdian) where the .env file is
base_dir = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GROQ_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=str(base_dir / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()