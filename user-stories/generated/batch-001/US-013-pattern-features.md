# US-013: Pattern Recognition Features

**Epic**: Feature Engineering  
**Priority**: P1 (Important)  
**Estimate**: 5 points  
**Dependencies**: US-011  

## User Story

**As a** System  
**I want to** identify and encode price patterns from resistance events  
**So that** traders can recognize market structure patterns

## Acceptance Criteria

- [ ] Classify patterns as HH (Higher High) or LH (Lower High)
- [ ] Implement 3-level sequence encoder (e.g., "101")
- [ ] Implement 4-level sequence encoder (e.g., "1011")
- [ ] Implement 5-level sequence encoder (e.g., "10110")
- [ ] Implement 6-level sequence encoder (e.g., "101101")
- [ ] Convert patterns to binary representation
- [ ] Identify pattern completions
- [ ] Track pattern success rates

## Technical Requirements

### Pattern Encoding
```python
def encode_pattern_sequences(events):
    """
    Encode resistance patterns as binary sequences
    HH (Higher High) = 1
    LH (Lower High) = 0
    """
    patterns = []
    
    for i in range(1, len(events)):
        if events[i].price_level > events[i-1].price_level:
            patterns.append('1')  # HH
        else:
            patterns.append('0')  # LH
    
    features = {}
    
    # Generate various length encodings
    for length in [3, 4, 5, 6]:
        if len(patterns) >= length:
            key = f'pattern_{length}_level'
            features[key] = ''.join(patterns[-length:])
            
            # Convert to decimal for ML models
            features[f'{key}_decimal'] = int(features[key], 2)
    
    return features
```

## Definition of Done

- [ ] Pattern classification accurate
- [ ] All sequence lengths working
- [ ] Binary encoding verified
- [ ] Pattern statistics tracked
- [ ] Documentation with examples