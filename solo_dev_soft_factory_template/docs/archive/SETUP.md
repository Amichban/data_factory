# Setup Guide for Solo Dev Software Factory Template

## Your Repository
https://github.com/Amichban/solo_dev_soft_factory_template

## Make it a Template Repository

1. Go to https://github.com/Amichban/solo_dev_soft_factory_template/settings
2. Under "General", check ✅ **Template repository**
3. Save changes

## Configure GitHub for Automation

### 1. Add Repository Secrets
Go to Settings → Secrets and variables → Actions → New repository secret

Required secrets:
- `ANTHROPIC_API_KEY` - Your Claude API key from [Anthropic Console](https://console.anthropic.com/)
- `PROJECT_TOKEN` - GitHub Personal Access Token for project automation (see below)

Optional secrets (for GCP deployment):
- `GCP_PROJECT_ID` - Your Google Cloud project ID  
- `GCP_SA_KEY` - Service account JSON key for GCP

### 2. Create PROJECT_TOKEN for Full Automation

The PROJECT_TOKEN enables automatic project board management with GitHub Projects v2:

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens/new)
2. Name it: "Solo Software Factory - Project Automation"
3. Select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `project` - Full control of projects
4. Generate token and copy it
5. Add to repository secrets: Settings → Secrets → Actions → New repository secret
   - Name: `PROJECT_TOKEN`
   - Value: Your token

### 3. Connect to Existing Database (Optional)

If you need to connect to an existing database instead of creating a new one:

```bash
# Run the database setup workflow
gh workflow run setup-database.yml \
  -f database_type=postgresql \
  -f generate_models=true

# Or via GitHub UI:
# Actions → setup-database → Run workflow
# Select your database type and whether to generate models
```

This will:
- Configure database connection
- Generate SQLAlchemy models from existing schema
- Create migration and backup scripts
- Set up proper isolation between existing and new tables

**Important for existing databases:**
- Models are auto-generated in `apps/api/app/models/generated.py`
- Never modify existing production tables directly
- Create new tables with `app_` prefix for new features
- Use read-only access where possible

### 4. Create GitHub Project Board (Automated!)

```bash
# After adding PROJECT_TOKEN secret, run:
gh workflow run setup-project.yml

# Or via GitHub UI:
# Actions tab → setup-project → Run workflow
```

This will:
- Create a new GitHub Project v2
- Add custom fields (Status, Priority, Risk, Points, etc.)
- Configure automation rules
- Link to your repository

**Manual Alternative**: If you prefer manual setup:
1. Go to your repository → Projects tab → New project
2. Select "Board" template
3. Add custom fields manually (Status, Priority, Risk, Points, Sprint)

## Using the Template for New Projects

Once configured as a template:

1. Click "Use this template" → "Create a new repository"
2. Name your new project
3. Clone and start developing:

```bash
git clone https://github.com/Amichban/your-new-project.git
cd your-new-project

# Copy environment configuration
cp .env.example .env

# Validate setup and check for port conflicts
./scripts/validate-setup.sh

# If you have port conflicts, edit .env to set custom ports:
# API_PORT=8007
# WEB_PORT=3015
# REDIS_PORT=6381
# DB_PORT=5433

# Install dependencies
cd apps/web && npm install && cd ../..
cd apps/api && pip install -r requirements.txt && cd ../..

# Start development environment
make dev
```

## Port Configuration

If you encounter port conflicts, customize ports in your `.env` file:

```bash
# Default ports (change if conflicts exist)
API_PORT=8000      # FastAPI backend
WEB_PORT=3000      # Next.js frontend  
REDIS_PORT=6379    # Redis cache
DB_PORT=5432       # PostgreSQL database
```

The template automatically uses these environment variables for:
- Docker Compose port mappings
- Application URLs and connections
- CORS configuration

## Start Your First Spec

1. **Create an Intent Issue**:
   - Go to Issues → New Issue
   - Use the "Intent Issue" template
   - Describe what you want to build

2. **Generate Scope**:
   ```bash
   /scope https://github.com/Amichban/your-project/issues/1
   ```

3. **Review and Accept**:
   - Review the generated slices
   - Comment `/accept-scope` to create development issues

4. **Start Building**:
   ```bash
   /issue #5
   /backend   # For API work
   /frontend  # For UI work
   ```

## Example Intent Issue

```markdown
# Intent: Task Management System

## Problem Statement
Need a simple way to track and manage team tasks

## Proposed Solution
Web app for creating, assigning, and tracking tasks

## Success Criteria
- Create/edit/delete tasks
- Assign tasks to team members
- Track task status
- Mobile responsive

## Constraints
- Budget: <$50/month on GCP
- Timeline: 2 weeks
- Technical: Simple authentication, PostgreSQL
```

## Local Development

```bash
# Validate setup before starting
./scripts/validate-setup.sh

# Start services
make dev
# Or with custom ports from .env:
PORT=3015 make dev  # For frontend port override

# View logs
docker-compose logs -f
docker-compose logs -f api  # API logs only
docker-compose logs -f web  # Frontend logs only

# Stop everything
make stop

# Run tests
make test

# Access services
# Frontend: http://localhost:${WEB_PORT:-3000}
# API Docs: http://localhost:${API_PORT:-8000}/docs
# Health Check: http://localhost:${WEB_PORT:-3000}/health
```

## Deploy to GCP

1. Setup GCP:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

2. Deploy:
```bash
make deploy
```

## Need Help?

- Check [Spec Process Guide](docs/SPEC_PROCESS.md)
- Review [Claude Code Memory](CLAUDE.md)
- See agent definitions in `.claude/agents/`

---

Your template is ready at: https://github.com/Amichban/solo_dev_soft_factory_template