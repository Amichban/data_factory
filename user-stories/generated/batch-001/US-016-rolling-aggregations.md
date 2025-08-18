# US-016: Rolling Aggregations

**Epic**: Feature Engineering  
**Priority**: P2 (Nice to have)  
**Estimate**: 3 points  
**Dependencies**: US-003  

## User Story

**As a** System  
**I want to** calculate rolling window aggregations  
**So that** traders can see event density and trends over time

## Acceptance Criteria

- [ ] Calculate sum_of_new_resistances_last_30_periods
- [ ] Support configurable window sizes (10, 20, 30, 50 periods)
- [ ] Update efficiently with new data
- [ ] Handle edge cases at data boundaries
- [ ] Calculate rolling mean, std, min, max
- [ ] Identify periods of high/low activity

## Technical Requirements

### Rolling Calculations
```python
def calculate_rolling_features(events, window_sizes=[10, 20, 30]):
    features = {}
    
    for window in window_sizes:
        if len(events) >= window:
            recent = events[-window:]
            
            features[f'count_last_{window}'] = len(recent)
            features[f'avg_distance_last_{window}'] = np.mean(
                [e.features.get('distance_from_last', 0) for e in recent]
            )
            features[f'volatility_last_{window}'] = np.std(
                [e.price_level for e in recent]
            )
    
    return features
```

## Definition of Done

- [ ] Rolling calculations accurate
- [ ] Performance optimized
- [ ] Multiple windows supported
- [ ] Tests verify correctness