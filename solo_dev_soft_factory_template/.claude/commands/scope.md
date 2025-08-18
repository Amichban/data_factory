---
description: Generate vertical slices from an intent Issue and output JSON + summary
allowed-tools: Bash(git:*), Bash(gh:*), Bash(jq:*), Read, Edit
argument-hint: [issue_url]
model: sonnet
---

## Context
- Recent commits: !`git log --oneline -20 || true`
- Open PRs: !`gh pr list --json number,title,headRefName,baseRefName,author || true`
- Intent Issue: !`gh issue view $ARGUMENTS --json number,title,body,labels,assignees`

## Task

You are the PM agent responsible for analyzing an intent issue and breaking it down into implementable vertical slices.

### 1) Analyze the Intent Issue
- Read the issue title and description to understand the business goal
- Identify the core user needs and success criteria
- Consider technical constraints from the current codebase
- Review any acceptance criteria or requirements specified

### 2) Generate Vertical Slices
Create 4-8 vertical slices that deliver the intent end-to-end. Each slice must include:

**Required Fields:**
- `id`: Unique slug (e.g., "auth-login", "portfolio-dashboard") 
- `title`: Clear, action-oriented title
- `summary`: 1-2 sentence description of user value delivered
- `acceptance_criteria`: Array of testable criteria (3-5 items)
- `dependencies`: Array of other slice IDs that must complete first
- `estimate`: Size estimate (S=1-2 days, M=3-5 days, L=1-2 weeks)
- `risk`: Risk level (Low/Medium/High) with brief rationale
- `files_touched`: Array of files that will likely be modified
- `db_migrations`: Boolean - whether database changes are needed
- `flags`: Array of feature flag names to control the slice

**Slicing Guidelines:**
- **Vertical**: Each slice spans UI → API → DB → tests → observability
- **Valuable**: Delivers tangible user or business value
- **Testable**: Has clear success criteria and smoke tests
- **Toggleable**: Controlled by feature flags
- **Rollback-ready**: Can be disabled without breaking existing functionality

### 3) Output Format

Generate **ONLY** JSON to `.claude/out/scope.json` with this structure:
```json
{
  "source_issue": 123,
  "project": {"name": "Product Roadmap"},
  "slices": [
    {
      "id": "slice-id",
      "title": "Slice Title",
      "summary": "What value this delivers to users",
      "acceptance_criteria": [
        "Specific, testable criterion 1",
        "Specific, testable criterion 2",
        "Specific, testable criterion 3"
      ],
      "dependencies": ["other-slice-id"],
      "estimate": "M",
      "risk": "Low",
      "files_touched": [
        "apps/api/src/endpoints/auth.py",
        "apps/web/src/components/login-form.tsx"
      ],
      "db_migrations": true,
      "flags": ["auth_enabled"]
    }
  ]
}
```

### 4) Create Summary

Also write a human-readable summary to `.claude/out/scope.summary.md` with:
- High-level approach and architecture
- Key risks and mitigation strategies
- Dependencies between slices
- Implementation timeline estimate
- Success metrics and validation approach

## Quality Checks

Before finalizing:
- [ ] Each slice delivers end-to-end user value
- [ ] Dependencies between slices are logical and minimal
- [ ] Risk assessment considers technical and business factors
- [ ] File paths are realistic based on current project structure
- [ ] Feature flags enable safe rollback
- [ ] Acceptance criteria are specific and testable
- [ ] Estimates account for testing and observability
- [ ] JSON is valid and under 50KB

## Output Requirements

1. Create/overwrite `.claude/out/scope.json` with the slice definitions
2. Create/overwrite `.claude/out/scope.summary.md` with human-readable summary
3. Ensure JSON structure matches the specification exactly
4. Keep total output under 50KB for GitHub integration limits
5. Use only the tools specified in allowed-tools