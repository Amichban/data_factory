# 🚀 Solo Software Factory - Complete Development Environment

> **Build production apps 10x faster** with AI-powered development, user story workflows, quality gates, and a modern dark-themed design system.

[![Claude Code](https://img.shields.io/badge/Powered%20by-Claude%20Code-blue)](https://claude.ai/code)
[![Design System](https://img.shields.io/badge/Design-Dark%20Theme-purple)](design-system/)
[![Quality](https://img.shields.io/badge/Min%20Quality-7.0+-green)](docs/SPEC_QUALITY_GUIDE.md)

## 🎯 What's New in This Enhanced Version

### **✨ Major Enhancements**
- 📝 **User Story-Driven Development** - Every feature starts with clear requirements
- 🔧 **Debug-First UI** - See your feature immediately with debug interfaces
- ✅ **Quality Gates** - Specifications must score ≥ 7.0 before development
- 🎨 **Dark Theme Design System** - Glass morphism, gradients, and glow effects
- 🧪 **Automated Test Generation** - Tests created from acceptance criteria
- 📊 **Parallel Work Planning** - Optimize development with parallel strategies

### **🤖 AI-Powered Development**
- **6 Specialized Agents**: PM, Architect, Backend, Frontend, Security, DBA
- **25+ Commands**: User stories, quality checks, test generation, and more
- **Intelligent Workflows**: Agents recommend optimal sequences

### **🛠 Complete Tech Stack**
- **Backend**: FastAPI (Python 3.11) with async support
- **Frontend**: Next.js 14 with TypeScript
- **Design**: Dark theme with glass morphism
- **Database**: PostgreSQL + Redis
- **Testing**: Automated acceptance, unit, and E2E tests
- **Deploy**: Railway, GCP Cloud Run, or any Docker host

## ⚡ Quick Start (5 Minutes)

### **1. Setup**
```bash
# Clone template
git clone https://github.com/yourusername/solo-software-factory.git my-app
cd my-app

# Quick install
cp .env.example .env
make install  # Or run commands manually
make dev
```

### **2. Your First Feature**
```bash
# Open Claude Code
claude

# Create user story
/user-story "As a user, I want to manage tasks"

# Build debug UI (see it immediately!)
/debug-ui US-001

# Implement with AI
/backend Create task CRUD API
/frontend Build task list with our design system

# Ship it
git commit -m "feat: Task management (US-001)"
git push
```

### **3. Access Points**
| Service | URL | Description |
|---------|-----|-------------|
| 🌐 **App** | http://localhost:3000 | Your application |
| 🔧 **Debug** | http://localhost:3000/debug | Debug interfaces |
| 🚀 **API** | http://localhost:8000 | Backend API |
| 📚 **Docs** | http://localhost:8000/docs | API documentation |

## 🔄 The Complete Development Process

```mermaid
graph LR
    A[💡 Idea] --> B[📝 User Story]
    B --> C[✅ Quality Check]
    C --> D[🔧 Debug UI]
    D --> E[💻 Implementation]
    E --> F[🧪 Testing]
    F --> G[🚀 Production]
```

### **Step-by-Step Workflow**

```bash
# 1. Define what you're building
/user-story "As a user, I want to view analytics"

# 2. Ensure quality (must score ≥ 7.0)
/spec-score
/spec-enhance  # If score < 7.0

# 3. Build debug UI for immediate feedback
/debug-ui US-001
# Visit: http://localhost:3000/debug/analytics

# 4. Implement with AI agents
/architect Design the analytics system
/dba Create analytics tables
/backend Build analytics API
/frontend Create dashboard with charts

# 5. Test and ship
/acceptance-test US-001
/security Review implementation
git commit -m "feat: Analytics dashboard (US-001)"
git push
```

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

## 📚 Key Commands Reference

### **Planning & Quality**
```bash
/user-story "As a..."          # Create user story
/spec-score                    # Check quality (must be ≥ 7.0)
/spec-enhance                  # Auto-improve specifications
/story-to-slice US-001 US-002  # Map to implementation
/parallel-strategy             # See what can be done in parallel
```

### **Development**
```bash
/debug-ui US-001              # Generate debug interface
/acceptance-test US-001       # Generate tests
/architect                    # System design help
/dba                         # Database design
/backend                     # API development
/frontend                    # UI development
/security                    # Security review
```

### **Utilities**
```bash
make dev                     # Start everything
make test                    # Run all tests
make logs                    # View logs
/issues                      # List GitHub issues
/help                        # Get help
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

## 🎨 Design System

The template includes a **modern dark theme** with glass morphism:

```tsx
// Beautiful components ready to use
import { Button, Card, StatCard } from '@/design-system/components';

<Card variant="glass" glow>
  <StatCard 
    title="Revenue" 
    value="$48,329"
    change={{ value: 12.5, trend: 'up' }}
  />
  <Button variant="primary" glow>
    Get Started
  </Button>
</Card>
```

### **Component Library**
- **Glass morphism** cards with blur effects
- **Gradient buttons** with glow on hover
- **Data visualization** components
- **Dark backgrounds** optimized for long coding sessions
- **Responsive** and mobile-first

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

## 📖 Documentation

### **Quick Guides**
- 🚀 [Quick Start Guide](QUICK_START.md) - Get running in 5 minutes
- 📘 [Complete Workflow Guide](docs/COMPLETE_WORKFLOW_GUIDE.md) - Detailed process documentation
- 📚 [Commands Reference](docs/COMMANDS_REFERENCE.md) - All commands explained

### **Feature Guides**
- 🎨 [Design System](design-system/DESIGN_SYSTEM.md) - Component library and styling
- ✅ [Quality Standards](docs/SPEC_QUALITY_GUIDE.md) - Specification requirements
- 🔄 [Spec Process](docs/SPEC_PROCESS.md) - Requirements workflow
- 📊 [Template Improvements](docs/TEMPLATE_IMPROVEMENTS.md) - What's new

### **Technical Guides**
- 🔧 [Setup Guide](SETUP.md) - Detailed setup instructions
- 🤖 [Claude Code Memory](CLAUDE.md) - AI agent configuration
- 🐛 [Troubleshooting](docs/TEMPLATE_FIXES.md) - Common issues & solutions

## 🏆 Why Use This Template?

### **For Solo Developers**
- **10x faster development** with AI assistance
- **Clear workflows** prevent getting stuck
- **Quality gates** ensure professional output
- **Incremental UI** approach saves debugging time

### **For Teams**
- **Consistent process** across all developers
- **Automated documentation** from user stories
- **Built-in code review** with security agent
- **Parallel work** optimization

### **For Startups**
- **Ship MVP in days** not months
- **Professional quality** from day one
- **Scalable architecture** that grows with you
- **Complete DevOps** pipeline included

## 💡 Best Practices

1. **Always start with user stories** - Clear requirements save time
2. **Build debug UI first** - See everything immediately
3. **Keep quality score ≥ 7.0** - Prevents technical debt
4. **Test continuously** - Catch issues early
5. **Use parallel work** - Maximize efficiency

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - Use it, modify it, ship it!

---

<div align="center">

**⭐ Star this repo if it helps you ship faster!**

[Quick Start](QUICK_START.md) • [Documentation](docs/) • [Design System](design-system/) • [Report Issue](https://github.com/yourusername/solo-software-factory/issues)

**Built with ❤️ for developers who ship fast**

</div>