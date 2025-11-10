"""
Database Reset and Recreation Script
WARNING: This will drop all tables and recreate them from scratch
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import Base, engine
from models import *  # Import all models

def reset_database():
    """Drop all tables and recreate from models"""
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print("\nWARNING: This will DELETE ALL DATA in the database!")
    print("=" * 60)

    response = input("\nAre you sure you want to continue? (type 'yes' to confirm): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return

    print("\n1. Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("   ✓ All tables dropped successfully")
    except Exception as e:
        print(f"   ✗ Error dropping tables: {e}")
        return

    print("\n2. Creating all tables from models...")
    try:
        Base.metadata.create_all(bind=engine)
        print("   ✓ All tables created successfully")
    except Exception as e:
        print(f"   ✗ Error creating tables: {e}")
        return

    print("\n3. Verifying table creation...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"   ✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"     - {table}")
    except Exception as e:
        print(f"   ✗ Error verifying tables: {e}")
        return

    print("\n" + "=" * 60)
    print("Database reset completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python create_initial_data.py")
    print("2. Restart your FastAPI server")
    print("=" * 60)

if __name__ == "__main__":
    reset_database()