# US-014: Volume Analysis Features

**Epic**: Feature Engineering  
**Priority**: P1 (Important)  
**Estimate**: 3 points  
**Dependencies**: US-003  

## User Story

**As a** System  
**I want to** calculate volume-based features from events  
**So that** traders can understand market participation at resistance levels

## Acceptance Criteria

- [ ] Calculate volume_roc between events
- [ ] Calculate double_volume_roc pattern
- [ ] Classify volume as accelerating/decelerating
- [ ] Handle missing volume data gracefully
- [ ] Normalize by average volume
- [ ] Identify unusual volume spikes
- [ ] Compare to historical volume patterns

## Technical Requirements

### Volume Analysis
```python
def calculate_volume_features(current_event, previous_events):
    features = {}
    
    if not current_event.volume_at_event:
        return features
    
    if previous_events and previous_events[-1].volume_at_event:
        last_volume = previous_events[-1].volume_at_event
        
        # Rate of change
        features['volume_roc'] = (
            (current_event.volume_at_event - last_volume) / last_volume
            if last_volume > 0 else None
        )
        
        # Double ROC pattern
        if len(previous_events) >= 2:
            prev_roc = previous_events[-1].features.get('volume_roc')
            if prev_roc and features['volume_roc']:
                features['volume_acceleration'] = (
                    features['volume_roc'] - prev_roc
                )
                features['volume_trend'] = (
                    'accelerating' if features['volume_acceleration'] > 0
                    else 'decelerating'
                )
    
    return features
```

## Definition of Done

- [ ] Volume ROC calculating correctly
- [ ] Missing data handled
- [ ] Normalization implemented
- [ ] Tests cover all scenarios