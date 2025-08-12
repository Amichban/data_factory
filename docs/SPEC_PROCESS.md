# Spec & PRD Process with Claude Code

## Overview

This template uses an AI-driven specification process that transforms ideas into actionable development plans through GitHub Issues and Claude Code agents.

## The Process Flow

```mermaid
graph LR
    A[Idea] --> B[Intent Issue]
    B --> C[/scope Command]
    C --> D[Review Slices]
    D --> E[/accept-scope]
    E --> F[GitHub Issues Created]
    F --> G[Development]
```

## Step 1: Create an Intent Issue

Create a new GitHub Issue with your product idea or feature request. Use this template:

```markdown
# Intent: [Feature Name]

## Problem Statement
What problem are we solving? Who has this problem?

## Proposed Solution
High-level description of what we want to build.

## Success Criteria
- What does success look like?
- Key metrics or outcomes

## Constraints
- Budget: 
- Timeline:
- Technical limitations:

## User Stories (optional)
- As a [user], I want to [action] so that [benefit]

## Non-Goals
What are we explicitly NOT doing?
```

### Example Intent Issue:

```markdown
# Intent: Task Management System MVP

## Problem Statement
Small teams need a simple way to track tasks and projects without the complexity of enterprise tools.

## Proposed Solution
Web app for creating, assigning, and tracking tasks with basic project grouping.

## Success Criteria
- Users can create and assign tasks
- Tasks have status (todo/in-progress/done)
- Basic project grouping
- Works on mobile

## Constraints
- Budget: <$50/month hosting
- Timeline: 2 weeks
- Technical: Simple authentication, PostgreSQL

## User Stories
- As a user, I want to create tasks with descriptions
- As a user, I want to see all my assigned tasks
- As a user, I want to mark tasks as complete

## Non-Goals
- No complex workflows
- No time tracking (initially)
- No integrations with other tools
```

## Step 2: Generate Scope with AI

Run the `/scope` command with your Intent Issue URL:

```bash
/scope https://github.com/yourusername/repo/issues/1
```

The PM agent will:
1. Analyze your intent
2. Generate 4-8 vertical slices
3. Define acceptance criteria
4. Identify dependencies
5. Estimate complexity
6. Output `scope.json` and post a summary

### What's a Vertical Slice?

A vertical slice is an end-to-end feature that delivers value:
- ✅ Database schema changes
- ✅ API endpoints
- ✅ Frontend UI
- ✅ Tests
- ✅ Documentation

Example slice:
```json
{
  "id": "create-task",
  "title": "Task creation flow",
  "summary": "Users can create tasks with title, description, and assignee",
  "acceptance_criteria": [
    "Form validates required fields",
    "Tasks persist to database",
    "Shows in task list immediately",
    "Sends notification to assignee"
  ],
  "estimate": "M",
  "risk": "Low"
}
```

## Step 3: Review and Refine

Review the generated scope. You can:
- Edit the scope.json manually
- Re-run `/scope` with more details
- Add comments to the Intent Issue

## Step 4: Accept and Create Issues

When satisfied, comment on the Intent Issue:

```
/accept-scope
```

This triggers GitHub Actions to:
1. Create individual GitHub Issues for each slice
2. Add them to your GitHub Project
3. Set initial status to "Todo"
4. Link back to the Intent Issue

## Step 5: Work the Slices

For each slice issue:

1. **Select the issue**: `/issue #5`
2. **Use appropriate agent**: 
   - `/architect` - Design decisions
   - `/backend` - API implementation
   - `/frontend` - UI implementation
   - `/dba` - Database schema

3. **Follow vertical slice pattern**:
   ```bash
   # 1. Database migration
   /dba Create schema for holdings table
   
   # 2. API endpoint
   /backend Implement POST /api/holdings endpoint
   
   # 3. Frontend form
   /frontend Create AddHolding component with form
   
   # 4. Tests
   /backend Write tests for holdings endpoint
   ```

## Step 6: PM Sync

The PM Sync workflow runs every 30 minutes to:
- Update issue statuses based on PR activity
- Flag blockers
- Track velocity
- Update PROJECT_STATE.md

## Advanced: Custom Agents for Your Domain

Create domain-specific agents in `.claude/agents/`:

```markdown
---
name: domain-expert
description: Specialist for your specific domain
tools: [Read, Edit, Bash]
---

Expertise:
- Domain-specific knowledge
- Industry best practices
- Compliance requirements
- Performance optimization

Rules:
- Follow domain conventions
- Ensure data integrity
- Handle edge cases gracefully
```

## Tips for Better Specs

1. **Be specific about constraints** - The AI works better with clear boundaries
2. **Include examples** - Show sample data or UI mockups
3. **Define success metrics** - What does "done" look like?
4. **Start small** - Better to ship MVP and iterate
5. **Use domain language** - The agents learn from your terminology

## Monitoring Progress

Check progress at any time:
- `/issues` - List all issues and status
- View GitHub Project board
- Check `.claude/PROJECT_STATE.md`
- Review PM Sync comments on issues

## Example Commands Flow

```bash
# Start new feature
/scope https://github.com/user/repo/issues/10

# Review and accept
/accept-scope

# Start development
/issue #15
/architect How should we structure the task service?
/backend Implement the task CRUD operations
/frontend Build the task list view

# Check progress
/issues
/pm What's blocking the task management feature?
```

## Making it a GitHub Template

To make this repo a template for future projects:

1. Go to Settings → General
2. Check "Template repository"
3. Future projects: "Use this template" → Create new repository
4. Each project gets its own Issues, Project board, and customization

---

Now you're ready to turn any idea into working software with AI-driven development!