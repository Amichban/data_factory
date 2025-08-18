---
name: pre-commit
description: Pre-commit validation for code quality, security, and consistency
trigger: before_commit
---

# Pre-commit Validation Hook

This hook runs before each commit to ensure code quality, security, and consistency standards are maintained.

## Validation Checks

### 1. Code Quality
- **Linting**: Python (ruff, black), TypeScript (ESLint, Prettier)
- **Type checking**: mypy for Python, TypeScript compiler
- **Formatting**: Consistent code style enforcement
- **Import organization**: Sorted and clean imports

### 2. Security Scanning
- **Secrets detection**: prevent credential leaks with detect-secrets
- **Dependency vulnerabilities**: safety check for Python, npm audit for Node.js
- **Static analysis**: bandit for Python security issues

### 3. Testing
- **Unit tests**: Run relevant tests for changed files
- **Type safety**: Ensure no type errors
- **Build validation**: Verify project builds successfully

### 4. Documentation
- **README updates**: Check if changes require documentation updates
- **API documentation**: Ensure OpenAPI specs are current
- **Comment quality**: Verify public functions have docstrings

## Hook Implementation

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Running pre-commit validation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation results
VALIDATION_FAILED=false

# Function to log validation results
log_check() {
    local status=$1
    local message=$2
    
    if [[ "$status" == "pass" ]]; then
        echo -e "   ${GREEN}✅${NC} ${message}"
    elif [[ "$status" == "warn" ]]; then
        echo -e "   ${YELLOW}⚠️${NC} ${message}"
    else
        echo -e "   ${RED}❌${NC} ${message}"
        VALIDATION_FAILED=true
    fi
}

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only)
PYTHON_FILES=$(echo "$STAGED_FILES" | grep -E '\.py$' || true)
TS_FILES=$(echo "$STAGED_FILES" | grep -E '\.(ts|tsx)$' || true)
SQL_FILES=$(echo "$STAGED_FILES" | grep -E '\.sql$' || true)

echo "📋 **Code Quality Checks**"

# Python code quality
if [[ -n "$PYTHON_FILES" ]]; then
    echo "   🐍 Checking Python files..."
    
    # Black formatting
    if command -v black >/dev/null 2>&1; then
        if black --check --diff $PYTHON_FILES >/dev/null 2>&1; then
            log_check "pass" "Python formatting (black)"
        else
            log_check "fail" "Python formatting issues - run 'black $PYTHON_FILES'"
        fi
    else
        log_check "warn" "Black not installed - skipping formatting check"
    fi
    
    # Ruff linting
    if command -v ruff >/dev/null 2>&1; then
        if ruff check $PYTHON_FILES >/dev/null 2>&1; then
            log_check "pass" "Python linting (ruff)"
        else
            log_check "fail" "Ruff linting issues - run 'ruff check --fix $PYTHON_FILES'"
        fi
    else
        log_check "warn" "Ruff not installed - skipping linting"
    fi
    
    # Type checking
    if command -v mypy >/dev/null 2>&1; then
        if mypy $PYTHON_FILES >/dev/null 2>&1; then
            log_check "pass" "Python type checking (mypy)"
        else
            log_check "fail" "MyPy type checking issues"
        fi
    else
        log_check "warn" "MyPy not installed - skipping type checks"
    fi
fi

# TypeScript/JavaScript code quality  
if [[ -n "$TS_FILES" ]]; then
    echo "   📜 Checking TypeScript/JavaScript files..."
    
    # ESLint
    if command -v eslint >/dev/null 2>&1; then
        if eslint $TS_FILES >/dev/null 2>&1; then
            log_check "pass" "TypeScript linting (ESLint)"
        else
            log_check "fail" "ESLint issues - run 'eslint --fix $TS_FILES'"
        fi
    else
        log_check "warn" "ESLint not available - skipping linting"
    fi
    
    # Prettier formatting
    if command -v prettier >/dev/null 2>&1; then
        if prettier --check $TS_FILES >/dev/null 2>&1; then
            log_check "pass" "TypeScript formatting (Prettier)"
        else
            log_check "fail" "Prettier formatting issues - run 'prettier --write $TS_FILES'"
        fi
    else
        log_check "warn" "Prettier not available - skipping formatting check"
    fi
    
    # TypeScript compilation
    if command -v tsc >/dev/null 2>&1 && [[ -f "apps/web/tsconfig.json" ]]; then
        if cd apps/web && tsc --noEmit >/dev/null 2>&1; then
            log_check "pass" "TypeScript compilation"
            cd - >/dev/null
        else
            log_check "fail" "TypeScript compilation errors"
            cd - >/dev/null
        fi
    fi
fi

echo ""
echo "🔒 **Security Checks**"

# Secrets detection
if command -v detect-secrets >/dev/null 2>&1; then
    if detect-secrets scan --baseline .secrets.baseline $STAGED_FILES >/dev/null 2>&1; then
        log_check "pass" "No secrets detected"
    else
        log_check "fail" "Potential secrets found - review and update .secrets.baseline if needed"
    fi
else
    log_check "warn" "detect-secrets not installed - skipping secrets scan"
fi

# Python security scan
if [[ -n "$PYTHON_FILES" ]] && command -v bandit >/dev/null 2>&1; then
    if bandit -r $PYTHON_FILES -f json >/dev/null 2>&1; then
        log_check "pass" "Python security scan (bandit)"
    else
        log_check "fail" "Bandit security issues found"
    fi
fi

# Dependency vulnerabilities
if [[ -f "apps/api/requirements.txt" ]] && command -v safety >/dev/null 2>&1; then
    if safety check -r apps/api/requirements.txt >/dev/null 2>&1; then
        log_check "pass" "Python dependencies security (safety)"
    else
        log_check "warn" "Python dependency vulnerabilities found"
    fi
fi

if [[ -f "apps/web/package.json" ]] && command -v npm >/dev/null 2>&1; then
    cd apps/web
    if npm audit --audit-level high >/dev/null 2>&1; then
        log_check "pass" "Node.js dependencies security (npm audit)"
    else
        log_check "warn" "Node.js dependency vulnerabilities found"
    fi
    cd - >/dev/null
fi

echo ""
echo "🧪 **Testing & Build Checks**"

# Run relevant tests for changed files
if [[ -n "$PYTHON_FILES" ]] && command -v pytest >/dev/null 2>&1; then
    # Find test files related to changed files
    TEST_FILES=""
    for file in $PYTHON_FILES; do
        test_file=$(echo "$file" | sed 's|apps/api/src/|apps/api/tests/test_|' | sed 's|\.py$|_test.py|')
        if [[ -f "$test_file" ]]; then
            TEST_FILES="$TEST_FILES $test_file"
        fi
    done
    
    if [[ -n "$TEST_FILES" ]]; then
        if pytest $TEST_FILES -q >/dev/null 2>&1; then
            log_check "pass" "Related Python tests"
        else
            log_check "fail" "Python test failures"
        fi
    else
        log_check "warn" "No related Python tests found"
    fi
fi

# Check if build succeeds
if [[ -n "$TS_FILES" ]] && [[ -f "apps/web/package.json" ]]; then
    cd apps/web
    if npm run build >/dev/null 2>&1; then
        log_check "pass" "Frontend build"
    else
        log_check "fail" "Frontend build failed"
    fi
    cd - >/dev/null
fi

echo ""
echo "📚 **Documentation Checks**"

# Check for README updates if package files changed
if echo "$STAGED_FILES" | grep -E '(package\.json|requirements\.txt|setup\.py)' >/dev/null; then
    log_check "warn" "Dependencies changed - consider updating README.md"
fi

# Check for missing docstrings in new Python functions
if [[ -n "$PYTHON_FILES" ]]; then
    MISSING_DOCSTRINGS=0
    for file in $PYTHON_FILES; do
        # Simple check for public functions without docstrings
        if git show ":$file" | grep -E '^def [^_]' | head -1 >/dev/null; then
            if ! git show ":$file" | grep -A1 -E '^def [^_]' | grep -E '"""' >/dev/null; then
                MISSING_DOCSTRINGS=$((MISSING_DOCSTRINGS + 1))
            fi
        fi
    done
    
    if [[ $MISSING_DOCSTRINGS -gt 0 ]]; then
        log_check "warn" "$MISSING_DOCSTRINGS public functions may need docstrings"
    else
        log_check "pass" "Python docstring coverage"
    fi
fi

echo ""

# Final result
if [[ "$VALIDATION_FAILED" == true ]]; then
    echo -e "${RED}❌ Pre-commit validation failed${NC}"
    echo "   Fix the issues above before committing"
    echo "   Use --no-verify to skip these checks (not recommended)"
    exit 1
else
    echo -e "${GREEN}✅ Pre-commit validation passed${NC}"
    echo "   Ready to commit!"
fi
```

## Configuration Files

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
        
  - repo: local
    hooks:
      - id: custom-validation
        name: Custom validation checks
        entry: .claude/hooks/pre-commit-custom.sh
        language: script
        pass_filenames: false
```

## Quality Gates

Before allowing commit:
- [ ] All linting passes
- [ ] No formatting issues
- [ ] No type errors
- [ ] No security issues detected
- [ ] No secrets in code
- [ ] Related tests pass
- [ ] Build succeeds
- [ ] Documentation is adequate

## Bypass Options

In emergency situations:
```bash
# Skip all pre-commit hooks (use carefully)
git commit --no-verify -m "Emergency fix"

# Skip specific checks
SKIP=black,ruff git commit -m "Work in progress"
```

## Performance Considerations

- Only run checks on staged files
- Cache results where possible
- Provide quick feedback
- Fail fast on critical issues
- Parallel execution for independent checks