from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    MODEL_NAME: str = "gpt-4o"
    
    # DB Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/copassist"
    
    # Vector DB Configuration
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    VECTOR_DB_PATH: Optional[str] = "./data/chroma_db"
    
    # CCTV Simulation
    MOCK_TELEMETRY_INTERVAL: int = 5 # seconds
    
    # Multi-Agent logic thresholds
    CRITICAL_CROWD_DENSITY: float = 0.8
    PERSON_THRESHOLD_NORMAL: int = 20
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
