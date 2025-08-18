# Learned Patterns & Best Practices

## Successful Patterns

### 1. Start Simple, Iterate Fast
- Always begin with raw data display
- Add complexity only after basics work
- Get visual feedback immediately
- Test at each iteration

### 2. Vertical Slicing Works
- Complete features end-to-end
- Database → API → UI in one slice
- Easier to test and validate
- Clear deliverables

### 3. Quality Gates Save Time
- Spec score ≥ 7.0 prevents rework
- Clear requirements reduce bugs
- Acceptance criteria guide testing
- Less debugging overall

### 4. Agent Specialization
- Right tool for right job
- PM agent for planning
- Backend agent for APIs
- Frontend agent for UI
- Better quality per domain

### 5. Incremental UI Development
- Step 1: Raw data (validate API)
- Step 2: Basic interactions (test UX)
- Step 3: Structure (organize components)
- Step 4: Polish (apply design system)

## Anti-Patterns to Avoid

### 1. Building Blind
❌ Creating complete UI without API
❌ Polishing before functionality works
❌ Skipping visual feedback

### 2. Skipping Planning
❌ Jumping straight to code
❌ No acceptance criteria
❌ Vague requirements

### 3. Big Bang Integration
❌ Building everything separately
❌ Integration at the end
❌ No incremental testing

### 4. Ignoring Quality
❌ Accepting spec score < 7.0
❌ No tests
❌ Skipping security review

## Common Issues & Solutions

### Issue: Slow API Response
**Solution**: 
- Add Redis caching
- Use database indexes
- Implement pagination
- Consider async operations

### Issue: Complex State Management
**Solution**:
- Start with local state
- Add context only when needed
- Consider Zustand for complex cases
- Keep state close to usage

### Issue: Type Mismatches
**Solution**:
- Generate types from OpenAPI
- Use Pydantic for validation
- Single source of truth
- Test type boundaries

### Issue: Test Failures
**Solution**:
- Write tests with implementation
- Use acceptance criteria
- Mock external dependencies
- Test incrementally

## Performance Optimizations

### Backend
- Use async/await properly
- Batch database queries
- Implement caching strategy
- Profile with middleware

### Frontend
- Use React.memo wisely
- Implement virtual scrolling
- Lazy load components
- Optimize bundle size

### Database
- Add appropriate indexes
- Use eager loading
- Implement connection pooling
- Regular VACUUM/ANALYZE

## Security Considerations

### Always
- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Sanitize user content
- Use HTTPS everywhere

### Never
- Store passwords in plain text
- Trust client-side validation only
- Expose internal errors
- Commit secrets
- Use eval() or exec()

## Workflow Optimizations

### Parallel Work
- Frontend and backend simultaneously
- Tests while implementing
- Documentation alongside code
- Multiple features in branches

### Sequential Work
- Database schema first
- API contract second
- Implementation third
- Polish last

## Code Quality Indicators

### Good Signs
✅ Tests pass on first run
✅ Clear variable names
✅ Single responsibility
✅ Consistent patterns
✅ Good error messages

### Warning Signs
⚠️ Complex nested logic
⚠️ Long functions
⚠️ Magic numbers
⚠️ Duplicate code
⚠️ No error handling

## Estimation Guidelines

### Story Points
- 1 point: < 2 hours
- 2 points: 2-4 hours
- 3 points: 4-8 hours (1 day)
- 5 points: 1-2 days
- 8 points: 2-3 days
- 13 points: Consider splitting

### Velocity Tracking
- Measure completed points per week
- Account for meetings/reviews
- Include testing time
- Add 20% buffer for unknowns

## Communication Patterns

### With Agents
- Be specific with requirements
- Provide context
- Show examples
- Verify understanding

### In Code
- Clear commit messages
- Helpful error messages
- Comprehensive comments for complex logic
- Update documentation

## Continuous Improvement

### Weekly Review
- What worked well?
- What was challenging?
- What patterns emerged?
- What to try next?

### Metrics to Track
- Story completion rate
- Bug rate
- Test coverage
- Performance metrics
- User feedback

---

*This document is continuously updated as new patterns are discovered.*