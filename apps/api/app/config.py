"""
Application configuration management using Pydantic Settings.

This module handles environment variable loading and validation
using Pydantic's BaseSettings class.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Assemble database URL from individual components."""
        if isinstance(v, str):
            return v
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_SERVER")
        port = values.get("POSTGRES_PORT", 5432)
        db = values.get("POSTGRES_DB")
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Redis (for caching, sessions, etc.)
    REDIS_URL: Optional[str] = None
    
    # Firestore Configuration
    FIRESTORE_PROJECT_ID: str = "dezoomcamp23"
    FIRESTORE_EMULATOR_HOST: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    FIRESTORE_ENABLED: bool = True
    
    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Market Data Configuration
    OANDA_API_KEY: Optional[str] = None
    OANDA_ACCOUNT_ID: Optional[str] = None
    OANDA_API_URL: str = "https://api-fxpractice.oanda.com"
    OANDA_STREAM_URL: str = "https://stream-fxpractice.oanda.com"
    
    # Market Data Settings
    SUPPORTED_INSTRUMENTS: List[str] = [
        "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD", "NZD_USD",
        "EUR_GBP", "EUR_JPY", "GBP_JPY", "CHF_JPY", "EUR_CHF", "AUD_JPY", "GBP_CHF",
        "NZD_JPY", "CAD_JPY", "AUD_CHF", "AUD_CAD", "AUD_NZD", "CAD_CHF", "EUR_AUD",
        "EUR_CAD", "EUR_NZD", "GBP_AUD", "GBP_CAD", "GBP_NZD", "NZD_CAD", "NZD_CHF",
        "USD_SEK"
    ]
    SUPPORTED_TIMEFRAMES: List[str] = ["H1", "H4", "D", "W"]
    
    # Rate Limiting Configuration
    MARKET_DATA_RATE_LIMIT: int = 100  # requests per minute
    MARKET_DATA_BURST_LIMIT: int = 10   # burst limit for concurrent requests
    MARKET_DATA_RETRY_ATTEMPTS: int = 3
    MARKET_DATA_RETRY_DELAY: float = 1.0  # seconds
    
    # Data Processing Settings
    BATCH_SIZE: int = 500  # for historical data processing
    MAX_HISTORICAL_DAYS: int = 90  # maximum days for historical backfill
    
    # Feature Flags
    FEATURE_FLAGS: dict = {
        "resistance_detection_enabled": False,  # Enable resistance event detection
        "firestore_enabled": True,
        "market_data_enabled": False,
        "batch_processing_enabled": False,  # Enable batch processing engine
        "parallel_processing": False,  # Enable parallel batch processing
        "spike_detection_enabled": False,  # Enable real-time spike detection
        "real_time_notifications": False,  # Enable real-time WebSocket notifications
        "api_v1_enabled": True,
        "max_concurrent_batch_jobs": 2  # Maximum concurrent batch jobs
    }
    
    # Testing
    TESTING: bool = False
    
    class Config:
        """Pydantic configuration."""
        case_sensitive = True
        env_file = ".env"


settings = Settings()