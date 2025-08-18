#!/bin/bash
# Post-action hook for Claude Code
# Updates project state and runs validations after actions

set -e

echo "🔄 Running post-action updates..."

# Update timestamp in PROJECT_STATE.md
if [ -f ".claude/PROJECT_STATE.md" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/Last Updated: .*/Last Updated: $(date +%Y-%m-%d)/" .claude/PROJECT_STATE.md
    else
        # Linux
        sed -i "s/Last Updated: .*/Last Updated: $(date +%Y-%m-%d)/" .claude/PROJECT_STATE.md
    fi
    echo "✅ Updated PROJECT_STATE.md"
fi

# Count user stories
if [ -d "user-stories" ]; then
    STORY_COUNT=$(ls user-stories/*.md 2>/dev/null | wc -l || echo 0)
    echo "📊 Total user stories: $STORY_COUNT"
fi

# Check for new test files
NEW_TESTS=$(git status --porcelain | grep -c "test" || echo 0)
if [ "$NEW_TESTS" -gt 0 ]; then
    echo "🧪 New test files detected: $NEW_TESTS"
fi

# Run linters if available (non-blocking)
if [ -f "apps/web/package.json" ] && command -v npm &> /dev/null; then
    echo "🔍 Running frontend linter..."
    (cd apps/web && npm run lint 2>/dev/null || echo "⚠️ Linting issues found")
fi

if [ -f "apps/api/requirements.txt" ] && command -v ruff &> /dev/null; then
    echo "🔍 Running backend linter..."
    (cd apps/api && ruff check . 2>/dev/null || echo "⚠️ Linting issues found")
fi

# Check for documentation updates
DOC_CHANGES=$(git status --porcelain | grep -c "\.md" || echo 0)
if [ "$DOC_CHANGES" -gt 0 ]; then
    echo "📚 Documentation changes detected: $DOC_CHANGES files"
fi

# Generate quick summary
echo ""
echo "📋 Action Summary:"
echo "-------------------"

# Check git status
MODIFIED=$(git status --porcelain | wc -l)
echo "• Modified files: $MODIFIED"

# Check for security issues
if command -v detect-secrets &> /dev/null; then
    SECRETS=$(detect-secrets scan 2>/dev/null | grep -c "secret" || echo 0)
    if [ "$SECRETS" -gt 0 ]; then
        echo "⚠️ Warning: Potential secrets detected!"
    else
        echo "• Security: No secrets detected ✅"
    fi
fi

# Memory update reminder
echo ""
echo "💡 Reminders:"
echo "• Update LEARNED_PATTERNS.md if you discovered new patterns"
echo "• Update DECISIONS.md for architectural changes"
echo "• Commit with descriptive message referencing user story (e.g., 'feat: Add auth (US-001)')"

echo ""
echo "✅ Post-action updates complete"