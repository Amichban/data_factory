"""
Database configuration and session management.

This module contains SQLAlchemy configuration for async database operations,
session management, and database table creation utilities.
"""

import structlog
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

logger = structlog.get_logger()

# SQLAlchemy async engine
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Async session maker
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# Base class for models
Base = declarative_base(metadata=metadata)


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.
    
    Yields:
        AsyncSession: Database session instance
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session error", error=str(e), exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """Create database tables."""
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they're registered
            from app.models import user  # noqa
            from app.models import resistance_event  # noqa
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e), exc_info=True)
        raise


async def drop_tables() -> None:
    """Drop all database tables (useful for testing)."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error("Failed to drop database tables", error=str(e), exc_info=True)
        raise


async def close_db() -> None:
    """Close database engine."""
    try:
        await engine.dispose()
        logger.info("Database engine disposed successfully")
    except Exception as e:
        logger.error("Failed to dispose database engine", error=str(e), exc_info=True)
        raise