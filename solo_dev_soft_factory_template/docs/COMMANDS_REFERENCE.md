# 📚 Commands & Agents Reference

> Complete documentation of all commands and AI agents in the Solo Software Factory template

---

## 🎯 Commands by Category

### **📝 Planning & User Stories**

#### `/user-story`
Create comprehensive user stories with acceptance criteria.

```bash
# Basic usage
/user-story "As a [role], I want to [action] so that [benefit]"

# Options
/user-story --epic "Feature Name"     # Group under epic
/user-story --template                 # Show story template
/user-story --from-issue #5           # Generate from GitHub issue
```

**Output:**
- `user-stories/US-XXX-[name].md`
- Acceptance criteria
- Test scenarios
- Technical specifications
- Debug UI requirements

---

#### `/scope`
Analyze GitHub issues and create implementation plan.

```bash
# From GitHub issue
/scope https://github.com/user/repo/issues/1

# From local issue
/scope #5
```

**Output:**
- Vertical slices
- User stories
- Dependencies
- Agent sequences
- Parallelization strategy

---

#### `/story-to-slice`
Map user stories to vertical slices for implementation.

```bash
# Map stories to new slice
/story-to-slice US-001 US-002 US-003

# Options
/story-to-slice --analyze             # Analyze relationships
/story-to-slice --optimize            # Optimize boundaries
/story-to-slice --from-epic "Epic"    # Create from epic
```

**Output:**
- `slices/VS-XXX/slice.yaml`
- Implementation phases
- Test matrix
- Agent sequence

---

#### `/parallel-strategy`
Analyze what work can be done in parallel.

```bash
/parallel-strategy
```

**Output:**
- Work tracks (Backend, Frontend, DevOps)
- Dependencies
- Suggested Git branches
- Optimal sequencing

---

### **✅ Quality & Validation**

#### `/spec-lint`
Find issues in specifications.

```bash
/spec-lint                    # Check current scope
/spec-lint --verbose         # Detailed output
```

**Issues Found:**
- Undefined terms
- Missing acceptance criteria
- Ambiguous requirements
- Incomplete edge cases

---

#### `/spec-score`
Rate specification quality (0-10).

```bash
/spec-score                   # Get quality score
/spec-score --verbose        # Detailed breakdown
```

**Scoring Dimensions:**
- Clarity (25%)
- Completeness (25%)
- Consistency (20%)
- Testability (15%)
- Implementability (15%)

**Required:** Score ≥ 7.0 to proceed

---

#### `/spec-enhance`
Automatically improve specifications.

```bash
/spec-enhance                      # Auto-improve
/spec-enhance --focus clarity      # Target specific area
/spec-enhance --interactive        # Guided improvement
/spec-enhance --target-score 8.5   # Enhance to target
```

**Improvements:**
- Adds missing elements
- Clarifies ambiguities
- Adds examples
- Defines terms

---

#### `/define-terms`
Generate technical glossary.

```bash
/define-terms                  # From current spec
/define-terms --domain finance # Include domain terms
/define-terms --formulas       # Add mathematical definitions
```

**Output:**
- Complete glossary
- Mathematical formulas
- Edge case definitions
- Domain terminology

---

#### `/check-consistency`
Verify internal consistency.

```bash
/check-consistency              # Check all
/check-consistency --deep       # Cross-slice validation
/check-consistency --fix        # Suggest fixes
```

**Checks:**
- Circular dependencies
- Data model conflicts
- API mismatches
- State conflicts

---

### **🔧 Development**

#### `/debug-ui`
Generate debug interface for immediate visual feedback.

```bash
/debug-ui US-001               # For user story
/debug-ui VS-001               # For vertical slice
/debug-ui --feature dashboard  # For feature
/debug-ui --bug US-B001        # For bug reproduction
/debug-ui --extend US-001      # Extend existing
```

**Creates:**
- Debug dashboard at `/debug/[feature]`
- Data viewers
- API testers
- State inspectors
- Test runners

---

#### `/acceptance-test`
Generate tests from user stories.

```bash
/acceptance-test US-001         # From story
/acceptance-test VS-001         # From slice
/acceptance-test --all          # All stories
```

**Output:**
- `tests/acceptance/test_us_xxx.py`
- Given-When-Then scenarios
- Performance tests
- Edge case tests

---

#### `/gen-tests`
Generate comprehensive test suites.

```bash
/gen-tests US-001              # All test types
/gen-tests --unit              # Unit tests only
/gen-tests --integration       # Integration tests
/gen-tests --e2e               # End-to-end tests
/gen-tests --performance       # Performance tests
/gen-tests --security          # Security tests
```

**Output:**
- Complete test coverage
- Test data factories
- Fixtures
- Mocks

---

#### `/issue`
Focus on specific GitHub issue.

```bash
/issue #5                      # Load issue context
/issue 123                     # Issue by number
```

**Actions:**
- Loads issue details
- Extracts acceptance criteria
- Shows agent recommendations
- Suggests branch name
- Updates project state

---

#### `/db-setup`
Setup database connection.

```bash
# Connect to existing database
/db-setup postgresql://user:pass@host:5432/dbname

# Options
/db-setup --generate-models    # Create SQLAlchemy models
/db-setup --dual-db            # Setup read/write split
/db-setup --introspect         # Analyze existing schema
```

**Output:**
- Database configuration
- Generated models
- Migration scripts
- Connection testing

---

### **📊 Project Management**

#### `/issues`
List all GitHub issues and status.

```bash
/issues                        # All issues
/issues --open                 # Open only
/issues --my                   # Assigned to me
```

---

#### `/review-agents`
Review recommended agent sequence.

```bash
/review-agents                 # For current work
/review-agents VS-001          # For specific slice
```

**Shows:**
- Recommended agent order
- Task for each agent
- Estimated time
- Dependencies

---

#### `/accept-scope`
Accept scope and create GitHub issues.

```bash
# As GitHub comment
/accept-scope

# In Claude Code
/accept-scope --confirm
```

**Actions:**
- Creates GitHub issues
- Links to project board
- Sets up tracking
- Assigns to milestone

---

## 🤖 AI Agents Reference

### **PM Agent** (`/pm`)

Product management and planning specialist.

```bash
/pm Help me plan a dashboard feature
/pm Analyze these requirements: [requirements]
/pm Create user stories for [feature]
/pm What's the status of [feature]?
```

**Capabilities:**
- Requirements analysis
- User story creation
- Scope definition
- Progress tracking
- Risk assessment

---

### **Architect Agent** (`/architect`)

System design and architecture specialist.

```bash
/architect Design authentication system
/architect What's the best pattern for [problem]?
/architect Review my architecture: [design]
/architect How should I handle [technical challenge]?
```

**Capabilities:**
- System design
- Pattern recommendations
- Architecture reviews
- Technology selection
- Performance optimization

---

### **DBA Agent** (`/dba`)

Database design and optimization specialist.

```bash
/dba Design schema for user management
/dba Optimize this query: [SQL]
/dba Create indexes for [table]
/dba Design migration for [change]
```

**Capabilities:**
- Schema design
- Query optimization
- Index planning
- Migration creation
- Performance tuning

---

### **Backend Agent** (`/backend`)

FastAPI and business logic specialist.

```bash
/backend Create CRUD endpoints for tasks
/backend Implement authentication with JWT
/backend Add WebSocket support for real-time updates
/backend Create background job for [task]
```

**Capabilities:**
- API development
- Business logic
- Authentication/Authorization
- Background jobs
- Integration with services

---

### **Frontend Agent** (`/frontend`)

React/Next.js UI development specialist.

```bash
/frontend Create dashboard with our design system
/frontend Build responsive navigation
/frontend Add real-time updates to [component]
/frontend Implement form with validation
```

**Capabilities:**
- Component development
- State management
- Responsive design
- Real-time features
- Performance optimization

---

### **Security Agent** (`/security`)

Security review and hardening specialist.

```bash
/security Review authentication implementation
/security Check for vulnerabilities
/security Implement rate limiting
/security Review API endpoints for security
```

**Capabilities:**
- Security audits
- Vulnerability assessment
- Authentication review
- Input validation
- Threat modeling

---

## 🔄 Command Workflows

### **Feature Development Flow**

```bash
# 1. Planning
/user-story "As a user, I want..."
/spec-score                    # Check quality

# 2. Design
/architect Design the feature
/review-agents                 # See recommendations

# 3. Development
/story-ui US-001              # Incremental UI (4 steps)
/dba Create schema
/backend Build API
/frontend Create UI

# 4. Testing
/acceptance-test US-001
/security Review implementation

# 5. Deployment
git commit -m "feat: (US-001)"
git push
```

### **Bug Fix Flow**

```bash
# 1. Document bug
/user-story "As a user, I want [bug] fixed"

# 2. Reproduce
/debug-ui --bug US-B001

# 3. Fix
/backend Fix the issue
/frontend Update UI if needed

# 4. Test
/run-acceptance US-B001
```

### **Database Change Flow**

```bash
# 1. Plan change
/dba Design new schema

# 2. Create migration
cd apps/api
alembic revision --autogenerate -m "description"

# 3. Apply
alembic upgrade head

# 4. Update code
/backend Update models and endpoints
```

---

## 📝 Command Options & Flags

### **Global Options**

Available for most commands:

- `--help` - Show command help
- `--verbose` - Detailed output
- `--dry-run` - Preview without changes
- `--force` - Override safety checks

### **Output Formats**

- `--json` - JSON output
- `--yaml` - YAML output
- `--markdown` - Markdown output

### **Filtering**

- `--filter [criteria]` - Filter results
- `--limit [n]` - Limit output
- `--since [date]` - Time-based filter

---

## 🎯 Quick Command Lookup

| Need | Command |
|------|---------|
| Create user story | `/user-story` |
| Check quality | `/spec-score` |
| Build debug UI | `/debug-ui` |
| Generate tests | `/acceptance-test` |
| Plan feature | `/pm` |
| Design system | `/architect` |
| Create database | `/dba` |
| Build API | `/backend` |
| Build UI | `/frontend` |
| Review security | `/security` |
| See all issues | `/issues` |
| Deploy | `git push` |

---

## 💡 Tips

1. **Chain Commands**: Commands can reference previous outputs
2. **Use Tab Completion**: Most commands support tab completion
3. **Check History**: Use up arrow to repeat commands
4. **Save Common Commands**: Create aliases for frequently used commands
5. **Combine Agents**: Multiple agents can work on same feature

---

## 🆘 Getting Help

```bash
/help                 # General help
/help [command]       # Specific command help
/commands             # List all commands
/agents               # List all agents
```

---

**Remember:** Commands and agents work together. Use commands for specific actions, agents for intelligent assistance!