#!/usr/bin/env python3
"""
Migration script to split the 'name' column into separate first_name, last_name, and middle_name columns
and convert level from string to integer.

This script should be run ONCE to migrate existing data before deploying the new schema.

Usage:
    python migrate_user_names.py

Requirements:
    - Backup your database before running this script
    - Ensure the database is not in active use during migration
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_user_names():
    """Migrate user name fields from single 'name' to separate first_name, last_name, middle_name"""

    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            logger.info("Starting user name migration...")

            # Step 1: Add new columns
            logger.info("Adding new name columns...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
                ADD COLUMN IF NOT EXISTS last_name VARCHAR(100),
                ADD COLUMN IF NOT EXISTS middle_name VARCHAR(100)
            """))

            # Step 2: Migrate existing data
            logger.info("Migrating existing name data...")

            # Get all existing users with their names
            result = conn.execute(text("SELECT id, name FROM users WHERE name IS NOT NULL"))
            users = result.fetchall()

            logger.info(f"Found {len(users)} users to migrate")

            for user_id, full_name in users:
                if not full_name:
                    continue

                # Split the name into parts
                name_parts = full_name.strip().split()

                if len(name_parts) == 1:
                    # Only one name - treat as first name
                    first_name = name_parts[0]
                    last_name = name_parts[0]  # Fallback to same name
                    middle_name = None
                elif len(name_parts) == 2:
                    # First and last name
                    first_name = name_parts[0]
                    last_name = name_parts[1]
                    middle_name = None
                else:
                    # First, middle(s), and last name
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
                    middle_name = " ".join(name_parts[1:-1])

                # Update the user record
                conn.execute(text("""
                    UPDATE users
                    SET first_name = :first_name,
                        last_name = :last_name,
                        middle_name = :middle_name
                    WHERE id = :user_id
                """), {
                    'first_name': first_name,
                    'last_name': last_name,
                    'middle_name': middle_name,
                    'user_id': user_id
                })

                logger.info(f"Migrated user {user_id}: '{full_name}' -> first: '{first_name}', middle: '{middle_name}', last: '{last_name}'")

            # Step 3: Set NOT NULL constraints on required fields
            logger.info("Setting NOT NULL constraints...")
            conn.execute(text("UPDATE users SET first_name = 'Unknown' WHERE first_name IS NULL"))
            conn.execute(text("UPDATE users SET last_name = 'Unknown' WHERE last_name IS NULL"))

            conn.execute(text("ALTER TABLE users ALTER COLUMN first_name SET NOT NULL"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN last_name SET NOT NULL"))

            # Step 4: Migrate level column from string to integer
            logger.info("Migrating level column...")

            # Add temporary integer column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS level_temp INTEGER"))

            # Try to convert existing level values to integers
            result = conn.execute(text("SELECT id, level FROM users WHERE level IS NOT NULL"))
            level_users = result.fetchall()

            for user_id, level_str in level_users:
                try:
                    # Try to extract integer from string
                    if level_str and level_str.strip():
                        # Look for digit patterns
                        import re
                        numbers = re.findall(r'\d+', str(level_str))
                        if numbers:
                            level_int = int(numbers[0])
                            # Validate range (1-17 for civil service)
                            if 1 <= level_int <= 17:
                                conn.execute(text("""
                                    UPDATE users SET level_temp = :level_int WHERE id = :user_id
                                """), {'level_int': level_int, 'user_id': user_id})
                            else:
                                logger.warning(f"User {user_id}: level {level_int} out of range (1-17), setting to NULL")
                        else:
                            logger.warning(f"User {user_id}: could not extract integer from level '{level_str}'")
                except Exception as e:
                    logger.warning(f"User {user_id}: error converting level '{level_str}': {e}")

            # Drop old level column and rename temp column
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS level"))
            conn.execute(text("ALTER TABLE users RENAME COLUMN level_temp TO level"))

            # Step 5: Clean up - we keep the old 'name' column for now for backward compatibility
            # You can drop it later after confirming the migration worked:
            # conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS name"))

            logger.info("Migration completed successfully!")
            logger.info("The old 'name' column has been kept for backward compatibility.")
            logger.info("You can drop it manually later with: ALTER TABLE users DROP COLUMN name;")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

def rollback_migration():
    """Rollback the migration (restore from backup is recommended instead)"""
    logger.warning("Rollback function - USE WITH CAUTION!")
    logger.warning("It's recommended to restore from a database backup instead")

    # This is a basic rollback - restore from backup is better
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        # Remove the new columns
        conn.execute(text("""
            ALTER TABLE users
            DROP COLUMN IF EXISTS first_name,
            DROP COLUMN IF EXISTS last_name,
            DROP COLUMN IF EXISTS middle_name
        """))

        # Convert level back to varchar
        conn.execute(text("ALTER TABLE users ADD COLUMN level_temp VARCHAR(100)"))
        conn.execute(text("UPDATE users SET level_temp = CAST(level AS VARCHAR) WHERE level IS NOT NULL"))
        conn.execute(text("ALTER TABLE users DROP COLUMN level"))
        conn.execute(text("ALTER TABLE users RENAME COLUMN level_temp TO level"))

        logger.info("Rollback completed")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        migrate_user_names()