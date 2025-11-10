"""
Migration to add urgency field to tasks table
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def run_migration():
    """Add urgency column to tasks table"""

    engine = create_engine(DATABASE_URL)

    print("Adding urgency column to tasks table...")

    try:
        with engine.begin() as connection:
            # First, create the enum type if it doesn't exist
            connection.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskurgency') THEN
                        CREATE TYPE taskurgency AS ENUM ('low', 'medium', 'high', 'urgent');
                    END IF;
                END$$;
            """))

            print("* TaskUrgency enum type created/verified")

            # Add the urgency column with default value
            connection.execute(text("""
                ALTER TABLE tasks
                ADD COLUMN IF NOT EXISTS urgency taskurgency DEFAULT 'medium';
            """))

            print("* Urgency column added to tasks table")

            # Update existing tasks to have medium urgency
            result = connection.execute(text("""
                UPDATE tasks
                SET urgency = 'medium'
                WHERE urgency IS NULL;
            """))

            print(f"* Updated {result.rowcount} existing tasks with default urgency")

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error: Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()