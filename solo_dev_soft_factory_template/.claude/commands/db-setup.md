---
name: db-setup
description: Analyze existing database and generate connection configuration
tools: [Read, Write, Edit, Bash]
---

# Database Setup Assistant

Helps you connect to an existing database, analyze its schema, and generate appropriate models and configuration.

## Process

1. Analyze existing database connection
2. Introspect schema and relationships
3. Generate SQLAlchemy models
4. Create safe migration strategy
5. Set up connection pooling and performance optimizations

## Usage

```bash
/db-setup postgresql://user:pass@host/dbname
```

Or interactively:
```bash
/db-setup
# Will prompt for connection details
```

## What This Command Does

### 1. Schema Analysis
- Connects to the existing database
- Reads all tables, columns, and relationships
- Identifies primary keys, foreign keys, and indexes
- Detects existing naming conventions

### 2. Model Generation
```python
# Generates models like:
class ExistingUsers(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships detected and mapped
    orders = relationship("Orders", back_populates="user")
```

### 3. Safety Configuration
- Sets up read-only models for critical tables
- Creates separate schema for new application tables
- Configures transaction isolation levels
- Sets up connection pooling

### 4. Migration Strategy
```python
# For existing tables - read-only by default
class ExistingCustomers(Base):
    __tablename__ = 'customers'
    __table_args__ = {
        'extend_existing': True,
        'autoload': True,
        'autoload_with': engine
    }

# For new features - new tables with app prefix
class AppUserPreferences(Base):
    __tablename__ = 'app_user_preferences'
    user_id = Column(Integer, ForeignKey('users.id'))
    # New columns for your app
```

### 5. Creates Helper Scripts
- `scripts/test-connection.py` - Verify database connection
- `scripts/backup-db.sh` - Backup existing data
- `scripts/sync-models.py` - Re-sync models with schema changes

## Safety Features

### Read-Only Mode
By default, marks existing tables as read-only:
```python
@event.listens_for(ExistingTable, 'before_insert')
def receive_before_insert(mapper, connection, target):
    raise Exception("Cannot insert into existing table - read-only mode")
```

### Separate Schemas
Creates new tables in a separate schema:
```sql
CREATE SCHEMA IF NOT EXISTS app_schema;
-- All new tables go here
CREATE TABLE app_schema.new_features (...);
```

### Transaction Safety
```python
# Wraps existing table access in read transactions
with db.session.begin_nested():
    existing_data = db.query(ExistingTable).all()
    # Read-only operations
```

## Configuration Options

### Connection Pooling
```python
# Optimized for existing database
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600,   # Recycle connections hourly
)
```

### Performance Optimization
- Configures appropriate index usage
- Sets up query result caching
- Implements lazy loading strategies
- Configures batch fetching

## Integration Patterns

### 1. Side-by-Side Tables
```python
# Existing table (read-only)
class Users(Base):
    __tablename__ = 'users'
    
# Your app's extension table
class AppUserExtensions(Base):
    __tablename__ = 'app_user_extensions'
    user_id = Column(Integer, ForeignKey('users.id'))
    preferences = Column(JSON)
```

### 2. View-Based Access
```sql
CREATE VIEW app_customer_summary AS
SELECT 
    c.id,
    c.name,
    COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;
```

### 3. Materialized Views for Performance
```sql
CREATE MATERIALIZED VIEW app_analytics AS
SELECT ... FROM existing_tables;

-- Refresh periodically
REFRESH MATERIALIZED VIEW app_analytics;
```

## Best Practices

1. **Never modify existing schema directly**
2. **Use database transactions for all operations**
3. **Implement audit logging for data access**
4. **Cache frequently accessed read-only data**
5. **Use connection pooling to prevent exhaustion**
6. **Monitor slow queries and optimize**
7. **Backup before any schema changes**

## Common Scenarios

### E-commerce Integration
```python
# Read from existing products
products = db.query(ExistingProducts).all()

# Write to your tables
new_recommendation = AppProductRecommendations(
    product_id=product.id,
    algorithm='collaborative',
    score=0.95
)
db.session.add(new_recommendation)
```

### User System Extension
```python
# Existing user from legacy system
user = db.query(ExistingUsers).filter_by(email=email).first()

# Your app's user profile
profile = AppUserProfile(
    user_id=user.id,
    avatar_url='...',
    bio='...'
)
```

### Analytics Dashboard
```python
# Read from multiple existing tables
orders = db.query(ExistingOrders).join(ExistingCustomers)

# Store aggregated results
cache.set(f'dashboard:{date}', results, timeout=3600)
```

## Output Files

After running `/db-setup`, you'll have:

1. `apps/api/app/models/existing.py` - Models for existing tables
2. `apps/api/app/models/app_tables.py` - Models for new tables
3. `apps/api/app/config/database.py` - Connection configuration
4. `apps/api/alembic/env.py` - Migration configuration
5. `docs/database-erd.png` - Visual schema diagram
6. `docs/DATABASE_INTEGRATION.md` - Integration guide

## Error Handling

- Connection failures → Suggests firewall/network checks
- Permission errors → Recommends read-only user creation
- Schema conflicts → Proposes namespacing solutions
- Performance issues → Provides optimization suggestions

## Security Considerations

1. **Use separate credentials for read/write**
2. **Implement row-level security where needed**
3. **Audit all data access**
4. **Encrypt sensitive data in transit and at rest**
5. **Use prepared statements to prevent SQL injection**
6. **Implement connection rate limiting**

This command ensures safe integration with existing databases while maintaining clean separation between legacy and new functionality.