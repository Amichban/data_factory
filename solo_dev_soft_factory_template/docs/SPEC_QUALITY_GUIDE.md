# Specification Quality Guide

Complete guide to creating high-quality specifications using the enhanced scope process.

## 🎯 The Quality-First Specification Process

```mermaid
graph TD
    A[Intent Issue] --> B[/scope]
    B --> C[/spec-lint]
    C --> D{Score >= 7?}
    D -->|No| E[/spec-enhance]
    E --> F[/define-terms]
    F --> C
    D -->|Yes| G[/spec-score --verbose]
    G --> H[/parallel-strategy]
    H --> I[/accept-scope]
    I --> J[High-Quality Issues Created]
```

## 📋 Command Reference

### Core Validation Commands

| Command | Purpose | When to Use | Output |
|---------|---------|-------------|--------|
| `/spec-lint` | Find issues and ambiguities | After `/scope` | JSON list of issues by severity |
| `/spec-score` | Rate quality (0-10) | Before `/accept-scope` | Score + detailed feedback |
| `/define-terms` | Generate glossary | When lint finds undefined terms | Complete glossary YAML |
| `/spec-enhance` | Fix issues automatically | When score < 7 | Enhanced specification |
| `/check-consistency` | Verify internal consistency | Before implementation | Dependency matrix |
| `/gen-tests` | Generate test scenarios | After enhancement | Test cases + examples |

### Workflow Commands

| Command | Purpose | Prerequisites |
|---------|---------|---------------|
| `/scope #1` | Generate initial specification | Intent issue exists |
| `/review-agents` | Review agent allocations | Scope generated |
| `/parallel-strategy` | Plan parallelization | Scope generated |
| `/accept-scope` | Create issues from scope | Score >= 7.0 |

## 📈 Quality Standards

### Minimum Scores by Stage

| Stage | Minimum Score | Blocking Issues | Required Elements |
|-------|---------------|-----------------|-------------------|
| **Draft** | 3.0 | - | Basic structure |
| **Review** | 5.0 | Critical issues | Acceptance criteria |
| **Development Ready** | 7.0 | Critical + High | Glossary, examples |
| **Production Ready** | 8.5 | Any High | Full test coverage |

### Score Breakdown

```yaml
Overall Score = Weighted Average of:
  - Clarity: 25%
  - Completeness: 25%
  - Consistency: 20%
  - Testability: 15%
  - Implementability: 15%
```

## 🔍 Common Issues and Fixes

### 1. Undefined Terms

**Issue**: Technical terms used without definition
```yaml
❌ BAD: "Process when spike occurs"
```

**Fix**: Define precisely
```yaml
✅ GOOD: 
term: spike
definition: "Price movement where abs(change) > ATR(14) * 2"
```

### 2. Ambiguous Formulas

**Issue**: Mathematical operations unclear
```yaml
❌ BAD: "Calculate percentage"
```

**Fix**: Provide complete formula
```yaml
✅ GOOD: 
formula: "(new - old) / old * 100"
edge_cases:
  - if old == 0: return 0
  - if new == null: return null
```

### 3. Missing Edge Cases

**Issue**: Boundary conditions not specified
```yaml
❌ BAD: "Validate user age"
```

**Fix**: Specify all boundaries
```yaml
✅ GOOD:
validation:
  age:
    min: 13
    max: 120
    null_handling: reject
    type: integer
```

### 4. Vague Success Criteria

**Issue**: Non-measurable outcomes
```yaml
❌ BAD: "System should be fast"
```

**Fix**: Specific metrics
```yaml
✅ GOOD:
performance:
  api_latency_p95: < 200ms
  api_latency_p99: < 500ms
  throughput: > 1000 req/sec
```

## 📝 Specification Template

### High-Quality Slice Structure

```yaml
slice:
  id: "user-authentication"
  title: "User Authentication System"
  
  # Clear description
  description: |
    Implement secure user authentication using JWT tokens
    with email/password credentials and session management
  
  # Measurable acceptance criteria
  acceptance_criteria:
    - "Users can register with email (RFC 5322) and password (8-128 chars)"
    - "Passwords hashed with bcrypt (cost 12) before storage"
    - "Login returns JWT (30 min) and refresh token (7 days)"
    - "Rate limiting: 5 attempts per 15 minutes per IP"
    - "Session timeout after 30 minutes of inactivity"
  
  # Technical specifications
  technical_details:
    api_endpoints:
      - method: POST
        path: /auth/register
        request: {email: string, password: string}
        response: {user_id: uuid, created_at: datetime}
      
      - method: POST
        path: /auth/login
        request: {email: string, password: string}
        response: {token: string, expires_in: number}
    
    database_schema:
      users:
        id: uuid primary key
        email: varchar(255) unique not null
        password_hash: varchar(60) not null
        created_at: timestamp default now()
        last_login: timestamp null
    
    validation_rules:
      email: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      password: 
        min_length: 8
        max_length: 128
        require_uppercase: true
        require_lowercase: true
        require_number: true
    
    error_codes:
      AUTH_001: "Invalid email format"
      AUTH_002: "Invalid credentials"
      AUTH_003: "Account locked"
      AUTH_004: "Token expired"
  
  # Examples with edge cases
  examples:
    successful_login:
      request: {email: "user@example.com", password: "SecurePass123!"}
      response: {token: "eyJ...", expires_in: 1800}
    
    failed_login:
      request: {email: "user@example.com", password: "wrong"}
      response: {error: "AUTH_002", message: "Invalid credentials"}
    
    rate_limited:
      request: {email: "user@example.com", password: "attempt6"}
      response: {error: "AUTH_003", message: "Too many attempts"}
  
  # Test scenarios
  test_scenarios:
    unit_tests:
      - "Password hashing uses bcrypt"
      - "Email validation follows RFC 5322"
      - "Token generation uses secure random"
    
    integration_tests:
      - "Full registration → login → logout flow"
      - "Rate limiting across multiple IPs"
      - "Token refresh before expiry"
    
    security_tests:
      - "SQL injection in email field"
      - "XSS in password field"
      - "Timing attacks on password comparison"
  
  # Dependencies and sequencing
  dependencies: []
  estimate: "M"  # S=3pts, M=5pts, L=8pts, XL=13pts
  risk: "Medium"
  
  # Agent sequence
  agent_sequence:
    - agent: architect
      task: "Design auth flow and token strategy"
    - agent: dba
      task: "Create user and session tables"
    - agent: backend
      task: "Implement auth endpoints"
    - agent: frontend
      task: "Create login/register forms"
    - agent: security
      task: "Security review and penetration test"
```

## 🚀 Best Practices

### 1. Start with Quality
```bash
# Don't rush to accept-scope
/scope #1
/spec-lint              # Find issues early
/spec-enhance           # Fix them automatically
/define-terms           # Create glossary
/spec-score            # Verify quality
# Only then...
/accept-scope
```

### 2. Define Everything
- Every technical term needs a definition
- Every calculation needs a formula
- Every edge case needs handling
- Every error needs a code

### 3. Include Examples
- Success scenarios
- Failure scenarios
- Edge cases
- Performance boundaries

### 4. Make It Testable
- Specific assertions
- Measurable outcomes
- Clear pass/fail criteria
- Test data requirements

### 5. Version Your Specs
```yaml
spec_version: 1.2.0
last_modified: 2024-01-15
modified_by: PM Agent
change_log:
  - v1.2.0: Added rate limiting
  - v1.1.0: Enhanced error codes
  - v1.0.0: Initial specification
```

## 📊 Quality Metrics

### Track Your Progress

```yaml
spec_quality_history:
  - date: 2024-01-10
    score: 4.5
    issues: {critical: 5, high: 12, medium: 8}
  
  - date: 2024-01-12
    score: 7.2
    issues: {critical: 0, high: 3, medium: 5}
    improvements:
      - Added glossary
      - Fixed formulas
      - Added examples
  
  - date: 2024-01-15
    score: 8.7
    issues: {critical: 0, high: 0, medium: 2}
    ready_for: production
```

### Success Indicators

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| First-time score | > 5.0 | Shows initial quality |
| Enhancement cycles | < 3 | Efficiency of improvement |
| Final score | > 8.0 | Production readiness |
| Undefined terms | 0 | Clarity |
| Test coverage | > 90% | Quality assurance |

## 🎓 Learning from High-Quality Specs

### Characteristics of 9+ Score Specs

1. **Complete Glossary**: Every term defined
2. **Rich Examples**: Multiple scenarios covered
3. **Clear Formulas**: Mathematical precision
4. **Error Catalog**: All errors documented
5. **Test Strategy**: Comprehensive test plan
6. **Performance Targets**: Specific SLAs
7. **Security Considerations**: Threat model included
8. **Monitoring Plan**: Observability defined

## 🔄 Continuous Improvement

### After Each Project

1. Review spec scores over time
2. Identify recurring issues
3. Update templates and patterns
4. Share learnings with team
5. Enhance linting rules
6. Improve enhancement algorithms

### Spec Quality Checklist

Before accepting any scope, verify:

- [ ] Score >= 7.0
- [ ] No critical issues
- [ ] No high priority issues
- [ ] Glossary complete
- [ ] Examples provided
- [ ] Test scenarios defined
- [ ] Error codes documented
- [ ] Performance targets set
- [ ] Security considered
- [ ] Monitoring planned

## 🆘 Troubleshooting

### Spec Won't Improve

If score plateaus below 7.0:
1. Run `/spec-lint --verbose` for detailed issues
2. Focus on one dimension: `/spec-enhance --focus clarity`
3. Add examples manually, then re-enhance
4. Break complex slices into smaller ones
5. Get human review for domain-specific issues

### Too Many Ambiguities

When lint finds 20+ issues:
1. Start with `/define-terms` to establish vocabulary
2. Run `/spec-enhance --interactive` for guided improvement
3. Focus on critical issues first
4. Use domain experts for business rules
5. Document decisions as you resolve ambiguities

---

**Remember**: High-quality specifications lead to faster development, fewer bugs, and happier developers. Invest time upfront to save time throughout the project!