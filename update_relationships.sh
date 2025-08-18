#!/bin/bash

echo "Updating VS-001 with story links..."
gh issue edit 22 --repo Amichban/data_factory --body "## Vertical Slice: Data Foundation

**Duration**: Week 1-2
**Priority**: P0 (Critical)
**Points**: 19

### User Stories
- [ ] #25 US-001: Firestore Integration (5 pts)
- [ ] #26 US-002: ATR Calculation (3 pts)
- [ ] #27 US-003: Event Detection (8 pts)
- [ ] #28 US-004: Database Setup (3 pts)

### Acceptance Criteria
- Connect to Firestore and fetch all 29 instruments
- Database schema supports all event properties
- ATR calculation matches expected values
- Event detection achieves 95% accuracy

### Dependencies
None - this is the foundation

### Implementation Order
1. Database setup (#28)
2. Firestore integration (#25)
3. ATR calculation (#26)
4. Event detection (#27)

**Parent:** #18"

echo "Updating VS-002 with story links..."
gh issue edit 19 --repo Amichban/data_factory --body "## Vertical Slice: Feature Engineering

**Duration**: Week 3
**Priority**: P1
**Points**: 29

### User Stories
- [ ] #30 US-011: Distance Features (5 pts)
- [ ] #31 US-012: Time Features (5 pts)
- [ ] #32 US-013: Pattern Features (5 pts)
- [ ] #33 US-014: Volume Features (3 pts)
- [ ] #29 US-016: Rolling Aggregations (3 pts)
- [ ] #34 US-017: Feature Storage (2 pts)
- [ ] #35 US-018: Feature Pipeline (3 pts)

### Dependencies
Requires: VS-001 (#22)

**Parent:** #18"

echo "Relationships updated!"
