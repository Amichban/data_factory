---
name: spec-score
description: Rate specification quality with detailed scoring rubric and feedback
tools: [Read, Write]
---

# Specification Quality Scorer

Provides a comprehensive quality score (0-10) with detailed feedback across multiple dimensions.

## Usage

```bash
/spec-score                    # Score the current scope.json
/spec-score --verbose         # Include detailed breakdown
/spec-score --fix             # Generate improved version
```

## Scoring Dimensions

### 1. **Clarity** (0-10)
- Unambiguous language
- Precise technical terms
- Clear success criteria
- Well-defined boundaries

### 2. **Completeness** (0-10)
- All user stories covered
- Edge cases specified
- Error scenarios defined
- Integration points documented

### 3. **Consistency** (0-10)
- No contradictions
- Uniform terminology
- Aligned data models
- Coherent workflows

### 4. **Testability** (0-10)
- Measurable criteria
- Verifiable outcomes
- Clear assertions
- Defined test data

### 5. **Implementability** (0-10)
- Technical feasibility
- Clear algorithms
- Defined data structures
- Realistic timelines

## Output Format

```markdown
## Specification Quality Report

**Overall Score: 7.5/10** (Good)

### Dimensional Breakdown
- ✅ **Clarity**: 8/10
- ⚠️ **Completeness**: 6/10  
- ✅ **Consistency**: 9/10
- ⚠️ **Testability**: 7/10
- ✅ **Implementability**: 8/10

### Strengths ✅
1. Well-structured vertical slices
2. Clear acceptance criteria format
3. Good separation of concerns
4. Realistic timeline estimates

### Areas for Improvement 🔧

#### Critical (Fix immediately)
- Missing glossary of technical terms
- Undefined error handling strategy
- No data validation rules

#### High Priority
- Add example calculations for complex formulas
- Specify timezone handling
- Define performance benchmarks

#### Medium Priority
- Include state diagrams
- Add API contract examples
- Specify monitoring requirements

### Detailed Feedback

#### Clarity Issues
```
Location: slice.auth-login.formula
Issue: "Calculate session timeout"
Problem: No formula or threshold specified
Fix: timeout_seconds = last_activity + (60 * 30) < current_time
```

#### Completeness Gaps
```
Missing: Password reset flow
Impact: Critical user journey undefined
Add: Password reset slice with email verification
```

### Recommendations

1. **Add Glossary Section**
   ```yaml
   glossary:
     session: JWT token with 30-min idle timeout
     active_user: User with activity in last 7 days
     spike: Price movement > 2 * ATR(14)
   ```

2. **Include Decision Log**
   ```yaml
   decisions:
     - id: D001
       question: How handle concurrent sessions?
       decision: Allow multiple, track all
       rationale: Better UX for multi-device users
   ```

3. **Add Example Scenarios**
   ```yaml
   examples:
     - scenario: Successful login
       input: {email: "user@example.com", password: "..."}
       output: {token: "jwt...", expires_in: 1800}
   ```

### Comparison to Standards

| Aspect | Your Spec | Industry Standard | Gap |
|--------|-----------|------------------|-----|
| Requirements Coverage | 75% | 90% | -15% |
| Edge Case Handling | 60% | 80% | -20% |
| Test Coverage Definition | 70% | 85% | -15% |
| Performance Specs | 80% | 75% | +5% ✅ |

### Quality Trend
```
Initial Score: 5.5/10
After /spec-enhance: 7.5/10 (+2.0)
Target Score: 8.5/10
```

### Action Items

**Immediate (Block release)**
- [ ] Define all technical terms
- [ ] Add error handling specs
- [ ] Specify data validation

**Before Development**
- [ ] Add integration test scenarios
- [ ] Define performance benchmarks
- [ ] Create monitoring plan

**Nice to Have**
- [ ] Add architecture diagrams
- [ ] Include sample data sets
- [ ] Create runbook templates
```

## Scoring Algorithm

```python
def calculate_score(spec):
    weights = {
        'clarity': 0.25,
        'completeness': 0.25,
        'consistency': 0.20,
        'testability': 0.15,
        'implementability': 0.15
    }
    
    scores = {
        'clarity': score_clarity(spec),
        'completeness': score_completeness(spec),
        'consistency': score_consistency(spec),
        'testability': score_testability(spec),
        'implementability': score_implementability(spec)
    }
    
    weighted_score = sum(
        scores[dim] * weights[dim] 
        for dim in weights
    )
    
    return round(weighted_score, 1)
```

## Quality Gates

| Gate | Minimum Score | When Applied |
|------|--------------|--------------|
| Ideation | 3.0 | Initial draft |
| Refinement | 5.0 | After first review |
| Development Ready | 7.0 | Before implementation |
| Production Ready | 8.5 | Before deployment |

## Auto-Enhancement

When run with `--fix` flag:

```bash
/spec-score --fix
```

Generates:
1. Enhanced specification with issues fixed
2. Glossary of all terms
3. Decision log for ambiguities
4. Example scenarios
5. Test scenarios

## Best Practices

1. **Score Early**: Get baseline score immediately after `/scope`
2. **Iterate**: Use `/spec-enhance` to improve specific dimensions
3. **Set Standards**: Require minimum 7.0 before development
4. **Track Progress**: Log scores over time
5. **Learn Patterns**: Study high-scoring specs
6. **Automate Gates**: Block low-quality specs in CI/CD