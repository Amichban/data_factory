# Solo Software Factory - Nimble Edition 🚀

A lean, AI-powered development template for solo developers. Build fast with Claude Code agents, deploy to GCP Cloud Run.

## Features

### 🤖 Claude Code Integration
- **6 AI Agents**: PM, Architect, Backend, Frontend, Security, DBA
- **Custom Commands**: `/scope`, `/accept-scope`, `/issue`
- **Hooks & Automation**: Validation and workflow automation
- **MCP Ready**: Extensible with Model Context Protocol

### 🛠 Minimal Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14
- **Database**: PostgreSQL
- **Cache**: Redis
- **Deploy**: GCP Cloud Run

### 📋 Smart Workflow
- **Vertical Slicing**: End-to-end feature development
- **GitHub Integration**: Issues → Project automation
- **CI/CD**: Simple test & deploy pipeline

## Quick Start

```bash
# 1. Clone
git clone https://github.com/yourusername/solo-software-factory.git
cd solo-software-factory

# 2. Setup environment
cp .env.example .env

# 3. Validate setup (checks ports, dependencies, etc.)
./scripts/validate-setup.sh

# 4. Install dependencies
cd apps/web && npm install && cd ../..
cd apps/api && pip install -r requirements.txt && cd ../..

# 5. Run locally
make dev
```

### Default Services
- API: http://localhost:8000
- Web: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:3000/health

### Port Configuration

If you have port conflicts, customize in `.env`:

```env
API_PORT=8007      # FastAPI backend
WEB_PORT=3015      # Next.js frontend
REDIS_PORT=6381    # Redis cache
DB_PORT=5433       # PostgreSQL database
```

Then services will be available at your custom ports.

## Development Flow

1. **Create Intent Issue** on GitHub
2. **Generate Scope**: `/scope https://github.com/user/repo/issues/1`
3. **Accept Scope**: Comment `/accept-scope` → Creates issues automatically
4. **Work with Agents**: `/backend`, `/frontend`, etc.
5. **Deploy**: Push to main → Auto-deploy to Cloud Run

## Project Structure

```
.
├── .claude/           # AI agents & commands
├── .github/           # GitHub workflows
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── scripts/
│   └── validate-setup.sh  # Setup validation
├── docs/
│   ├── SPEC_PROCESS.md    # Spec workflow guide
│   └── TEMPLATE_FIXES.md  # Troubleshooting
├── docker-compose.yml # Local dev
├── cloudbuild.yaml   # GCP deployment
├── CLAUDE.md         # Claude Code instructions
├── SETUP.md          # Detailed setup guide
└── Makefile          # Dev commands
```

## Commands

```bash
# Development
make dev          # Start all services
make stop         # Stop services
make logs         # View all logs
make clean        # Clean everything

# Testing
make test         # Run all tests
cd apps/api && pytest              # Backend tests
cd apps/web && npm test            # Frontend tests

# Database
cd apps/api
alembic upgrade head               # Run migrations
alembic revision --autogenerate    # Create migration

# Validation
./scripts/validate-setup.sh        # Check setup
```

## Deploy to GCP

1. **Setup GCP**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable Services**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

3. **Add GitHub Secrets**:
   - `GCP_PROJECT_ID`: Your GCP project
   - `GCP_SA_KEY`: Service account JSON key
   - `ANTHROPIC_API_KEY`: Your Claude API key

4. **Deploy**:
   ```bash
   make deploy
   ```

## Claude Code Agents

- **PM** (`/pm`): Requirements → Implementation plans
- **Backend** (`/backend`): FastAPI development
- **Frontend** (`/frontend`): Next.js development
- **Security** (`/security`): Code review
- **DBA** (`/dba`): Database design
- **Architect** (`/architect`): System design

### Agent Usage Examples

```bash
# Analyze a feature request
/scope https://github.com/user/repo/issues/1

# Work on specific issue
/issue #5
/backend  # For API work

# Get security review
/security Review the authentication implementation

# Database design help
/dba Design schema for user management
```

## Environment Variables

```env
# Local Development (customize ports if needed)
DATABASE_URL=postgresql://dev:dev@localhost:${DB_PORT:-5432}/app
REDIS_URL=redis://localhost:${REDIS_PORT:-6379}
CORS_ORIGINS=http://localhost:${WEB_PORT:-3000}
NEXT_PUBLIC_API_URL=http://localhost:${API_PORT:-8000}

# Port Configuration
API_PORT=8000
WEB_PORT=3000
REDIS_PORT=6379
DB_PORT=5432

# Production (set in Cloud Run)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## Troubleshooting

### Port Conflicts
```bash
# Check what's using a port
lsof -i :3000

# Set custom port in .env
WEB_PORT=3015

# Run with custom port
make dev
```

### Docker Issues
```bash
# Reset Docker
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose build --no-cache
make dev
```

### Dependencies
```bash
# Frontend issues
cd apps/web
rm -rf node_modules package-lock.json
npm install

# Backend issues
cd apps/api
pip install -r requirements.txt --upgrade
```

See [docs/TEMPLATE_FIXES.md](docs/TEMPLATE_FIXES.md) for detailed troubleshooting.

## Contributing

1. Fork the template
2. Create feature branch
3. Make improvements
4. Test with fresh clone
5. Submit PR with clear description

## Resources

- [Setup Guide](SETUP.md) - Detailed setup instructions
- [Claude Code Memory](CLAUDE.md) - AI agent instructions
- [Spec Process](docs/SPEC_PROCESS.md) - Requirements workflow
- [Template Fixes](docs/TEMPLATE_FIXES.md) - Common issues & solutions

## License

MIT

---

Built for solo developers who ship fast with AI assistance.