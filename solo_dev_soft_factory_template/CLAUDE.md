# CLAUDE.md - AI Agent Instructions

This file provides technical context for Claude Code agents. Users should read HOW_TO_USE.md instead.

## Context Management

### Priority Context
Always maintain awareness of:
1. Current user story being worked on (check PROJECT_STATE.md)
2. Active vertical slice and phase
3. Quality score requirements (≥ 7.0)
4. Recent architecture decisions (DECISIONS.md)
5. Learned patterns (LEARNED_PATTERNS.md)

### Memory Persistence
- Project state: `.claude/PROJECT_STATE.md`
- Architecture decisions: `.claude/DECISIONS.md`
- Patterns: `.claude/LEARNED_PATTERNS.md`
- Update these files after significant changes

### Context Windows
- Summarize before hitting 80% capacity
- Prioritize active work files
- Reference by path rather than including full content
- Use @file references when possible

## Project Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11), SQLAlchemy ORM, PostgreSQL, Redis
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Infrastructure**: Docker Compose (dev), Railway/GCP (prod)
- **CI/CD**: GitHub Actions

### Project Structure
```
.claude/          # Agent configuration
apps/api/         # FastAPI backend
apps/web/         # Next.js frontend  
design-system/    # UI components
user-stories/     # Requirements
```

### Key Patterns
1. **User Story First**: Every feature starts with a user story
2. **Incremental UI**: Build in 4 steps (raw → basic → structured → polished)
3. **Vertical Slicing**: Complete features end-to-end
4. **Quality Gates**: Spec score must be ≥ 7.0
5. **Test Generation**: Tests created from acceptance criteria

## Available Agents

- **PM Agent** (`/pm`): Requirements analysis, story creation
- **Architect Agent** (`/architect`): System design, patterns
- **DBA Agent** (`/dba`): Database schema, migrations
- **Backend Agent** (`/backend`): FastAPI endpoints, business logic
- **Frontend Agent** (`/frontend`): React components, UI
- **Security Agent** (`/security`): Code review, vulnerability assessment

## Key Commands for Development

**User Stories & Specs:**
- `/spec-to-stories` - Generate multiple stories from spec
- `/user-story` - Create single story
- `/spec-score` - Check quality (must be ≥ 7.0)
- `/spec-enhance` - Auto-improve specifications

**Development:**
- `/story-ui` - Build UI incrementally (4 steps)
- `/acceptance-test` - Generate tests from stories
- `/parallel-strategy` - Identify parallel work

**Database:**
- `alembic revision --autogenerate -m "description"` - Create migration
- `alembic upgrade head` - Apply migrations

**Testing:**
- `cd apps/api && pytest` - Backend tests
- `cd apps/web && npm test` - Frontend tests

## Hooks and Automation

### Pre-Action Hooks
- Validate spec quality before implementation
- Check database migrations are current
- Verify tests exist for dependencies

### Post-Action Hooks
- Update PROJECT_STATE.md
- Generate/update tests
- Run linters and formatters

## Best Practices

### Always
- Start with user story and acceptance criteria
- Build UI incrementally (4 steps)
- Maintain spec quality ≥ 7.0
- Test at each development phase
- Update memory files after major changes
- Commit with story reference (e.g., "feat: Add auth (US-001)")

### Never
- Skip quality gates
- Build complete UI before testing API
- Commit without tests
- Ignore security warnings
- Store secrets in code

## Performance Optimization

- Use SQLAlchemy eager loading
- Implement pagination for list endpoints
- Use React Server Components
- Cache with Redis where appropriate
- Profile with middleware when needed

## Security Considerations

1. **Never commit secrets** - Use environment variables
2. **Pre-commit hooks** scan automatically
3. **CORS configuration** in `apps/api/app/main.py`
4. **Rate limiting** on all endpoints
5. **Input validation** with Pydantic models

---

*This file is for Claude agents. Users should read HOW_TO_USE.md for instructions.*