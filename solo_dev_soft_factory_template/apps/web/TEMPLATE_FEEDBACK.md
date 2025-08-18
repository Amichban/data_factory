# Solo Software Factory Template - Feedback & Recommendations

## Executive Summary

After implementing the QuantX Platform using the Solo Software Factory template, this document provides comprehensive feedback and recommendations for improving the template based on real-world usage, challenges encountered, and solutions developed.

## 1. Core Template Improvements

### 1.1 Database Configuration

**Issues Encountered:**
- Port conflicts with default PostgreSQL (5432)
- Missing async database setup patterns
- No connection pooling configuration

**Recommendations:**
```env
# .env.example should include:
DATABASE_URL=postgresql+asyncpg://dev:devpass@localhost:${DB_PORT:-5444}/app_dev
DATABASE_POOL_SIZE=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_OVERFLOW=10
```

**Add to template:**
```python
# apps/api/app/database_async.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.async_session = None
    
    async def initialize(self):
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_POOL_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            poolclass=NullPool if settings.TESTING else None
        )
```

### 1.2 API Client Architecture

**Issues Encountered:**
- Confusion between `/api` and `/api/v1` paths
- Manual URL construction errors
- Missing retry logic and error handling

**Recommendations:**
```typescript
// apps/web/lib/api/client-factory.ts
export class ApiClientFactory {
  private static instance: ApiClient;
  
  static create(config?: ApiClientConfig): ApiClient {
    if (!this.instance) {
      this.instance = new ApiClient({
        baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8006/api/v1',
        timeout: 10000,
        retries: 3,
        retryDelay: 1000,
        onError: (error) => console.error('API Error:', error),
      });
    }
    return this.instance;
  }
}
```

### 1.3 Environment Management

**Add port conflict detection:**
```javascript
// scripts/check-ports.js
const net = require('net');

const checkPort = (port) => new Promise((resolve) => {
  const server = net.createServer();
  server.listen(port, () => {
    server.close(() => resolve(true));
  });
  server.on('error', () => resolve(false));
});

async function findAvailablePort(startPort, endPort) {
  for (let port = startPort; port <= endPort; port++) {
    if (await checkPort(port)) return port;
  }
  throw new Error('No available ports');
}

// Use in startup scripts
const apiPort = await findAvailablePort(8000, 8010);
const webPort = await findAvailablePort(3000, 3020);
```

## 2. Debug-First UI Strategy

### 2.1 Debug Dashboard Template

**Add to template from day 1:**
```typescript
// apps/web/app/debug/layout.tsx
export default function DebugLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="px-4 py-2">
          <h1 className="text-lg font-semibold">Debug Dashboard</h1>
        </div>
      </nav>
      <main className="p-4">{children}</main>
    </div>
  );
}

// apps/web/app/debug/page.tsx
export default function DebugDashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <HealthCheck />
      <DatabaseStats />
      <ApiTester />
      <EventStream />
      <JobQueue />
      <ConfigViewer />
    </div>
  );
}
```

### 2.2 Debug Components Library

```typescript
// apps/web/lib/debug-components/index.ts
export { JsonViewer } from './JsonViewer';
export { ApiTester } from './ApiTester';
export { DataTable } from './DataTable';
export { LiveLog } from './LiveLog';
export { MetricsCard } from './MetricsCard';
export { HealthIndicator } from './HealthIndicator';
export { ConfigEditor } from './ConfigEditor';
```

## 3. User Story Integration

### 3.1 Project Structure Enhancement

```
project/
├── user-stories/
│   ├── templates/
│   │   ├── user-story.md
│   │   └── acceptance-criteria.md
│   ├── active/
│   │   ├── US-001-view-data.md
│   │   └── US-002-filter-results.md
│   └── completed/
├── slices/
│   ├── VS-001-data-layer/
│   │   ├── README.md
│   │   ├── user-stories.yaml    # Links to user stories
│   │   ├── acceptance-tests/
│   │   ├── debug-ui/
│   │   └── implementation/
```

### 3.2 User Story Template

```markdown
# US-[NUMBER]: [Title]

## Story Statement
As a **[role]**
I want to **[capability]**
So that **[benefit]**

## Acceptance Criteria
- [ ] Given [context], When [action], Then [outcome]
- [ ] Performance: [metric] must be under [threshold]
- [ ] Error handling: [scenario] shows [message]

## Debug UI Requirements
- Component: [ComponentName]
- Route: /debug/[feature]
- Data displayed: [list of fields]

## Production UI Requirements
- Component: [ComponentName]
- Route: /[feature]
- Interactions: [list of user actions]

## Technical Notes
- API endpoints needed: [list]
- Database changes: [migrations needed]
- External dependencies: [services/APIs]

## Test Scenarios
1. Happy path: [description]
2. Edge case: [description]
3. Error case: [description]

## Definition of Done
- [ ] Acceptance tests passing
- [ ] Debug UI functional
- [ ] API documented
- [ ] Error handling complete
- [ ] Performance requirements met
- [ ] Code reviewed
- [ ] Deployed to staging
```

### 3.3 Story-to-Slice Mapping

```yaml
# slices/VS-001-data-layer/user-stories.yaml
slice: data-layer
priority: P0
user_stories:
  primary:
    - id: US-001
      title: View real-time data
      points: 5
      acceptance_tests:
        - test_data_appears_within_5_seconds
        - test_data_format_is_correct
  
  secondary:
    - id: US-003
      title: Export data
      points: 3
      acceptance_tests:
        - test_export_csv
        - test_export_json
  
  optional:
    - id: US-007
      title: Configure refresh rate
      points: 2

implementation_phases:
  phase_1_debug:
    - Create debug UI at /debug/data
    - Display raw data in table
    - Add manual refresh button
    
  phase_2_core:
    - Implement data service
    - Add caching layer
    - Create API endpoints
    
  phase_3_production:
    - Build production UI components
    - Add real-time updates
    - Implement export functionality
```

## 4. Testing Strategy

### 4.1 Three-Layer Testing Approach

```python
# tests/layer1_debug/test_debug_ui.py
"""Layer 1: Debug UI Tests - Fast feedback during development"""
def test_debug_dashboard_loads():
    response = client.get("/debug")
    assert response.status_code == 200
    assert "Debug Dashboard" in response.text

# tests/layer2_acceptance/test_us_001.py
"""Layer 2: Acceptance Tests - Validate user stories"""
@pytest.mark.acceptance
async def test_us_001_user_views_data():
    """US-001: User can view real-time data"""
    # Given: System has data
    await seed_test_data()
    
    # When: User navigates to data view
    response = await client.get("/api/v1/data")
    
    # Then: Data is returned within 5 seconds
    assert response.status_code == 200
    assert len(response.json()["items"]) > 0
    assert response.elapsed.total_seconds() < 5

# tests/layer3_e2e/test_production_ui.py
"""Layer 3: E2E Tests - Full production validation"""
@pytest.mark.e2e
async def test_production_data_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        # Full user journey test
```

### 4.2 Test Data Management

```python
# tests/fixtures/data_factory.py
class TestDataFactory:
    """Centralized test data generation"""
    
    @staticmethod
    def create_user_story_data(story_id: str):
        """Generate data specific to user story requirements"""
        if story_id == "US-001":
            return {
                "events": [create_event() for _ in range(10)],
                "timeframe": "5_seconds",
                "expected_count": 10
            }
```

## 5. Development Workflow

### 5.1 Sprint Planning Template

```yaml
# sprints/sprint-001.yaml
sprint_number: 1
duration: 1 week
goal: "Establish data flow with debug UI"

user_stories:
  - US-001: 5 points
  - US-002: 3 points
  - US-003: 5 points

daily_plan:
  monday:
    - Setup debug dashboard
    - Create user story acceptance tests
    - Implement basic data model
    
  tuesday:
    - Connect to data source
    - Display in debug UI
    - Add refresh functionality
    
  wednesday:
    - Implement filtering
    - Add export button
    - Write API tests
    
  thursday:
    - Performance optimization
    - Error handling
    - Update documentation
    
  friday:
    - Bug fixes
    - Demo preparation
    - Stakeholder demo

success_criteria:
  - All acceptance tests passing
  - Debug UI fully functional
  - Data flow demonstrated end-to-end
```

### 5.2 Progressive Enhancement Path

```mermaid
graph LR
    A[Debug UI] --> B[Core Logic]
    B --> C[API Layer]
    C --> D[Basic UI]
    D --> E[Enhanced UI]
    E --> F[Production UI]
    
    A --> G[Immediate Feedback]
    B --> H[Business Value]
    C --> I[Integration]
    D --> J[User Testing]
    E --> K[Polish]
    F --> L[Release]
```

## 6. Real-time Features

### 6.1 WebSocket/SSE Setup

```python
# apps/api/app/realtime/__init__.py
from fastapi import WebSocket
from typing import Dict, Set
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        
    async def broadcast(self, message: dict, channel: str):
        if channel in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            # Clean up dead connections
            self.active_connections[channel] -= dead_connections
```

### 6.2 React Hooks for Real-time

```typescript
// apps/web/lib/hooks/useRealtime.ts
export function useRealtime<T>(channel: string) {
  const [data, setData] = useState<T[]>([]);
  const [status, setStatus] = useState<'connected' | 'disconnected'>('disconnected');
  
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/ws/${channel}`);
    
    ws.onopen = () => setStatus('connected');
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setData(prev => [message, ...prev].slice(0, 100));
    };
    ws.onclose = () => setStatus('disconnected');
    
    return () => ws.close();
  }, [channel]);
  
  return { data, status };
}
```

## 7. Batch Processing Framework

### 7.1 Job Management System

```python
# apps/api/app/jobs/manager.py
from enum import Enum
from typing import Optional, Dict, Any
import asyncio

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        
    async def create_job(
        self,
        job_type: str,
        parameters: Dict[str, Any],
        priority: int = 5
    ) -> str:
        job = Job(
            type=job_type,
            parameters=parameters,
            priority=priority,
            status=JobStatus.PENDING
        )
        self.jobs[job.id] = job
        await self.queue.put(job)
        return job.id
        
    async def process_jobs(self):
        while True:
            job = await self.queue.get()
            await self.execute_job(job)
```

### 7.2 Progress Tracking

```typescript
// apps/web/components/JobProgress.tsx
export function JobProgress({ jobId }: { jobId: string }) {
  const { data: job, isLoading } = useQuery(
    ['job', jobId],
    () => fetchJob(jobId),
    { refetchInterval: 1000 }
  );
  
  if (isLoading) return <Skeleton />;
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between">
        <span>{job.type}</span>
        <Badge status={job.status} />
      </div>
      <Progress value={job.progress} />
      <div className="text-sm text-gray-500">
        {job.processedItems} / {job.totalItems} items
      </div>
    </div>
  );
}
```

## 8. Configuration Management

### 8.1 Feature Flags System

```python
# apps/api/app/config/features.py
from pydantic import BaseSettings
from typing import Dict, Any

class FeatureFlags(BaseSettings):
    """Centralized feature flag management"""
    
    # Core features
    ENABLE_REALTIME: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    ENABLE_DEBUG_UI: bool = True
    
    # API versions
    API_V1_ENABLED: bool = True
    API_V2_ENABLED: bool = False
    
    # Performance
    CACHE_ENABLED: bool = True
    RATE_LIMITING_ENABLED: bool = True
    
    # UI features
    SHOW_ADMIN_PANEL: bool = False
    ENABLE_DARK_MODE: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "FEATURE_"
```

### 8.2 Dynamic Configuration UI

```typescript
// apps/web/app/admin/config/page.tsx
export default function ConfigManager() {
  const [config, setConfig] = useState({});
  
  return (
    <div className="space-y-4">
      <h2>Feature Flags</h2>
      {Object.entries(config).map(([key, value]) => (
        <div key={key} className="flex items-center justify-between">
          <label>{key}</label>
          <Switch
            checked={value}
            onChange={(checked) => updateConfig(key, checked)}
          />
        </div>
      ))}
    </div>
  );
}
```

## 9. Error Handling & Monitoring

### 9.1 Centralized Error Handler

```python
# apps/api/app/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
import traceback
import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    async def __call__(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": str(e), "type": "validation_error"}
            )
        except PermissionError as e:
            logger.warning(f"Permission denied: {e}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Permission denied", "type": "permission_error"}
            )
        except Exception as e:
            logger.error(f"Unhandled error: {e}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error", "type": "server_error"}
            )
```

### 9.2 Frontend Error Boundary

```typescript
// apps/web/components/ErrorBoundary.tsx
export class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to monitoring service
    if (window.Sentry) {
      window.Sentry.captureException(error);
    }
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.toString()}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            Reload page
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

## 10. Performance Optimization

### 10.1 Caching Strategy

```python
# apps/api/app/cache/manager.py
from typing import Optional, Any
import redis.asyncio as redis
import json
import hashlib

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        
    def make_key(self, prefix: str, params: dict) -> str:
        """Generate cache key from parameters"""
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{param_hash}"
        
    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
        
    async def set(self, key: str, value: Any, expire: int = 300):
        await self.redis.set(
            key,
            json.dumps(value),
            ex=expire
        )
        
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

### 10.2 Query Optimization

```python
# apps/api/app/database/optimizations.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

class QueryOptimizer:
    @staticmethod
    def optimize_event_query(query):
        """Apply common optimizations to event queries"""
        return query.options(
            selectinload('related_events'),
            joinedload('metadata')
        ).execution_options(
            populate_existing=True,
            synchronize_session='fetch'
        )
```

## 11. Documentation

### 11.1 API Documentation

```python
# apps/api/app/docs/__init__.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="API Documentation",
        version="1.0.0",
        description="""
        ## Overview
        This API provides endpoints for data management and analysis.
        
        ## Authentication
        Use Bearer token in Authorization header.
        
        ## Rate Limiting
        - 100 requests per minute per IP
        - 1000 requests per hour per user
        
        ## Common Responses
        - 200: Success
        - 400: Bad Request
        - 401: Unauthorized
        - 429: Too Many Requests
        - 500: Internal Server Error
        """,
        routes=app.routes,
    )
    
    # Add custom examples
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if "requestBody" in openapi_schema["paths"][path][method]:
                # Add request examples
                pass
                
    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

### 11.2 Component Documentation

```typescript
// apps/web/components/README.md
# Component Library

## DataTable
Generic data table with sorting, filtering, and pagination.

### Usage
```tsx
<DataTable
  data={events}
  columns={[
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
  ]}
  onSort={(key, order) => handleSort(key, order)}
  onFilter={(filters) => handleFilter(filters)}
/>
```

### Props
- `data`: Array of objects to display
- `columns`: Column configuration
- `onSort`: Sort handler
- `onFilter`: Filter handler
```

## 12. Deployment & DevOps

### 12.1 Health Checks

```python
# apps/api/app/health/__init__.py
from typing import Dict, Any
import asyncio
from datetime import datetime

class HealthChecker:
    async def check_database(self) -> Dict[str, Any]:
        try:
            # Run simple query
            await db.execute("SELECT 1")
            return {"status": "healthy", "latency_ms": 5}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
            
    async def check_redis(self) -> Dict[str, Any]:
        try:
            await redis.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
            
    async def check_external_apis(self) -> Dict[str, Any]:
        # Check external dependencies
        pass
        
    async def get_health_status(self) -> Dict[str, Any]:
        checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_external_apis(),
            return_exceptions=True
        )
        
        return {
            "status": "healthy" if all(c.get("status") == "healthy" for c in checks) else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": checks[0],
                "redis": checks[1],
                "external_apis": checks[2]
            }
        }
```

### 12.2 Docker Compose Enhancements

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./apps/api
    environment:
      - PORT=${API_PORT:-8006}
    ports:
      - "${API_PORT:-8006}:8006"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8006/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
        
  web:
    build: ./apps/web
    environment:
      - PORT=${WEB_PORT:-3015}
      - NEXT_PUBLIC_API_URL=http://api:8006/api/v1
    ports:
      - "${WEB_PORT:-3015}:3015"
    depends_on:
      api:
        condition: service_healthy
        
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD:-devpass}
      - POSTGRES_DB=${DB_NAME:-app_dev}
    ports:
      - "${DB_PORT:-5444}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      
  redis:
    image: redis:7-alpine
    ports:
      - "${REDIS_PORT:-6381}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## 13. Security Best Practices

### 13.1 Input Validation

```python
# apps/api/app/validators/__init__.py
from pydantic import BaseModel, validator
import re

class SecureInputValidator:
    @staticmethod
    def validate_sql_safe(value: str) -> str:
        """Prevent SQL injection"""
        dangerous_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
            r"(--|#|/\*|\*/)",
            r"(\bOR\b.*=.*)",
            r"(\bAND\b.*=.*)"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially dangerous input detected")
        return value
        
    @staticmethod
    def validate_xss_safe(value: str) -> str:
        """Prevent XSS attacks"""
        dangerous_patterns = [
            r"<script",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially dangerous HTML detected")
        return value
```

### 13.2 Rate Limiting

```python
# apps/api/app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from typing import Dict, Tuple
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
        
    async def check_rate_limit(self, request: Request):
        client_id = request.client.host
        now = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < 60
        ]
        
        if len(self.requests[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
            
        self.requests[client_id].append(now)
```

## 14. Makefile Commands

```makefile
# Makefile
.PHONY: help dev test clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Development
dev: ## Start development environment
	@./scripts/check-ports.sh
	docker-compose up -d
	@echo "API: http://localhost:$${API_PORT:-8006}"
	@echo "Web: http://localhost:$${WEB_PORT:-3015}"
	@echo "Debug: http://localhost:$${WEB_PORT:-3015}/debug"

dev-logs: ## Show development logs
	docker-compose logs -f

stop: ## Stop development environment
	docker-compose down

clean: ## Clean all generated files and containers
	docker-compose down -v
	rm -rf apps/api/__pycache__
	rm -rf apps/web/.next
	rm -rf apps/web/node_modules

# Testing
test: ## Run all tests
	@echo "Running API tests..."
	cd apps/api && pytest
	@echo "Running Web tests..."
	cd apps/web && npm test

test-acceptance: ## Run acceptance tests only
	cd apps/api && pytest -m acceptance

test-coverage: ## Run tests with coverage
	cd apps/api && pytest --cov=app --cov-report=html
	cd apps/web && npm run test:coverage

# Database
db-migrate: ## Run database migrations
	cd apps/api && alembic upgrade head

db-rollback: ## Rollback last migration
	cd apps/api && alembic downgrade -1

db-reset: ## Reset database
	docker-compose down -v db
	docker-compose up -d db
	sleep 5
	$(MAKE) db-migrate

# Code Quality
lint: ## Run linters
	cd apps/api && ruff check .
	cd apps/web && npm run lint

format: ## Format code
	cd apps/api && black .
	cd apps/web && npm run format

type-check: ## Run type checking
	cd apps/api && mypy .
	cd apps/web && npm run type-check

# Documentation
docs: ## Generate documentation
	cd apps/api && python -m mkdocs build
	cd apps/web && npm run build-storybook

# Deployment
build: ## Build production images
	docker build -t api:latest apps/api
	docker build -t web:latest apps/web

deploy-staging: ## Deploy to staging
	./scripts/deploy.sh staging

deploy-production: ## Deploy to production
	./scripts/deploy.sh production
```

## 15. Summary of Key Recommendations

1. **Start with Debug UI**: Every feature should have a debug view from day 1
2. **User Stories First**: Link every slice to specific user stories with acceptance criteria
3. **Progressive Enhancement**: Simple → Functional → Beautiful
4. **Test at Three Levels**: Debug UI tests → Acceptance tests → E2E tests
5. **Real Data Early**: Connect to real data sources as soon as possible
6. **Error Handling**: Comprehensive error handling at every layer
7. **Performance Monitoring**: Built-in performance metrics from the start
8. **Configuration Management**: Feature flags and environment-specific configs
9. **Documentation**: Living documentation that grows with the code
10. **Health Checks**: Comprehensive health monitoring for all services

## Conclusion

The Solo Software Factory template provides a solid foundation, but these enhancements based on real-world implementation experience will make it more robust, developer-friendly, and production-ready. The key insight is to prioritize immediate feedback through debug UI, maintain strong connection to user stories, and build complexity progressively rather than all at once.