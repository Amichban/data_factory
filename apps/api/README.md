# FastAPI Backend

A production-ready FastAPI backend application with PostgreSQL, Alembic migrations, comprehensive testing, and structured logging.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Async/Await Support**: Full async support with asyncio and async database operations
- **PostgreSQL Database**: Production-ready database with connection pooling
- **Database Migrations**: Alembic for database schema versioning
- **Authentication Ready**: JWT token authentication structure
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Structured Logging**: JSON-structured logging with request tracing
- **Health Checks**: Kubernetes-ready health endpoints
- **CORS Support**: Configurable cross-origin resource sharing
- **Environment Configuration**: Pydantic settings with validation

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials and settings
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 3. Database Setup

```bash
# Start PostgreSQL (using Docker)
docker run --name postgres-fastapi -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=fastapi_db -p 5432:5432 -d postgres:15

# Initialize database migrations
alembic init alembic  # Already done
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Run the Application

```bash
# Development server
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --port 8000
```

### 5. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health.py -v
```

## API Endpoints

### Health Checks
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system health
- `GET /api/v1/health/liveness` - Kubernetes liveness probe
- `GET /api/v1/health/readiness` - Kubernetes readiness probe

### Documentation
- `GET /api/v1/docs` - Swagger UI (development only)
- `GET /api/v1/redoc` - ReDoc documentation (development only)

## Project Structure

```
apps/api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API route handlers
│   └── middleware/          # Custom middleware
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example            # Environment template
└── .gitignore              # Git ignore rules
```

## Development

### Database Migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

See `.env.example` for all available configuration options.

## Monitoring

The application provides comprehensive health checks and structured logging for monitoring:

- **Health Endpoints**: Multiple endpoints for different monitoring needs
- **Request Tracing**: Each request gets a unique ID for tracing
- **Structured Logs**: JSON-formatted logs with consistent fields
- **Performance Metrics**: Response times and system resource usage

## Contributing

1. Install development dependencies
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Format code with black and isort
7. Submit a pull request