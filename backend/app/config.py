import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "E.V.I.D.A."
    APP_VERSION: str = "1.0.0"
    DOMAIN: str = "Healthcare Research"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/evida_db")
    USE_SQLITE_FALLBACK: bool = True  # Automatically fallback to SQLite if PostgreSQL is unavailable
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # openai, gemini, ollama, mock
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Embedding Provider Configuration
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "mock")  # openai, gemini, sentence-transformers, mock
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION: int = 384
    
    # Search Provider Configuration
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "duckduckgo")  # tavily, duckduckgo, mock
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")
    
    # Security
    AUTH_SECRET: str = os.getenv("AUTH_SECRET", "evida_super_secret_jwt_key_2026_healthcare_research")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Chunking & Research Parameters
    CHUNK_SIZE: int = 600  # Target token length (~600 tokens)
    CHUNK_OVERLAP: int = 75 # Token overlap (~75 tokens)
    MAX_REFLECTION_CYCLES: int = 3
    MAX_FILE_SIZE_MB: int = 25
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
