# 📘 Complete Workflow Guide - Solo Software Factory

> **The definitive guide** to using every feature of the template effectively, from idea to production.

---

## 📋 Table of Contents

1. [Overview - What We've Built](#overview---what-weve-built)
2. [The Complete Process](#the-complete-process)
3. [Commands & Agents Reference](#commands--agents-reference)
4. [Step-by-Step Workflows](#step-by-step-workflows)
5. [Best Practices](#best-practices)
6. [Quick Reference Card](#quick-reference-card)

---

## Overview - What We've Built

### **The Template Now Includes:**

```
🎯 Core Features:
├── 📝 User Story-Driven Development (NEW)
├── 🔧 Incremental UI Development (NEW)
├── ✅ Quality Gates & Validation (NEW)
├── 🤖 6 Specialized AI Agents
├── 🎨 Dark Theme Design System (NEW)
├── 🧪 Automated Test Generation (NEW)
└── 🚀 Complete DevOps Pipeline
```

### **The Development Flow:**

```mermaid
graph LR
    A[💡 Idea] --> B[📝 User Story]
    B --> C[✅ Quality Check]
    C --> D[🔧 Incremental UI]
    D --> E[🧪 Tests]
    E --> F[💻 Implementation]
    F --> G[🚀 Production]
```

---

## The Complete Process

### **Phase 1: Planning & Definition** 📝

**Purpose:** Transform vague ideas into clear, testable requirements

```bash
# Step 1: Create a user story
/user-story "As a [user type], I want to [action] so that [benefit]"
# Creates: US-001-[feature].md with acceptance criteria

# Step 2: Check quality
/spec-lint          # Find issues
/spec-score         # Must be ≥ 7.0
/spec-enhance       # Auto-improve if needed
/define-terms       # Create glossary

# Step 3: Map to implementation
/story-to-slice US-001 US-002 US-003
# Creates: VS-001 vertical slice with phases
```

### **Phase 2: Incremental Development** 🔧

**Purpose:** Build UI progressively from raw data to polished interface

```bash
# Step 4: Start incremental UI development
/story-ui US-001 --step 1
# Step 1: Display raw data (verify API connection)
# Step 2: Basic interactions (functionality)
# Step 3: Structure & layout (organization)
# Step 4: Polish & design system (beauty)

# Step 5: Generate tests
/acceptance-test US-001
# Creates: Automated tests from acceptance criteria

# Step 6: Check parallelization
/parallel-strategy
# Shows: What can be built simultaneously
```

### **Phase 3: Implementation** 💻

**Purpose:** Build the actual feature with AI assistance

```bash
# Step 7: Follow agent sequence
/architect Design the system architecture
/dba Create database schema
/backend Implement API endpoints
/frontend Build UI components
/security Review implementation

# Step 8: Test continuously
/run-acceptance US-001
```

### **Phase 4: Production** 🚀

**Purpose:** Polish and deploy

```bash
# Step 9: Final quality check
/spec-score         # Verify still ≥ 7.0
/security Review all code

# Step 10: Deploy
git commit -m "feat: [feature] (US-001)"
git push            # Auto-deploys
```

---

## Commands & Agents Reference

### **🎯 Planning Commands**

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| **`/user-story`** | Create user story | Feature description | US-XXX.md with acceptance criteria |
| **`/scope`** | Analyze GitHub issue | Issue URL | Vertical slices + user stories |
| **`/story-to-slice`** | Map stories to implementation | US-001 US-002 | VS-XXX with phases |
| **`/parallel-strategy`** | Plan parallel work | None | Work tracks + dependencies |
| **`/review-agents`** | See agent recommendations | None | Suggested agent sequence |
### **✅ Quality Commands**

| Command | Purpose | Requirement | Action if Fails |
|---------|---------|-------------|-----------------|
| **`/spec-lint`** | Find specification issues | None | Fix issues found |
| **`/spec-score`** | Rate quality (0-10) | Score ≥ 7.0 | Run `/spec-enhance` |
| **`/spec-enhance`** | Auto-improve specs | None | Adds missing elements |
| **`/define-terms`** | Create technical glossary | None | Defines all terms |
| **`/check-consistency`** | Verify internal consistency | None | Resolve conflicts |

### **🔧 Development Commands**

| Command | Purpose | Creates | Access At |
|---------|---------|---------|-----------|
| **`/story-ui`** | Build incremental UI | Progressive UI components | /app/[feature] |
| **`/acceptance-test`** | Generate tests from story | Test files | tests/acceptance/ |
| **`/gen-tests`** | Generate all test types | Unit/integration/E2E | tests/ |
| **`/issue`** | Focus on GitHub issue | Context + branch | Current work |
| **`/db-setup`** | Connect existing database | Models + migrations | apps/api/models/ |

### **🤖 AI Agents**

| Agent | Command | Specialization | When to Use |
|-------|---------|----------------|-------------|
| **PM** | `/pm` | Planning, stories, coordination | Start of feature |
| **Architect** | `/architect` | System design, patterns | Before building |
| **DBA** | `/dba` | Database schema, optimization | Data layer work |
| **Backend** | `/backend` | FastAPI, business logic | API development |
| **Frontend** | `/frontend` | React, Next.js, UI | User interface |
| **Security** | `/security` | Auth, validation, threats | Review & hardening |

---

## Step-by-Step Workflows

### **Workflow 1: Building a New Feature** 🆕

```bash
# 1. Define what you're building
/user-story "As a user, I want to see analytics dashboard"

# 2. Validate quality
/spec-lint
/spec-score  # Must be ≥ 7.0

# 3. Build UI incrementally for immediate feedback
/story-ui US-001 --step 1  # Start with raw data
# Progress through steps as you develop
# Visit: http://localhost:3000/analytics

# 4. Generate tests
/acceptance-test US-001

# 5. Build backend
/architect How should I structure the analytics system?
/dba Create tables for analytics data
/backend Implement these endpoints:
  - GET /api/v1/analytics/summary
  - GET /api/v1/analytics/trends
  - WebSocket /ws/analytics for real-time

# 6. Build frontend
/frontend Create analytics dashboard using:
  - StatCard components for KPIs
  - DataGrid for tabular data
  - Charts for trends
  - Real-time updates via WebSocket

# 7. Review and test
/security Review the analytics implementation
/run-acceptance US-001

# 8. Ship it
git add .
git commit -m "feat: Analytics dashboard (US-001)"
git push
```

### **Workflow 2: Fixing a Bug** 🐛

```bash
# 1. Create bug story
/user-story "As a user, I want the login error to be fixed"

# 2. Create minimal UI to reproduce
/story-ui US-B001 --step 1  # Raw data to see the issue

# 3. Investigate
/backend Debug the login endpoint issue
/frontend Check login form validation

# 4. Fix and test
/backend Fix the authentication bug
/run-acceptance US-B001

# 5. Verify fix
/security Review the bug fix
git commit -m "fix: Login authentication error (US-B001)"
```

### **Workflow 3: Adding to Existing Feature** ➕

```bash
# 1. Create enhancement story
/user-story "As a user, I want to export data as PDF"

# 2. Check where it fits
/story-to-slice US-010  # Add to existing slice

# 3. Continue incremental UI
/story-ui US-010 --step 3  # Continue from structure phase

# 4. Add functionality
/backend Add PDF export endpoint
/frontend Add export button to dashboard

# 5. Test enhancement
/acceptance-test US-010
/run-acceptance US-010
```

### **Workflow 4: Database Changes** 🗄️

```bash
# 1. Plan the change
/dba I need to add user preferences table

# 2. Create migration
cd apps/api
alembic revision --autogenerate -m "Add user preferences"

# 3. Update models
/backend Update SQLAlchemy models for preferences

# 4. Run migration
alembic upgrade head

# 5. Test
/backend Create CRUD operations for preferences
```

### **Workflow 5: Using Existing Database** 🔌

```bash
# 1. Connect to existing database
/db-setup postgresql://user:pass@host:5432/existing_db

# 2. Generate models from database
/dba Generate SQLAlchemy models from existing schema

# 3. Create safe integration
/architect How do I safely read from existing, write to new?

# 4. Implement dual-database pattern
/backend Implement read from legacy, write to new pattern
```

---

## Best Practices

### **✅ DO's - The Right Way**

#### **1. Always Start with User Stories**
```bash
# ✅ GOOD - Clear requirement first
/user-story "As a user, I want to search products"
/debug-ui US-001
/backend Implement search

# ❌ BAD - Jumping to code
/backend Just build search somehow
```

#### **2. Build UI Incrementally**
```bash
# ✅ GOOD - Progressive development with visual feedback
/story-ui US-001 --step 1  # Start with raw data
/story-ui US-001 --step 2  # Add basic interactions
/story-ui US-001 --step 3  # Structure properly
/story-ui US-001 --step 4  # Polish with design system

# ❌ BAD - Building complete UI from start
/frontend Create production UI directly
```

#### **3. Check Quality Gates**
```bash
# ✅ GOOD - Ensure quality
/spec-score  # Must be ≥ 7.0 before building

# ❌ BAD - Skip validation
/accept-scope  # Without checking score
```

#### **4. Follow Agent Sequences**
```bash
# ✅ GOOD - Logical order
/architect Design first
/dba Schema second
/backend API third
/frontend UI last

# ❌ BAD - Random order
/frontend Build UI without API
```

#### **5. Test Continuously**
```bash
# ✅ GOOD - Test each phase
/run-acceptance US-001  # After each major change

# ❌ BAD - Test only at end
# Build everything then test
```

### **📊 Quality Metrics to Track**

```yaml
Track These:
  story_completion_rate: 85%+
  spec_quality_score: 7.0+
  test_coverage: 80%+
  incremental_ui_steps: All 4 steps
  agent_utilization: High
```

---

## Quick Reference Card

### **🚀 Feature Development Checklist**

```markdown
□ 1. Create user story (`/user-story`)
□ 2. Check quality (`/spec-score` ≥ 7.0)
□ 3. Start incremental UI (`/story-ui --step 1`)
□ 4. Generate tests (`/acceptance-test`)
□ 5. Design architecture (`/architect`)
□ 6. Create database (`/dba`)
□ 7. Build backend (`/backend`)
□ 8. Continue UI steps (`/story-ui --step 2,3,4`)
□ 9. Security review (`/security`)
□ 10. Run tests (`/run-acceptance`)
□ 11. Commit with story ID
□ 12. Push to deploy
```

### **🎯 Command Quick Reference**

```bash
# Planning
/user-story "As a..."     # Create story
/story-to-slice US-001     # Map to implementation
/parallel-strategy         # Plan parallel work

# Quality
/spec-lint                 # Find issues
/spec-score               # Check quality (≥7.0)
/spec-enhance             # Auto-improve

# Development
/story-ui US-001          # Incremental UI (4 steps)
/acceptance-test US-001   # Generate tests
/[agent] [task]           # Use AI agent

# Deployment
git commit -m "feat: (US-001)"
git push                  # Auto-deploy
```

### **🤖 Agent Selection Guide**

```yaml
For Planning: /pm
For Design: /architect
For Database: /dba
For API: /backend
For UI: /frontend
For Security: /security
```

### **📁 File Structure After Commands**

```
project/
├── user-stories/
│   └── US-001-dashboard.md     # From /user-story
├── slices/
│   └── VS-001/                 # From /story-to-slice
│       └── tests/              # From /acceptance-test
├── apps/
│   ├── api/                    # Modified by /backend
│   └── web/
│       └── app/
│           └── [feature]/
│               ├── step-1-raw.tsx     # From /story-ui --step 1
│               ├── step-2-basic.tsx   # From /story-ui --step 2
│               ├── step-3-structured.tsx # From /story-ui --step 3
│               ├── step-4-polished.tsx   # From /story-ui --step 4
│               └── page.tsx           # Current active version
└── tests/
    └── acceptance/             # From /acceptance-test
```

---

## Common Scenarios

### **"I have a vague idea"**
```bash
/pm Help me clarify this idea: [your idea]
/user-story [refined idea]
/scope
```

### **"I need to move fast"**
```bash
/parallel-strategy          # See what can be done in parallel
# Then open multiple terminals:
# Terminal 1: /backend
# Terminal 2: /frontend
# Terminal 3: /dba
```

### **"I'm not sure about the architecture"**
```bash
/architect What's the best way to [your challenge]?
/architect Review my approach: [your plan]
```

### **"I want to see it working quickly"**
```bash
/story-ui US-001 --step 1  # Start with raw data display
/backend Create mock data endpoint
# See data immediately, then progressively enhance
```

---

## Tips for Maximum Productivity

1. **Batch Similar Work**: Do all `/dba` work together, all `/frontend` together
2. **Build Incrementally**: Progress through all 4 UI steps
3. **Test After Each Step**: Validate at each UI phase
4. **Commit Frequently**: Small, focused commits with story IDs
5. **Review Weekly**: Check your spec scores and test coverage

---

## Getting Help

- **See all commands**: `/help`
- **Check current work**: `/issues`
- **Review project state**: Check `.claude/PROJECT_STATE.md`
- **Debug problems**: Check step-by-step UI files
- **Quality issues**: Run `/spec-enhance`

---

## Summary

The enhanced Solo Software Factory template now provides:

1. **Clear Process**: Idea → Story → Incremental UI → Test → Build → Ship
2. **Quality Gates**: Nothing ships below 7.0 quality score
3. **Progressive Development**: Build UI in 4 steps (raw → basic → structured → polished)
4. **AI Assistance**: Right agent for right task
5. **Automated Testing**: Tests generated from stories

**Remember**: The key is to follow the incremental process. Don't skip UI steps - each validates different aspects. Start with raw data display to verify your API works before investing in complex UI!