# US-012: Time-Based Features

**Epic**: Feature Engineering  
**Priority**: P1 (Important)  
**Estimate**: 5 points  
**Dependencies**: US-003, US-009  

## User Story

**As a** System  
**I want to** calculate temporal features from resistance events  
**So that** traders can understand event frequency and timing patterns

## Acceptance Criteria

- [ ] Calculate time_between_new_and_last_new_resistance (hours)
- [ ] Calculate double_time_between_new_resistance pattern
- [ ] Calculate time_since_new_resistance (incremental)
- [ ] Update time_since at each market snapshot
- [ ] Handle timezone conversions properly
- [ ] Track day_of_week and hour_of_day patterns
- [ ] Identify clustering in time
- [ ] Support different time units (minutes, hours, days)

## Technical Requirements

### Feature Calculations
```python
def calculate_time_features(current_event, previous_events, current_time):
    features = {}
    
    if previous_events:
        last_event = previous_events[-1]
        
        # Time between events
        time_diff = current_event.timestamp - last_event.timestamp
        features['time_between_events_hours'] = time_diff.total_seconds() / 3600
        
        # Frequency analysis
        if len(previous_events) >= 2:
            prev_time_diff = last_event.features.get('time_between_events_hours')
            if prev_time_diff:
                ratio = features['time_between_events_hours'] / prev_time_diff
                features['frequency_pattern'] = (
                    'accelerating' if ratio < 0.8 else
                    'decelerating' if ratio > 1.2 else
                    'stable'
                )
    
    # Time since last event (updated continuously)
    if previous_events:
        time_since = current_time - previous_events[-1].timestamp
        features['time_since_last_hours'] = time_since.total_seconds() / 3600
    
    return features
```

## Definition of Done

- [ ] All time features calculating correctly
- [ ] Timezone handling verified
- [ ] Incremental updates working
- [ ] Performance optimized
- [ ] Tests cover edge cases