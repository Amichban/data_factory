# Context Summary

## Recent Enhancements (2025-08-14)

### New Features Added
1. **Spec-to-Stories Command** (`/spec-to-stories`)
   - Generates multiple user stories from initial specification
   - Organizes by epics with priorities

2. **Incremental UI Development** (`/story-ui`)
   - Replaced debug-first approach
   - 4-step progression: raw → basic → structured → polished
   - Each step validates different aspects

3. **Enhanced Memory Management**
   - Created settings.json with context configuration
   - Added DECISIONS.md for architecture records
   - Added LEARNED_PATTERNS.md for discovered patterns
   - Implemented hooks for pre/post actions

4. **GitHub Actions Integration**
   - Quality gate checks on PRs
   - Command handling via comments
   - Automatic context synchronization
   - Specification quality validation

5. **Claude Hooks System**
   - Pre-action validation
   - Post-action updates
   - Spec quality checking
   - Automatic state management

## Project Structure
```
.claude/
├── settings.json         # Configuration
├── PROJECT_STATE.md      # Current work tracking
├── DECISIONS.md         # Architecture decisions
├── LEARNED_PATTERNS.md  # Discovered patterns
├── CONTEXT_SUMMARY.md   # This file
├── hooks/               # Automation scripts
│   ├── pre-action.sh
│   ├── post-action.sh
│   └── spec-quality.sh
├── agents/              # AI agent definitions
└── commands/            # Custom commands
```

## Active Configuration

### Context Management
- Max tokens: 200,000
- Strategy: Sliding window with smart summary
- Priority files maintained in context
- Automatic summarization at 80% capacity

### Memory Persistence
- Auto-save every 5 minutes
- Key files tracked: PROJECT_STATE, DECISIONS, LEARNED_PATTERNS
- Git integration for version control

### Quality Standards
- Minimum spec score: 7.0
- Required elements: User stories, acceptance criteria, tests
- Automated validation via hooks
- GitHub Actions enforcement

### Workflow
- User Story-Driven Development
- Incremental UI (4 steps)
- Vertical slicing
- Parallel work optimization
- Continuous validation

## Quick Start Commands

```bash
# Start new feature
/spec-to-stories "Initial requirements"
/user-story "Specific story"
/spec-score  # Must be ≥ 7.0

# Development
/story-ui US-001 --step 1  # Start incremental UI
/backend  # Build API
/frontend  # Build UI
/acceptance-test US-001  # Generate tests

# Memory management
Update PROJECT_STATE.md after changes
Add decisions to DECISIONS.md
Document patterns in LEARNED_PATTERNS.md
```

## Integration Points

### GitHub
- Issues created from accepted scopes
- PR quality gates
- Command handling in comments
- Automatic project board updates

### Development
- Docker Compose for local dev
- GitHub Actions for CI/CD
- Pre-commit hooks for quality
- Railway/GCP for deployment

## Recent Decisions

1. **Incremental UI over Debug UI**: Build progressively to validate at each step
2. **Quality Gates**: Enforce 7.0 minimum score before implementation
3. **Memory Persistence**: Track decisions and patterns for long-term learning
4. **GitHub Integration**: Use GitHub as single source of truth

## Next Actions

To use the enhanced template:
1. Review new commands in COMMANDS_REFERENCE.md
2. Set up GitHub Actions secrets if deploying
3. Configure .env for local development
4. Start with `/spec-to-stories` for new features
5. Use `/story-ui` for incremental development

## Support

- Documentation: `/docs/`
- Commands: `/help` in Claude Code
- Issues: GitHub Issues
- Context: This file and related .claude/ files

---

*Last Updated: 2025-08-14*
*Template Version: 2.0.0*