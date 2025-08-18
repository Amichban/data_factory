# US-015: Advanced Sequence Analysis

**Epic**: Feature Engineering  
**Priority**: P2 (Nice to have)  
**Estimate**: 8 points  
**Dependencies**: US-011, US-012  

## User Story

**As a** System  
**I want to** perform advanced sequence analysis on resistance distances  
**So that** traders can understand momentum, acceleration, and urgency patterns

## Acceptance Criteria

- [ ] Implement encode_sequence_full algorithm
- [ ] Calculate change and change_rate
- [ ] Calculate final_velocity
- [ ] Calculate acceleration and curvature
- [ ] Determine is_accelerating flag
- [ ] Determine is_geometric_decay flag
- [ ] Calculate urgency_level (1-3 scale)
- [ ] Handle sequences of varying lengths (1-4)
- [ ] Provide confidence scores

## Technical Requirements

### Advanced Analysis Implementation
```python
def encode_sequence_full(sequence: List[float]) -> Dict:
    """
    Full encoding of distance sequence with advanced features
    
    Args:
        sequence: Last 4 distance_from_last_new_resistance values in ATR
    
    Returns:
        Dictionary with encoded features including physics-based metrics
    """
    if not sequence:
        return {'no_data': 1, 'error': 'Empty sequence'}
    
    features = {
        'last': sequence[-1],
        'count': len(sequence),
        'mean': np.mean(sequence),
        'std': np.std(sequence) if len(sequence) > 1 else 0
    }
    
    if len(sequence) >= 2:
        # First order: velocity
        features['change'] = sequence[-1] - sequence[0]
        features['change_rate'] = (
            features['change'] / abs(sequence[0]) 
            if sequence[0] != 0 else 0
        )
        features['final_velocity'] = sequence[-1] - sequence[-2]
        
    if len(sequence) >= 3:
        # Second order: acceleration
        velocity1 = sequence[-2] - sequence[-3]
        velocity2 = sequence[-1] - sequence[-2]
        features['acceleration'] = velocity2 - velocity1
        
        # Curvature (rate of direction change)
        features['curvature'] = (
            abs(features['acceleration']) / max(abs(velocity1), 0.0001)
        )
        
    if len(sequence) >= 4:
        # Third order: jerk (rate of acceleration change)
        accel1 = (sequence[-2] - sequence[-3]) - (sequence[-3] - sequence[-4])
        accel2 = (sequence[-1] - sequence[-2]) - (sequence[-2] - sequence[-3])
        features['jerk'] = accel2 - accel1
    
    # Pattern flags
    features['is_accelerating'] = 1 if features.get('acceleration', 0) > 0 else 0
    features['is_geometric_decay'] = (
        1 if all(abs(sequence[i]) < abs(sequence[i-1]) * 0.9 
                for i in range(1, len(sequence))) 
        else 0
    )
    
    # Urgency based on last value and trend
    urgency = min(3, max(1, int(abs(features.get('last', 0)) * 3)))
    if features.get('is_accelerating'):
        urgency = min(3, urgency + 1)
    features['urgency_level'] = urgency
    
    # Confidence score based on sequence length and consistency
    confidence = len(sequence) / 4.0  # Max 1.0 for 4 elements
    if features['std'] < features.get('mean', 1) * 0.2:  # Low variance
        confidence *= 1.2
    features['confidence'] = min(1.0, confidence)
    
    return features
```

## Definition of Done

- [ ] Algorithm implemented with all metrics
- [ ] Edge cases handled
- [ ] Performance optimized for real-time
- [ ] Comprehensive test coverage
- [ ] Documentation with examples
- [ ] Visualization of patterns