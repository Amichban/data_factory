# Feedback for Template

## Issues Encountered During Setup

### 1. React Version Incompatibility

**Issue:** 
The template's `package.json` in `apps/web` specified React 19.1.0, which is incompatible with @testing-library/react@14 that requires React 18.

**Error Message:**
```
npm error code ERESOLVE
npm error ERESOLVE unable to resolve dependency tree
npm error
npm error While resolving: web@1.0.0
npm error Found: react@19.1.0
npm error node_modules/react
npm error   react@"19.1.0" from the root project
npm error
npm error Could not resolve dependency:
npm error peer react@"^18.0.0" from @testing-library/react@14.3.1
```

**Solution:**
Downgrade React and React DOM to version 18:
- Changed `"react": "19.1.0"` to `"react": "^18.3.1"`
- Changed `"react-dom": "19.1.0"` to `"react-dom": "^18.3.1"`
- Changed `"@types/react": "^19"` to `"@types/react": "^18"`
- Changed `"@types/react-dom": "^19"` to `"@types/react-dom": "^18"`

**Recommendation:**
The template should either:
1. Use React 18 for compatibility with current testing libraries, OR
2. Update @testing-library/react to a version that supports React 19 when available

### 2. Repository Clone Location

**Issue:**
When cloning the repository using `git clone https://github.com/Amichban/solo_dev_soft_factory_template.git`, it created a nested directory structure where the repository was cloned into a `data_factory` folder within the current `data_factory` directory.

**Recommendation:**
Consider updating the setup instructions to clarify the expected directory structure or provide clearer guidance on where to clone the repository.

## Additional Warnings (Non-Breaking)

The following deprecation warnings appeared during npm install but don't break functionality:
- `inflight@1.0.6`: Memory leak issues, not supported
- `abab@2.0.6`: Should use platform's native atob() and btoa()
- `glob@7.2.3`: Version prior to v9 not supported
- `domexception@4.0.0`: Should use platform's native DOMException

These are likely coming from transitive dependencies and may need updates in the dependency chain.

## Critical Automation Gap

### 3. /accept-scope Workflow Not Triggering Automatically

**Issue:**
The `/accept-scope` command successfully posts a comment to the GitHub issue, but the `scope-to-issues.yml` workflow doesn't trigger automatically because:
1. The workflow is configured to trigger on `workflow_dispatch` or `repository_dispatch` events
2. There's no workflow listening for issue comments with `/accept-scope`
3. The automation chain is broken between the Claude Code command and GitHub Actions

**Current Workflow Configuration:**
```yaml
on:
  workflow_dispatch:
    inputs:
      scope_json:
        description: 'JSON scope from Claude Code /scope command'
        required: true
        type: string
  repository_dispatch:
    types: [accept-scope]
```

**Expected Behavior:**
When `/accept-scope` is posted as a comment, it should automatically:
1. Detect the comment trigger
2. Read the scope.json from the repository
3. Create GitHub issues for each slice
4. Update the project board

**Proposed Solution:**

Create a new workflow file `.github/workflows/issue-comment-trigger.yml`:

```yaml
name: Issue Comment Trigger

on:
  issue_comment:
    types: [created]

jobs:
  handle-accept-scope:
    if: github.event.issue.number && contains(github.event.comment.body, '/accept-scope')
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Check for scope.json
        id: check-scope
        run: |
          if [ -f ".claude/out/scope.json" ]; then
            echo "scope_exists=true" >> $GITHUB_OUTPUT
            echo "scope_json=$(cat .claude/out/scope.json | jq -c .)" >> $GITHUB_OUTPUT
          else
            echo "scope_exists=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Trigger scope-to-issues workflow
        if: steps.check-scope.outputs.scope_exists == 'true'
        uses: actions/github-script@v6
        with:
          script: |
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'scope-to-issues.yml',
              ref: 'main',
              inputs: {
                scope_json: '${{ steps.check-scope.outputs.scope_json }}'
              }
            });
            
      - name: Comment on issue
        if: steps.check-scope.outputs.scope_exists == 'true'
        uses: actions/github-script@v6
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: '🤖 Workflow triggered! Creating issues from scope...'
            });
```

**Alternative Solution (Simpler):**

Modify the `/accept-scope` command to directly trigger the workflow using GitHub CLI:

```bash
# In .claude/commands/accept-scope.md, after posting the comment:
SCOPE_JSON=$(cat .claude/out/scope.json | jq -c .)
gh workflow run scope-to-issues.yml -f scope_json="$SCOPE_JSON"
```

**Recommendation:**
The template should include the issue comment trigger workflow by default to ensure full automation of the PM workflow. This is critical for the "solo developer with agent assistance" model to work smoothly.

### 4. Scope JSON Structure Mismatch

**Issue:**
The `scope-to-issues.yml` workflow expects a different JSON structure than what the `/scope` command generates:

**Expected by workflow:**
- `slice.name` (but scope generates `slice.title`)
- `slice.description` (but scope generates `slice.summary`)
- `slice.tasks` array (not generated by scope)
- `slice.points` (but scope generates `slice.estimate`)
- `slice.primary_component` (not generated by scope)
- `scope.intent_url`, `scope.total_points`, `scope.target_date`, `scope.intent_title`, `scope.milestone_number` (not generated)

**Generated by /scope:**
- `slice.title`, `slice.summary`, `slice.acceptance_criteria`, `slice.dependencies`
- `slice.estimate`, `slice.risk`, `slice.files_touched`, `slice.db_migrations`, `slice.flags`

**Impact:**
The workflow fails with `TypeError: Cannot read properties of undefined (reading 'map')` because it tries to access fields that don't exist.

**Proposed Solution:**
Either:
1. Update `scope-to-issues.yml` to match the structure generated by `/scope`
2. Update `/scope` command to generate the structure expected by the workflow
3. Add a transformation step in the issue-comment-trigger workflow

**Recommendation:**
The template should have consistent data contracts between the PM agent and GitHub Actions workflows. This requires coordination between `.claude/commands/scope.md` and `.github/workflows/scope-to-issues.yml`.

## Complete Solution Implemented

### Overview
We successfully created a fully automated pipeline from Claude Code PM analysis to GitHub Issues creation:

```
/scope #1 → scope.json → /accept-scope → GitHub Actions → Issues Created
```

### Components Created/Modified

#### 1. **New Workflow: `.github/workflows/issue-comment-trigger.yml`**
Listens for `/accept-scope` comments on issues and triggers the scope-to-issues workflow.

```yaml
name: Issue Comment Trigger
on:
  issue_comment:
    types: [created]
jobs:
  handle-accept-scope:
    if: contains(github.event.comment.body, '/accept-scope')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      actions: write
    steps:
      - Checkout code
      - Check for scope.json
      - Trigger scope-to-issues workflow
      - Comment success/failure on issue
```

#### 2. **Modified: `.gitignore`**
Removed `.claude/out/` from gitignore to allow GitHub Actions to access scope files.

```diff
- .claude/out/
+ # .claude/out/ is intentionally tracked for GitHub Actions integration
```

#### 3. **Fixed: `.github/workflows/scope-to-issues.yml`**
Updated to match the actual JSON structure from `/scope`:

**Key Changes:**
- Added permissions: `issues: write`
- Map `slice.title` (not `slice.name`)
- Use `slice.summary` (not `slice.description`)
- Convert estimates to points: S=3, M=5, L=8, XL=13
- Handle risk labels and feature flags
- Fixed project board integration with error handling
- Updated meta issue with calculated timeline

#### 4. **Committed: Scope Files**
- `.claude/out/scope.json` - The slice definitions
- `.claude/out/scope.summary.md` - Human-readable summary

### How It Works Now

1. **Developer runs `/scope #1`**
   - PM agent analyzes the issue
   - Creates scope.json with vertical slices
   - Creates scope.summary.md

2. **Developer runs `/accept-scope`**
   - Posts comment to GitHub issue
   - issue-comment-trigger workflow detects comment
   - Reads scope.json from repository
   - Triggers scope-to-issues workflow

3. **GitHub Actions creates issues**
   - Creates one issue per slice with:
     - Acceptance criteria
     - File list
     - Risk level
     - Story points
     - Feature flags
   - Creates meta tracking issue
   - Comments back on original issue

### Status Management

Currently, status is managed through:
- **Labels**: `vertical-slice`, `points:N`, `risk:level`
- **Issue State**: Open/Closed
- **Meta Issue**: Tracks overall progress with checkboxes

### Project Board and Status Management

We've implemented comprehensive automation for status tracking:

#### **Implemented: Status Label System**
The `project-board-automation.yml` workflow provides:
- **Automatic status labels** on all new issues
- **Comment commands** for status updates:
  - `/status:todo` - Move to Todo
  - `/status:in-progress` - Start work
  - `/status:review` - Ready for review
  - `/status:blocked` - Blocked by dependency
  - `/status:done` - Complete
- **Meta issue checkbox updates** when slices complete
- **Automatic label cleanup** (removes conflicting status labels)

#### **Note: GitHub Projects v2 Required**
GitHub Classic Projects are deprecated. For full board automation:
1. Manually create a GitHub Project (v2) from the Projects tab
2. Add custom fields for points, risk, etc.
3. Use GitHub's built-in automation rules for status changes
4. The workflows will still update labels for tracking

### Who Maintains Status?

Status is maintained through multiple touchpoints:

1. **Developers** - Use comment commands (`/status:in-progress`) when starting work
2. **GitHub Actions** - Automatically update on:
   - Issue creation → `status:backlog`
   - Issue closed → `status:done`
   - PR linked → Can trigger `status:review`
3. **Project Manager** - Can manually update via labels or comments
4. **Meta Issue** - Automatically tracks completion of vertical slices

### Recommended Template Improvements

1. **Fix JSON Contract Mismatch** - Align `/scope` output with workflow expectations
2. **Include Issue Comment Trigger** - Add by default for `/accept-scope`
3. **Track `.claude/out/`** - Remove from default `.gitignore`
4. **Add Status Labels** - Pre-create status labels on repo initialization
5. **Projects v2 Integration** - Update to use new Projects API (GraphQL)
6. **Documentation** - Add clear setup instructions for the PM workflow