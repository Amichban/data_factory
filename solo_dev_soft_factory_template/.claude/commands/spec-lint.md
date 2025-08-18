---
name: spec-lint
description: Validate specification for ambiguities, inconsistencies, and missing elements
tools: [Read, Write]
---

# Specification Linter

Analyzes your specification to identify issues categorized by severity (Critical, High, Medium, Low).

## Usage

```bash
/spec-lint                    # Lint the current scope.json
/spec-lint #<issue-number>   # Lint spec from a specific issue
```

## What It Checks

### 🔴 Critical Issues
- **Undefined Terms**: Technical terms used but not defined
- **Formula Ambiguities**: Mathematical expressions that could be interpreted multiple ways
- **Missing Success Criteria**: No measurable definition of "done"
- **Conflicting Requirements**: Requirements that contradict each other

### 🟠 High Priority Issues
- **Incomplete Edge Cases**: Boundary conditions not specified
- **Missing Error Handling**: No specification for failure scenarios
- **Unclear Data Types**: Ambiguous data formats or structures
- **Performance Targets Missing**: No specific SLAs or benchmarks

### 🟡 Medium Priority Issues
- **Vague Descriptions**: Using words like "fast", "easy", "simple" without metrics
- **Missing Examples**: No concrete examples for complex logic
- **Unspecified Dependencies**: External systems or data not clearly defined
- **Incomplete API Contracts**: Missing request/response formats

### 🟢 Low Priority Issues
- **Documentation Gaps**: Missing operational guides
- **Test Coverage Unclear**: No test strategy specified
- **Monitoring Undefined**: No observability requirements

## Output Format

```json
{
  "score": 7.5,
  "total_issues": 24,
  "critical": [
    {
      "type": "undefined_term",
      "location": "slice.auth-login.description",
      "issue": "Term 'green candle' used but not defined",
      "suggestion": "Add: green_candle = close > open",
      "impact": "Developers may implement incorrectly"
    }
  ],
  "high": [...],
  "medium": [...],
  "low": [...],
  "recommendations": [
    "Add a glossary section with all technical terms",
    "Include example calculations for each formula",
    "Specify error handling for all external dependencies"
  ]
}
```

## Common Issues Found

### 1. Ambiguous Comparisons
```
❌ BAD: "Process when price is high"
✅ GOOD: "Process when price > moving_average_20 * 1.02"
```

### 2. Undefined Edge Cases
```
❌ BAD: "Calculate percentage change"
✅ GOOD: "Calculate (new-old)/old, return 0 if old==0"
```

### 3. Missing Time Zones
```
❌ BAD: "Process at midnight"
✅ GOOD: "Process at 00:00 UTC (20:00 ET/19:00 ET DST)"
```

### 4. Vague Performance
```
❌ BAD: "Should be fast"
✅ GOOD: "P95 latency < 200ms, P99 < 500ms"
```

### 5. Incomplete Formulas
```
❌ BAD: "Calculate ATR"
✅ GOOD: "ATR(14) using Wilder's smoothing: ATR = ((ATR_prev * 13) + TR) / 14"
```

## Validation Rules

### Data Validation
- All fields have explicit types
- Null handling specified
- Range constraints defined
- Units clearly stated (seconds, USD, percentage)

### Logic Validation
- All conditions have else clauses
- State transitions fully defined
- Concurrent access handling specified
- Transaction boundaries clear

### Integration Validation
- External API contracts complete
- Retry logic specified
- Timeout values defined
- Circuit breaker thresholds set

### Security Validation
- Authentication requirements clear
- Authorization rules specified
- Data encryption requirements stated
- Audit logging defined

## Auto-Fix Suggestions

The linter provides automatic fix suggestions:

```yaml
issue: "Undefined term: 'spike'"
suggestion: |
  Add to glossary:
  spike: A price movement where:
    - price_change > ATR * threshold
    - volume > volume_ma_20 * 1.5
    - Occurs within single candle period
```

## Integration with Scope Process

Run after `/scope` but before `/accept-scope`:

```bash
/scope #1           # Generate initial scope
/spec-lint          # Identify issues
/spec-enhance       # Fix critical issues
/spec-lint          # Verify improvements
/accept-scope       # Proceed with clean spec
```

## Scoring Rubric

| Score | Quality | Description |
|-------|---------|-------------|
| 9-10  | Excellent | No critical/high issues, < 5 medium |
| 7-8   | Good | No critical, < 3 high, < 10 medium |
| 5-6   | Acceptable | < 2 critical, < 5 high |
| 3-4   | Poor | Multiple critical issues |
| 1-2   | Unworkable | Specification cannot be implemented |

## Best Practices

1. **Run Early and Often**: Lint after each major spec change
2. **Fix Critical First**: Address red issues before proceeding
3. **Document Decisions**: When lint finds ambiguity, document the decision
4. **Include Examples**: Add examples for any complex logic
5. **Define All Terms**: Create comprehensive glossary
6. **Specify All Edge Cases**: Think about boundaries, nulls, errors
7. **Make It Testable**: Every requirement should be verifiable