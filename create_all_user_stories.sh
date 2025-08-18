#!/bin/bash

echo "Creating ALL user stories with proper relationships..."

# VS-001 Stories (Data Foundation)
echo "=== Creating VS-001 Stories (Data Foundation) ==="

gh issue create --repo Amichban/data_factory \
  --title "US-001: Setup Firestore Integration" \
  --body "$(cat user-stories/generated/batch-001/US-001-firestore-integration.md)

**Part of:** VS-001 (#22)
**Parent:** Intent (#18)
**Priority:** P0
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-002: Implement ATR Calculation" \
  --body "$(cat user-stories/generated/batch-001/US-002-atr-calculation.md)

**Part of:** VS-001 (#22)
**Parent:** Intent (#18)
**Priority:** P0
**Points:** 3" &

gh issue create --repo Amichban/data_factory \
  --title "US-003: Core Event Detection" \
  --body "$(cat user-stories/generated/batch-001/US-003-event-detection.md)

**Part of:** VS-001 (#22)
**Parent:** Intent (#18)
**Priority:** P0
**Points:** 8" &

gh issue create --repo Amichban/data_factory \
  --title "US-004: Database Setup and Schema" \
  --body "$(cat user-stories/generated/batch-001/US-004-database-setup.md)

**Part of:** VS-001 (#22)
**Parent:** Intent (#18)
**Priority:** P0
**Points:** 3" &

wait

# VS-002 Stories (Feature Engineering)
echo "=== Creating VS-002 Stories (Feature Engineering) ==="

gh issue create --repo Amichban/data_factory \
  --title "US-011: Distance-Based Features" \
  --body "$(cat user-stories/generated/batch-001/US-011-distance-features.md)

**Part of:** VS-002 (#19)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-012: Time-Based Features" \
  --body "$(cat user-stories/generated/batch-001/US-012-time-features.md)

**Part of:** VS-002 (#19)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-013: Pattern Recognition Features" \
  --body "$(cat user-stories/generated/batch-001/US-013-pattern-features.md)

**Part of:** VS-002 (#19)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-014: Volume Analysis Features" \
  --body "$(cat user-stories/generated/batch-001/US-014-volume-features.md)

**Part of:** VS-002 (#19)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 3" &

gh issue create --repo Amichban/data_factory \
  --title "US-016: Rolling Aggregations" \
  --body "$(cat user-stories/generated/batch-001/US-016-rolling-aggregations.md)

**Part of:** VS-002 (#19)
**Parent:** Intent (#18)
**Priority:** P2
**Points:** 3" &

gh issue create --repo Amichban/data_factory \
  --title "US-017: Feature Storage Schema" \
  --body "$(cat user-stories/generated/batch-001/US-017-feature-storage.md)

**Part of:** VS-002 (#19)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 2" &

gh issue create --repo Amichban/data_factory \
  --title "US-018: Feature Update Pipeline" \
  --body "$(cat user-stories/generated/batch-001/US-018-feature-pipeline.md)

**Part of:** VS-002 (#19)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 3" &

wait

# VS-003 Stories (User Interface)
echo "=== Creating VS-003 Stories (User Interface) ==="

gh issue create --repo Amichban/data_factory \
  --title "US-005: Events Dashboard UI" \
  --body "$(cat user-stories/generated/batch-001/US-005-events-dashboard.md)

**Part of:** VS-003 (#20)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-019: Features Dashboard" \
  --body "$(cat user-stories/generated/batch-001/US-019-features-dashboard.md)

**Part of:** VS-003 (#20)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-020: Operations Monitoring Page" \
  --body "$(cat user-stories/generated/batch-001/US-020-operations-monitoring.md)

**Part of:** VS-003 (#20)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 3" &

wait

# VS-004 Stories (Processing Pipeline)
echo "=== Creating VS-004 Stories (Processing Pipeline) ==="

gh issue create --repo Amichban/data_factory \
  --title "US-006: Batch Processing Mode" \
  --body "$(cat user-stories/generated/batch-001/US-006-batch-processing.md)

**Part of:** VS-004 (#21)
**Parent:** Intent (#18)
**Priority:** P0
**Points:** 8" &

gh issue create --repo Amichban/data_factory \
  --title "US-007: Spike Mode Real-time Processing" \
  --body "$(cat user-stories/generated/batch-001/US-007-spike-processing.md)

**Part of:** VS-004 (#21)
**Parent:** Intent (#18)
**Priority:** P0
**Points:** 8" &

gh issue create --repo Amichban/data_factory \
  --title "US-021: Automated Scheduling Setup" \
  --body "$(cat user-stories/generated/batch-001/US-021-automated-scheduling.md)

**Part of:** VS-004 (#21)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 3" &

wait

# VS-005 Stories (Operations & Quality)
echo "=== Creating VS-005 Stories (Operations & Quality) ==="

gh issue create --repo Amichban/data_factory \
  --title "US-008: Validate Instrument Support" \
  --body "$(cat user-stories/generated/batch-001/US-008-validate-instruments.md)

**Part of:** VS-005 (Operations & Quality)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 2" &

gh issue create --repo Amichban/data_factory \
  --title "US-009: Store Events Transaction" \
  --body "$(cat user-stories/generated/batch-001/US-009-store-events-transaction.md)

**Part of:** VS-005 (Operations & Quality)
**Parent:** Intent (#18)
**Priority:** P0
**Points:** 3" &

gh issue create --repo Amichban/data_factory \
  --title "US-010: Data Retention Policies" \
  --body "$(cat user-stories/generated/batch-001/US-010-data-retention.md)

**Part of:** VS-005 (Operations & Quality)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-022: Data Quality Validation" \
  --body "$(cat user-stories/generated/batch-001/US-022-data-quality.md)

**Part of:** VS-005 (Operations & Quality)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 5" &

gh issue create --repo Amichban/data_factory \
  --title "US-023: Performance Monitoring" \
  --body "$(cat user-stories/generated/batch-001/US-023-performance-monitoring.md)

**Part of:** VS-005 (Operations & Quality)
**Parent:** Intent (#18)
**Priority:** P1
**Points:** 2" &

wait

# VS-006 Stories (Advanced Features)
echo "=== Creating VS-006 Stories (Advanced Features) ==="

gh issue create --repo Amichban/data_factory \
  --title "US-015: Advanced Sequence Analysis" \
  --body "$(cat user-stories/generated/batch-001/US-015-sequence-analysis.md)

**Part of:** VS-006 (Advanced Features)
**Parent:** Intent (#18)
**Priority:** P2
**Points:** 8" &

gh issue create --repo Amichban/data_factory \
  --title "US-024: Documentation & Training" \
  --body "$(cat user-stories/generated/batch-001/US-024-documentation.md)

**Part of:** VS-006 (Advanced Features)
**Parent:** Intent (#18)
**Priority:** P2
**Points:** 2" &

wait

echo "All user stories created!"
