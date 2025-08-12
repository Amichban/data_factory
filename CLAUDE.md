# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Solo Software Factory template repository that provides a comprehensive blueprint for setting up an agent-augmented development workflow. The project integrates Claude Code sub-agents, GitHub automation, and modern full-stack development practices.

## Core Development Workflow

### Project Management Flow
Intent (requirements) → Scope (vertical slices) → Issues (GitHub) → Implementation (Claude Code agents)

### Key Commands

**Scope Management:**
- `/scope <issue-url>` - Analyze intent and generate vertical slices
- `/accept-scope` - Accept scope and create GitHub issues  
- `/issues` - List current issues and status
- `/issue #N` - Select specific issue to work on

**Development:**
- `make dev` - Start development environment with Docker Compose
- `docker-compose up` - Start all services (API, web, database, Redis)
- `docker-compose logs -f api` - View API logs
- `docker-compose logs -f web` - View frontend logs

**Backend (FastAPI):**
- `cd apps/api && pip install -r requirements-dev.txt` - Install dependencies
- `alembic upgrade head` - Run database migrations
- `alembic revision --autogenerate -m "description"` - Create new migration
- `pytest` - Run backend tests
- `pytest -v tests/test_specific.py` - Run specific test file

**Frontend (Next.js):**
- `cd apps/web && npm install` - Install dependencies
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Run linting

**Quality Checks:**
- `pre-commit install` - Setup pre-commit hooks
- `pre-commit run --all-files` - Run all checks manually
- `detect-secrets scan` - Scan for secrets

## Architecture

### Stack
- **Backend**: FastAPI (Python 3.11), SQLAlchemy ORM, PostgreSQL, Redis
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Infrastructure**: Docker Compose (dev), Railway (prod)
- **CI/CD**: GitHub Actions, automated testing and deployment

### Project Structure
```
.claude/          # Claude Code configuration and agents
apps/api/         # FastAPI backend service
apps/web/         # Next.js frontend application  
docs/             # Architecture and design documentation
.github/          # GitHub Actions workflows and automation
```

### Key Patterns
1. **Vertical Slicing**: Each feature is developed end-to-end (DB → API → UI)
2. **Agent Specialization**: Different Claude sub-agents handle PM, backend, frontend, security, and database tasks
3. **Automated PM**: GitHub Issues and Projects track work with automatic status updates
4. **Health Monitoring**: Both API and frontend expose health endpoints at `/health`

## Working with Claude Code Agents

### Available Sub-Agents
- **PM Agent** (`/pm`): Analyzes requirements and creates implementation plans
- **Backend Agent** (`/backend`): Implements FastAPI endpoints and business logic
- **Frontend Agent** (`/frontend`): Implements React components and pages
- **Security Agent** (`/security`): Reviews code for vulnerabilities
- **DBA Agent** (`/dba`): Handles database schema and migrations

### Agent Usage Examples
```bash
# Analyze and scope a new feature
/scope https://github.com/user/repo/issues/1

# Work on a specific issue with appropriate agent
/issue #5
/backend  # If it's a backend task

# Get PM perspective on current work
/pm What's the status of the authentication feature?
```

## Database Operations

### Migrations
```bash
# Create new migration
cd apps/api
alembic revision --autogenerate -m "Add user authentication"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Database Access
- Development DB: `postgresql://dev:devpass@localhost:5432/app_dev`
- Redis: `redis://localhost:6379`

## Testing Strategy

### Backend Testing
```bash
cd apps/api
pytest                          # Run all tests
pytest tests/test_auth.py       # Run specific test file
pytest -k "test_login"          # Run tests matching pattern
pytest --cov=app                # Run with coverage
```

### Frontend Testing  
```bash
cd apps/web
npm test                        # Run all tests
npm test -- --watch            # Run in watch mode
npm test -- auth.test.tsx      # Run specific test file
```

## Deployment

### Local Development
```bash
make dev  # Starts all services via Docker Compose
```

### Production Deployment (Railway)
- Push to main branch triggers automatic deployment
- Environment variables managed in Railway dashboard
- Database migrations run automatically on deploy

## Security Considerations

1. **Never commit secrets** - Use environment variables
2. **Pre-commit hooks** scan for secrets automatically
3. **CORS configuration** in `apps/api/app/main.py`
4. **Rate limiting** configured on all API endpoints
5. **Input validation** using Pydantic models

## Common Tasks

### Add New API Endpoint
1. Create Pydantic models in `apps/api/app/models/`
2. Add endpoint in `apps/api/app/routers/`
3. Write tests in `apps/api/tests/`
4. Update OpenAPI docs automatically generated at `/docs`

### Add New Frontend Page
1. Create page component in `apps/web/app/`
2. Add any API calls to `apps/web/lib/api/`
3. Update types in `apps/web/types/`
4. Add tests in `apps/web/__tests__/`

### Debug Issues
- API logs: `docker-compose logs -f api`
- Frontend logs: Browser console + `docker-compose logs -f web`
- Database queries: Enable SQLAlchemy echo in development
- Network requests: Browser DevTools Network tab

## Performance Optimization

- Database queries use SQLAlchemy eager loading where appropriate
- API responses use pagination for list endpoints
- Frontend uses React Server Components for initial load
- Static assets served via CDN in production
- Redis caching for frequently accessed data