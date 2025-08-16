from pydantic_settings import BaseSettings
from typing import List
import secrets
from functools import lru_cache

class Settings(BaseSettings):
    # MongoDB Settings
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "resumatch"
    MONGODB_USERS_COLLECTION: str = "users"
    MONGODB_JOBS_COLLECTION: str = "jobs"
    MONGODB_MESSAGES_COLLECTION: str = "messages"
    MONGODB_CHATROOMS_COLLECTION: str = "chat_rooms"

    # JWT Settings
    JWT_SECRET: str = secrets.token_hex(32)  # Generates a secure random secret if not provided
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Settings
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Google API Settings
    GOOGLE_API_KEY: str

    # Rate Limiting
    RATE_LIMIT_PER_SECOND: int = 10

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache to avoid reading the .env file for every request
    """
    return Settings()

# Initialize settings instance
settings = get_settings()
