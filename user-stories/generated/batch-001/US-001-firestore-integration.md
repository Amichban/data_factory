# US-001: Setup Firestore Integration

**Epic**: Data Integration & Core  
**Priority**: P0 (Core)  
**Estimate**: 5 points  
**Dependencies**: None  

## User Story

**As a** Data Engineer  
**I want to** connect to the Firestore market data collection  
**So that** I can fetch OHLC data for event detection and analysis

## Acceptance Criteria

- [ ] Successfully authenticate with Firestore using service account credentials
- [ ] Connect to project "dezoomcamp23" 
- [ ] Query market_data collection for any instrument
- [ ] Support all 4 granularities (H1, H4, D, W)
- [ ] Handle connection timeouts (30 second timeout)
- [ ] Implement retry logic (3 attempts with exponential backoff)
- [ ] Cache connections for performance
- [ ] Log all connection attempts and failures
- [ ] Support batch queries for multiple instruments
- [ ] Return data in standardized format

## Technical Requirements

### Configuration
```python
{
    "project_id": "dezoomcamp23",
    "collection": "market_data",
    "credentials": "path/to/service-account.json",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "connection_pool_size": 10
}
```

### Data Format
```python
{
    "instrument": "EUR_USD",
    "granularity": "D",
    "timestamp": datetime,
    "candle": {
        "open": 1.08550,
        "high": 1.08780,
        "low": 1.08420,
        "close": 1.08650,
        "volume": 125000.0
    }
}
```

### Error Handling
- Connection failures: Retry with exponential backoff
- Missing data: Log warning and continue
- Invalid credentials: Alert and halt
- Rate limiting: Implement queue and throttling

## Test Scenarios

1. **Happy Path**: Connect and fetch EUR_USD daily data
2. **Connection Failure**: Simulate network timeout
3. **Invalid Credentials**: Test with wrong service account
4. **Missing Data**: Query non-existent date range
5. **Concurrent Requests**: Test connection pooling
6. **Large Batch**: Query 140k candles

## Definition of Done

- [ ] Unit tests pass with >90% coverage
- [ ] Integration test with real Firestore
- [ ] Connection pooling verified
- [ ] Error handling documented
- [ ] Performance: <100ms for single query
- [ ] Code reviewed by senior engineer
- [ ] Documentation updated

## UI/UX Notes

N/A - Backend service only

## Related Stories

- US-002: Implement ATR Calculation (requires data)
- US-003: Core Event Detection (requires data)
- US-015: Batch Processing Mode (uses this integration)