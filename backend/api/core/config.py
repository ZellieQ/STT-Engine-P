import os
from pydantic import BaseSettings
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Speech-to-Text Transcription Service"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Authentication settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "stt_service")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "stt_transcriptions")
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Speech recognition settings
    DEFAULT_LANGUAGE: str = "en-US"
    SUPPORTED_LANGUAGES: List[str] = ["en-US", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR", "ja-JP", "zh-CN"]
    
    # File storage settings
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = ["mp3", "wav", "m4a", "flac", "ogg", "mp4"]
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()

# Set the SQLAlchemy database URI
settings.SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
)
