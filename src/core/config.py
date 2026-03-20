from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# CopAssist AI Configuration
class Settings(BaseSettings):
    # API Keys are loaded from the LOCAL .env file for security.
    # Note: I removed the hardcoded keys to keep your account safe! - Neel
    GEMINI_API_KEY: Optional[str] = None
    MODEL_NAME: str = "gemini-2.0-flash" 
    
    # DB Credentials (PgAdmin)
    DATABASE_URL: str = "postgresql://postgres:Neel%401234@localhost:5432/CopAssistAI"
    
    # Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    VECTOR_DB_PATH: Optional[str] = "./data/chroma_db"
    
    # System Parameters
    MOCK_TELEMETRY_INTERVAL: int = 5
    
    # Environment config
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
