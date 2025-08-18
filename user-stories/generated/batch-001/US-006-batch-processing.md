# US-006: Batch Processing Mode

**Epic**: Processing Pipeline  
**Priority**: P0 (Core)  
**Estimate**: 8 points  
**Dependencies**: US-001, US-002, US-003, US-004  

## User Story

**As a** Data Engineer  
**I want to** backfill historical events and features  
**So that** I have complete historical data for analysis and model training

## Acceptance Criteria

- [ ] Process up to 140,000 H1 candles per instrument
- [ ] Support all 29 instruments × 4 granularities
- [ ] Vectorize calculations for performance
- [ ] Complete processing in < 10 minutes locally
- [ ] Provide progress reporting (% complete, ETA)
- [ ] Support interruption and resume from checkpoint
- [ ] Handle missing data gracefully
- [ ] Generate summary statistics after completion
- [ ] Support export/import for cloud deployment
- [ ] Validate data integrity after processing

## Technical Requirements

### Processing Pipeline
```python
class BatchProcessor:
    def __init__(self, config):
        self.batch_size = config.get('batch_size', 1000)
        self.max_workers = config.get('max_workers', 4)
        self.checkpoint_interval = 10000
        
    def process_instrument(self, instrument, granularity):
        """
        Process historical data for one instrument
        """
        # 1. Load checkpoint if exists
        checkpoint = self.load_checkpoint(instrument, granularity)
        
        # 2. Fetch data in batches
        for batch in self.fetch_batches(start=checkpoint):
            # 3. Calculate ATR (vectorized)
            atr_values = self.calculate_atr_vectorized(batch)
            
            # 4. Detect events (vectorized)
            events = self.detect_events_vectorized(batch, atr_values)
            
            # 5. Calculate features
            features = self.calculate_features_vectorized(events)
            
            # 6. Bulk insert to database
            self.bulk_insert(events, features)
            
            # 7. Update checkpoint
            self.save_checkpoint(instrument, granularity, batch.last_timestamp)
            
            # 8. Report progress
            self.report_progress(batch.progress)
```

### Performance Optimizations
- Use numpy/pandas for vectorization
- Implement chunked processing (1000 records/chunk)
- Parallel processing for independent instruments
- Connection pooling for database
- Memory-mapped files for large datasets

### Checkpoint System
```json
{
  "instrument": "EUR_USD",
  "granularity": "H1",
  "last_processed": "2024-12-31T23:00:00Z",
  "events_processed": 45230,
  "features_calculated": 45230,
  "errors": [],
  "status": "in_progress"
}
```

## Test Scenarios

1. **Full Backfill**: Process 5 years of EUR_USD H1 data
2. **Resume from Checkpoint**: Interrupt and resume
3. **Parallel Processing**: Run 4 instruments simultaneously
4. **Missing Data**: Handle gaps in market data
5. **Performance**: Verify < 10 minute target
6. **Memory Usage**: Monitor RAM consumption
7. **Data Validation**: Compare sample with manual calculation
8. **Error Recovery**: Simulate database connection loss

## Definition of Done

- [ ] Vectorized implementation complete
- [ ] Performance target achieved (< 10 min)
- [ ] Checkpoint system working
- [ ] Progress reporting accurate
- [ ] Parallel processing tested
- [ ] Memory usage optimized (< 4GB)
- [ ] Export/import functionality
- [ ] Summary statistics generated
- [ ] Documentation with examples
- [ ] Integration tests pass
- [ ] Data validation scripts created

## UI/UX Notes

### Progress Display
```
Processing EUR_USD H1...
[████████████████░░░░] 80% | 112,000/140,000 | ETA: 2:15
Events detected: 8,453
Features calculated: 8,453
Errors: 0
```

### Summary Report
```
Batch Processing Complete
========================
Duration: 8:34
Instruments: 29
Total Candles: 4,060,000
Events Detected: 245,123
Features Generated: 2,451,230
Data Quality Score: 99.8%
```

## Related Stories

- US-007: Spike Mode Processing (uses same pipeline)
- US-008: Feature Calculation (integrated here)
- US-009: Data Quality Checks (validation)