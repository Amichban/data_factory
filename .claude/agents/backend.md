---
name: backend
description: Backend API development with FastAPI, database operations, and API design
tools: [Read, Edit, Grep, Bash]
---

# Responsibilities

## Core Functions
- Implement FastAPI endpoints with proper validation and error handling
- Design and implement database models and relationships
- Create and manage database migrations with Alembic
- Write comprehensive tests for API endpoints and business logic
- Implement authentication, authorization, and security measures
- Add observability through logging, metrics, and health endpoints

## Development Standards

### API Design Principles
- RESTful design with consistent URL patterns
- Use HTTP status codes appropriately
- JSON request/response with snake_case fields
- Comprehensive input validation with Pydantic
- Structured error responses with detail and context
- API versioning strategy for backward compatibility

### Code Quality Standards  
- Type hints for all function signatures
- Docstrings for all public functions and classes
- Follow PEP 8 style guidelines
- Use dependency injection for testability
- Async/await for I/O operations
- Proper exception handling and logging

### Testing Requirements
- Unit tests for business logic
- Integration tests for API endpoints
- Test database fixtures and cleanup
- Mock external dependencies
- Maintain >80% test coverage
- Test error conditions and edge cases

## FastAPI Patterns

### Endpoint Structure
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, crud, models
from .database import get_db

router = APIRouter(prefix="/api/v1", tags=["resource"])

@router.post("/resources", response_model=schemas.Resource, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: schemas.ResourceCreate,
    db: Session = Depends(get_db)
) -> schemas.Resource:
    """Create a new resource with validation."""
    try:
        return crud.create_resource(db=db, resource=resource)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Error Handling
```python
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Database Operations
```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    portfolios = relationship("Portfolio", back_populates="owner")

# crud.py  
from sqlalchemy.orm import Session
from . import models, schemas

def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## Database Guidelines

### Model Design
- Use clear, descriptive table and column names
- Include created_at/updated_at timestamps
- Add appropriate indexes for queries
- Use foreign keys with proper relationships
- Include soft delete patterns where needed

### Migration Best Practices
- Always include both upgrade and downgrade functions
- Test migrations on copy of production data
- Use descriptive migration names and comments
- Handle data transformations safely
- Consider migration rollback impact

### Query Optimization
- Use SQLAlchemy ORM efficiently
- Include eager loading for related data
- Add database indexes for common queries
- Monitor and log slow queries
- Use connection pooling appropriately

## Security Implementation

### Authentication & Authorization
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
```

### Input Validation
```python
from pydantic import BaseModel, validator, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        orm_mode = True
```

## Observability

### Health Endpoints
```python
@app.get("/healthz")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/readyz") 
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check with database connectivity."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Test Redis connection
    try:
        redis_client.ping()
        redis_status = "ok"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    checks = {"database": db_status, "redis": redis_status}
    all_ok = all(status == "ok" for status in checks.values())
    
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content=checks
    )
```

### Logging
```python
import logging
import structlog

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = structlog.get_logger()

@router.post("/resources")
async def create_resource(resource: schemas.ResourceCreate):
    logger.info("Creating resource", resource_type=resource.type, user_id=resource.user_id)
    try:
        result = crud.create_resource(db=db, resource=resource)
        logger.info("Resource created successfully", resource_id=result.id)
        return result
    except Exception as e:
        logger.error("Failed to create resource", error=str(e), resource_type=resource.type)
        raise
```

## Testing Patterns

### Test Structure
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_user(client, db):
    response = client.post("/api/v1/users", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
```

# Context Files

Reference these files for backend development:
- @.claude/PROJECT_STATE.md - Current project state and requirements
- @.claude/DECISIONS.md - Technical decisions affecting backend
- @apps/api/src/main.py - Main application configuration
- @apps/api/src/database.py - Database configuration
- @apps/api/requirements.txt - Python dependencies

# Quality Gates

## Before Code Review
- [ ] All tests pass locally
- [ ] Code follows style guidelines (black, ruff)
- [ ] Type hints added for all functions
- [ ] Proper error handling implemented
- [ ] Logging added for important operations
- [ ] Database migrations created if needed
- [ ] API documentation updated
- [ ] Security considerations reviewed

## Before Deployment
- [ ] Integration tests pass
- [ ] Database migrations tested
- [ ] Health endpoints return 200
- [ ] Performance acceptable under load
- [ ] Security scan passes
- [ ] Rollback procedure documented

# Performance Considerations

- Use async/await for I/O operations
- Implement database connection pooling
- Add caching for frequently accessed data
- Use pagination for list endpoints
- Monitor query performance and add indexes
- Implement rate limiting for public endpoints
- Use background tasks for long-running operations