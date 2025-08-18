---
description: Select and focus on a specific issue for implementation
allowed-tools: Bash(gh:*), Read, Edit, Grep
argument-hint: [issue_number]
model: sonnet
---

## Context

This command focuses the development session on a specific GitHub issue, providing context and setting up the environment for implementation.

## Task

### 1) Load Issue Context
- Fetch the specified issue details
- Parse acceptance criteria and requirements
- Identify the issue type (slice, bug, enhancement, etc.)
- Check dependencies and blockers

### 2) Analyze Implementation Requirements
- Determine which agent(s) should handle this work
- Identify files that need to be modified
- Check for database migrations or schema changes
- Review security and testing requirements

### 3) Set Up Development Context
- Update PROJECT_STATE.md with current focus
- Create or switch to appropriate branch
- Prepare development environment
- Load relevant context for the assigned agent

### 4) Provide Implementation Guidance
- Break down the issue into implementation steps
- Suggest the appropriate agent to use
- Provide file paths and starting points
- Highlight testing and validation requirements

## Implementation

```bash
#!/bin/bash
set -euo pipefail

# Get issue number from arguments
ISSUE_NUMBER="${ARGUMENTS:-}"

if [[ -z "$ISSUE_NUMBER" ]]; then
    echo "❌ Error: Issue number required"
    echo "Usage: /issue #123 or /issue 123"
    exit 1
fi

# Clean issue number (remove # if present)
ISSUE_NUMBER=$(echo "$ISSUE_NUMBER" | sed 's/#//' | sed 's/[^0-9]//g')

echo "🎯 **Loading Issue #${ISSUE_NUMBER}**"
echo "=================================="

# Fetch issue details
if ! gh issue view "$ISSUE_NUMBER" --json number,title,body,labels,assignees,state > .claude/out/current-issue.json 2>/dev/null; then
    echo "❌ Error: Could not fetch issue #${ISSUE_NUMBER}"
    echo "   Check that the issue exists and you have access"
    exit 1
fi

# Extract issue details
TITLE=$(jq -r '.title' .claude/out/current-issue.json)
STATE=$(jq -r '.state' .claude/out/current-issue.json)
BODY=$(jq -r '.body // ""' .claude/out/current-issue.json)

echo "📋 **Issue Details**"
echo "   Title: ${TITLE}"
echo "   State: ${STATE}"
echo "   URL: $(gh issue view $ISSUE_NUMBER --json url -q '.url')"
echo ""

# Check if issue is open
if [[ "$STATE" != "open" ]]; then
    echo "⚠️  Warning: Issue is ${STATE}"
    echo "   Consider working on open issues instead"
    echo ""
fi

# Determine issue type and agent
LABELS=$(jq -r '.labels[]?.name // empty' .claude/out/current-issue.json)
ISSUE_TYPE="general"
SUGGESTED_AGENT=""

if echo "$LABELS" | grep -q "slice"; then
    ISSUE_TYPE="slice"
    echo "🎯 **Issue Type**: Vertical Slice"
    
    # Analyze slice requirements to suggest agent
    if echo "$BODY" | grep -qi "database\|migration\|schema"; then
        SUGGESTED_AGENT="dba"
    elif echo "$BODY" | grep -qi "api\|backend\|endpoint"; then
        SUGGESTED_AGENT="backend"
    elif echo "$BODY" | grep -qi "ui\|frontend\|component"; then
        SUGGESTED_AGENT="frontend"
    elif echo "$BODY" | grep -qi "security\|auth"; then
        SUGGESTED_AGENT="security"
    else
        SUGGESTED_AGENT="backend"  # Default for slices
    fi
elif echo "$LABELS" | grep -q "bug"; then
    ISSUE_TYPE="bug"
    echo "🐛 **Issue Type**: Bug Fix"
elif echo "$LABELS" | grep -q "enhancement"; then
    ISSUE_TYPE="enhancement"
    echo "✨ **Issue Type**: Enhancement"
fi

# Extract acceptance criteria
if echo "$BODY" | grep -q "Acceptance Criteria\|**Acceptance"; then
    echo ""
    echo "✅ **Acceptance Criteria**"
    echo "$BODY" | sed -n '/[Aa]cceptance [Cc]riteria/,/^$/p' | sed '1d' | sed '/^$/q' | sed 's/^/   /'
fi

# Extract Development Sequence if present
if echo "$BODY" | grep -q "Development Sequence\|🤖 Development Sequence"; then
    echo ""
    echo "🤖 **Recommended Agent Sequence**"
    echo "$BODY" | sed -n '/Development Sequence/,/^###\|^##/p' | grep -E '^\*\*`/|^[0-9]+\.' | sed 's/^/   /'
    echo ""
    echo "   💡 This sequence was proposed by the PM agent during scoping."
    echo "   You can follow it or adjust based on your needs."
    
    # Store sequence for potential automation
    echo "$BODY" | sed -n '/Development Sequence/,/^###\|^##/p' > .claude/out/current-agent-sequence.txt
fi

# Check dependencies
if echo "$BODY" | grep -q "Dependencies\|**Dependencies"; then
    echo ""
    echo "🔗 **Dependencies**"
    echo "$BODY" | sed -n '/[Dd]ependencies/,/^$/p' | sed '1d' | sed '/^$/q' | sed 's/^/   /'
fi

# Suggest branch name
BRANCH_NAME=$(echo "issue-${ISSUE_NUMBER}-${TITLE}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g' | cut -c1-50)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")

echo ""
echo "🌿 **Branch Setup**"
echo "   Current branch: ${CURRENT_BRANCH}"
echo "   Suggested branch: ${BRANCH_NAME}"

if [[ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]]; then
    echo "   💡 To create and switch to the suggested branch, run:"
    echo "      git checkout -b ${BRANCH_NAME}"
fi

# Update PROJECT_STATE.md with current work
echo ""
echo "📝 **Updating Project State**"

# Read current PROJECT_STATE.md
if [[ -f ".claude/PROJECT_STATE.md" ]]; then
    # Update the "Active Work" section
    sed -i.bak '/^## Active Work/,/^## / {
        /^## Active Work/!{/^## /!d;}
        /^## Active Work/a\
- [x] Working on Issue #'$ISSUE_NUMBER': '$TITLE'
    }' .claude/PROJECT_STATE.md
    
    echo "   ✅ Updated PROJECT_STATE.md with current focus"
fi

# Provide next steps
echo ""
echo "🚀 **Next Steps**"

# Check if we have a recommended agent sequence
if [[ -f ".claude/out/current-agent-sequence.txt" ]]; then
    if grep -q "/[a-z]" .claude/out/current-agent-sequence.txt 2>/dev/null; then
        echo "   📋 Follow the recommended agent sequence above:"
        echo ""
        # Extract just the agent commands
        grep -E '/[a-z]+' .claude/out/current-agent-sequence.txt 2>/dev/null | head -5 | sed 's/^/   /'
        echo ""
        echo "   Or proceed with your own approach:"
    fi
elif [[ "$ISSUE_TYPE" == "slice" ]]; then
    echo "   1. 📋 Review acceptance criteria carefully"
    echo "   2. 🏗️  Plan implementation approach (UI → API → DB → Tests)"
    echo "   3. 🚩 Implement feature flag if needed"
    
    if [[ -n "$SUGGESTED_AGENT" ]]; then
        echo "   4. 🤖 Use /${SUGGESTED_AGENT} agent for implementation"
    fi
    
    echo "   5. ✅ Create tests and update documentation"
    echo "   6. 🔍 Test acceptance criteria"
    echo "   7. 📤 Create PR and link to this issue"
else
    echo "   1. 🔍 Reproduce the issue/understand requirements"
    echo "   2. 💡 Plan your approach"
    echo "   3. 🛠️  Implement the changes"
    echo "   4. ✅ Test your changes"
    echo "   5. 📤 Create PR and link to this issue"
fi

# File analysis for context
if [[ "$ISSUE_TYPE" == "slice" ]] && echo "$BODY" | grep -q "Files touched\|files_touched"; then
    echo ""
    echo "📁 **Files to Modify** (based on slice definition)"
    echo "$BODY" | grep -A 10 "files_touched\|Files touched" | grep -E '\.(py|tsx?|sql)' | sed 's/^/   /'
fi

echo ""
echo "💡 **Tips**"
echo "   - Use Claude Code agents for specialized help"
echo "   - Update issue with progress comments"
echo "   - Test thoroughly before creating PR"
echo "   - Link PR to issue with 'Closes #${ISSUE_NUMBER}'"
echo ""
echo "📊 **Current Focus**: Issue #${ISSUE_NUMBER} - ${TITLE}"
```

## Quality Checks

- [ ] Issue exists and is accessible
- [ ] Issue details are properly parsed
- [ ] Acceptance criteria are extracted and displayed
- [ ] Appropriate agent is suggested based on issue content
- [ ] Branch naming follows conventions
- [ ] PROJECT_STATE.md is updated with current focus
- [ ] Next steps are relevant to issue type

## Error Handling

- Invalid issue numbers
- Network/API errors
- Missing issue access permissions
- Git branch creation failures

## Context Updates

The command updates:
1. `.claude/out/current-issue.json` - Full issue data for other commands
2. `.claude/PROJECT_STATE.md` - Current work focus
3. Git branch (optionally) - Dedicated branch for the issue

This provides context for other Claude Code agents and commands to understand the current development focus.