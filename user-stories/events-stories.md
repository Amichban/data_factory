# Generated User Stories from Events Specification

## Analysis Summary
- **Identified Personas**: Data Engineer, Trader/Analyst, System Administrator, System (automated)
- **Feature Areas**: 6 main areas (Event Detection, Event Storage, Feature Engineering, UI/Visualization, Batch Processing, Real-time Processing)
- **Total Stories**: 18 stories
- **Suggested Phases**: 3 development phases

## Epic 1: Event Detection & Core Infrastructure

### US-001: Setup Market Data Integration
**As a** Data Engineer  
**I want to** connect to Firestore market data collection  
**So that** I can fetch OHLC data for event detection

**Acceptance Criteria:**
- [ ] Configure Firestore client with credentials for project "dezoomcamp23"
- [ ] Implement data fetcher for market_data collection
- [ ] Support querying by instrument (EUR_USD, etc.)
- [ ] Support querying by granularity (H1, H4, D, W)
- [ ] Handle missing data gracefully
- [ ] Implement retry logic for connection failures

**Priority:** P0 (Core)  
**Estimate:** 5 points  
**Dependencies:** None  
**Technical Notes:**
- Use google-cloud-firestore SDK
- Implement connection pooling
- Cache frequently accessed data

---

### US-002: Detect New Resistance Events
**As a** System  
**I want to** automatically detect new resistance events from market data  
**So that** traders can be alerted to potential trading levels

**Acceptance Criteria:**
- [ ] Identify pattern: green candle followed by red candle
- [ ] Calculate event_price_level = max(high of previous candle, high of current candle)
- [ ] Generate unique event_id for each detection
- [ ] Capture event_creation_date in UTC
- [ ] Calculate new_resistance_negative_rebound = close - high
- [ ] Calculate new_resistance_negative_rebound_in_atr = (close - high) / atr_at_event
- [ ] Handle divide by zero for ATR calculations
- [ ] Store day_of_week and hour_of_day

**Priority:** P0 (Core)  
**Estimate:** 8 points  
**Dependencies:** US-001  
**Technical Notes:**
- Implement pattern detection algorithm
- Need ATR indicator calculation
- Volume data capture at event time

---

### US-003: Calculate ATR Indicator
**As a** System  
**I want to** calculate Average True Range (ATR) for all instruments  
**So that** I can normalize event measurements

**Acceptance Criteria:**
- [ ] Calculate ATR with configurable period (default 14)
- [ ] Update ATR values for each new candle
- [ ] Store historical ATR values
- [ ] Handle initialization period correctly
- [ ] Support all granularities (H1, H4, D, W)

**Priority:** P0 (Core)  
**Estimate:** 5 points  
**Dependencies:** US-001  
**Technical Notes:**
- Use standard ATR formula
- Optimize for vectorized calculations
- Cache recent ATR values

---

## Epic 2: Data Storage & Management

### US-004: Create Event Storage Tables
**As a** Data Engineer  
**I want to** create database tables for storing resistance events  
**So that** events can be persisted and queried

**Acceptance Criteria:**
- [ ] Create new_resistance_events_table with all required fields
- [ ] Create support_and_resistance_master_table
- [ ] Set up proper indexes for query performance
- [ ] Implement data retention policies
- [ ] Add constraints for data integrity
- [ ] Support partitioning by instrument/granularity

**Priority:** P0 (Core)  
**Estimate:** 3 points  
**Dependencies:** None  
**Technical Notes:**
- Consider using PostgreSQL or BigQuery
- Implement proper foreign keys
- Add created_at/updated_at timestamps

---

### US-005: Store Resistance Events
**As a** System  
**I want to** persist detected resistance events to database  
**So that** they can be analyzed and used for features

**Acceptance Criteria:**
- [ ] Insert events into new_resistance_events_table
- [ ] Insert corresponding entry in master table
- [ ] Handle duplicate event detection
- [ ] Implement batch insert for performance
- [ ] Add transaction support for consistency
- [ ] Log all database operations

**Priority:** P0 (Core)  
**Estimate:** 3 points  
**Dependencies:** US-002, US-004  

---

## Epic 3: Feature Engineering

### US-006: Calculate Distance Features
**As a** System  
**I want to** calculate distance-based features from resistance events  
**So that** traders can understand price level relationships

**Acceptance Criteria:**
- [ ] Calculate distance_from_last_new_resistance
- [ ] Calculate new_resistance_distance_velocity
- [ ] Calculate distance_from_last_resistance_in_atr
- [ ] Store features in dedicated table
- [ ] Update features with each new event
- [ ] Handle first event edge case

**Priority:** P1 (Important)  
**Estimate:** 5 points  
**Dependencies:** US-005  

---

### US-007: Calculate Time-Based Features
**As a** System  
**I want to** calculate temporal features from resistance events  
**So that** traders can understand event frequency patterns

**Acceptance Criteria:**
- [ ] Calculate time_between_new_and_last_new_resistance
- [ ] Calculate double_time_between_new_resistance
- [ ] Calculate time_since_new_resistance (incremental)
- [ ] Update at each market snapshot
- [ ] Handle timezone conversions properly

**Priority:** P1 (Important)  
**Estimate:** 5 points  
**Dependencies:** US-005  

---

### US-008: Calculate Pattern Features
**As a** System  
**I want to** calculate pattern-based features from resistance events  
**So that** traders can identify market structure

**Acceptance Criteria:**
- [ ] Calculate new_resistance_pattern (HH/LH classification)
- [ ] Implement 3-level sequence encoder
- [ ] Implement 4-level sequence encoder
- [ ] Implement 5-level sequence encoder
- [ ] Implement 6-level sequence encoder
- [ ] Convert patterns to binary representations

**Priority:** P1 (Important)  
**Estimate:** 5 points  
**Dependencies:** US-006  

---

### US-009: Calculate Advanced Sequence Analysis
**As a** System  
**I want to** perform advanced sequence analysis on resistance distances  
**So that** traders can understand momentum and acceleration

**Acceptance Criteria:**
- [ ] Implement encode_sequence_full function
- [ ] Calculate change, change_rate, final_velocity
- [ ] Calculate acceleration and curvature
- [ ] Determine is_accelerating flag
- [ ] Determine is_geometric_decay flag
- [ ] Calculate urgency_level (1-3 scale)
- [ ] Handle sequences of varying lengths

**Priority:** P2 (Nice to have)  
**Estimate:** 8 points  
**Dependencies:** US-006  

---

### US-010: Calculate Volume Features
**As a** System  
**I want to** calculate volume-based features from events  
**So that** traders can understand market participation

**Acceptance Criteria:**
- [ ] Calculate volume_roc between events
- [ ] Calculate double_volume_roc
- [ ] Classify as accelerating/decelerating
- [ ] Handle missing volume data
- [ ] Normalize by average volume

**Priority:** P1 (Important)  
**Estimate:** 3 points  
**Dependencies:** US-005  

---

### US-011: Calculate Rolling Aggregations
**As a** System  
**I want to** calculate rolling window features  
**So that** traders can see recent event density

**Acceptance Criteria:**
- [ ] Calculate sum_of_new_resistances_last_30_periods
- [ ] Support configurable window sizes
- [ ] Update efficiently with new data
- [ ] Handle edge cases at data boundaries

**Priority:** P2 (Nice to have)  
**Estimate:** 3 points  
**Dependencies:** US-005  

---

## Epic 4: User Interface

### US-012: Create Events Dashboard
**As a** Trader/Analyst  
**I want to** view resistance events in a web interface  
**So that** I can monitor market structure changes

**Acceptance Criteria:**
- [ ] Add "Events" as collapsible menu in sidebar
- [ ] Create events table page
- [ ] Add instrument selector (dropdown)
- [ ] Add granularity selector (H1, H4, D, W)
- [ ] Add event type selector
- [ ] Display paginated table of events
- [ ] Show all event properties in columns

**Priority:** P0 (Core)  
**Estimate:** 5 points  
**Dependencies:** US-005  

---

### US-013: Create Features Dashboard
**As a** Trader/Analyst  
**I want to** view calculated features in a web interface  
**So that** I can analyze market patterns

**Acceptance Criteria:**
- [ ] Add "Features" as collapsible menu in sidebar
- [ ] Create features table page
- [ ] Add instrument/granularity selectors
- [ ] Display all calculated features
- [ ] Support sorting and filtering
- [ ] Export to CSV functionality

**Priority:** P1 (Important)  
**Estimate:** 5 points  
**Dependencies:** US-006, US-007, US-008  

---

### US-014: Create Operations Monitoring Page
**As a** System Administrator  
**I want to** monitor system operations and performance  
**So that** I can ensure reliable event detection

**Acceptance Criteria:**
- [ ] Add "Operations" to sidebar menu
- [ ] Display last run times for batch/spike modes
- [ ] Show table statistics (row counts, last update)
- [ ] Display processing performance metrics
- [ ] Show error logs and alerts
- [ ] Add manual trigger buttons for processes

**Priority:** P1 (Important)  
**Estimate:** 5 points  
**Dependencies:** US-015, US-016  

---

## Epic 5: Batch Processing

### US-015: Implement Batch Processing Mode
**As a** Data Engineer  
**I want to** backfill historical events and features  
**So that** I have complete historical data for analysis

**Acceptance Criteria:**
- [ ] Process up to 140k candles for H1 data
- [ ] Vectorize calculations for performance
- [ ] Support all instruments and granularities
- [ ] Provide progress reporting
- [ ] Handle interruption and resume
- [ ] Complete in reasonable time (<10 minutes locally)
- [ ] Support export/import for cloud deployment

**Priority:** P0 (Core)  
**Estimate:** 8 points  
**Dependencies:** US-002, US-006, US-007, US-008  
**Technical Notes:**
- Use numpy/pandas for vectorization
- Implement chunked processing
- Add checkpointing for resume capability

---

## Epic 6: Real-time Processing

### US-016: Implement Spike Mode Processing
**As a** System  
**I want to** process new market data in real-time  
**So that** events are detected as they occur

**Acceptance Criteria:**
- [ ] Trigger hourly for H1, every 4 hours for H4, etc.
- [ ] Check last processed timestamp
- [ ] Fetch only new data since last run
- [ ] Process in <1 second
- [ ] Update all events and features
- [ ] Support cloud function deployment
- [ ] Implement proper error handling and retries

**Priority:** P0 (Core)  
**Estimate:** 8 points  
**Dependencies:** US-002, US-006, US-007, US-008  
**Technical Notes:**
- Consider Cloud Functions or Kubernetes CronJob
- Implement idempotency
- Add monitoring and alerting

---

### US-017: Setup Automated Scheduling
**As a** System Administrator  
**I want to** schedule automatic processing runs  
**So that** the system runs without manual intervention

**Acceptance Criteria:**
- [ ] Configure schedulers for each granularity
- [ ] H1: Every hour at :05
- [ ] H4: Every 4 hours at 1:05, 5:05, 9:05, 13:05, 17:05, 21:05
- [ ] D: Daily at 21:05 UTC
- [ ] W: Weekly on Sunday at 21:05 UTC
- [ ] Handle DST transitions
- [ ] Implement job monitoring

**Priority:** P1 (Important)  
**Estimate:** 3 points  
**Dependencies:** US-016  

---

### US-018: Implement Data Quality Checks
**As a** Data Engineer  
**I want to** validate data quality automatically  
**So that** I can trust the event detection system

**Acceptance Criteria:**
- [ ] Check for data gaps in market data
- [ ] Validate event detection logic
- [ ] Verify feature calculations
- [ ] Alert on anomalies
- [ ] Generate daily quality reports
- [ ] Store quality metrics

**Priority:** P2 (Nice to have)  
**Estimate:** 5 points  
**Dependencies:** US-015, US-016  

---

## Suggested Implementation Phases

### Phase 1: Core Event Detection (MVP)
- US-001: Setup Market Data Integration
- US-003: Calculate ATR Indicator
- US-002: Detect New Resistance Events
- US-004: Create Event Storage Tables
- US-005: Store Resistance Events
- US-012: Create Events Dashboard
- US-015: Implement Batch Processing Mode

**Estimated Duration:** 2-3 weeks

### Phase 2: Feature Engineering & Real-time
- US-006: Calculate Distance Features
- US-007: Calculate Time-Based Features
- US-008: Calculate Pattern Features
- US-010: Calculate Volume Features
- US-013: Create Features Dashboard
- US-016: Implement Spike Mode Processing
- US-017: Setup Automated Scheduling

**Estimated Duration:** 2-3 weeks

### Phase 3: Advanced Features & Operations
- US-009: Calculate Advanced Sequence Analysis
- US-011: Calculate Rolling Aggregations
- US-014: Create Operations Monitoring Page
- US-018: Implement Data Quality Checks

**Estimated Duration:** 1-2 weeks

## Story Metrics
- **Total Stories:** 18
- **Total Points:** 96
- **P0 (Core):** 7 stories (39%)
- **P1 (Important):** 8 stories (44%)
- **P2 (Nice to have):** 3 stories (17%)

## Technical Considerations

### Performance Requirements
- Batch mode: Process 140k records in <10 minutes
- Spike mode: Process new data in <1 second
- UI: Load events table in <2 seconds
- Feature calculation: <100ms per event

### Data Volumes
- H1: ~8,760 candles per year per instrument
- 29 instruments × 4 granularities = 116 data streams
- Expected events: 10-20 per day per instrument
- Storage estimate: ~10GB first year

### Technology Stack Recommendations
- **Database**: PostgreSQL with TimescaleDB extension
- **Backend**: Python with FastAPI
- **Processing**: Apache Beam or Airflow for batch
- **Real-time**: Cloud Functions or Kubernetes
- **Frontend**: React with Material-UI
- **Monitoring**: Grafana + Prometheus

## Next Steps
1. Review and prioritize stories based on business value
2. Set up development environment
3. Begin Phase 1 implementation
4. Set up CI/CD pipeline
5. Plan user testing for Phase 1 features