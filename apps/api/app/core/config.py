"""
Core configuration constants and utilities for market data ingestion
"""

from enum import Enum
from typing import Dict, List

# Market Data Constants
class MarketDataConstants:
    """Constants for market data processing"""
    
    # OANDA specific configurations
    OANDA_MAX_CANDLES_PER_REQUEST = 5000
    OANDA_MAX_CONCURRENT_REQUESTS = 10
    OANDA_REQUEST_TIMEOUT_SECONDS = 30
    
    # Data validation constants
    MAX_PRICE_DEVIATION_PERCENT = 10.0  # Maximum allowed price deviation
    MIN_VOLUME_THRESHOLD = 0            # Minimum volume threshold
    MAX_GAP_TOLERANCE_PERCENT = 5.0     # Maximum allowed price gap
    
    # Timeframe configurations
    TIMEFRAME_MINUTES = {
        "H1": 60,
        "H4": 240,
        "D": 1440,
        "W": 10080
    }
    
    # Instrument groups for better organization
    MAJOR_PAIRS = [
        "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", 
        "AUD_USD", "USD_CAD", "NZD_USD"
    ]
    
    MINOR_PAIRS = [
        "EUR_GBP", "EUR_JPY", "GBP_JPY", "CHF_JPY", 
        "EUR_CHF", "AUD_JPY", "GBP_CHF"
    ]
    
    EXOTIC_PAIRS = [
        "NZD_JPY", "CAD_JPY", "AUD_CHF", "AUD_CAD", "AUD_NZD",
        "CAD_CHF", "EUR_AUD", "EUR_CAD", "EUR_NZD", "GBP_AUD",
        "GBP_CAD", "GBP_NZD", "NZD_CAD", "NZD_CHF", "USD_SEK"
    ]


class ProcessingModes(str, Enum):
    """Data processing modes"""
    HISTORICAL = "historical"
    REAL_TIME = "real_time"  
    BACKFILL = "backfill"
    VALIDATION = "validation"


class DataQualityThresholds:
    """Thresholds for data quality assessment"""
    
    EXCELLENT_QUALITY = 0.95      # >95% quality score
    GOOD_QUALITY = 0.85           # >85% quality score
    ACCEPTABLE_QUALITY = 0.70     # >70% quality score
    POOR_QUALITY = 0.50           # >50% quality score
    
    MAX_MISSING_PERIODS = 10      # Maximum missing periods before alert
    MAX_DUPLICATE_PERIODS = 5     # Maximum duplicates before alert
    MAX_PRICE_GAPS = 20          # Maximum price gaps before alert


class CollectionNames:
    """Firestore collection names"""
    
    MARKET_DATA = "market_data"
    RESISTANCE_EVENTS = "resistance_events" 
    CONFIGURATIONS = "configurations"
    INGESTION_LOGS = "ingestion_logs"
    QUALITY_METRICS = "quality_metrics"
    RATE_LIMIT_STATUS = "rate_limit_status"


class RetryPolicies:
    """Retry policies for different operations"""
    
    API_REQUEST_RETRIES = 3
    API_REQUEST_DELAY = [1, 2, 4]  # Exponential backoff in seconds
    
    DATABASE_RETRIES = 2
    DATABASE_DELAY = [0.5, 1.0]
    
    VALIDATION_RETRIES = 1


def get_timeframe_duration_minutes(timeframe: str) -> int:
    """Get duration in minutes for a timeframe"""
    return MarketDataConstants.TIMEFRAME_MINUTES.get(timeframe, 60)


def get_instrument_category(instrument: str) -> str:
    """Get the category (major/minor/exotic) for an instrument"""
    if instrument in MarketDataConstants.MAJOR_PAIRS:
        return "major"
    elif instrument in MarketDataConstants.MINOR_PAIRS:
        return "minor"
    elif instrument in MarketDataConstants.EXOTIC_PAIRS:
        return "exotic"
    else:
        return "unknown"


def get_quality_rating(score: float) -> str:
    """Get quality rating based on score"""
    if score >= DataQualityThresholds.EXCELLENT_QUALITY:
        return "excellent"
    elif score >= DataQualityThresholds.GOOD_QUALITY:
        return "good"
    elif score >= DataQualityThresholds.ACCEPTABLE_QUALITY:
        return "acceptable"
    elif score >= DataQualityThresholds.POOR_QUALITY:
        return "poor"
    else:
        return "critical"


# Rate limiting configuration per instrument category
RATE_LIMITS_BY_CATEGORY = {
    "major": {
        "requests_per_minute": 120,
        "burst_limit": 15,
        "priority": 1
    },
    "minor": {
        "requests_per_minute": 100,
        "burst_limit": 12,
        "priority": 2
    },
    "exotic": {
        "requests_per_minute": 80,
        "burst_limit": 10,
        "priority": 3
    }
}