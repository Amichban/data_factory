#!/bin/bash

# Create Vertical Slice Issues (Milestones)
echo "Creating Vertical Slice issues..."

# VS-001: Data Foundation
gh issue create --repo Amichban/data_factory \
  --title "VS-001: Data Foundation" \
  --label "vertical-slice,priority:P0" \
  --body "## Vertical Slice: Data Foundation

**Duration**: Week 1-2
**Priority**: P0 (Critical)
**Points**: 19

### User Stories
- [ ] US-001: Firestore Integration (5 pts)
- [ ] US-002: ATR Calculation (3 pts)
- [ ] US-003: Event Detection (8 pts)
- [ ] US-004: Database Setup (3 pts)

### Acceptance Criteria
- Connect to Firestore and fetch all 29 instruments
- Database schema supports all event properties
- ATR calculation matches expected values
- Event detection achieves 95% accuracy

### Dependencies
None - this is the foundation

### Implementation Order
1. Database setup (US-004)
2. Firestore integration (US-001)
3. ATR calculation (US-002)
4. Event detection (US-003)

Parent: #18"

# Create individual story issues for VS-001
echo "Creating US-001..."
gh issue create --repo Amichban/data_factory \
  --title "US-001: Setup Firestore Integration" \
  --label "user-story,backend,priority:P0" \
  --body "$(cat user-stories/generated/batch-001/US-001-firestore-integration.md)

Part of: VS-001
Parent: #18"

echo "Creating US-002..."
gh issue create --repo Amichban/data_factory \
  --title "US-002: Implement ATR Calculation" \
  --label "user-story,backend,priority:P0" \
  --body "$(cat user-stories/generated/batch-001/US-002-atr-calculation.md)

Part of: VS-001
Parent: #18"

echo "Creating US-003..."
gh issue create --repo Amichban/data_factory \
  --title "US-003: Core Event Detection" \
  --label "user-story,backend,priority:P0" \
  --body "$(cat user-stories/generated/batch-001/US-003-event-detection.md)

Part of: VS-001
Parent: #18"

echo "Creating US-004..."
gh issue create --repo Amichban/data_factory \
  --title "US-004: Database Setup and Schema" \
  --label "user-story,database,priority:P0" \
  --body "$(cat user-stories/generated/batch-001/US-004-database-setup.md)

Part of: VS-001
Parent: #18"

echo "Issues created successfully!"
