#!/usr/bin/env python
"""
Initialize the database for Event Detection System
"""
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

from app.database import init_db, engine
from app.models import events
from sqlalchemy import text

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database
    from app.config import settings
    
    # Extract database name from URL
    db_url = settings.DATABASE_URL
    
    # Check if database exists
    if not database_exists(db_url):
        create_database(db_url)
        print(f"Database created: {db_url}")
    else:
        print(f"Database already exists: {db_url}")

def verify_tables():
    """Verify that all tables were created"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        
        expected_tables = [
            'new_resistance_events',
            'support_and_resistance_master',
            'resistance_features',
            'processing_state'
        ]
        
        print("\nCreated tables:")
        for table in tables:
            status = "✓" if table in expected_tables else "?"
            print(f"  {status} {table}")
        
        missing = set(expected_tables) - set(tables)
        if missing:
            print(f"\nWarning: Missing tables: {missing}")
        else:
            print("\nAll expected tables created successfully!")

if __name__ == "__main__":
    try:
        # Create database if needed
        print("Checking database...")
        create_database_if_not_exists()
        
        # Initialize tables
        print("\nInitializing database schema...")
        init_db()
        
        # Verify creation
        verify_tables()
        
        print("\nDatabase initialization complete!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)