#!/bin/bash

echo "Creating all user story issues..."

# Create US-001 through US-008
stories=(
  "US-001: Setup Firestore Integration"
  "US-002: Implement ATR Calculation" 
  "US-003: Core Event Detection"
  "US-004: Database Setup and Schema"
  "US-005: Events Dashboard UI"
  "US-006: Batch Processing Mode"
  "US-007: Spike Mode Real-time Processing"
  "US-008: Validate Instrument Support"
)

for i in {1..8}; do
  num=$(printf "%03d" $i)
  title="${stories[$i-1]}"
  echo "Creating $title..."
  
  if [ -f "user-stories/generated/batch-001/US-${num}*.md" ]; then
    file=$(ls user-stories/generated/batch-001/US-${num}*.md | head -1)
    gh issue create --repo Amichban/data_factory \
      --title "$title" \
      --body "$(cat $file)

Part of: VS-001
Parent: #18"
  fi
done

echo "Adding remaining stories..."
# Create a few more key stories
gh issue create --repo Amichban/data_factory \
  --title "US-011: Distance-Based Features" \
  --body "See user-stories/generated/batch-001/US-011-distance-features.md
Part of: VS-002
Parent: #18"

gh issue create --repo Amichban/data_factory \
  --title "US-012: Time-Based Features" \
  --body "See user-stories/generated/batch-001/US-012-time-features.md
Part of: VS-002  
Parent: #18"

echo "User stories created!"
