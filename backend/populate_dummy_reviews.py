"""
Script to populate dummy review data
Run with: python populate_dummy_reviews.py
"""

import sys
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ReviewAssignment, ReviewQuestion, ReviewCycleTrait, ReviewResponse as ReviewResponseModel
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost/pms_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def populate_dummy_data():
    db = SessionLocal()

    try:
        # Get first incomplete assignment
        assignment = db.query(ReviewAssignment).filter(
            ReviewAssignment.status != 'completed'
        ).first()

        if not assignment:
            print("No incomplete assignments found!")
            return

        print(f"Processing assignment: {assignment.id}")
        print(f"Review type: {assignment.review_type}")
        print(f"Cycle: {assignment.cycle_id}")

        # Get cycle traits
        cycle_traits = db.query(ReviewCycleTrait).filter(
            ReviewCycleTrait.cycle_id == assignment.cycle_id
        ).all()

        trait_ids = [ct.trait_id for ct in cycle_traits]
        print(f"Found {len(trait_ids)} traits for this cycle")

        # Get questions for this assignment
        questions_query = db.query(ReviewQuestion).filter(
            ReviewQuestion.trait_id.in_(trait_ids)
        )

        # Filter by review type
        if assignment.review_type == 'self':
            questions_query = questions_query.filter(ReviewQuestion.applies_to_self == True)
        elif assignment.review_type == 'peer':
            questions_query = questions_query.filter(ReviewQuestion.applies_to_peer == True)
        elif assignment.review_type == 'supervisor':
            questions_query = questions_query.filter(ReviewQuestion.applies_to_supervisor == True)

        questions = questions_query.all()
        print(f"Found {len(questions)} questions")

        if not questions:
            print("No questions found for this assignment!")
            return

        # Insert responses
        responses_added = 0
        for question in questions:
            # Check if response already exists
            existing = db.query(ReviewResponseModel).filter(
                ReviewResponseModel.assignment_id == assignment.id,
                ReviewResponseModel.question_id == question.id
            ).first()

            if not existing:
                # Generate random rating between 3-5 (realistic high performance)
                rating = random.randint(3, 5)

                comments = [
                    "Excellent performance, consistently exceeds expectations.",
                    "Good performance, meets expectations well.",
                    "Satisfactory performance with room for growth.",
                    "Strong contributor to the team.",
                    "Demonstrates good understanding of responsibilities."
                ]

                response = ReviewResponseModel(
                    assignment_id=assignment.id,
                    question_id=question.id,
                    rating=rating,
                    comment=random.choice(comments)
                )

                db.add(response)
                responses_added += 1

        # Mark assignment as completed
        assignment.status = 'completed'
        assignment.completed_at = datetime.now()

        db.commit()

        print(f"[OK] Successfully added {responses_added} responses")
        print(f"[OK] Marked assignment as completed")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("Populating dummy review data...")
    populate_dummy_data()
    print("Done!")
