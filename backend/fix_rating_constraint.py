"""Fix rating constraint to allow 1-10 scale"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost/pms_db"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Drop old constraint
        conn.execute(text("ALTER TABLE review_responses DROP CONSTRAINT IF EXISTS valid_rating"))
        # Add new constraint for 1-10 scale
        conn.execute(text("ALTER TABLE review_responses ADD CONSTRAINT valid_rating CHECK (rating >= 1 AND rating <= 10)"))
        conn.commit()
        print("[OK] Updated rating constraint to allow 1-10 scale")
except Exception as e:
    print(f"Error: {e}")
