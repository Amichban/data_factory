"""
Configuration settings for Event Detection System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Event Detection System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/events_db",
        env="DATABASE_URL"
    )
    
    # Firestore
    GCP_PROJECT_ID: str = Field(default="dezoomcamp23", env="GCP_PROJECT_ID")
    GCP_CREDENTIALS_PATH: Optional[str] = Field(default=None, env="GCP_CREDENTIALS_PATH")
    FIRESTORE_COLLECTION: str = Field(default="market_data", env="FIRESTORE_COLLECTION")
    
    # Processing
    BATCH_SIZE: int = Field(default=1000, env="BATCH_SIZE")
    MAX_WORKERS: int = Field(default=4, env="MAX_WORKERS")
    ATR_PERIOD: int = Field(default=14, env="ATR_PERIOD")
    PROCESSING_MODE: str = Field(default="spike", env="PROCESSING_MODE")  # batch or spike
    
    # Performance
    CACHE_TTL: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    RETRY_ATTEMPTS: int = Field(default=3, env="RETRY_ATTEMPTS")
    RETRY_DELAY: float = Field(default=1.0, env="RETRY_DELAY")
    
    # Monitoring
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Supported instruments
    SUPPORTED_INSTRUMENTS: list = [
        'EUR_USD', 'USD_THB', 'GBP_PLN', 'CAD_CHF', 'EUR_NOK',
        'USD_CZK', 'USD_SEK', 'USD_RON', 'USD_HUF', 'AUD_HKD',
        'USD_HKD', 'USD_DKK', 'USD_PHP', 'USD_TRY', 'EUR_PLN',
        'SGD_JPY', 'USD_PLN', 'USD_MXN', 'USD_ZAR', 'GBP_CHF',
        'NZD_JPY', 'CHF_JPY', 'CAD_JPY', 'EUR_JPY', 'AUD_JPY',
        'EUR_CHF', 'EUR_GBP', 'GBP_USD', 'EUR_AUD'
    ]
    
    # Supported granularities
    SUPPORTED_GRANULARITIES: list = ['H1', 'H4', 'D', 'W']
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()