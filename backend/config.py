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
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # ChromaDB Settings
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "ml_knowledge_base"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Security Settings
    MAX_INPUT_LENGTH: int = 5000
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # App Settings
    APP_NAME: str = "ML-Guardian"

    model_config = SettingsConfigDict(
        env_file=str(base_dir / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()