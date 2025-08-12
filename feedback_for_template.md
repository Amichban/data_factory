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