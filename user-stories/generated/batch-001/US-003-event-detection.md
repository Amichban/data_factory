# US-003: Core Event Detection

**Epic**: Event Detection Engine  
**Priority**: P0 (Core)  
**Estimate**: 8 points  
**Dependencies**: US-001, US-002  

## User Story

**As a** System  
**I want to** automatically detect new resistance events from market data  
**So that** traders can be alerted to potential reversal levels in real-time

## Acceptance Criteria

- [ ] Detect pattern: green candle followed by red candle
- [ ] Additional filter: rejection must be > 0.3 * ATR
- [ ] Generate unique UUID for each event
- [ ] Capture UTC timestamp of detection
- [ ] Calculate event_price_level = MAX(prev.high, curr.high)
- [ ] Calculate negative rebound = close - high (must be < 0)
- [ ] Normalize rebound by ATR
- [ ] Store day_of_week (0-6) and hour_of_day (0-23)
- [ ] Process all instruments and granularities
- [ ] Achieve 95% accuracy vs manual detection
- [ ] False positive rate < 10%

## Technical Requirements

### Detection Algorithm
```python
def detect_new_resistance(prev_candle, curr_candle, atr):
    """
    Detect new resistance formation
    """
    # Check pattern
    is_prev_green = prev_candle.close > prev_candle.open
    is_curr_red = curr_candle.close < curr_candle.open
    
    # Check rejection magnitude
    rejection = curr_candle.high - curr_candle.close
    is_significant = rejection > (0.3 * atr)
    
    if is_prev_green and is_curr_red and is_significant:
        return {
            'detected': True,
            'price_level': max(prev_candle.high, curr_candle.high),
            'rebound': curr_candle.close - curr_candle.high,
            'rebound_in_atr': (curr_candle.close - curr_candle.high) / atr if atr > 0 else None
        }
    return {'detected': False}
```

### Performance Requirements
- Detection latency: <100ms per candle
- Batch processing: 1000 candles/second
- Memory usage: <50MB per instrument

### Validation Rules
- Price level must be positive
- Rebound must be negative
- ATR must be > 0 for normalization
- Timestamp must align with candle boundaries

## Test Scenarios

1. **Classic Pattern**: Green to red with significant rejection
2. **No Detection**: Both green candles
3. **Small Rejection**: Pattern present but rejection < 0.3 * ATR
4. **Edge Cases**: 
   - First candle in series
   - Missing ATR value
   - Zero volume candles
5. **Accuracy Test**: Compare with 100 manually marked resistances
6. **Performance Test**: Process 1 year of H1 data

## Definition of Done

- [ ] Detection algorithm implemented and optimized
- [ ] 95% accuracy achieved on test dataset
- [ ] All event properties correctly calculated
- [ ] UUID generation working
- [ ] Timestamp handling correct for all timezones
- [ ] Integration tests with real market data
- [ ] Performance benchmarks met
- [ ] Error handling for edge cases
- [ ] Logging for all detections

## UI/UX Notes

Events should trigger:
- Real-time notification (if enabled)
- Update to events table
- Chart annotation at price level
- Feature recalculation

## Related Stories

- US-004: Store Events in Database
- US-005: Create Events Dashboard
- US-006: Calculate Distance Features