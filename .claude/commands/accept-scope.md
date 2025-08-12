---
description: Accept the generated scope and trigger GitHub Issues creation workflow
allowed-tools: Bash(gh:*), Read
argument-hint: []
model: sonnet
---

## Context

This command is used after reviewing the output from `/scope` to accept the proposed slicing and trigger the creation of GitHub Issues and Project items.

## Task

### 1) Validate Scope Files
- Verify that `.claude/out/scope.json` exists and is valid JSON
- Check that `.claude/out/scope.summary.md` exists
- Ensure the scope contains at least one slice with required fields

### 2) Post Acceptance Comment
- Comment on the source issue with "/accept-scope" to trigger the GitHub workflow
- Include a brief summary of what will be created (number of slices, estimated timeline)

### 3) Provide Next Steps
- Display the slices that will be created
- Show the estimated timeline and dependencies
- Provide instructions for monitoring the automated issue creation

## Implementation

```bash
#!/bin/bash
set -euo pipefail

# Check if scope.json exists
if [[ ! -f ".claude/out/scope.json" ]]; then
    echo "❌ Error: No scope.json found. Run /scope <issue-url> first."
    exit 1
fi

# Validate JSON structure
if ! jq -e '.slices and (.slices|length>0) and .source_issue' .claude/out/scope.json >/dev/null 2>&1; then
    echo "❌ Error: Invalid scope.json structure."
    exit 1
fi

# Extract source issue number
SOURCE_ISSUE=$(jq -r '.source_issue' .claude/out/scope.json)
SLICE_COUNT=$(jq -r '.slices | length' .claude/out/scope.json)

echo "✅ Scope validation passed:"
echo "   - Source Issue: #${SOURCE_ISSUE}"
echo "   - Slices to create: ${SLICE_COUNT}"

# Post acceptance comment to trigger workflow
echo "📝 Posting acceptance comment to issue #${SOURCE_ISSUE}..."
gh issue comment "${SOURCE_ISSUE}" --body "/accept-scope

🚀 **Scope Accepted**

This will create ${SLICE_COUNT} implementation slices as GitHub Issues and add them to the project board.

The GitHub Action workflow will now:
- Create individual issues for each slice
- Add them to the project with 'Todo' status
- Link them back to this intent issue

Monitor progress at: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/actions"

echo "✅ Acceptance comment posted successfully!"
echo ""
echo "🔄 Next steps:"
echo "   1. Watch for the 'Scope → Issues' GitHub Action to complete"
echo "   2. Review the created issues in your project board"
echo "   3. Start working on slices in dependency order"
echo "   4. Use /issues to see current work status"
echo ""
echo "📋 Slice Overview:"
jq -r '.slices[] | "   - \(.id): \(.title) (\(.estimate))"' .claude/out/scope.json
```

## Quality Checks

Before posting the acceptance:
- [ ] scope.json is valid JSON with required fields
- [ ] Source issue number is valid and accessible
- [ ] All slice IDs are unique
- [ ] Dependencies reference valid slice IDs
- [ ] Acceptance criteria are testable
- [ ] Feature flags are properly named

## Error Handling

If validation fails:
- Display clear error message
- Suggest corrective actions (re-run /scope, fix JSON)
- Do not post the acceptance comment

If GitHub operations fail:
- Check authentication (gh auth status)
- Verify repository access permissions
- Ensure issue exists and is accessible

## Output

Success output includes:
1. Validation confirmation
2. Summary of slices to be created
3. GitHub Action monitoring link
4. Next steps for the user
5. Overview of slice titles and estimates