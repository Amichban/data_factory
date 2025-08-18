# Enhanced Events Specification: New Resistance Event Detection System

## 1. Executive Summary

A real-time market structure analysis system that detects and tracks resistance levels in forex markets, providing traders with actionable insights through pattern recognition, feature engineering, and predictive analytics.

## 2. Event Definition

### 2.1 Core Concept
**New Resistance Event**: A price level where selling pressure exceeds buying pressure, creating a potential reversal or consolidation zone.

### 2.2 Detection Algorithm
```
WHEN:
  previous_candle.close > previous_candle.open (green/bullish)
  AND current_candle.close < current_candle.open (red/bearish)
THEN:
  new_resistance_detected = TRUE
```

### 2.3 Event Properties

| Property | Type | Description | Validation Rules |
|----------|------|-------------|------------------|
| original_event_id | UUID | Unique identifier | Must be unique, auto-generated |
| event_type | String | Fixed value: 'new_resistance' | Enum: ['new_resistance'] |
| event_creation_date | DateTime | UTC timestamp of detection | Must be valid UTC datetime |
| granularity | String | Time frame | Enum: ['W', 'D', 'H4', 'H1'] |
| instrument | String | Trading pair | Must match supported instruments |
| event_price_level | Decimal | Resistance level | Formula: MAX(previous.high, current.high) |
| atr_at_event | Decimal | ATR value at event time | Must be > 0, 14-period default |
| volume_at_event | Decimal | Trading volume | Must be >= 0, nullable if unavailable |
| new_resistance_negative_rebound | Decimal | Price rejection magnitude | Formula: current.close - current.high, must be < 0 |
| new_resistance_negative_rebound_in_atr | Decimal | Normalized rejection | Formula: rebound / atr_at_event, handle divide-by-zero |
| day_of_week | Integer | Day number | Range: 0-6 (Monday=0) |
| hour_of_day | Integer | Hour in UTC | Range: 0-23 |

## 3. Data Architecture

### 3.1 Database Schema

#### Table: new_resistance_events
```sql
CREATE TABLE new_resistance_events (
    original_event_id UUID PRIMARY KEY,
    event_type VARCHAR(20) NOT NULL CHECK (event_type = 'new_resistance'),
    event_creation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    granularity VARCHAR(2) NOT NULL CHECK (granularity IN ('W', 'D', 'H4', 'H1')),
    instrument VARCHAR(10) NOT NULL,
    event_price_level DECIMAL(18,6) NOT NULL,
    atr_at_event DECIMAL(18,6) NOT NULL CHECK (atr_at_event > 0),
    volume_at_event DECIMAL(18,2),
    new_resistance_negative_rebound DECIMAL(18,6) NOT NULL CHECK (new_resistance_negative_rebound <= 0),
    new_resistance_negative_rebound_in_atr DECIMAL(18,6) NOT NULL,
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    hour_of_day SMALLINT NOT NULL CHECK (hour_of_day BETWEEN 0 AND 23),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_instrument_granularity (instrument, granularity),
    INDEX idx_event_creation_date (event_creation_date),
    INDEX idx_price_level (event_price_level)
);
```

#### Table: support_and_resistance_master
```sql
CREATE TABLE support_and_resistance_master (
    id UUID PRIMARY KEY,
    original_event_id UUID NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    -- All columns from new_resistance_events plus:
    last_test_date TIMESTAMP WITH TIME ZONE,
    test_count INTEGER DEFAULT 0,
    breach_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'breached', 'expired')),
    FOREIGN KEY (original_event_id) REFERENCES new_resistance_events(original_event_id)
);
```

### 3.2 Data Source Configuration

**Firestore Connection:**
```python
{
    "project_id": "dezoomcamp23",
    "collection": "market_data",
    "credentials": "path/to/service-account.json",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0
}
```

## 4. Feature Engineering Specifications

### 4.1 Distance-Based Features

| Feature | Formula | Edge Cases |
|---------|---------|------------|
| distance_from_last_new_resistance | current.level - previous.level | First event: NULL |
| new_resistance_distance_velocity | current_distance - previous_distance | < 2 events: NULL |
| distance_from_last_resistance_in_atr | distance / atr_at_event | ATR = 0: NULL |

### 4.2 Time-Based Features

| Feature | Formula | Update Frequency |
|---------|---------|------------------|
| time_between_new_and_last_new_resistance | current.time - previous.time (hours) | On new event |
| double_time_between_new_resistance | Compare last two time intervals | On new event |
| time_since_new_resistance | NOW() - last_event.time (hours) | Every snapshot |

### 4.3 Pattern Features

| Feature | Algorithm | Output Format |
|---------|-----------|---------------|
| new_resistance_pattern | IF distance > 0 THEN 'HH' ELSE 'LH' | String enum |
| 3_levels_sequence_encoder | Convert last 3 patterns to binary | e.g., "101" |
| 4_levels_sequence_encoder | Convert last 4 patterns to binary | e.g., "1011" |
| 5_levels_sequence_encoder | Convert last 5 patterns to binary | e.g., "10110" |
| 6_levels_sequence_encoder | Convert last 6 patterns to binary | e.g., "101101" |

### 4.4 Advanced Sequence Analysis

```python
def encode_sequence_full(sequence: List[float]) -> Dict:
    """
    Full encoding of distance sequence with all features
    
    Args:
        sequence: List of last 4 distance_from_last_new_resistance values in ATR
    
    Returns:
        Dictionary with encoded features
    """
    if not sequence or len(sequence) == 0:
        return {'no_data': 1, 'error': 'Empty sequence'}
    
    features = {
        'last': sequence[-1] if sequence else None,
        'count': len(sequence)
    }
    
    if len(sequence) >= 2:
        features['change'] = sequence[-1] - sequence[0]
        features['change_rate'] = features['change'] / abs(sequence[0]) if sequence[0] != 0 else 0
        features['final_velocity'] = sequence[-1] - sequence[-2]
        
    if len(sequence) >= 3:
        velocity1 = sequence[-2] - sequence[-3]
        velocity2 = sequence[-1] - sequence[-2]
        features['acceleration'] = velocity2 - velocity1
        features['curvature'] = abs(features['acceleration']) / max(abs(velocity1), 1)
        
    # Derived flags
    features['is_accelerating'] = 1 if features.get('acceleration', 0) > 0 else 0
    features['is_geometric_decay'] = 1 if all(abs(sequence[i]) < abs(sequence[i-1]) 
                                             for i in range(1, len(sequence))) else 0
    features['urgency_level'] = min(3, max(1, int(abs(features.get('last', 0)) * 3)))
    
    return features
```

### 4.5 Volume Features

| Feature | Formula | Null Handling |
|---------|---------|---------------|
| volume_roc | (current.volume - previous.volume) / previous.volume | If previous = 0: NULL |
| double_volume_roc | current_roc - previous_roc | < 2 ROCs: NULL |
| volume_classification | IF double_roc > 0 THEN 'accelerating' ELSE 'decelerating' | String |

## 5. Performance Requirements

### 5.1 Processing Performance

| Mode | Requirement | Measurement |
|------|-------------|-------------|
| Batch Processing | < 10 minutes for 140,000 candles | End-to-end time |
| Spike Processing | < 1 second per update cycle | 95th percentile |
| Event Detection | < 100ms per candle | Average latency |
| Feature Calculation | < 50ms per event | Average latency |
| Database Write | < 200ms per batch (100 records) | 95th percentile |

### 5.2 UI Performance

| Component | Requirement | Measurement |
|-----------|-------------|-------------|
| Events Table Load | < 2 seconds for 1000 records | First meaningful paint |
| Features Table Load | < 2 seconds for 1000 records | First meaningful paint |
| Filter Application | < 500ms | Response time |
| Export to CSV | < 5 seconds for 10,000 records | Download start |

## 6. Error Handling & Recovery

### 6.1 Data Source Errors

| Error Type | Detection | Recovery Action |
|------------|-----------|-----------------|
| Firestore Connection Failure | Connection timeout > 30s | Retry 3x with exponential backoff |
| Missing Candle Data | Gap in timestamps | Log warning, skip processing |
| Invalid OHLC Values | Negative prices, H < L | Log error, quarantine record |
| ATR Calculation Error | Division by zero | Use previous valid ATR |

### 6.2 Processing Errors

| Error Type | Detection | Recovery Action |
|------------|-----------|-----------------|
| Duplicate Event | Same timestamp & instrument | Skip, log as duplicate |
| Feature Calculation Failure | Exception in calculation | Set feature to NULL, log error |
| Database Write Failure | Transaction rollback | Retry 3x, then dead letter queue |
| Memory Overflow | > 80% heap usage | Reduce batch size by 50% |

## 7. Acceptance Criteria

### 7.1 Event Detection Accuracy

- [ ] Correctly identifies 95% of manual resistance levels marked by expert traders
- [ ] False positive rate < 10%
- [ ] Detects events within 1 candle of occurrence
- [ ] Handles all 29 instruments × 4 granularities

### 7.2 Data Quality

- [ ] No duplicate events for same timestamp/instrument
- [ ] All required fields populated (non-nullable)
- [ ] ATR values within 3 standard deviations of historical mean
- [ ] Event timestamps align with candle boundaries

### 7.3 System Reliability

- [ ] 99.5% uptime for spike processing
- [ ] < 0.1% data loss rate
- [ ] Automatic recovery from transient failures
- [ ] Complete audit trail for all events

## 8. Testing Scenarios

### 8.1 Unit Tests

```python
test_cases = [
    {
        "name": "test_basic_resistance_detection",
        "input": {
            "prev_candle": {"open": 1.0850, "high": 1.0860, "low": 1.0840, "close": 1.0855},
            "curr_candle": {"open": 1.0855, "high": 1.0865, "low": 1.0845, "close": 1.0848},
            "atr": 0.0010
        },
        "expected": {
            "detected": True,
            "price_level": 1.0865,
            "rebound": -0.0017,
            "rebound_in_atr": -1.7
        }
    },
    {
        "name": "test_no_resistance_both_green",
        "input": {
            "prev_candle": {"open": 1.0850, "high": 1.0860, "low": 1.0840, "close": 1.0855},
            "curr_candle": {"open": 1.0855, "high": 1.0865, "low": 1.0850, "close": 1.0862},
            "atr": 0.0010
        },
        "expected": {"detected": False}
    }
]
```

### 8.2 Integration Tests

- Database connection with retry logic
- End-to-end event detection pipeline
- Feature calculation with missing data
- Concurrent processing of multiple instruments

### 8.3 Performance Tests

- Load test: 1 million candles in batch mode
- Stress test: 116 concurrent instrument streams
- Spike test: Sudden 10x volume increase
- Endurance test: 7-day continuous operation

## 9. Monitoring & Operations

### 9.1 Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Events Detected per Hour | 10-50 per instrument | < 5 or > 100 |
| Processing Latency (p95) | < 1 second | > 2 seconds |
| Feature Calculation Success Rate | > 99.9% | < 99% |
| Database Write Queue Depth | < 1000 | > 5000 |
| Memory Usage | < 70% | > 85% |

### 9.2 Operational Procedures

**Daily Checks:**
- Verify all scheduled jobs completed
- Review error logs for patterns
- Check data quality metrics
- Validate feature distributions

**Weekly Maintenance:**
- Database vacuum and reindex
- Clear old logs (> 30 days)
- Review and optimize slow queries
- Update ATR calculation parameters if needed

## 10. Security & Compliance

### 10.1 Access Control
- Service accounts for Firestore access
- Role-based access for UI (Viewer, Analyst, Admin)
- API key rotation every 90 days
- Audit logging for all data modifications

### 10.2 Data Protection
- Encryption at rest for database
- TLS for all network communication
- No PII stored in event tables
- Data retention: 2 years for events, 5 years for aggregated features

## 11. Deployment Configuration

### 11.1 Environment Variables

```yaml
# Database
DB_HOST: ${DB_HOST}
DB_PORT: 5432
DB_NAME: resistance_events
DB_USER: ${DB_USER}
DB_PASSWORD: ${DB_PASSWORD}
DB_POOL_SIZE: 20

# Firestore
GCP_PROJECT_ID: dezoomcamp23
GCP_CREDENTIALS_PATH: /secrets/gcp-credentials.json

# Processing
BATCH_SIZE: 1000
MAX_WORKERS: 4
ATR_PERIOD: 14
PROCESSING_MODE: ${PROCESSING_MODE} # batch|spike

# Monitoring
PROMETHEUS_PORT: 9090
LOG_LEVEL: INFO
```

### 11.2 Resource Requirements

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Batch Processor | 4 cores | 8 GB | 50 GB |
| Spike Processor | 2 cores | 4 GB | 10 GB |
| Database | 8 cores | 16 GB | 500 GB SSD |
| UI Server | 2 cores | 2 GB | 5 GB |

## 12. Success Metrics

### 12.1 Business Metrics
- Number of profitable trades using resistance levels
- Reduction in false breakout trades
- Time saved in manual chart analysis
- User adoption rate

### 12.2 Technical Metrics
- System availability: > 99.5%
- Event detection accuracy: > 95%
- Processing latency: < 1 second (p95)
- Data completeness: > 99.9%

## 13. Future Enhancements

### Phase 4 (Next Quarter)
- Support levels detection (mirror of resistance)
- Multi-timeframe confluence analysis
- Machine learning for pattern prediction
- Mobile app notifications

### Phase 5 (Future)
- Options flow integration
- Sentiment analysis correlation
- Automated trading signals
- Backtesting framework

## Appendix A: Supported Instruments

```python
SUPPORTED_INSTRUMENTS = [
    'EUR_USD', 'USD_THB', 'GBP_PLN', 'CAD_CHF', 'EUR_NOK',
    'USD_CZK', 'USD_SEK', 'USD_RON', 'USD_HUF', 'AUD_HKD',
    'USD_HKD', 'USD_DKK', 'USD_PHP', 'USD_TRY', 'EUR_PLN',
    'SGD_JPY', 'USD_PLN', 'USD_MXN', 'USD_ZAR', 'GBP_CHF',
    'NZD_JPY', 'CHF_JPY', 'CAD_JPY', 'EUR_JPY', 'AUD_JPY',
    'EUR_CHF', 'EUR_GBP', 'GBP_USD', 'EUR_AUD'
]
```

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| ATR | Average True Range - volatility indicator |
| Resistance | Price level where selling pressure increases |
| HH | Higher High - new high above previous high |
| LH | Lower High - new high below previous high |
| ROC | Rate of Change - percentage change metric |
| Spike Mode | Real-time processing triggered on schedule |
| Batch Mode | Historical data processing in bulk |

---

**Document Version**: 1.1  
**Last Updated**: 2025-08-15  
**Status**: Ready for Development  
**Quality Score Target**: ≥ 7.0