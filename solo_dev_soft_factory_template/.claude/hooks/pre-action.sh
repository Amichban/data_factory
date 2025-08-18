#!/bin/bash
# Pre-action hook for Claude Code
# Validates actions before execution

set -e

echo "🔍 Running pre-action validation..."

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "⚠️ Warning: Not in a git repository"
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ Warning: You have uncommitted changes"
    git status --short
fi

# Validate project structure
REQUIRED_DIRS=(".claude" "apps/api" "apps/web" "docs")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Error: Required directory missing: $dir"
        exit 1
    fi
done

# Check for active user story
if [ -f ".claude/PROJECT_STATE.md" ]; then
    ACTIVE_STORY=$(grep -m1 "Active Work" .claude/PROJECT_STATE.md | grep -o "US-[0-9]*" || echo "")
    if [ -n "$ACTIVE_STORY" ]; then
        echo "📝 Active story: $ACTIVE_STORY"
    else
        echo "⚠️ No active user story found"
    fi
fi

# Validate quality score if spec files exist
if [ -d "user-stories" ] && [ "$(ls user-stories/*.md 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "✅ User stories found - remember to check quality score (must be ≥ 7.0)"
fi

# Check for test coverage
if command -v pytest &> /dev/null; then
    echo "🧪 pytest available for testing"
fi

if command -v npm &> /dev/null; then
    echo "📦 npm available for frontend testing"
fi

# Environment check
if [ -f ".env" ]; then
    echo "✅ Environment file exists"
else
    echo "⚠️ No .env file found - using defaults"
fi

# Database connectivity check (optional)
if [ -n "$DATABASE_URL" ]; then
    echo "🗄️ Database URL configured"
fi

echo "✅ Pre-action validation complete"