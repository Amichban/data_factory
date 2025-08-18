---
name: gen-tests
description: Generate comprehensive test scenarios from specifications
tools: [Read, Write, Edit]
---

# Test Scenario Generator

Automatically generates test cases, test data, and testing strategies from your specifications.

## Usage

```bash
/gen-tests                          # Generate all test types
/gen-tests --unit                   # Generate unit tests only
/gen-tests --integration            # Generate integration tests
/gen-tests --e2e                    # Generate end-to-end tests
/gen-tests --performance            # Generate performance test scenarios
/gen-tests --security               # Generate security test cases
/gen-tests --data                   # Generate test data fixtures
/gen-tests --coverage-report        # Analyze test coverage gaps
```

## Test Types Generated

### 1. **Unit Tests**
```typescript
// Generated from: auth-login slice
describe('AuthService', () => {
  describe('validateEmail', () => {
    it('should accept valid RFC 5322 email', () => {
      const validEmails = [
        'user@example.com',
        'user+tag@example.com',
        'user.name@example.co.uk',
        '123@example.com'
      ];
      validEmails.forEach(email => {
        expect(validateEmail(email)).toBe(true);
      });
    });
    
    it('should reject invalid email formats', () => {
      const invalidEmails = [
        'notanemail',
        '@example.com',
        'user@',
        'user @example.com',
        'user@example',
        null,
        undefined,
        ''
      ];
      invalidEmails.forEach(email => {
        expect(validateEmail(email)).toBe(false);
      });
    });
  });
  
  describe('hashPassword', () => {
    it('should hash password with bcrypt cost 12', async () => {
      const password = 'SecurePass123!';
      const hash = await hashPassword(password);
      expect(hash).toMatch(/^\$2[aby]\$12\$/);
      expect(hash.length).toBe(60);
    });
    
    it('should generate different hashes for same password', async () => {
      const password = 'SecurePass123!';
      const hash1 = await hashPassword(password);
      const hash2 = await hashPassword(password);
      expect(hash1).not.toBe(hash2);
    });
  });
});
```

### 2. **Integration Tests**
```python
# Generated from: user-profile slice
class TestUserProfileAPI:
    def test_create_and_retrieve_profile(self, client, db_session):
        """Test complete profile creation and retrieval flow"""
        # Create user
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        }
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["user_id"]
        
        # Login to get token
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["token"]
        
        # Get profile with auth
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/api/users/{user_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]
        assert response.json()["name"] == user_data["name"]
    
    def test_profile_update_with_validation(self, client, auth_headers):
        """Test profile update with validation rules"""
        update_data = {
            "name": "Updated Name",
            "phone": "+1234567890",
            "timezone": "America/New_York"
        }
        response = client.patch("/api/users/me", 
                              json=update_data, 
                              headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]
```

### 3. **End-to-End Tests**
```javascript
// Generated from: complete user journey
describe('User Journey: Registration to First Action', () => {
  it('should complete full user onboarding flow', async () => {
    // Navigate to homepage
    await page.goto('http://localhost:3000');
    
    // Click sign up
    await page.click('[data-testid="signup-button"]');
    
    // Fill registration form
    await page.fill('[name="email"]', 'newuser@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.fill('[name="confirmPassword"]', 'SecurePass123!');
    await page.fill('[name="name"]', 'New User');
    
    // Submit form
    await page.click('[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard');
    
    // Verify welcome message
    const welcome = await page.textContent('[data-testid="welcome-message"]');
    expect(welcome).toContain('Welcome, New User');
    
    // Create first task
    await page.click('[data-testid="create-task-button"]');
    await page.fill('[name="title"]', 'My First Task');
    await page.fill('[name="description"]', 'Testing the task creation');
    await page.click('[data-testid="save-task"]');
    
    // Verify task appears in list
    const taskTitle = await page.textContent('[data-testid="task-0-title"]');
    expect(taskTitle).toBe('My First Task');
  });
});
```

### 4. **Performance Tests**
```yaml
# Generated k6 performance test
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Spike to 200
    { duration: '5m', target: 200 },  // Stay at 200
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],  // 95% of requests under 200ms
    errors: ['rate<0.01'],              // Error rate under 1%
  },
};

export default function () {
  // Test login endpoint performance
  const loginRes = http.post('http://api.example.com/auth/login', 
    JSON.stringify({
      email: 'perf.test@example.com',
      password: 'TestPass123!'
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  check(loginRes, {
    'login successful': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 200,
  });
  
  errorRate.add(loginRes.status !== 200);
  
  if (loginRes.status === 200) {
    const token = loginRes.json('token');
    
    // Test authenticated endpoint
    const profileRes = http.get('http://api.example.com/users/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    check(profileRes, {
      'profile retrieved': (r) => r.status === 200,
      'profile response fast': (r) => r.timings.duration < 100,
    });
  }
  
  sleep(1);
}
```

### 5. **Security Tests**
```python
# Generated security test cases
class TestSecurityVulnerabilities:
    def test_sql_injection_in_login(self, client):
        """Test SQL injection protection in login endpoint"""
        injection_attempts = [
            "' OR '1'='1",
            "admin'--",
            "' OR '1'='1' /*",
            "'; DROP TABLE users--",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in injection_attempts:
            response = client.post("/api/auth/login", json={
                "email": payload,
                "password": "any"
            })
            assert response.status_code in [400, 401]
            assert "AUTH_001" in response.json().get("error", "")
    
    def test_xss_protection(self, client, auth_headers):
        """Test XSS protection in user inputs"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/tasks", 
                                 json={"title": payload},
                                 headers=auth_headers)
            if response.status_code == 201:
                # Verify stored value is escaped
                task_id = response.json()["id"]
                get_response = client.get(f"/api/tasks/{task_id}",
                                        headers=auth_headers)
                assert "<script>" not in get_response.json()["title"]
                assert "javascript:" not in get_response.json()["title"]
    
    def test_rate_limiting(self, client):
        """Test rate limiting on sensitive endpoints"""
        for i in range(10):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": f"attempt{i}"
            })
            if i < 5:
                assert response.status_code == 401
            else:
                assert response.status_code == 429
                assert "AUTH_003" in response.json()["error"]
```

## Test Data Generation

### Fixtures and Factories

```python
# Generated test data factories
from factory import Factory, Faker, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime, timedelta
import random

class UserFactory(SQLAlchemyModelFactory):
    """Generate test users with realistic data"""
    class Meta:
        model = User
        sqlalchemy_session = db.session
    
    id = Faker('uuid4')
    email = Faker('email')
    name = Faker('name')
    password_hash = '$2b$12$KIXxPfxQxGxMr4hR2kHGOuLMjW5M5XH5M.vZM5XH5M'  # "password123"
    created_at = Faker('date_time_between', start_date='-1y', end_date='now')
    last_login = Faker('date_time_between', start_date='-30d', end_date='now')
    is_active = True
    email_verified = Faker('boolean', chance_of_getting_true=75)

class TaskFactory(SQLAlchemyModelFactory):
    """Generate test tasks with various states"""
    class Meta:
        model = Task
    
    id = Faker('uuid4')
    title = Faker('sentence', nb_words=4)
    description = Faker('text', max_nb_chars=200)
    status = Faker('random_element', elements=['todo', 'in_progress', 'done'])
    priority = Faker('random_element', elements=['low', 'medium', 'high'])
    due_date = Faker('date_between', start_date='today', end_date='+30d')
    created_by = SubFactory(UserFactory)
    assigned_to = SubFactory(UserFactory)

# Edge case data
edge_cases = {
    'emails': [
        'a@b.c',                           # Minimum valid
        'test+tag@example.com',            # Plus addressing
        'user.name@example.co.uk',         # Subdomain
        'very.long.email.address@very.long.domain.name.example.com',  # Long
    ],
    'passwords': [
        'A1!aaaaa',                        # Minimum requirements
        'A' * 128,                         # Maximum length
        'Пароль123!',                      # Unicode
        '🔒Secure123!',                    # Emoji
    ],
    'numbers': [
        0, -1, 1,                          # Boundaries
        2147483647,                        # Max int32
        -2147483648,                       # Min int32
        3.14159265359,                     # Float precision
        float('inf'),                      # Infinity
        float('nan'),                      # NaN
    ],
    'dates': [
        datetime.min,                      # Earliest
        datetime.max,                      # Latest
        datetime(2000, 2, 29),            # Leap year
        datetime.now() + timedelta(days=365*100),  # Far future
    ]
}
```

### Boundary Value Testing

```yaml
boundary_tests:
  string_length:
    - value: ""
      expected: "Validation error: Required field"
    - value: "a"
      expected: "Validation error: Minimum length 2"
    - value: "a" * 255
      expected: "Success"
    - value: "a" * 256
      expected: "Validation error: Maximum length 255"
  
  numeric_ranges:
    age:
      - value: 12
        expected: "Validation error: Minimum age 13"
      - value: 13
        expected: "Success"
      - value: 120
        expected: "Success"
      - value: 121
        expected: "Validation error: Maximum age 120"
    
    percentage:
      - value: -0.01
        expected: "Validation error: Must be between 0-100"
      - value: 0
        expected: "Success"
      - value: 100
        expected: "Success"
      - value: 100.01
        expected: "Validation error: Must be between 0-100"
```

## Coverage Analysis

### Coverage Report
```yaml
test_coverage:
  unit_tests:
    total_functions: 45
    tested_functions: 42
    coverage: 93.3%
    missing:
      - "formatCurrency() - edge case: negative values"
      - "calculateTax() - edge case: zero income"
      - "parseDate() - edge case: invalid format"
  
  integration_tests:
    total_endpoints: 28
    tested_endpoints: 26
    coverage: 92.8%
    missing:
      - "DELETE /api/users/{id} - admin only"
      - "POST /api/reports/export - large datasets"
  
  e2e_tests:
    total_user_flows: 12
    tested_flows: 10
    coverage: 83.3%
    missing:
      - "Password reset flow"
      - "Account deletion flow"
  
  edge_cases:
    identified: 47
    tested: 39
    coverage: 82.9%
    high_priority_missing:
      - "Concurrent user updates"
      - "Database connection loss"
      - "Rate limit edge cases"
```

## Test Strategy Document

```markdown
# Test Strategy for [Project Name]

## Test Pyramid
- **Unit Tests**: 70% - Fast, isolated, comprehensive
- **Integration Tests**: 20% - API contracts, database operations
- **E2E Tests**: 10% - Critical user journeys only

## Test Environments
1. **Local**: Docker-compose with test database
2. **CI**: GitHub Actions with PostgreSQL service
3. **Staging**: Production-like with anonymized data
4. **Production**: Smoke tests only

## Test Data Management
- Factories for consistent test data
- Seeders for demo environments
- Anonymized production snapshots for staging
- Cleanup after each test run

## Performance Targets
- Unit tests: < 5 seconds total
- Integration tests: < 30 seconds total
- E2E tests: < 2 minutes total
- Full test suite: < 5 minutes

## Security Testing
- OWASP Top 10 coverage
- Dependency vulnerability scanning
- Static code analysis
- Penetration testing quarterly
```

## CI/CD Integration

```yaml
# Generated GitHub Actions workflow
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          npm test -- --coverage
          pytest tests/unit --cov
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: |
          npm run test:integration
          pytest tests/integration
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose up -d
      - name: Run E2E tests
        run: npx playwright test
      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: test-results/
```

## Best Practices

1. **Test Naming**: Use descriptive names that explain what and why
2. **Arrange-Act-Assert**: Structure tests consistently
3. **Test Independence**: Each test should run in isolation
4. **Data Cleanup**: Always clean up test data
5. **Meaningful Assertions**: Test behavior, not implementation
6. **Edge Cases First**: Prioritize boundary and error conditions
7. **Performance Benchmarks**: Set and monitor performance targets
8. **Security by Default**: Include security tests from the start