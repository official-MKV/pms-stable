"""
Clear all review data except users and questions
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost/pms_db"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("Clearing review data...")

        # Clear in order of dependencies
        conn.execute(text("DELETE FROM performance_scores"))
        print("  - Cleared performance_scores")

        conn.execute(text("DELETE FROM review_scores"))
        print("  - Cleared review_scores")

        conn.execute(text("DELETE FROM review_responses"))
        print("  - Cleared review_responses")

        conn.execute(text("DELETE FROM review_assignments"))
        print("  - Cleared review_assignments")

        conn.execute(text("DELETE FROM reviews"))
        print("  - Cleared reviews")

        conn.execute(text("DELETE FROM peer_reviews"))
        print("  - Cleared peer_reviews")

        conn.execute(text("DELETE FROM review_cycle_traits"))
        print("  - Cleared review_cycle_traits")

        conn.execute(text("DELETE FROM review_cycles"))
        print("  - Cleared review_cycles")

        conn.commit()
        print("\n[OK] All review data cleared successfully!")
        print("Users and review questions/traits remain intact.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
