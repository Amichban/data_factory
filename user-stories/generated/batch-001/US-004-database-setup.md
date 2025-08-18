# US-004: Database Setup and Schema

**Epic**: Data Storage & Management  
**Priority**: P0 (Core)  
**Estimate**: 3 points  
**Dependencies**: None  

## User Story

**As a** Data Engineer  
**I want to** create database tables for storing events and features  
**So that** all detected events are persisted and queryable

## Acceptance Criteria

- [ ] Create new_resistance_events table with all required columns
- [ ] Create support_and_resistance_master table
- [ ] Set up proper indexes for query performance
- [ ] Add foreign key constraints
- [ ] Implement partitioning by instrument/granularity
- [ ] Add created_at/updated_at timestamps
- [ ] Set up data retention policies (2 years events, 5 years features)
- [ ] Create database backup strategy
- [ ] Document schema migrations process
- [ ] Support 500GB+ data growth

## Technical Requirements

### Schema Definition
```sql
-- Main events table
CREATE TABLE new_resistance_events (
    original_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(20) NOT NULL DEFAULT 'new_resistance',
    event_creation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    granularity VARCHAR(2) NOT NULL CHECK (granularity IN ('W','D','H4','H1')),
    instrument VARCHAR(10) NOT NULL,
    event_price_level DECIMAL(18,6) NOT NULL CHECK (event_price_level > 0),
    atr_at_event DECIMAL(18,6) NOT NULL CHECK (atr_at_event > 0),
    volume_at_event DECIMAL(18,2),
    new_resistance_negative_rebound DECIMAL(18,6) NOT NULL CHECK (new_resistance_negative_rebound <= 0),
    new_resistance_negative_rebound_in_atr DECIMAL(18,6) NOT NULL,
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    hour_of_day SMALLINT NOT NULL CHECK (hour_of_day BETWEEN 0 AND 23),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_events_instrument_granularity 
    ON new_resistance_events(instrument, granularity);
CREATE INDEX idx_events_creation_date 
    ON new_resistance_events(event_creation_date DESC);
CREATE INDEX idx_events_price_level 
    ON new_resistance_events(event_price_level);

-- Master table for all support/resistance levels
CREATE TABLE support_and_resistance_master (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_event_id UUID NOT NULL REFERENCES new_resistance_events(original_event_id),
    event_type VARCHAR(20) NOT NULL,
    last_test_date TIMESTAMP WITH TIME ZONE,
    test_count INTEGER DEFAULT 0,
    breach_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' 
        CHECK (status IN ('active', 'breached', 'expired')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Requirements
- Insert: <10ms per record
- Bulk insert: 1000 records/second
- Query by instrument: <100ms
- Range queries: <500ms for 10k records

## Test Scenarios

1. **Schema Creation**: Verify all tables and constraints
2. **Data Insertion**: Test single and bulk inserts
3. **Query Performance**: Test indexed queries
4. **Constraint Validation**: Test CHECK constraints
5. **Foreign Keys**: Verify referential integrity
6. **Concurrent Access**: Test with multiple writers
7. **Data Growth**: Simulate 1 year of data

## Definition of Done

- [ ] All tables created with proper constraints
- [ ] Indexes optimized for query patterns
- [ ] Migration scripts versioned
- [ ] Backup strategy documented
- [ ] Performance benchmarks met
- [ ] Database monitoring configured
- [ ] Documentation complete
- [ ] Rollback procedure tested

## UI/UX Notes

Database performance directly impacts:
- Dashboard loading times
- Real-time event notifications
- Feature calculation speed

## Related Stories

- US-003: Event Detection (generates data)
- US-005: Store Events (uses schema)
- US-015: Batch Processing (bulk operations)