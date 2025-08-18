# API Design Principles and Patterns

## Overview

This document outlines the API design principles, patterns, and standards used across the QuantX Platform. It ensures consistency, maintainability, and developer experience across all service interfaces.

## API Design Philosophy

### Core Principles

1. **API-First Design**: APIs are designed before implementation
2. **Consumer-Centric**: Designed from the consumer's perspective
3. **Consistency**: Uniform patterns across all services
4. **Discoverability**: Self-documenting and explorable
5. **Versioning**: Backward compatibility with clear evolution paths
6. **Security by Design**: Built-in security considerations
7. **Performance**: Optimized for speed and efficiency

### Design Values

- **Simplicity over Cleverness**: Clear, straightforward interfaces
- **Predictability**: Consistent naming and behavior patterns
- **Flexibility**: Support for diverse use cases
- **Reliability**: Robust error handling and resilience
- **Observability**: Built-in monitoring and debugging capabilities

## REST API Standards

### URL Design

**Resource-Oriented Design**:
```
Good:
  GET  /api/v1/portfolios
  GET  /api/v1/portfolios/{id}
  POST /api/v1/portfolios
  PUT  /api/v1/portfolios/{id}
  DELETE /api/v1/portfolios/{id}

Bad:
  GET  /api/v1/getPortfolios
  POST /api/v1/createPortfolio
  GET  /api/v1/portfolio?action=get&id=123
```

**URL Structure Standards**:
- Use lowercase letters and hyphens for readability
- Plural nouns for collections (`/portfolios`, `/users`)
- Singular nouns for single resources (`/portfolio/{id}`)
- Hierarchical relationships (`/portfolios/{id}/holdings`)
- Query parameters for filtering and pagination

**Path Parameters vs Query Parameters**:
```
Path Parameters (Resource Identification):
  /api/v1/portfolios/{portfolioId}
  /api/v1/users/{userId}/settings

Query Parameters (Filtering/Options):
  /api/v1/portfolios?user_id=123&status=active
  /api/v1/market/quotes?symbols=AAPL,GOOGL&fields=price,volume
```

### HTTP Methods

**Standard HTTP Verbs**:
```
GET    - Retrieve resources (idempotent, safe)
POST   - Create resources (non-idempotent)
PUT    - Update/replace resources (idempotent)
PATCH  - Partial updates (idempotent)
DELETE - Remove resources (idempotent)
HEAD   - Retrieve headers only (idempotent, safe)
OPTIONS - Retrieve allowed methods (idempotent, safe)
```

**Method Usage Patterns**:
```javascript
// Collection Operations
GET    /api/v1/portfolios           // List portfolios
POST   /api/v1/portfolios           // Create portfolio

// Resource Operations  
GET    /api/v1/portfolios/{id}      // Get portfolio
PUT    /api/v1/portfolios/{id}      // Replace portfolio
PATCH  /api/v1/portfolios/{id}      // Update portfolio
DELETE /api/v1/portfolios/{id}      // Delete portfolio

// Sub-resource Operations
GET    /api/v1/portfolios/{id}/holdings    // Get holdings
POST   /api/v1/portfolios/{id}/holdings    // Add holding
DELETE /api/v1/portfolios/{id}/holdings/{holdingId}  // Remove holding
```

### Request/Response Format

**Content Type Standards**:
```http
Content-Type: application/json; charset=utf-8
Accept: application/json
```

**Request Format**:
```json
{
  "data": {
    "type": "portfolio",
    "attributes": {
      "name": "Growth Portfolio",
      "description": "Long-term growth strategy",
      "risk_level": "moderate"
    },
    "relationships": {
      "user": {
        "data": { "type": "user", "id": "user123" }
      }
    }
  }
}
```

**Response Format**:
```json
{
  "data": {
    "id": "portfolio456",
    "type": "portfolio",
    "attributes": {
      "name": "Growth Portfolio",
      "description": "Long-term growth strategy",
      "risk_level": "moderate",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "relationships": {
      "user": {
        "data": { "type": "user", "id": "user123" },
        "links": { "self": "/api/v1/users/user123" }
      }
    },
    "links": {
      "self": "/api/v1/portfolios/portfolio456"
    }
  },
  "meta": {
    "created_at": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

### Pagination

**Cursor-Based Pagination** (Preferred for real-time data):
```json
{
  "data": [...],
  "pagination": {
    "has_more": true,
    "next_cursor": "eyJpZCI6MTIzLCJ0aW1lc3RhbXAiOjE2NDI2...",
    "prev_cursor": "eyJpZCI6OTg3LCJ0aW1lc3RhbXAiOjE2NDI1...",
    "limit": 50
  }
}
```

**Offset-Based Pagination** (For stable datasets):
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_pages": 10,
    "total_count": 487,
    "has_more": true
  }
}
```

**Request Parameters**:
```
GET /api/v1/portfolios?cursor=next_cursor_value&limit=50
GET /api/v1/portfolios?page=1&per_page=50
```

### Filtering and Sorting

**Filtering Syntax**:
```
GET /api/v1/portfolios?filter[status]=active&filter[risk_level]=moderate
GET /api/v1/portfolios?status=active&created_after=2024-01-01
GET /api/v1/market/quotes?symbols=AAPL,GOOGL,TSLA
```

**Sorting**:
```
GET /api/v1/portfolios?sort=name              // Ascending
GET /api/v1/portfolios?sort=-created_at       // Descending  
GET /api/v1/portfolios?sort=name,-created_at  // Multiple fields
```

**Field Selection**:
```
GET /api/v1/portfolios?fields=id,name,status
GET /api/v1/portfolios/{id}?include=holdings,user
```

## Error Handling

### Error Response Format

**Standard Error Structure**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Email address is not valid"
      },
      {
        "field": "password",
        "code": "TOO_SHORT",
        "message": "Password must be at least 8 characters"
      }
    ],
    "request_id": "req_1234567890abcdef",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### HTTP Status Codes

**Success Codes**:
- `200 OK` - Successful GET, PUT, PATCH, DELETE
- `201 Created` - Successful POST with resource creation
- `202 Accepted` - Request accepted for async processing
- `204 No Content` - Successful request with no response body

**Client Error Codes**:
- `400 Bad Request` - Invalid request syntax or parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Valid authentication but insufficient permissions
- `404 Not Found` - Resource not found
- `405 Method Not Allowed` - HTTP method not supported
- `409 Conflict` - Resource conflict (duplicate, version mismatch)
- `422 Unprocessable Entity` - Valid syntax but semantic errors
- `429 Too Many Requests` - Rate limit exceeded

**Server Error Codes**:
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Invalid response from upstream server
- `503 Service Unavailable` - Service temporarily unavailable
- `504 Gateway Timeout` - Upstream server timeout

### Error Code Categories

**Business Logic Errors**:
```json
{
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Account balance is insufficient for this trade",
    "details": {
      "required_amount": 10000,
      "available_balance": 8500,
      "currency": "USD"
    }
  }
}
```

**Validation Errors**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "quantity",
        "code": "REQUIRED",
        "message": "Quantity is required"
      }
    ]
  }
}
```

**System Errors**:
```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Market data service is temporarily unavailable",
    "retry_after": 30,
    "service": "market-data"
  }
}
```

## Authentication and Authorization

### Authentication Methods

**JWT Bearer Token**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**API Key Authentication**:
```http
X-API-Key: your-api-key-here
X-API-Secret: your-api-secret-here
```

### Token Structure

**JWT Claims**:
```json
{
  "sub": "user123",
  "iat": 1642636800,
  "exp": 1642723200,
  "aud": "quantx-api",
  "iss": "quantx-auth",
  "scope": ["portfolio:read", "portfolio:write", "trading:execute"],
  "user_id": "user123",
  "role": "trader",
  "tenant_id": "org456"
}
```

### Authorization Patterns

**Role-Based Access Control (RBAC)**:
```json
{
  "roles": {
    "admin": {
      "permissions": ["*:*"]
    },
    "trader": {
      "permissions": [
        "portfolio:read", "portfolio:write",
        "trading:execute", "market:read"
      ]
    },
    "viewer": {
      "permissions": ["portfolio:read", "market:read"]
    }
  }
}
```

**Resource-Based Permissions**:
```
portfolio:123:read
portfolio:123:write  
trading:account:456:execute
```

## API Versioning

### Versioning Strategy

**URL Path Versioning** (Primary):
```
/api/v1/portfolios
/api/v2/portfolios
```

**Header Versioning** (Alternative):
```http
Accept: application/vnd.quantx.v1+json
API-Version: 1.0
```

### Version Lifecycle

**Version States**:
1. **Beta** - `v1.0.0-beta.1` - Preview features
2. **Stable** - `v1.0.0` - Production ready
3. **Deprecated** - `v1.0.0` (with deprecation notice)
4. **Retired** - No longer available

**Deprecation Process**:
```json
{
  "data": {...},
  "meta": {
    "deprecation": {
      "deprecated": true,
      "sunset_date": "2024-12-31",
      "migration_guide": "https://docs.quantx.com/migration/v1-to-v2",
      "replacement_version": "v2"
    }
  }
}
```

### Breaking Changes

**Non-Breaking Changes** (Patch/Minor versions):
- Adding optional fields
- Adding new endpoints
- Adding new optional query parameters
- Adding new response fields
- Improving error messages

**Breaking Changes** (Major versions):
- Removing fields or endpoints
- Changing field types or formats
- Modifying required parameters
- Changing authentication mechanisms
- Altering response structure

## Real-Time APIs

### WebSocket Design

**Connection Establishment**:
```javascript
const ws = new WebSocket('wss://api.quantx.com/v1/stream');

// Authentication
ws.send(JSON.stringify({
  type: 'auth',
  token: 'Bearer jwt-token'
}));

// Subscribe to market data
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'market.quotes',
  symbols: ['AAPL', 'GOOGL', 'TSLA']
}));
```

**Message Format**:
```json
{
  "type": "market.quote",
  "channel": "market.quotes",
  "data": {
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 1000000,
    "timestamp": "2024-01-15T15:30:00Z"
  },
  "sequence": 12345,
  "timestamp": "2024-01-15T15:30:00.123Z"
}
```

### Server-Sent Events (SSE)

**Event Stream**:
```http
GET /api/v1/stream/portfolio/123/updates
Accept: text/event-stream
Authorization: Bearer jwt-token
```

**Event Format**:
```
event: portfolio.update
data: {"portfolio_id": "123", "total_value": 50000, "change": 2.5}
id: evt_1234567890
retry: 5000

event: portfolio.alert
data: {"type": "risk", "message": "Portfolio exceeds risk limit"}
id: evt_1234567891
```

## Rate Limiting

### Rate Limiting Strategy

**Rate Limit Headers**:
```http
X-Rate-Limit-Limit: 1000
X-Rate-Limit-Remaining: 999
X-Rate-Limit-Reset: 1642636800
X-Rate-Limit-Window: 3600
Retry-After: 60
```

**Rate Limit Tiers**:
```json
{
  "rate_limits": {
    "free": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000,
      "burst_limit": 10
    },
    "pro": {
      "requests_per_minute": 600,
      "requests_per_hour": 10000,
      "burst_limit": 100
    },
    "enterprise": {
      "requests_per_minute": 6000,
      "requests_per_hour": 100000,
      "burst_limit": 1000
    }
  }
}
```

### Rate Limiting by Resource

**Resource-Specific Limits**:
```json
{
  "endpoints": {
    "/api/v1/market/quotes": {
      "limit": 100,
      "window": 60,
      "scope": "user"
    },
    "/api/v1/trading/orders": {
      "limit": 10,
      "window": 60,
      "scope": "user"
    },
    "/api/v1/analytics/backtest": {
      "limit": 5,
      "window": 3600,
      "scope": "user"
    }
  }
}
```

## Caching Strategy

### HTTP Caching

**Cache Headers**:
```http
Cache-Control: public, max-age=300, s-maxage=600
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Mon, 15 Jan 2024 10:30:00 GMT
Vary: Accept-Encoding, Authorization
```

**Caching Patterns**:
```
Static Data (Reference Data):
  Cache-Control: public, max-age=86400 (24 hours)

Market Data (Frequent Updates):  
  Cache-Control: public, max-age=30, s-maxage=60

User-Specific Data:
  Cache-Control: private, max-age=300

Real-Time Data:
  Cache-Control: no-cache, must-revalidate
```

### Application-Level Caching

**Cache Keys**:
```
user:{user_id}:portfolio:{portfolio_id}
market:quote:{symbol}:latest  
analytics:performance:{portfolio_id}:{date_range}
```

**Cache TTL Strategy**:
```json
{
  "cache_policies": {
    "user_data": {"ttl": 900, "refresh": true},
    "market_data": {"ttl": 30, "refresh": false},
    "analytics": {"ttl": 1800, "refresh": true},
    "reference_data": {"ttl": 86400, "refresh": false}
  }
}
```

## Documentation Standards

### OpenAPI Specification

**API Documentation Structure**:
```yaml
openapi: 3.0.3
info:
  title: QuantX Platform API
  description: Comprehensive quantitative analysis platform API
  version: 1.0.0
  contact:
    name: API Support
    url: https://support.quantx.com
    email: api-support@quantx.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.quantx.com/v1
    description: Production server
  - url: https://staging-api.quantx.com/v1  
    description: Staging server

paths:
  /portfolios:
    get:
      summary: List portfolios
      description: Retrieve a paginated list of user portfolios
      operationId: listPortfolios
      tags:
        - Portfolios
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PortfolioList'
```

### Code Examples

**Multi-Language Examples**:
```javascript
// JavaScript/Node.js
const response = await fetch('/api/v1/portfolios', {
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
});
const portfolios = await response.json();
```

```python
# Python
import requests

response = requests.get(
    'https://api.quantx.com/v1/portfolios',
    headers={'Authorization': f'Bearer {token}'}
)
portfolios = response.json()
```

```curl
# cURL
curl -X GET \
  'https://api.quantx.com/v1/portfolios' \
  -H 'Authorization: Bearer your-jwt-token' \
  -H 'Accept: application/json'
```

## API Testing Standards

### Test Categories

**Unit Tests**:
- Request/response validation
- Business logic testing
- Error handling scenarios

**Integration Tests**:  
- Service-to-service communication
- Database interactions
- External API integrations

**Contract Tests**:
- API schema validation
- Backward compatibility checks
- Consumer-driven contract testing

**Performance Tests**:
- Load testing under normal conditions
- Stress testing at peak capacity
- Endurance testing for stability

### Test Data Management

**Test Data Strategies**:
```json
{
  "environments": {
    "unit": "mocked_data",
    "integration": "test_database",
    "staging": "synthetic_data",
    "load_test": "generated_data"
  }
}
```

This comprehensive API design guide ensures consistent, maintainable, and developer-friendly interfaces across the QuantX Platform ecosystem.