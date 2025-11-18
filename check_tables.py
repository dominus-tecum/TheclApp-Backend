#!/usr/bin/env python3
"""
Script to check if abdominal and diabetes progress tables exist
and verify their structure - SQLite Version
"""

import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect, text
from app.database import engine, Base, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables_exist():
    """Check if the required tables exist in the database"""
    try:
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        print("🔍 CHECKING DATABASE TABLES")
        print("=" * 50)
        
        # Check for our specific tables
        required_tables = {
            'abdominal_progress_entries': False,
            'diabetes_progress_entries': False
        }
        
        print("📊 All tables in database:")
        for table in sorted(all_tables):
            exists = table in required_tables
            status = "✅" if exists else "  "
            print(f"   {status} {table}")
            if exists:
                required_tables[table] = True
        
        print("\n🎯 REQUIRED TABLES STATUS:")
        for table, exists in required_tables.items():
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"   {status}: {table}")
        
        return all(required_tables.values())
        
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False

def check_table_structure():
    """Check the structure of our tables"""
    try:
        inspector = inspect(engine)
        
        print("\n🔧 TABLE STRUCTURES")
        print("=" * 50)
        
        tables_to_check = ['abdominal_progress_entries', 'diabetes_progress_entries']
        
        for table_name in tables_to_check:
            if table_name in inspector.get_table_names():
                print(f"\n📋 Table: {table_name}")
                print("-" * 30)
                columns = inspector.get_columns(table_name)
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    primary_key = " 🔑" if col.get('primary_key', False) else ""
                    print(f"   {col['name']:20} {str(col['type']):15} {nullable:10}{primary_key}")
            else:
                print(f"\n❌ Table {table_name} not found!")
                
    except Exception as e:
        logger.error(f"Error checking table structure: {e}")

def test_connection():
    """Test database connection - SQLite version"""
    try:
        with engine.connect() as conn:
            # SQLite doesn't have version(), use a simple query instead
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            print(f"\n🗄️  Database connected: SQLite")
            print(f"   Found {len(tables)} tables in database")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def create_missing_tables():
    """Create missing tables if they don't exist"""
    try:
        print("\n🔄 ATTEMPTING TO CREATE MISSING TABLES...")
        
        # Import the models to ensure they're registered with Base
        try:
            from app.health_progress.abdominal.models import AbdominalProgressEntry
            from app.health_progress.diabetes.models import DiabetesProgressEntry
            print("✅ Successfully imported model classes")
        except ImportError as e:
            print(f"❌ Error importing models: {e}")
            return False
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables creation attempted")
        
        # Verify creation
        return check_tables_exist()
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def check_sqlite_file():
    """Check SQLite database file"""
    try:
        from app.database import SQLALCHEMY_DATABASE_URL
        print(f"\n💾 Database URL: {SQLALCHEMY_DATABASE_URL}")
        
        # Extract file path from SQLite URL
        if SQLALCHEMY_DATABASE_URL.startswith('sqlite:///'):
            db_file = SQLALCHEMY_DATABASE_URL.replace('sqlite:///', '')
            if os.path.exists(db_file):
                file_size = os.path.getsize(db_file)
                print(f"   Database file: {db_file}")
                print(f"   File size: {file_size} bytes")
                return True
            else:
                print(f"❌ Database file not found: {db_file}")
                return False
        else:
            print(f"   Using in-memory SQLite database")
            return True
    except Exception as e:
        print(f"❌ Error checking database file: {e}")
        return False

def main():
    """Main function to run all checks"""
    print("🚀 STARTING DATABASE TABLE CHECK (SQLite)")
    print("=" * 50)
    
    # Check SQLite database file
    check_sqlite_file()
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot connect to database. Exiting.")
        return
    
    # Check if tables exist
    tables_exist = check_tables_exist()
    
    # Show table structures
    check_table_structure()
    
    if not tables_exist:
        print("\n❌ Some required tables are missing!")
        create_tables = input("Create missing tables? (y/n): ").lower().strip()
        if create_tables == 'y':
            if create_missing_tables():
                print("✅ Tables created successfully!")
            else:
                print("❌ Failed to create tables")
        else:
            print("⚠️  Tables not created. API will fail when saving data.")
    else:
        print("\n🎉 All required tables exist! API is ready to accept data.")
    
    print("\n" + "=" * 50)
    print("✅ DATABASE CHECK COMPLETE")

if __name__ == "__main__":
    main()