---
name: parallel-strategy
description: Display parallelization strategy and Git workflow for current scope
tools: [Read, Bash]
---

# Display Parallelization Strategy

After running `/scope` and before `/accept-scope`, use this command to see the recommended parallelization strategy and Git branching workflow.

## Process

1. Read the current scope.json file
2. Analyze dependencies between slices
3. Display parallel work tracks
4. Show Git branching commands
5. Provide work sequencing recommendations

## Usage

```bash
/parallel-strategy
```

## Example Output

```markdown
## 🚀 Parallelization Strategy

### Currently Available (No blockers):
✅ Ready to start immediately:
- #1: Database Schema Setup
- #7: Monitoring Dashboard (basic version)
- #9: CI/CD Pipeline Setup

### Parallel Work Opportunities:

After completing #1 (Database), you can parallelize:

**Track 1: Backend Pipeline**
- #2: Authentication API
  └─> #3: User Management
  └─> #4: Session Handling

**Track 2: Frontend Components**  
- #5: Login UI
  └─> #6: Dashboard Layout
  
**Track 3: DevOps/Testing**
- #7: Monitoring (enhanced)
- #8: Integration Tests

### 📁 Git Workflow:

```bash
# Foundation work (required first)
git checkout -b feature/database-schema
/issue #1
/dba
# Complete and merge

# Then create parallel branches
git checkout main
git checkout -b feature/backend-auth
/issue #2
/backend

# In parallel (different terminal/Claude session)
git checkout main  
git checkout -b feature/frontend-auth
/issue #5
/frontend

# Also in parallel
git checkout main
git checkout -b feature/monitoring
/issue #7
/frontend
```

### 📊 Recommended Schedule:

**Week 1:**
- Morning: Database Schema (#1)
- Afternoon: Start Auth API (#2) + Monitoring (#7)

**Week 2:**
- Track 1: Complete Auth API, start User Management (#3)
- Track 2: Login UI (#5), Dashboard (#6)
- Track 3: Enhanced monitoring, CI/CD

### 🎯 Benefits:
- 🚀 2.5x faster development through parallelization
- 🔄 Context switching between different types of work
- 🧪 Isolated testing per feature branch
- 🔀 Clean Git history with logical merges

### 💡 Tips:
- Use `git worktree` to work on multiple branches simultaneously
- Keep branches small and focused
- Merge frequently to avoid conflicts
- Use feature flags to deploy incomplete features safely
```

## Implementation Script

```bash
#!/bin/bash
set -euo pipefail

# Check if scope.json exists
if [[ ! -f ".claude/out/scope.json" ]]; then
    echo "❌ Error: No scope.json found. Run /scope first."
    exit 1
fi

# Parse scope and analyze dependencies
SCOPE=$(cat .claude/out/scope.json)

# Extract slices and dependencies
echo "## 🚀 Parallelization Strategy for Scope"
echo ""

# Identify slices with no dependencies (can start immediately)
echo "### Currently Available (No blockers):"
echo "✅ Ready to start immediately:"
jq -r '.slices[] | select(.dependencies | length == 0) | "- \(.id): \(.title)"' .claude/out/scope.json

echo ""
echo "### Parallel Work Tracks:"
echo ""

# Display parallelization info if available
if jq -e '.parallelization' .claude/out/scope.json >/dev/null 2>&1; then
    jq -r '.parallelization.tracks[] | "**\(.name)**\nSlices: \(.slices | join(", "))\nCan start: \(.can_start)\n"' .claude/out/scope.json
fi

echo "### 📁 Git Workflow:"
echo '```bash'
if jq -e '.parallelization.git_workflow' .claude/out/scope.json >/dev/null 2>&1; then
    jq -r '.parallelization.git_workflow[]' .claude/out/scope.json
else
    # Generate default Git workflow
    echo "# Create feature branches for parallel work"
    jq -r '.slices[] | "git checkout -b feature/\(.id)"' .claude/out/scope.json | head -3
fi
echo '```'

echo ""
echo "### 🎯 Optimization Tips:"
echo "- Use \`git worktree add ../project-\<branch\> \<branch\>\` for simultaneous work"
echo "- Run \`git branch --all\` to see all branches"
echo "- Use \`git log --graph --oneline --all\` to visualize branch structure"
```

## Quality Checks

- Verify dependency chains are accurate
- Ensure parallel tracks don't have hidden dependencies
- Validate that Git branch names follow conventions
- Check that suggested parallelization is realistic

## Integration with Development

After reviewing the parallelization strategy:
1. Create the suggested Git branches
2. Use `/accept-scope` to create issues
3. Work on parallel tracks simultaneously
4. Use `/issue #N` to switch between tracks
5. Merge completed branches back to main