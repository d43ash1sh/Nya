"""
Configuration management for ঞ (Nya) Search API.
Uses Pydantic Settings to load and validate environment variables with safe defaults.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(ROOT_DIR / ".env"), str(BASE_DIR / ".env"), ".env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    ENVIRONMENT: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Database: SQLite default for local zero-dependency Windows execution,
    # or PostgreSQL in Docker / production
    DATABASE_URL: str = "sqlite+aiosqlite:///./nya_search.db"

    # Search defaults
    SEARCH_PAGE_SIZE: int = 10
    SEARCH_MAX_QUERY_LENGTH: int = 250
    SEARCH_TIMEOUT_SECONDS: float = 2.5

    # Privacy controls - STRICT: No raw search query logging
    ENABLE_RAW_QUERY_LOGGING: bool = False
    ENABLE_SEARCH_HISTORY: bool = False
    SEARCH_HISTORY_RETENTION_DAYS: int = 30

    # Grounded AI Provider Configuration
    AI_PROVIDER: str = "gemini"  # "gemini", "openai", "ollama", "mock"
    AI_MODEL_NAME: str = "gemini-3.5-flash"
    AI_API_KEY: Optional[str] = None
    AI_MONTHLY_BUDGET_USD: float = 10.0
    AI_MONTHLY_USAGE_USD: float = 0.0
    AI_TIMEOUT_SECONDS: float = 30.0
    AI_MAX_EVIDENCE_DOCS: int = 5
    AI_MIN_GROUNDING_CONFIDENCE: float = 0.70

    # Ingestion policy & Crawler configuration
    CRAWLER_USER_AGENT: str = "NyaSearchBot/1.0 (+https://nya-search.org/bot; bot@nya-search.org)"
    CRAWLER_RESPECT_ROBOTS_TXT: bool = True
    CRAWLER_DEFAULT_RATE_LIMIT_DELAY: float = 1.5
    CRAWLER_MAX_CONCURRENT_REQUESTS: int = 2
    CRAWLER_TIMEOUT_SECONDS: float = 10.0


settings = Settings()
