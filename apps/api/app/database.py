"""
Database configuration for Event Detection System
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with all tables"""
    # Import all models to ensure they're registered
    from app.models import events
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def drop_all_tables():
    """Drop all tables - use with caution!"""
    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped!")