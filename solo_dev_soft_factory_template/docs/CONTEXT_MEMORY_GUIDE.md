# Context & Memory Management Guide

> **Best practices** for managing context and memory in Claude Code sessions to maximize efficiency and maintain continuity.

## Table of Contents
1. [Context Management](#context-management)
2. [Memory Persistence](#memory-persistence)
3. [Claude Hooks](#claude-hooks)
4. [GitHub Actions Integration](#github-actions-integration)
5. [Best Practices](#best-practices)

---

## Context Management

### Understanding Context Windows

Claude has a limited context window (~200k tokens). To work efficiently:

#### Priority Files (Always in Context)
```
.claude/
├── CLAUDE.md           # Project instructions (high priority)
├── PROJECT_STATE.md    # Current work status
├── settings.json       # Configuration
└── CONTEXT_SUMMARY.md  # Recent changes
```

#### Smart Context Loading
```bash
# Instead of including entire files
cat entire_file.py  # ❌ Uses lots of context

# Reference by path and load specific sections
@file:app/api/routes.py#L50-100  # ✅ Efficient
```

### Context Optimization Strategies

#### 1. Summarize Before Hitting Limits
```markdown
When context is ~80% full:
1. Summarize the conversation so far
2. Save important decisions to DECISIONS.md
3. Update PROJECT_STATE.md
4. Start fresh with summary
```

#### 2. Use References Instead of Content
```bash
# Bad: Including full documentation
"Here's the entire API documentation: [10,000 lines]"

# Good: Reference locations
"API docs are in docs/api.md, specifically the auth section"
```

#### 3. Batch Related Work
```bash
# Group similar tasks to maintain relevant context
- All database work together
- All API endpoints together
- All UI components together
```

---

## Memory Persistence

### Key Memory Files

#### 1. PROJECT_STATE.md
**Purpose**: Track current work and progress
```markdown
## Active Work
- Current Story: US-001
- Current Phase: Implementation
- Blockers: None

## Completed Today
- [x] Database schema
- [x] API endpoints
- [ ] Frontend UI
```

#### 2. DECISIONS.md
**Purpose**: Architecture decisions and rationale
```markdown
## ADR-001: Choice of Database
Date: 2024-01-15
Decision: PostgreSQL
Reason: ACID compliance, complex queries
Consequences: Need to manage migrations
```

#### 3. LEARNED_PATTERNS.md
**Purpose**: Patterns that work in this codebase
```markdown
## Successful Patterns
- Always validate input with Pydantic
- Use async/await for all database calls
- Component structure: Container/Presenter
```

### Memory Update Workflow

```bash
# After completing a feature
1. Update PROJECT_STATE.md with completion
2. Add any architectural decisions to DECISIONS.md
3. Document new patterns in LEARNED_PATTERNS.md
4. Commit with clear message
```

### Automatic Memory Management

The template includes automatic memory updates:

```json
// .claude/settings.json
{
  "memory": {
    "persistent": true,
    "autoSave": true,
    "saveInterval": 300,  // Save every 5 minutes
    "memoryFiles": [
      ".claude/PROJECT_STATE.md",
      ".claude/DECISIONS.md",
      ".claude/LEARNED_PATTERNS.md"
    ]
  }
}
```

---

## Claude Hooks

### Available Hooks

#### 1. Pre-Action Hook
**Location**: `.claude/hooks/pre-action.sh`
**Purpose**: Validate before executing actions
```bash
#!/bin/bash
# Runs before any Claude action
- Check git status
- Validate project structure
- Verify quality scores
- Check for active story
```

#### 2. Post-Action Hook
**Location**: `.claude/hooks/post-action.sh`
**Purpose**: Update state after actions
```bash
#!/bin/bash
# Runs after Claude actions
- Update PROJECT_STATE.md
- Run linters
- Check for new tests
- Generate summary
```

#### 3. Spec Quality Hook
**Location**: `.claude/hooks/spec-quality.sh`
**Purpose**: Validate specification quality
```bash
#!/bin/bash
# Checks spec quality score
- Validate user story format
- Check acceptance criteria
- Score quality (must be ≥ 7.0)
- Provide improvement suggestions
```

### Configuring Hooks

```json
// .claude/settings.json
{
  "hooks": {
    "enabled": true,
    "preCommit": {
      "enabled": true,
      "commands": [
        "npm run lint",
        "npm test",
        "pytest",
        "detect-secrets scan"
      ]
    },
    "preAction": {
      "enabled": true,
      "script": ".claude/hooks/pre-action.sh"
    },
    "postAction": {
      "enabled": true,
      "script": ".claude/hooks/post-action.sh"
    }
  }
}
```

### Custom Hook Creation

```bash
# Create custom hook
cat > .claude/hooks/my-hook.sh << 'EOF'
#!/bin/bash
echo "Running custom hook..."
# Your logic here
EOF

chmod +x .claude/hooks/my-hook.sh
```

---

## GitHub Actions Integration

### Claude-Aware Workflows

#### 1. Context Sync Workflow
**File**: `.github/workflows/claude-integration.yml`
```yaml
name: Sync Claude Context
on:
  push:
    branches: [main]
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - Update PROJECT_STATE.md
      - Generate CONTEXT_SUMMARY.md
      - Commit changes
```

#### 2. Quality Gate Workflow
```yaml
name: Quality Gate
on:
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - Check user stories exist
      - Validate spec quality
      - Run tests
      - Check documentation
```

#### 3. Command Handler Workflow
```yaml
name: Handle Claude Commands
on:
  issue_comment:
    types: [created]
jobs:
  execute:
    if: startsWith(github.event.comment.body, '/')
    steps:
      - Parse command
      - Execute action
      - Post results
```

### GitHub Integration Benefits

1. **Automatic Context Updates**: Keep memory files current
2. **Quality Enforcement**: Block PRs without proper specs
3. **Command Execution**: Run Claude commands via comments
4. **Progress Tracking**: Update project boards automatically

---

## Best Practices

### 1. Start Each Session Right

```bash
# Beginning of session checklist
1. Read PROJECT_STATE.md - understand current work
2. Check CONTEXT_SUMMARY.md - see recent changes
3. Review active user story - know the goal
4. Load only needed files - preserve context
```

### 2. Maintain Context Hygiene

```bash
# During long sessions
- Summarize every 10-15 exchanges
- Save important code snippets
- Update memory files regularly
- Clear unnecessary variables
```

### 3. Use Structured Communication

```markdown
## Clear Request Format
**Goal**: What you want to achieve
**Context**: Relevant background
**Constraints**: Any limitations
**Success Criteria**: How to know it's done
```

### 4. Leverage Memory Files

```bash
# Don't repeat information
❌ "Remember, we decided to use PostgreSQL because..."
✅ "As noted in DECISIONS.md #ADR-001..."

# Reference previous work
❌ "We built an auth system last week that..."
✅ "See auth implementation in PROJECT_STATE.md#completed"
```

### 5. Optimize File References

```bash
# Efficient file loading
@file:specific.py#function  # Load specific function
@file:api/routes/*          # Load directory structure
@file:*.md                  # Load all markdown files
```

### 6. Context Preservation Strategies

#### For Long Features
```bash
1. Create feature-specific context file
   echo "## Feature: Authentication" > .claude/contexts/auth.md
2. Document decisions as you go
3. Summarize at milestones
4. Reference in future sessions
```

#### For Debugging
```bash
1. Save error state to .claude/debug/error-001.md
2. Include minimal reproduction
3. Document attempted solutions
4. Reference in new session if needed
```

### 7. Session Handoff

When ending a session:
```markdown
## Session Summary - [Date]
### Completed
- [List what was done]

### In Progress
- [Current work state]

### Next Steps
- [What to do next]

### Important Context
- [Key decisions or discoveries]
```

---

## Common Patterns

### Pattern 1: Feature Development
```bash
1. Load user story → 
2. Check PROJECT_STATE → 
3. Implement incrementally → 
4. Update memory files → 
5. Commit with reference
```

### Pattern 2: Bug Fixing
```bash
1. Document bug in .claude/debug/ → 
2. Load minimal context → 
3. Fix issue → 
4. Update LEARNED_PATTERNS → 
5. Close with reference
```

### Pattern 3: Architecture Changes
```bash
1. Document in DECISIONS.md → 
2. Update affected components → 
3. Run tests → 
4. Update documentation → 
5. Sync context files
```

---

## Troubleshooting

### Issue: Context Window Full
```bash
Solution:
1. Run: /summarize  # Summarize conversation
2. Save to .claude/summaries/session-[date].md
3. Clear context
4. Reload with summary + priority files
```

### Issue: Lost Context Between Sessions
```bash
Solution:
1. Always update PROJECT_STATE.md before ending
2. Use CONTEXT_SUMMARY.md for quick reload
3. Reference specific files rather than re-explaining
```

### Issue: Conflicting Information
```bash
Solution:
1. DECISIONS.md is source of truth for architecture
2. PROJECT_STATE.md is source of truth for current work
3. User stories are source of truth for requirements
```

---

## Quick Reference

### Essential Commands
```bash
# Memory management
/update-state          # Update PROJECT_STATE.md
/save-decision        # Add to DECISIONS.md
/document-pattern     # Add to LEARNED_PATTERNS.md

# Context management
/summarize           # Summarize current conversation
/clear-context       # Clear unnecessary context
/load-context        # Load priority files
```

### File Priorities
```
Priority 1 (Always load):
- CLAUDE.md
- PROJECT_STATE.md
- Current user story

Priority 2 (Load as needed):
- DECISIONS.md
- LEARNED_PATTERNS.md
- Active code files

Priority 3 (Reference only):
- Documentation
- Test files
- Historical decisions
```

### Memory Checklist
- [ ] PROJECT_STATE.md updated
- [ ] DECISIONS.md has new architectures
- [ ] LEARNED_PATTERNS.md has new patterns
- [ ] CONTEXT_SUMMARY.md reflects changes
- [ ] Hooks are configured and working
- [ ] GitHub Actions are syncing

---

## Summary

Effective context and memory management enables:
1. **Continuity**: Pick up where you left off
2. **Efficiency**: Don't repeat information
3. **Quality**: Maintain standards automatically
4. **Collaboration**: Clear handoffs between sessions
5. **Learning**: Build on discovered patterns

Remember: The system is designed to help you. Use the memory files, hooks, and automation to maintain context across sessions and ensure consistent, high-quality development.