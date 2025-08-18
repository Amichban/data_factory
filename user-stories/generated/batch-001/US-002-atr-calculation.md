# US-002: Implement ATR Calculation

**Epic**: Data Integration & Core  
**Priority**: P0 (Core)  
**Estimate**: 3 points  
**Dependencies**: US-001 (Firestore Integration)  

## User Story

**As a** System  
**I want to** calculate Average True Range (ATR) for all instruments  
**So that** I can normalize event measurements and detect significant price movements

## Acceptance Criteria

- [ ] Calculate 14-period ATR by default
- [ ] Support configurable period (7, 14, 21 periods)
- [ ] Handle all granularities (H1, H4, D, W)
- [ ] Process all 29 supported instruments
- [ ] Update ATR with each new candle
- [ ] Store historical ATR values
- [ ] Handle initialization period correctly (need 14+ candles)
- [ ] Prevent division by zero errors
- [ ] Cache recent ATR values for performance
- [ ] Vectorize calculations for batch processing

## Technical Requirements

### ATR Formula
```python
def calculate_atr(high, low, close_prev, period=14):
    """
    True Range = MAX(
        high - low,
        abs(high - close_prev),
        abs(low - close_prev)
    )
    ATR = Moving Average of True Range over period
    """
    # Initial ATR: Simple average of first 'period' TR values
    # Subsequent: ATR = ((prev_ATR * (period-1)) + current_TR) / period
```

### Performance Requirements
- Single ATR calculation: <1ms
- Batch (1000 candles): <50ms
- Memory usage: <100MB for all instruments

### Edge Cases
- First candle: TR = high - low
- Missing previous close: Skip calculation
- Negative values: Log error, use previous ATR
- Zero ATR: Use minimum threshold (0.0001)

## Test Scenarios

1. **Basic Calculation**: Verify ATR formula correctness
2. **Initialization**: Test with exactly 14 candles
3. **Continuous Update**: Add new candles and verify updates
4. **Edge Cases**: Test with gaps, missing data
5. **Performance**: Process 140k candles in <1 second
6. **Multiple Instruments**: Concurrent ATR calculations

## Definition of Done

- [ ] ATR calculation matches expected values (±0.0001)
- [ ] Unit tests cover all edge cases
- [ ] Performance benchmarks met
- [ ] Vectorized implementation complete
- [ ] Cache mechanism working
- [ ] Documentation includes examples
- [ ] Integration with data pipeline verified

## UI/UX Notes

ATR values should be displayed in:
- Event details (for normalization context)
- Technical indicators panel
- Feature calculation views

## Related Stories

- US-001: Firestore Integration (provides data)
- US-003: Core Event Detection (uses ATR)
- US-006: Distance Features (uses ATR for normalization)