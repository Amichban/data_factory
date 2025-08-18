# US-007: Spike Mode Real-time Processing

**Epic**: Processing Pipeline  
**Priority**: P0 (Core)  
**Estimate**: 8 points  
**Dependencies**: US-001, US-002, US-003, US-004, US-006  

## User Story

**As a** System  
**I want to** process new market data in real-time as it arrives  
**So that** events are detected immediately and traders receive timely alerts

## Acceptance Criteria

- [ ] Trigger processing based on granularity schedule
- [ ] H1: Every hour at :05 past
- [ ] H4: At 1:05, 5:05, 9:05, 13:05, 17:05, 21:05 UTC
- [ ] D: Daily at 21:05 UTC
- [ ] W: Weekly Sunday at 21:05 UTC
- [ ] Check last processed timestamp
- [ ] Fetch only new data since last run
- [ ] Complete processing in < 1 second
- [ ] Update all events and features incrementally
- [ ] Support cloud function deployment
- [ ] Implement idempotency (safe to run multiple times)
- [ ] Send notifications for significant events

## Technical Requirements

### Scheduler Configuration
```yaml
schedulers:
  H1:
    cron: "5 * * * *"  # Every hour at :05
    timeout: 30
    retry: 2
  H4:
    cron: "5 1,5,9,13,17,21 * * *"  # Every 4 hours
    timeout: 30
    retry: 2
  D:
    cron: "5 21 * * *"  # Daily at 21:05 UTC
    timeout: 60
    retry: 2
  W:
    cron: "5 21 * * 0"  # Sunday at 21:05 UTC
    timeout: 60
    retry: 2
```

### Processing Function
```python
def spike_process(event, context):
    """
    Cloud function for real-time processing
    """
    # 1. Extract trigger info
    granularity = event.get('granularity')
    
    # 2. Get last processed timestamp
    last_processed = get_last_processed(granularity)
    
    # 3. Fetch new candles
    new_candles = fetch_new_candles(
        since=last_processed,
        granularity=granularity,
        instruments=ACTIVE_INSTRUMENTS
    )
    
    if not new_candles:
        return {'status': 'no_new_data'}
    
    # 4. Process each instrument
    results = []
    for instrument, candles in new_candles.items():
        # Calculate ATR
        atr = calculate_incremental_atr(instrument, candles)
        
        # Detect events
        events = detect_events(candles, atr)
        
        # Calculate features
        if events:
            features = calculate_incremental_features(events)
            store_events_and_features(events, features)
            
            # Send notifications
            notify_significant_events(events)
            
        results.append({
            'instrument': instrument,
            'candles_processed': len(candles),
            'events_detected': len(events)
        })
    
    # 5. Update last processed
    update_last_processed(granularity, new_candles.latest_timestamp)
    
    return {
        'status': 'success',
        'processed': results,
        'duration_ms': context.elapsed_ms
    }
```

### State Management
```python
# Store processing state
processing_state = {
    "granularity": "H1",
    "last_processed": "2025-01-15T14:00:00Z",
    "last_run": "2025-01-15T14:05:03Z",
    "consecutive_failures": 0,
    "total_events_detected": 12453
}
```

### Notification Criteria
- New resistance at key psychological level (round numbers)
- Multiple instruments showing resistance at same time
- Unusual volume spike with resistance
- Pattern completion (HH-HH-HH or LH-LH-LH)

## Test Scenarios

1. **Normal Processing**: New H1 candle arrives and processed
2. **No New Data**: Run when no new candles available
3. **Multiple Events**: Several instruments trigger simultaneously
4. **Idempotency**: Run twice with same data
5. **Performance**: Process 29 instruments in < 1 second
6. **Error Recovery**: Database temporarily unavailable
7. **Notification Test**: Verify alerts sent correctly
8. **DST Transition**: Handle daylight saving time changes

## Definition of Done

- [ ] Cloud functions deployed for each granularity
- [ ] Schedulers configured and tested
- [ ] Processing < 1 second for all instruments
- [ ] Idempotency verified
- [ ] State management working
- [ ] Error handling and retries
- [ ] Notifications configured
- [ ] Monitoring and alerting setup
- [ ] Documentation for operations
- [ ] Integration tests in cloud environment
- [ ] Rollback procedure documented

## UI/UX Notes

### Real-time Updates
- WebSocket connection for live updates
- Dashboard shows "Last Updated" timestamp
- Visual indicator when processing
- Alert badge for new events

### Monitoring Dashboard
```
Spike Processing Status
======================
H1:  ✓ Last run: 2 min ago  | Next: 58 min
H4:  ✓ Last run: 1 hr ago   | Next: 3 hrs
D:   ✓ Last run: 4 hrs ago  | Next: 20 hrs
W:   ✓ Last run: 2 days ago | Next: 5 days

Recent Events: 24
Active Alerts: 3
System Health: Healthy
```

## Related Stories

- US-006: Batch Processing (shares processing logic)
- US-008: Operations Monitoring (tracks spike runs)
- US-009: Notification System (sends alerts)
- US-010: Data Quality Checks (validates results)