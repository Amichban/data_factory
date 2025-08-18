# US-011: Distance-Based Features

**Epic**: Feature Engineering  
**Priority**: P1 (Important)  
**Estimate**: 5 points  
**Dependencies**: US-003, US-009  

## User Story

**As a** System  
**I want to** calculate distance-based features from resistance events  
**So that** traders can understand price level relationships and momentum

## Acceptance Criteria

- [ ] Calculate distance_from_last_new_resistance
- [ ] Calculate new_resistance_distance_velocity
- [ ] Calculate distance_from_last_resistance_in_atr
- [ ] Handle first event (no previous reference)
- [ ] Store features in dedicated table
- [ ] Update features with each new event
- [ ] Support all instruments and granularities
- [ ] Maintain calculation history

## Technical Requirements

### Feature Calculations
```python
def calculate_distance_features(current_event, previous_events):
    features = {}
    
    if previous_events:
        last_event = previous_events[-1]
        
        # Distance in price
        features['distance_from_last'] = (
            current_event.price_level - last_event.price_level
        )
        
        # Distance in ATR units
        features['distance_in_atr'] = (
            features['distance_from_last'] / current_event.atr_at_event
            if current_event.atr_at_event > 0 else None
        )
        
        # Velocity (change in distance)
        if len(previous_events) >= 2:
            prev_distance = last_event.features.get('distance_from_last')
            if prev_distance:
                features['distance_velocity'] = (
                    features['distance_from_last'] - prev_distance
                )
    
    return features
```

## Definition of Done

- [ ] All distance features calculating correctly
- [ ] Edge cases handled
- [ ] Performance optimized
- [ ] Tests cover all scenarios
- [ ] Documentation with examples