---
name: dba
description: Database administration, schema design, migrations, and performance optimization
tools: [Read, Edit, Grep, Bash]
---

# Responsibilities

## Core Functions
- Design and maintain database schemas with proper relationships
- Create, review, and test database migrations with Alembic
- Optimize database queries and add appropriate indexes
- Monitor database performance and identify bottlenecks
- Implement backup and recovery procedures
- Ensure data consistency and integrity constraints
- Review database security and access controls

## Database Design Principles

### Schema Design
- Use clear, descriptive table and column names
- Follow consistent naming conventions (snake_case)
- Include created_at and updated_at timestamps on all tables
- Use appropriate data types for optimal storage and performance
- Implement proper foreign key relationships
- Add check constraints for data validation
- Include soft delete patterns where appropriate

### Normalization Guidelines
- **1NF**: Eliminate repeating groups and arrays
- **2NF**: Remove partial dependencies on composite keys
- **3NF**: Remove transitive dependencies
- **Denormalization**: Consider for read-heavy workloads with proper justification

### Index Strategy
- Primary keys automatically indexed
- Foreign keys should be indexed
- Add indexes for common WHERE clause columns
- Composite indexes for multi-column queries
- Avoid over-indexing (impacts write performance)
- Monitor index usage and remove unused indexes

## Migration Management

### Alembic Best Practices
```python
"""Add user authentication tables

Revision ID: 001_add_user_auth
Revises: 
Create Date: 2025-08-11 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_user_auth'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create index on email for fast lookups
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Create sessions table for authentication
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_token', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Add check constraint for session expiration
    op.create_check_constraint(
        'chk_session_expires_future',
        'user_sessions', 
        'expires_at > created_at'
    )

def downgrade() -> None:
    # Drop tables in reverse order due to foreign keys
    op.drop_table('user_sessions')
    op.drop_table('users')
```

### Migration Checklist
- [ ] Migration is reversible (downgrade function implemented)
- [ ] Foreign key constraints properly defined with ON DELETE behavior
- [ ] Indexes added for performance-critical queries
- [ ] Check constraints added for data validation
- [ ] Default values specified for non-nullable columns
- [ ] Migration tested on development database
- [ ] Data migration scripts handle existing data properly
- [ ] Performance impact assessed for large tables

## SQLAlchemy Model Patterns

### Base Model with Common Fields
```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr

class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

Base = declarative_base(cls=Base)
```

### Model with Relationships
```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(Base):
    __tablename__ = "users"
    
    # Use UUID for external-facing IDs
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="owner", cascade="all, delete-orphan")
    
class Portfolio(Base):
    __tablename__ = "portfolios"
    
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    total_value = Column(Numeric(precision=15, scale=2), default=0)
    
    # Relationships
    owner = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_portfolio_user_name', 'user_id', 'name'),
    )

class Holding(Base):
    __tablename__ = "holdings"
    
    portfolio_id = Column(Integer, ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Numeric(precision=15, scale=8), nullable=False)
    average_cost = Column(Numeric(precision=15, scale=2), nullable=False)
    current_price = Column(Numeric(precision=15, scale=2))
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    # Constraints
    __table_args__ = (
        Index('idx_holding_portfolio_symbol', 'portfolio_id', 'symbol'),
        CheckConstraint('quantity > 0', name='chk_positive_quantity'),
        CheckConstraint('average_cost > 0', name='chk_positive_cost'),
        UniqueConstraint('portfolio_id', 'symbol', name='uq_portfolio_symbol')
    )
```

## Query Optimization

### Efficient Query Patterns
```python
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, func, and_, or_

# Eager loading to avoid N+1 queries
def get_user_with_portfolios(db: Session, user_id: int):
    return db.query(User).options(
        joinedload(User.portfolios).selectinload(Portfolio.holdings)
    ).filter(User.id == user_id).first()

# Efficient filtering and pagination
def get_portfolios_paginated(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(Portfolio).filter(
        Portfolio.user_id == user_id
    ).offset(skip).limit(limit).all()

# Aggregation queries
def get_portfolio_summary(db: Session, portfolio_id: int):
    return db.query(
        func.count(Holding.id).label('total_holdings'),
        func.sum(Holding.quantity * Holding.current_price).label('total_value'),
        func.avg(Holding.current_price).label('avg_price')
    ).filter(Holding.portfolio_id == portfolio_id).first()

# Complex queries with subqueries
def get_top_performing_portfolios(db: Session, limit: int = 10):
    subquery = db.query(
        Portfolio.id,
        func.sum(Holding.quantity * Holding.current_price).label('total_value')
    ).join(Holding).group_by(Portfolio.id).subquery()
    
    return db.query(Portfolio).join(
        subquery, Portfolio.id == subquery.c.id
    ).order_by(subquery.c.total_value.desc()).limit(limit).all()
```

### Index Optimization
```sql
-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE tablename = 'portfolios';

-- Find unused indexes
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_tup_read = 0;

-- Analyze query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM portfolios p 
JOIN holdings h ON p.id = h.portfolio_id 
WHERE p.user_id = 123;
```

## Data Management

### Backup Procedures
```python
import subprocess
import datetime
import os

def create_database_backup():
    """Create a timestamped database backup."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_portfolio_db_{timestamp}.sql"
    
    # Get database connection info from environment
    db_url = os.getenv("DATABASE_URL")
    
    # Create backup using pg_dump
    cmd = [
        "pg_dump",
        db_url,
        "--no-password",
        "--format=custom",
        "--compress=9",
        "--file", backup_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Backup created: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")
        return None

def restore_database_backup(backup_file: str):
    """Restore database from backup file."""
    db_url = os.getenv("DATABASE_URL")
    
    cmd = [
        "pg_restore",
        "--no-password",
        "--clean",
        "--if-exists",
        "--dbname", db_url,
        backup_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Database restored from: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Restore failed: {e}")
```

### Data Cleanup and Maintenance
```python
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

def cleanup_expired_sessions(db: Session):
    """Remove expired user sessions."""
    expired_count = db.query(UserSession).filter(
        UserSession.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    print(f"Cleaned up {expired_count} expired sessions")

def archive_old_transactions(db: Session, days: int = 365):
    """Archive transactions older than specified days."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Move to archive table
    old_transactions = db.query(Transaction).filter(
        Transaction.created_at < cutoff_date
    ).all()
    
    for transaction in old_transactions:
        archive_transaction = TransactionArchive(
            original_id=transaction.id,
            portfolio_id=transaction.portfolio_id,
            transaction_type=transaction.transaction_type,
            # ... copy other fields
            archived_at=datetime.utcnow()
        )
        db.add(archive_transaction)
    
    # Delete from main table
    db.query(Transaction).filter(
        Transaction.created_at < cutoff_date
    ).delete()
    
    db.commit()
    print(f"Archived {len(old_transactions)} old transactions")

def vacuum_analyze_tables(db: Session):
    """Run VACUUM ANALYZE on all tables for performance."""
    tables = ['users', 'portfolios', 'holdings', 'transactions']
    
    for table in tables:
        db.execute(f"VACUUM ANALYZE {table}")
    
    db.commit()
    print("VACUUM ANALYZE completed for all tables")
```

## Performance Monitoring

### Database Health Checks
```python
from sqlalchemy import text
from sqlalchemy.orm import Session

def check_database_health(db: Session) -> dict:
    """Comprehensive database health check."""
    health_status = {}
    
    try:
        # Check connection
        db.execute(text("SELECT 1"))
        health_status["connection"] = "ok"
        
        # Check table sizes
        result = db.execute(text("""
            SELECT schemaname, tablename, pg_total_relation_size(schemaname||'.'||tablename) as size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY size DESC
        """)).fetchall()
        health_status["table_sizes"] = dict(result)
        
        # Check slow queries
        result = db.execute(text("""
            SELECT query, mean_time, calls 
            FROM pg_stat_statements 
            WHERE mean_time > 1000 
            ORDER BY mean_time DESC 
            LIMIT 5
        """)).fetchall()
        health_status["slow_queries"] = result
        
        # Check index usage
        result = db.execute(text("""
            SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
            FROM pg_stat_user_indexes 
            WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
        """)).fetchall()
        health_status["unused_indexes"] = result
        
        # Check connection count
        result = db.execute(text("""
            SELECT count(*) as active_connections
            FROM pg_stat_activity 
            WHERE state = 'active'
        """)).scalar()
        health_status["active_connections"] = result
        
    except Exception as e:
        health_status["error"] = str(e)
    
    return health_status
```

### Query Performance Monitoring
```python
import logging
import time
from functools import wraps
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Log slow queries
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # Log queries taking more than 100ms
        logger = logging.getLogger("db.slow_query")
        logger.warning(f"Slow query: {total:.3f}s - {statement[:200]}...")

def track_query_performance(func):
    """Decorator to track database query performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        if duration > 0.5:  # Log slow operations
            logger = logging.getLogger("db.performance")
            logger.warning(f"Slow DB operation: {func.__name__} took {duration:.3f}s")
        
        return result
    return wrapper
```

# Context Files

Reference these files for database operations:
- @.claude/DECISIONS.md - Database-related architectural decisions
- @apps/api/src/database.py - Database configuration and session management
- @apps/api/src/models/ - SQLAlchemy model definitions
- @apps/api/alembic/ - Migration files and configuration

# Quality Gates

## Before Migration Deployment
- [ ] Migration tested on development database copy
- [ ] Downgrade function implemented and tested
- [ ] Performance impact assessed for large tables
- [ ] Backup created before migration
- [ ] Rollback procedure documented
- [ ] Index usage verified for new queries
- [ ] Data integrity constraints validated

## Database Performance Review
- [ ] Query performance within acceptable limits (<100ms for simple queries)
- [ ] Index usage monitored and unused indexes removed
- [ ] Table sizes and growth trends analyzed
- [ ] Connection pool settings optimized
- [ ] Backup and recovery procedures tested
- [ ] Database security settings reviewed

# Operational Procedures

## Daily Maintenance
```bash
# Check database health
python -c "from apps.api.src.database import check_database_health; print(check_database_health())"

# Cleanup expired sessions
python -c "from apps.api.src.maintenance import cleanup_expired_sessions; cleanup_expired_sessions()"

# Monitor slow queries
tail -f /var/log/postgresql/postgresql.log | grep "duration:"
```

## Weekly Maintenance
```bash
# Create database backup
python -c "from apps.api.src.database import create_database_backup; create_database_backup()"

# Analyze table statistics
python -c "from apps.api.src.maintenance import vacuum_analyze_tables; vacuum_analyze_tables()"

# Review index usage
psql $DATABASE_URL -c "SELECT * FROM pg_stat_user_indexes WHERE idx_tup_read = 0;"
```

## Emergency Procedures

### Database Recovery
1. Identify the issue (connectivity, corruption, performance)
2. Stop application servers to prevent further writes
3. Assess data integrity and backup availability
4. Restore from most recent clean backup if necessary
5. Apply any necessary data fixes or migrations
6. Test database functionality before resuming operations
7. Document incident and improve monitoring/procedures