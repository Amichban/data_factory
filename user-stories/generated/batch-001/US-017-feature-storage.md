# US-017: Feature Storage Schema

**Epic**: Feature Engineering  
**Priority**: P1 (Important)  
**Estimate**: 2 points  
**Dependencies**: US-004, US-011  

## User Story

**As a** Data Engineer  
**I want to** create optimized storage for calculated features  
**So that** features can be efficiently queried and analyzed

## Acceptance Criteria

- [ ] Design features table schema
- [ ] Support all feature types (distance, time, pattern, volume)
- [ ] Optimize for time-series queries
- [ ] Implement proper indexing
- [ ] Support feature versioning
- [ ] Enable fast joins with events table

## Technical Requirements

### Schema Design
```sql
CREATE TABLE resistance_features (
    feature_id UUID PRIMARY KEY,
    event_id UUID REFERENCES new_resistance_events(original_event_id),
    feature_set_version INT DEFAULT 1,
    
    -- Distance features
    distance_from_last DECIMAL(18,6),
    distance_in_atr DECIMAL(18,6),
    distance_velocity DECIMAL(18,6),
    
    -- Time features
    time_between_events_hours DECIMAL(18,2),
    time_since_last_hours DECIMAL(18,2),
    frequency_pattern VARCHAR(20),
    
    -- Pattern features
    pattern_3_level VARCHAR(3),
    pattern_4_level VARCHAR(4),
    pattern_5_level VARCHAR(5),
    pattern_6_level VARCHAR(6),
    
    -- Volume features
    volume_roc DECIMAL(18,6),
    volume_trend VARCHAR(20),
    
    -- Advanced features
    urgency_level SMALLINT,
    confidence_score DECIMAL(5,4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_features_event (event_id),
    INDEX idx_features_version (feature_set_version)
);
```

## Definition of Done

- [ ] Schema created and optimized
- [ ] Indexes verified for performance
- [ ] Migration scripts ready
- [ ] Documentation complete