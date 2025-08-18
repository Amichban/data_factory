---
name: pr-review
description: Pull request review validation for code quality, completeness, and best practices
trigger: before_pr_merge
---

# Pull Request Review Hook

This hook runs comprehensive validation before merging pull requests to ensure code quality, security, and completeness standards.

## Review Checklist

### 1. Code Quality & Standards
- **Style consistency**: All code follows established formatting standards
- **Type safety**: No type errors in TypeScript/Python code
- **Error handling**: Proper exception handling and error responses
- **Performance**: No obvious performance regressions
- **Code complexity**: Functions and classes are reasonably sized and focused

### 2. Testing & Coverage
- **Test coverage**: New code has appropriate test coverage
- **Test quality**: Tests are meaningful and test actual functionality
- **Integration tests**: API endpoints have integration tests
- **Edge cases**: Error conditions and edge cases are tested

### 3. Security & Compliance
- **Authentication**: Proper auth checks on protected endpoints
- **Authorization**: Role-based access controls implemented correctly
- **Input validation**: All inputs are validated and sanitized
- **SQL injection**: No dynamic SQL query construction
- **Secrets management**: No hardcoded secrets or credentials

### 4. Documentation & Communication
- **PR description**: Clear explanation of changes and rationale
- **Breaking changes**: Breaking changes are documented
- **API documentation**: OpenAPI specs updated for API changes
- **Comments**: Complex logic is well-commented

### 5. Database & Migrations
- **Migration safety**: Database migrations are reversible and safe
- **Data integrity**: Foreign key constraints and validations in place
- **Performance impact**: Migration performance on large datasets considered
- **Index optimization**: New queries have appropriate indexes

## Hook Implementation

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "🔍 **Pull Request Review Validation**"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Track validation results
VALIDATION_FAILED=false
WARNINGS=0

# Function to log validation results
log_check() {
    local status=$1
    local message=$2
    local details=${3:-""}
    
    if [[ "$status" == "pass" ]]; then
        echo -e "   ${GREEN}✅${NC} ${message}"
    elif [[ "$status" == "warn" ]]; then
        echo -e "   ${YELLOW}⚠️${NC} ${message}"
        if [[ -n "$details" ]]; then
            echo -e "      ${details}"
        fi
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "   ${RED}❌${NC} ${message}"
        if [[ -n "$details" ]]; then
            echo -e "      ${details}"
        fi
        VALIDATION_FAILED=true
    fi
}

# Get PR information (assume we're on a PR branch)
CURRENT_BRANCH=$(git branch --show-current)
TARGET_BRANCH="main"  # or get from PR info

# Get changed files
CHANGED_FILES=$(git diff --name-only $TARGET_BRANCH..HEAD)
PYTHON_FILES=$(echo "$CHANGED_FILES" | grep -E '\.py$' || true)
TS_FILES=$(echo "$CHANGED_FILES" | grep -E '\.(ts|tsx)$' || true)
SQL_FILES=$(echo "$CHANGED_FILES" | grep -E '\.sql$' || true)
TEST_FILES=$(echo "$CHANGED_FILES" | grep -E '_test\.py$|\.test\.(ts|tsx)$|\.spec\.(ts|tsx)$' || true)

echo "📊 **Change Summary**"
echo "   Branch: $CURRENT_BRANCH → $TARGET_BRANCH"
echo "   Files changed: $(echo "$CHANGED_FILES" | wc -l)"
echo "   Python files: $(echo "$PYTHON_FILES" | wc -l)"
echo "   TypeScript files: $(echo "$TS_FILES" | wc -l)"
echo "   Test files: $(echo "$TEST_FILES" | wc -l)"
echo ""

echo "🔧 **Code Quality Validation**"

# Check if all tests pass
if command -v pytest >/dev/null 2>&1; then
    echo "   🧪 Running Python tests..."
    if pytest apps/api/tests/ -v --tb=short >/dev/null 2>&1; then
        log_check "pass" "All Python tests passing"
    else
        log_check "fail" "Python test failures detected"
    fi
fi

if [[ -f "apps/web/package.json" ]]; then
    echo "   🧪 Running frontend tests..."
    cd apps/web
    if npm test -- --watchAll=false >/dev/null 2>&1; then
        log_check "pass" "All frontend tests passing"
    else
        log_check "fail" "Frontend test failures detected"
    fi
    cd - >/dev/null
fi

# Check test coverage for new code
if [[ -n "$PYTHON_FILES" ]] && command -v pytest >/dev/null 2>&1; then
    echo "   📊 Analyzing test coverage..."
    if pytest apps/api/tests/ --cov=apps/api/src --cov-report=term-missing --cov-fail-under=80 >/dev/null 2>&1; then
        log_check "pass" "Test coverage above 80%"
    else
        log_check "warn" "Test coverage below 80%" "Consider adding more tests for new code"
    fi
fi

echo ""
echo "🔒 **Security Validation**"

# Check for security issues
if [[ -n "$PYTHON_FILES" ]] && command -v bandit >/dev/null 2>&1; then
    if bandit -r $PYTHON_FILES -f json >/dev/null 2>&1; then
        log_check "pass" "No Python security issues (bandit)"
    else
        log_check "fail" "Security issues found by bandit"
    fi
fi

# Check for secrets
if command -v detect-secrets >/dev/null 2>&1; then
    if detect-secrets scan --baseline .secrets.baseline $CHANGED_FILES >/dev/null 2>&1; then
        log_check "pass" "No secrets detected"
    else
        log_check "fail" "Potential secrets found in changed files"
    fi
fi

# Check dependency vulnerabilities
if [[ -f "apps/api/requirements.txt" ]] && echo "$CHANGED_FILES" | grep -q requirements.txt; then
    echo "   🔍 Checking Python dependencies..."
    if safety check -r apps/api/requirements.txt >/dev/null 2>&1; then
        log_check "pass" "Python dependencies secure"
    else
        log_check "warn" "Python dependency vulnerabilities found"
    fi
fi

echo ""
echo "🗃️ **Database Validation**"

# Check for migration files
MIGRATION_FILES=$(echo "$CHANGED_FILES" | grep -E 'alembic/versions/.*\.py$' || true)
if [[ -n "$MIGRATION_FILES" ]]; then
    echo "   🔄 Found database migrations..."
    
    # Check if migrations are reversible
    for migration in $MIGRATION_FILES; do
        if grep -q "def downgrade" "$migration"; then
            log_check "pass" "Migration has downgrade function: $(basename $migration)"
        else
            log_check "fail" "Migration missing downgrade function: $(basename $migration)"
        fi
    done
    
    # Test migration (dry run)
    if command -v alembic >/dev/null 2>&1; then
        cd apps/api
        if alembic check >/dev/null 2>&1; then
            log_check "pass" "Migration syntax valid"
        else
            log_check "fail" "Migration syntax errors"
        fi
        cd - >/dev/null
    fi
fi

# Check for direct SQL in Python files
if [[ -n "$PYTHON_FILES" ]]; then
    SQL_INJECTION_RISK=false
    for file in $PYTHON_FILES; do
        if grep -E '(execute|query).*%.*s' "$file" >/dev/null 2>&1; then
            log_check "warn" "Potential SQL injection risk in $file" "Use parameterized queries"
            SQL_INJECTION_RISK=true
        fi
    done
    
    if [[ "$SQL_INJECTION_RISK" == false ]]; then
        log_check "pass" "No SQL injection risks detected"
    fi
fi

echo ""
echo "📚 **Documentation Validation**"

# Check if API endpoints have proper documentation
API_FILES=$(echo "$PYTHON_FILES" | grep -E '(router|endpoint|api)' || true)
if [[ -n "$API_FILES" ]]; then
    UNDOCUMENTED_ENDPOINTS=0
    for file in $API_FILES; do
        # Look for @router or @app decorators without docstrings
        if grep -E '@(router|app)\.(get|post|put|delete)' "$file" >/dev/null; then
            if ! grep -A5 -E '@(router|app)\.(get|post|put|delete)' "$file" | grep -E '"""' >/dev/null; then
                UNDOCUMENTED_ENDPOINTS=$((UNDOCUMENTED_ENDPOINTS + 1))
            fi
        fi
    done
    
    if [[ $UNDOCUMENTED_ENDPOINTS -gt 0 ]]; then
        log_check "warn" "$UNDOCUMENTED_ENDPOINTS API endpoints may need documentation"
    else
        log_check "pass" "API endpoints are documented"
    fi
fi

# Check if significant changes have updated README
SIGNIFICANT_CHANGES=$(echo "$CHANGED_FILES" | grep -E '(requirements\.txt|package\.json|docker|setup)' || true)
README_UPDATED=$(echo "$CHANGED_FILES" | grep -i readme || true)

if [[ -n "$SIGNIFICANT_CHANGES" ]] && [[ -z "$README_UPDATED" ]]; then
    log_check "warn" "Significant changes made but README not updated" "Consider updating documentation"
fi

echo ""
echo "🏗️ **Build & Integration Validation**"

# Check if the application builds successfully
if [[ -f "apps/web/package.json" ]]; then
    cd apps/web
    if npm run build >/dev/null 2>&1; then
        log_check "pass" "Frontend builds successfully"
    else
        log_check "fail" "Frontend build fails"
    fi
    cd - >/dev/null
fi

# Check if health endpoints still work
if command -v curl >/dev/null 2>&1; then
    # Start services in background for testing
    docker-compose up -d >/dev/null 2>&1
    sleep 10  # Wait for services to start
    
    if curl -f http://localhost:8000/healthz >/dev/null 2>&1; then
        log_check "pass" "API health check passes"
    else
        log_check "warn" "API health check fails" "Services may not be running"
    fi
    
    # Cleanup
    docker-compose down >/dev/null 2>&1
fi

echo ""
echo "📋 **PR Completeness Check**"

# Check if PR has proper title and description
# (This would typically be done by GitHub Actions with PR context)
log_check "warn" "Verify PR has descriptive title and detailed description"
log_check "warn" "Verify breaking changes are documented"
log_check "warn" "Verify acceptance criteria are met"

# Check if issue is linked
# (Would check PR body for "Closes #123" or similar)
log_check "warn" "Verify PR is linked to relevant issue"

echo ""

# Summary
TOTAL_CHECKS=15  # Approximate number of automated checks
PASSED_CHECKS=$((TOTAL_CHECKS - WARNINGS))

if [[ "$WARNINGS" -gt 5 ]]; then
    log_check "warn" "High number of warnings ($WARNINGS)" "Review and address warnings before merging"
fi

echo "📊 **Validation Summary**"
echo "   Total automated checks: ~$TOTAL_CHECKS"
echo "   Warnings: $WARNINGS"

if [[ "$VALIDATION_FAILED" == true ]]; then
    echo -e "   ${RED}❌ Critical issues found${NC}"
    echo ""
    echo "🚫 **Merge blocked due to critical issues**"
    echo "   Address the failing checks above before merging"
    exit 1
elif [[ "$WARNINGS" -gt 3 ]]; then
    echo -e "   ${YELLOW}⚠️ Multiple warnings present${NC}"
    echo ""
    echo "🟡 **Consider addressing warnings before merge**"
    echo "   While not blocking, addressing warnings improves code quality"
else
    echo -e "   ${GREEN}✅ Ready for review${NC}"
    echo ""
    echo "✅ **Automated validation passed**"
    echo "   PR is ready for human review and merge"
fi

echo ""
echo "👥 **Manual Review Checklist**"
echo "   □ Code logic is correct and efficient"
echo "   □ Changes align with acceptance criteria"  
echo "   □ UI/UX changes are user-friendly"
echo "   □ Performance impact is acceptable"
echo "   □ Error handling is comprehensive"
echo "   □ Code is maintainable and readable"
```

## Integration with GitHub

### GitHub Actions Workflow
```yaml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for comparison
      
      - name: Run PR Review Hook
        run: .claude/hooks/pr-review.sh
        
      - name: Comment PR with results
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🔍 **Automated PR Review Failed**\n\nPlease check the workflow logs and address the issues before merging.'
            })
```

### Branch Protection Rules
Configure these in GitHub repository settings:
- Require status checks to pass before merging
- Require pull request reviews before merging  
- Dismiss stale PR approvals when new commits are pushed
- Require review from code owners
- Restrict pushes to matching branches

## Quality Gates

Critical (blocking):
- [ ] All tests pass
- [ ] No security vulnerabilities
- [ ] No secrets in code
- [ ] Build succeeds
- [ ] Database migrations are safe

Warnings (recommend addressing):
- [ ] Test coverage below threshold
- [ ] Documentation gaps
- [ ] Code complexity issues
- [ ] Performance concerns
- [ ] Dependency vulnerabilities

## Manual Review Guidelines

Reviewers should verify:
1. **Correctness**: Does the code solve the intended problem?
2. **Design**: Is the solution well-architected?
3. **Maintainability**: Is the code readable and easy to modify?
4. **Performance**: Are there any performance implications?
5. **Security**: Are there any security considerations?
6. **Testing**: Is the testing strategy adequate?