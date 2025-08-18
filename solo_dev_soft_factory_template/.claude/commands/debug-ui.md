---
name: debug-ui
description: Generate debug UI components for rapid development and testing
tools: [Read, Write, Edit]
---

# Debug UI Generator

Creates debug interfaces for immediate visual feedback during development, enabling rapid iteration and testing before building production UI.

## Usage

```bash
/debug-ui US-001                    # Generate debug UI for user story
/debug-ui VS-001                    # Generate debug UI for vertical slice
/debug-ui --feature dashboard       # Generate debug UI for feature
/debug-ui --component DataTable     # Generate specific debug component
```

## What It Generates

### 1. Debug Dashboard Page

```typescript
// apps/web/app/debug/[feature]/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { DebugLayout } from '@/components/debug/DebugLayout';
import { JsonViewer } from '@/components/debug/JsonViewer';
import { ApiTester } from '@/components/debug/ApiTester';
import { DataTable } from '@/components/debug/DataTable';
import { StateInspector } from '@/components/debug/StateInspector';
import { MetricsPanel } from '@/components/debug/MetricsPanel';
import { TestRunner } from '@/components/debug/TestRunner';

export default function Debug[Feature]Page() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [testResults, setTestResults] = useState([]);

  // Story information
  const storyInfo = {
    id: 'US-001',
    title: 'User views dashboard',
    acceptanceCriteria: [
      'Data loads within 5 seconds',
      'Shows last 24 hours by default',
      'Updates every 30 seconds'
    ]
  };

  // Fetch data function
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/[endpoint]');
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Test scenarios
  const runTest = async (scenario) => {
    const result = await fetch(`/api/debug/test/${scenario}`);
    const data = await result.json();
    setTestResults(prev => [...prev, data]);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <DebugLayout
      title="Debug: [Feature]"
      story={storyInfo}
      refreshAction={fetchData}
    >
      {/* Status Bar */}
      <div className="bg-gray-100 p-4 rounded-lg mb-6">
        <div className="flex justify-between items-center">
          <div className="flex gap-4">
            <StatusBadge label="API" status={data ? 'success' : 'error'} />
            <StatusBadge label="Loading" status={loading ? 'active' : 'idle'} />
            <StatusBadge label="Error" status={error ? 'error' : 'success'} />
          </div>
          <div className="flex gap-2">
            <button onClick={fetchData} className="btn btn-primary">
              Refresh Data
            </button>
            <button onClick={() => setData(null)} className="btn">
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Data Display - Left Side */}
        <div className="col-span-7 space-y-6">
          {/* Raw JSON View */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">Raw Data</h3>
            <JsonViewer 
              data={data} 
              collapsed={false}
              searchable={true}
              copyable={true}
            />
          </div>

          {/* Data Table View */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">Table View</h3>
            <DataTable
              data={data?.items || []}
              columns={[
                { key: 'id', label: 'ID', sortable: true },
                { key: 'name', label: 'Name', sortable: true },
                { key: 'status', label: 'Status', sortable: true },
                { key: 'created_at', label: 'Created', sortable: true }
              ]}
              pagination={true}
              pageSize={10}
              searchable={true}
              exportable={true}
            />
          </div>

          {/* Metrics */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">Metrics</h3>
            <MetricsPanel
              metrics={[
                { label: 'Total Items', value: data?.total || 0 },
                { label: 'Response Time', value: `${data?.responseTime || 0}ms` },
                { label: 'Cache Hit', value: data?.cacheHit ? 'Yes' : 'No' },
                { label: 'Last Updated', value: new Date().toLocaleTimeString() }
              ]}
            />
          </div>
        </div>

        {/* Testing Tools - Right Side */}
        <div className="col-span-5 space-y-6">
          {/* API Tester */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">API Tester</h3>
            <ApiTester
              defaultEndpoint="/api/v1/[endpoint]"
              methods={['GET', 'POST', 'PUT', 'DELETE']}
              savedRequests={[
                { name: 'Get All', method: 'GET', path: '/api/v1/items' },
                { name: 'Create Item', method: 'POST', path: '/api/v1/items' },
                { name: 'Update Item', method: 'PUT', path: '/api/v1/items/1' }
              ]}
              onResponse={(response) => console.log('API Response:', response)}
            />
          </div>

          {/* Test Runner */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">Test Scenarios</h3>
            <TestRunner
              scenarios={[
                { id: 'happy', name: 'Happy Path', description: 'Normal flow' },
                { id: 'empty', name: 'Empty Data', description: 'No results' },
                { id: 'error', name: 'Error Case', description: 'API failure' },
                { id: 'slow', name: 'Slow Network', description: '3s delay' },
                { id: 'large', name: 'Large Dataset', description: '10k items' }
              ]}
              onRun={runTest}
              results={testResults}
            />
          </div>

          {/* State Inspector */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">State Inspector</h3>
            <StateInspector
              state={{
                data,
                loading,
                error,
                testResults
              }}
              editable={true}
              onStateChange={(newState) => {
                if (newState.data !== undefined) setData(newState.data);
                if (newState.loading !== undefined) setLoading(newState.loading);
                if (newState.error !== undefined) setError(newState.error);
              }}
            />
          </div>

          {/* Acceptance Criteria Checklist */}
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">Acceptance Criteria</h3>
            <AcceptanceCriteriaChecklist
              criteria={storyInfo.acceptanceCriteria}
              testable={true}
              onTest={(criterion) => console.log('Testing:', criterion)}
            />
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-6 bg-red-50 border border-red-200 p-4 rounded-lg">
          <h4 className="text-red-800 font-semibold">Error</h4>
          <pre className="text-red-600 text-sm mt-2">{error}</pre>
        </div>
      )}
    </DebugLayout>
  );
}
```

### 2. Debug Components Library

```typescript
// apps/web/components/debug/index.ts
export { DebugLayout } from './DebugLayout';
export { JsonViewer } from './JsonViewer';
export { ApiTester } from './ApiTester';
export { DataTable } from './DataTable';
export { StateInspector } from './StateInspector';
export { MetricsPanel } from './MetricsPanel';
export { TestRunner } from './TestRunner';
export { LiveLog } from './LiveLog';
export { QueryBuilder } from './QueryBuilder';
export { WebSocketTester } from './WebSocketTester';

// Component implementations
// apps/web/components/debug/JsonViewer.tsx
export function JsonViewer({ 
  data, 
  collapsed = false, 
  searchable = false,
  copyable = false,
  theme = 'light'
}) {
  const [search, setSearch] = useState('');
  const [isCollapsed, setIsCollapsed] = useState(collapsed);
  
  const highlightSearch = (str) => {
    if (!search) return str;
    // Highlight matching text
    return str.replace(new RegExp(search, 'gi'), '<mark>$&</mark>');
  };
  
  return (
    <div className="json-viewer">
      {searchable && (
        <input
          type="text"
          placeholder="Search JSON..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="mb-2 p-2 border rounded w-full"
        />
      )}
      
      {copyable && (
        <button
          onClick={() => navigator.clipboard.writeText(JSON.stringify(data, null, 2))}
          className="mb-2 btn btn-sm"
        >
          Copy JSON
        </button>
      )}
      
      <pre className={`p-4 bg-gray-50 rounded overflow-auto ${theme}`}>
        <code dangerouslySetInnerHTML={{
          __html: highlightSearch(JSON.stringify(data, null, 2))
        }} />
      </pre>
    </div>
  );
}

// apps/web/components/debug/ApiTester.tsx
export function ApiTester({ 
  defaultEndpoint, 
  methods = ['GET', 'POST', 'PUT', 'DELETE'],
  savedRequests = [],
  onResponse 
}) {
  const [method, setMethod] = useState('GET');
  const [endpoint, setEndpoint] = useState(defaultEndpoint);
  const [headers, setHeaders] = useState('{}');
  const [body, setBody] = useState('{}');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const sendRequest = async () => {
    setLoading(true);
    try {
      const options = {
        method,
        headers: JSON.parse(headers)
      };
      
      if (['POST', 'PUT', 'PATCH'].includes(method)) {
        options.body = body;
        options.headers['Content-Type'] = 'application/json';
      }
      
      const res = await fetch(endpoint, options);
      const data = await res.json();
      
      setResponse({
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries()),
        data
      });
      
      onResponse?.(data);
    } catch (error) {
      setResponse({ error: error.message });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="api-tester space-y-4">
      {/* Method & Endpoint */}
      <div className="flex gap-2">
        <select 
          value={method} 
          onChange={(e) => setMethod(e.target.value)}
          className="px-3 py-2 border rounded"
        >
          {methods.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        
        <input
          type="text"
          value={endpoint}
          onChange={(e) => setEndpoint(e.target.value)}
          placeholder="API endpoint"
          className="flex-1 px-3 py-2 border rounded"
        />
        
        <button
          onClick={sendRequest}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
      
      {/* Headers */}
      <div>
        <label className="block text-sm font-medium mb-1">Headers (JSON)</label>
        <textarea
          value={headers}
          onChange={(e) => setHeaders(e.target.value)}
          className="w-full p-2 border rounded font-mono text-sm"
          rows={3}
        />
      </div>
      
      {/* Body */}
      {['POST', 'PUT', 'PATCH'].includes(method) && (
        <div>
          <label className="block text-sm font-medium mb-1">Body (JSON)</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            className="w-full p-2 border rounded font-mono text-sm"
            rows={5}
          />
        </div>
      )}
      
      {/* Saved Requests */}
      {savedRequests.length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-1">Saved Requests</label>
          <div className="flex gap-2 flex-wrap">
            {savedRequests.map((req, i) => (
              <button
                key={i}
                onClick={() => {
                  setMethod(req.method);
                  setEndpoint(req.path);
                  if (req.body) setBody(JSON.stringify(req.body, null, 2));
                }}
                className="px-2 py-1 bg-gray-100 rounded text-sm hover:bg-gray-200"
              >
                {req.name}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Response */}
      {response && (
        <div>
          <label className="block text-sm font-medium mb-1">Response</label>
          <div className="bg-gray-50 p-3 rounded">
            {response.status && (
              <div className="mb-2 text-sm">
                Status: <span className={response.status < 400 ? 'text-green-600' : 'text-red-600'}>
                  {response.status} {response.statusText}
                </span>
              </div>
            )}
            <pre className="text-xs overflow-auto">
              {JSON.stringify(response.data || response.error, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 3. Debug API Endpoints

```python
# apps/api/app/debug/__init__.py
from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
import random
import time

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/test/{scenario}")
async def run_test_scenario(scenario: str) -> Dict[str, Any]:
    """Run predefined test scenarios for debugging"""
    
    scenarios = {
        "happy": {
            "status": "success",
            "data": [{"id": i, "value": f"Item {i}"} for i in range(10)],
            "message": "Happy path successful"
        },
        "empty": {
            "status": "success",
            "data": [],
            "message": "No data available"
        },
        "error": {
            "status": "error",
            "error": "Simulated error for testing",
            "code": "TEST_ERROR_001"
        },
        "slow": {
            "status": "success",
            "data": [{"id": 1}],
            "message": "Slow response simulated",
            "delay": 3000
        },
        "large": {
            "status": "success",
            "data": [{"id": i} for i in range(10000)],
            "message": "Large dataset"
        }
    }
    
    if scenario == "slow":
        await asyncio.sleep(3)
    
    return scenarios.get(scenario, {"status": "error", "message": "Unknown scenario"})

@router.post("/mock-data")
async def generate_mock_data(
    count: int = Query(10, ge=1, le=1000),
    schema: str = Query("default")
) -> Dict[str, Any]:
    """Generate mock data for testing"""
    
    schemas = {
        "default": lambda i: {
            "id": i,
            "name": f"Item {i}",
            "status": random.choice(["active", "inactive", "pending"]),
            "value": random.randint(1, 100)
        },
        "user": lambda i: {
            "id": i,
            "email": f"user{i}@example.com",
            "name": f"User {i}",
            "role": random.choice(["admin", "user", "guest"])
        },
        "event": lambda i: {
            "id": i,
            "type": random.choice(["click", "view", "submit"]),
            "timestamp": time.time() - random.randint(0, 86400),
            "user_id": random.randint(1, 100)
        }
    }
    
    generator = schemas.get(schema, schemas["default"])
    data = [generator(i) for i in range(1, count + 1)]
    
    return {
        "data": data,
        "count": len(data),
        "schema": schema
    }

@router.get("/state")
async def get_debug_state() -> Dict[str, Any]:
    """Get current application debug state"""
    return {
        "database": {
            "connected": True,
            "pool_size": 10,
            "active_connections": 3
        },
        "cache": {
            "enabled": True,
            "hit_rate": 0.85,
            "size": "2.3 MB"
        },
        "api": {
            "requests_per_minute": 150,
            "average_response_time": 45,
            "error_rate": 0.02
        },
        "features": {
            "debug_mode": True,
            "rate_limiting": False,
            "caching": True
        }
    }

@router.post("/clear-cache")
async def clear_cache() -> Dict[str, str]:
    """Clear all caches for debugging"""
    # Clear Redis cache
    # Clear in-memory cache
    return {"status": "Cache cleared successfully"}
```

### 4. Debug Layout Component

```typescript
// apps/web/components/debug/DebugLayout.tsx
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function DebugLayout({ 
  children, 
  title, 
  story,
  refreshAction 
}) {
  const pathname = usePathname();
  
  const debugRoutes = [
    { path: '/debug', label: 'Overview' },
    { path: '/debug/api', label: 'API' },
    { path: '/debug/database', label: 'Database' },
    { path: '/debug/cache', label: 'Cache' },
    { path: '/debug/logs', label: 'Logs' },
    { path: '/debug/metrics', label: 'Metrics' }
  ];
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🔧 Debug Mode</h1>
              {title && <p className="text-sm text-gray-600 mt-1">{title}</p>}
            </div>
            
            {refreshAction && (
              <button
                onClick={refreshAction}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                🔄 Refresh
              </button>
            )}
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="px-6 pb-3">
          <div className="flex gap-4">
            {debugRoutes.map(route => (
              <Link
                key={route.path}
                href={route.path}
                className={`px-3 py-1 rounded text-sm ${
                  pathname === route.path
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {route.label}
              </Link>
            ))}
          </div>
        </nav>
      </header>
      
      {/* Story Info Banner */}
      {story && (
        <div className="bg-blue-50 border-b border-blue-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-semibold text-blue-900">{story.id}:</span>
              <span className="ml-2 text-blue-700">{story.title}</span>
            </div>
            <div className="flex gap-2">
              {story.acceptanceCriteria?.map((ac, i) => (
                <span key={i} className="px-2 py-1 bg-blue-100 rounded text-xs">
                  AC{i + 1} ✓
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Main Content */}
      <main className="p-6">
        {children}
      </main>
      
      {/* Footer */}
      <footer className="mt-12 px-6 py-4 border-t bg-white text-center text-sm text-gray-500">
        Debug UI - Development Only | 
        <Link href="/" className="ml-2 text-blue-500 hover:underline">
          Production UI →
        </Link>
      </footer>
    </div>
  );
}
```

## Debug UI Patterns

### Data Display Pattern
```typescript
<DebugDataDisplay
  title="User Data"
  data={userData}
  views={['json', 'table', 'cards']}
  defaultView="table"
  searchable={true}
  exportable={true}
/>
```

### Testing Pattern
```typescript
<DebugTestPanel
  tests={[
    { name: 'Load data', fn: testLoadData },
    { name: 'Submit form', fn: testSubmitForm },
    { name: 'Handle error', fn: testErrorHandling }
  ]}
  autoRun={false}
  showResults={true}
/>
```

### Monitoring Pattern
```typescript
<DebugMonitor
  endpoints={['/api/health', '/api/metrics']}
  interval={5000}
  alerts={[
    { metric: 'responseTime', threshold: 1000, type: 'warning' },
    { metric: 'errorRate', threshold: 0.05, type: 'error' }
  ]}
/>
```

## Best Practices

1. **Start with debug UI**: Build debug interface before production
2. **Include all states**: Show loading, error, empty, and success states
3. **Make it interactive**: Allow data manipulation and state changes
4. **Test from UI**: Include test runners and scenario triggers
5. **Show raw data**: Always have JSON view available
6. **Track metrics**: Display performance and quality metrics
7. **Link to stories**: Show which user story is being implemented
8. **Keep it simple**: Debug UI doesn't need to be pretty, just functional

## Integration

### With User Stories
```bash
/user-story "As a user, I want to view data"
/debug-ui US-001
# Generates debug UI with story context
```

### With Slices
```bash
/story-to-slice US-001 US-002
/debug-ui VS-001
# Generates debug UI for entire slice
```

### With Tests
```bash
/debug-ui US-001
/acceptance-test US-001
# Debug UI and tests work together
```

## Output Structure

```
apps/
├── web/
│   ├── app/
│   │   └── debug/
│   │       ├── layout.tsx
│   │       ├── page.tsx
│   │       └── [feature]/
│   │           └── page.tsx
│   └── components/
│       └── debug/
│           ├── index.ts
│           ├── DebugLayout.tsx
│           ├── JsonViewer.tsx
│           ├── ApiTester.tsx
│           └── [other components]
└── api/
    └── app/
        └── debug/
            ├── __init__.py
            ├── routes.py
            └── test_scenarios.py
```