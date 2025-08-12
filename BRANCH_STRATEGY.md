# Branch Strategy for Parallel Development

## Current Branch Structure

```
main (stable)
├── feature/issue-3-market-data     [IN PROGRESS] Market Data Ingestion
├── feature/issue-8-monitoring      [IN PROGRESS] System Monitoring Dashboard
└── (future branches)
    ├── feature/issue-4-resistance  [BLOCKED by #3]
    ├── feature/issue-5-batch       [BLOCKED by #4]
    └── feature/issue-6-spike       [BLOCKED by #4]
```

## Active Branches

### Track 1: Data Pipeline
**Branch:** `feature/issue-3-market-data`
**Issue:** #3 - Market Data Ingestion Pipeline
**Status:** 🚀 In Progress
**Dependencies:** Firestore (✅ Complete)

### Track 2: UI/Monitoring  
**Branch:** `feature/issue-8-monitoring`
**Issue:** #8 - System Monitoring Dashboard
**Status:** 🚀 In Progress
**Dependencies:** None (can work in parallel)

## Workflow Commands

### Switch Between Branches
```bash
# Work on Market Data
git checkout feature/issue-3-market-data
/issue #3

# Work on Monitoring
git checkout feature/issue-8-monitoring
/issue #8

# Check current branch
git branch --show-current
```

### View All Branches
```bash
# See local branches
git branch

# See all branches with last commit
git branch -v

# Visual tree
git log --graph --oneline --all -10
```

### Stash Changes When Switching
```bash
# Save work in progress
git stash save "WIP: feature description"

# Switch branch
git checkout other-branch

# Restore work
git checkout original-branch
git stash pop
```

## Merge Strategy

### When a Feature is Complete
```bash
# 1. Commit all changes
git add -A
git commit -m "feat: Complete [feature name]"

# 2. Update from main
git checkout main
git pull origin main

# 3. Merge feature
git merge feature/issue-X-name

# 4. Push to remote
git push origin main

# 5. Delete local branch
git branch -d feature/issue-X-name

# 6. Close issue
gh issue close X
```

## Parallel Work Tips

1. **Keep branches focused** - One issue per branch
2. **Commit frequently** - Small, logical commits
3. **Pull main regularly** - Stay updated with merged features
4. **Use stash** - Save WIP when switching contexts
5. **Document conflicts** - Note any integration points

## Current Work Distribution

| Developer | Branch | Issue | Component |
|-----------|--------|-------|-----------|
| You | feature/issue-3-market-data | #3 | Backend/Data |
| You | feature/issue-8-monitoring | #8 | Frontend/UI |

## Next Available Work

Once #3 is complete, these become available:
- #4: Core Resistance Event Detection Algorithm
- After #4: Both #5 (Batch) and #6 (Spike) can be done in parallel

## Integration Points

Be aware of these integration points between parallel work:
- Market Data (#3) ↔ Monitoring (#8): Dashboard will need to show data ingestion status
- Both will use the Firestore service from #2

## Conflict Resolution

If conflicts arise when merging:
```bash
# 1. Update main
git checkout main
git pull origin main

# 2. Merge main into feature branch
git checkout feature/issue-X
git merge main

# 3. Resolve conflicts
# Edit conflicted files
git add resolved-files
git commit -m "fix: Resolve merge conflicts with main"

# 4. Test thoroughly
pytest  # or appropriate tests

# 5. Complete merge
git checkout main
git merge feature/issue-X
```