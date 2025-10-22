from pydantic_settings import BaseSettings
from functools import lru_cache
from datetime import datetime

class Settings(BaseSettings):
    APP_NAME: str = "RAG System API"
    APP_VERSION: str = "1.0.0"
    GROQ_API_KEY: str
    TAVILY_API_KEY: str
    COLLECTION_NAME: str = "default_collection"
    DEFAULT_USER: str = "system"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

def get_current_time():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def get_current_user():
    # In a real application, this would get the authenticated user
    return "Victoriakovuru"