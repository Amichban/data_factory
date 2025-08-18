---
description: List current issues and their status for project overview
allowed-tools: Bash(gh:*), Read
argument-hint: []
model: sonnet
---

## Context

This command provides a comprehensive overview of current work items, their status, and helps with project planning and prioritization.

## Task

### 1) Fetch Current Issues
- Get all issues in the repository with relevant metadata
- Filter for slice issues and other work items
- Include status information from labels and project fields

### 2) Analyze Status
- Categorize issues by status (Todo, In Progress, Blocked, In Review, Done)
- Identify dependencies and blockers
- Calculate progress metrics

### 3) Display Summary
- Show current sprint/active work
- Highlight blockers and risks
- Provide actionable next steps

## Implementation

```bash
#!/bin/bash
set -euo pipefail

echo "📋 **Current Issues Overview**"
echo "================================"

# Fetch all issues with labels and project info
gh issue list --limit 50 --json number,title,labels,state,assignees,createdAt,updatedAt > .claude/out/issues.json

# Count issues by status
TOTAL=$(jq '[.[] | select(.state == "open")] | length' .claude/out/issues.json)
SLICES=$(jq '[.[] | select(.state == "open") | select(.labels[].name | contains("slice"))] | length' .claude/out/issues.json)

echo "📊 **Summary**"
echo "   Total Open Issues: ${TOTAL}"
echo "   Slice Issues: ${SLICES}"
echo ""

# Group by status based on labels
echo "🔄 **By Status**"

TODO=$(jq -r '[.[] | select(.state == "open") | select(.labels[]?.name == "Status: Todo")] | length' .claude/out/issues.json)
IN_PROGRESS=$(jq -r '[.[] | select(.state == "open") | select(.labels[]?.name == "Status: In Progress")] | length' .claude/out/issues.json)
BLOCKED=$(jq -r '[.[] | select(.state == "open") | select(.labels[]?.name == "Status: Blocked")] | length' .claude/out/issues.json)
IN_REVIEW=$(jq -r '[.[] | select(.state == "open") | select(.labels[]?.name == "Status: In Review")] | length' .claude/out/issues.json)

echo "   📝 Todo: ${TODO}"
echo "   🔄 In Progress: ${IN_PROGRESS}"
echo "   🚫 Blocked: ${BLOCKED}"
echo "   👀 In Review: ${IN_REVIEW}"
echo ""

# Show slice issues in detail
echo "🎯 **Slice Issues**"
echo ""

if [[ $SLICES -eq 0 ]]; then
    echo "   No slice issues found."
    echo "   💡 Create some with: /scope <issue-url> then /accept-scope"
else
    jq -r '.[] | select(.state == "open") | select(.labels[].name | contains("slice")) | 
        "   #\(.number) \(.title)" +
        (if .labels[]?.name | startswith("Status:") then
            " [\(.labels[] | select(.name | startswith("Status:")) | .name | ltrimstr("Status: "))]"
        else
            " [No Status]"
        end) +
        (if .assignees | length > 0 then
            " (@\(.assignees[0].login))"
        else
            ""
        end)' .claude/out/issues.json
fi

echo ""

# Show blocked issues if any
if [[ $BLOCKED -gt 0 ]]; then
    echo "🚫 **Blocked Issues** (Immediate attention needed)"
    jq -r '.[] | select(.state == "open") | select(.labels[]?.name == "Status: Blocked") |
        "   #\(.number) \(.title)"' .claude/out/issues.json
    echo ""
fi

# Show in progress issues
if [[ $IN_PROGRESS -gt 0 ]]; then
    echo "🔄 **In Progress**"
    jq -r '.[] | select(.state == "open") | select(.labels[]?.name == "Status: In Progress") |
        "   #\(.number) \(.title)" +
        (if .assignees | length > 0 then " (@\(.assignees[0].login))" else "" end)' .claude/out/issues.json
    echo ""
fi

# Show ready to work issues
if [[ $TODO -gt 0 ]]; then
    echo "📝 **Ready to Start**"
    jq -r '.[] | select(.state == "open") | select(.labels[]?.name == "Status: Todo") |
        "   #\(.number) \(.title)"' .claude/out/issues.json
    echo ""
fi

# Show next actions
echo "🎯 **Suggested Next Actions**"

if [[ $BLOCKED -gt 0 ]]; then
    echo "   1. 🚨 Resolve blocked issues first"
fi

if [[ $IN_PROGRESS -gt 0 ]]; then
    echo "   2. 🏃 Complete in-progress work"
fi

if [[ $TODO -gt 0 ]]; then
    echo "   3. 📋 Pick up todo items with /issue #<number>"
fi

if [[ $SLICES -eq 0 ]]; then
    echo "   1. 🎯 Create intent issue and run /scope to generate work"
fi

echo ""
echo "💡 **Tips**"
echo "   - Use /issue #123 to focus on a specific issue"
echo "   - Create new scope with /scope <intent-issue-url>"
echo "   - Check project board for visual overview"
```

## Output Format

The command provides:

1. **Summary Statistics**
   - Total open issues
   - Number of slice issues  
   - Status distribution

2. **Detailed Issue Lists**
   - Slice issues with status and assignee
   - Blocked issues (highlighted)
   - In-progress work
   - Ready-to-start items

3. **Actionable Guidance**
   - Prioritized next actions
   - Workflow suggestions
   - Tips for productivity

## Status Detection

Issues are categorized by labels:
- `Status: Todo` - Ready to start
- `Status: In Progress` - Currently being worked
- `Status: Blocked` - Cannot proceed (needs attention)
- `Status: In Review` - PR open, pending review
- `Status: Done` - Completed (should be closed)

## Quality Checks

- [ ] All open issues are displayed
- [ ] Status labels are correctly interpreted
- [ ] Blocked issues are highlighted
- [ ] Next actions are relevant and actionable
- [ ] Output is concise but informative