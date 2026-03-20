from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Configuration for the CopAssist AI system
# Note: I used pydantic-settings because it's way easier to handle .env files this way! - Neel
class Settings(BaseSettings):
    # LLM Settings (Using Gemini as requested)
    GEMINI_API_KEY: str = "AIzaSyAMRaSkgOR30f-Q2wJcMSLF8yXX7y_FNhk"
    MODEL_NAME: str = "gemini-2.0-flash" # Gemini 2.0 Flash is even better! - Neel
    
    # DB Setup for pgAdmin
    # Format: postgresql://postgres:Neel%401234@localhost:5432/CopAssistAI
    DATABASE_URL: str = "postgresql://postgres:Neel%401234@localhost:5432/CopAssistAI"
    
    # Vector DB settings for our RAG system
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    VECTOR_DB_PATH: Optional[str] = "./data/chroma_db"
    
    # CCTV Simulator settings
    MOCK_TELEMETRY_INTERVAL: int = 5 
    
    # Basic Thresholds for alerts
    CRITICAL_CROWD_DENSITY: float = 0.8
    PERSON_THRESHOLD_NORMAL: int = 20
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
