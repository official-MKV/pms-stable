"""
Create a complete review cycle with all assignments filled
This will create realistic review data to test the performance page
"""

import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    ReviewCycle, ReviewCycleTrait, ReviewTrait, ReviewQuestion,
    ReviewAssignment, ReviewResponse as ReviewResponseModel,
    ReviewScore, PerformanceScore, User
)
import uuid

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost/pms_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_complete_cycle():
    db = SessionLocal()

    try:
        print("="*60)
        print("Creating Complete Review Cycle")
        print("="*60)

        # Step 1: Create Review Cycle
        print("\n[1/6] Creating review cycle...")
        cycle = ReviewCycle(
            name="Q4 2024 Performance Review",
            type="quarterly",
            period="Q4-2024",
            start_date=datetime(2024, 10, 1),
            end_date=datetime(2024, 12, 31),
            status="completed",  # Mark as completed
            phase_schedule={
                "setup": {"start": "2024-10-01", "duration": "1_week"},
                "reviews": {"start": "2024-10-08", "duration": "3_weeks"},
                "analysis": {"start": "2024-12-24", "duration": "1_week"}
            },
            buffer_time='1_week',
            components={
                "self_review": True,
                "supervisor_review": True,
                "peer_review": True,
                "peer_count": 3,
                "auto_assign": True
            },
            created_by=db.query(User).first().id  # Use first user as creator
        )
        db.add(cycle)
        db.flush()
        print(f"   [OK] Created cycle: {cycle.name} (ID: {cycle.id})")

        # Step 2: Associate all traits with this cycle
        print("\n[2/6] Adding all company traits to cycle...")
        traits = db.query(ReviewTrait).all()
        for trait in traits:
            cycle_trait = ReviewCycleTrait(
                cycle_id=cycle.id,
                trait_id=trait.id
            )
            db.add(cycle_trait)
        db.flush()
        print(f"   [OK] Added {len(traits)} traits to cycle")

        # Step 3: Create review assignments for all users
        print("\n[3/6] Creating review assignments for all users...")
        users = db.query(User).filter(User.status == 'active').all()
        print(f"   Found {len(users)} active users")

        assignments_created = 0
        for user in users:
            # Self review assignment
            self_assignment = ReviewAssignment(
                cycle_id=cycle.id,
                reviewer_id=user.id,
                reviewee_id=user.id,
                review_type='self',
                status='pending'
            )
            db.add(self_assignment)
            assignments_created += 1

            # Peer review assignments (3 peers per user)
            other_users = [u for u in users if u.id != user.id]
            peers = random.sample(other_users, min(3, len(other_users)))
            for peer in peers:
                peer_assignment = ReviewAssignment(
                    cycle_id=cycle.id,
                    reviewer_id=user.id,
                    reviewee_id=peer.id,
                    review_type='peer',
                    status='pending'
                )
                db.add(peer_assignment)
                assignments_created += 1

            # Supervisor review assignment (simplified - first peer becomes supervisor)
            if other_users:
                supervisor = random.choice(other_users)
                supervisor_assignment = ReviewAssignment(
                    cycle_id=cycle.id,
                    reviewer_id=supervisor.id,
                    reviewee_id=user.id,
                    review_type='supervisor',
                    status='pending'
                )
                db.add(supervisor_assignment)
                assignments_created += 1

        db.flush()
        print(f"   [OK] Created {assignments_created} review assignments")

        # Step 4: Fill all assignments with responses
        print("\n[4/6] Filling all assignments with responses...")
        assignments = db.query(ReviewAssignment).filter(
            ReviewAssignment.cycle_id == cycle.id
        ).all()

        trait_ids = [t.id for t in traits]
        responses_created = 0

        for assignment in assignments:
            # Get questions for this review type
            questions_query = db.query(ReviewQuestion).filter(
                ReviewQuestion.trait_id.in_(trait_ids)
            )

            if assignment.review_type == 'self':
                questions_query = questions_query.filter(ReviewQuestion.applies_to_self == True)
            elif assignment.review_type == 'peer':
                questions_query = questions_query.filter(ReviewQuestion.applies_to_peer == True)
            elif assignment.review_type == 'supervisor':
                questions_query = questions_query.filter(ReviewQuestion.applies_to_supervisor == True)

            questions = questions_query.all()

            for question in questions:
                # Generate realistic ratings (mostly 3-5, some 2s)
                rating = random.choices([2, 3, 4, 5], weights=[10, 20, 40, 30])[0]

                comments = [
                    "Excellent performance, consistently exceeds expectations.",
                    "Good performance, meets expectations well.",
                    "Satisfactory performance with room for growth.",
                    "Strong contributor to the team.",
                    "Demonstrates good understanding of responsibilities.",
                    "Shows initiative and takes ownership.",
                    "Communicates effectively with team members.",
                    "Delivers quality work on time."
                ]

                response = ReviewResponseModel(
                    assignment_id=assignment.id,
                    question_id=question.id,
                    rating=rating,
                    comment=random.choice(comments)
                )
                db.add(response)
                responses_created += 1

            # Mark assignment as completed
            assignment.status = 'completed'
            assignment.completed_at = datetime.now()

        db.flush()
        print(f"   [OK] Created {responses_created} responses")
        print(f"   [OK] Marked all {len(assignments)} assignments as completed")

        # Step 5: Calculate review scores for each user/trait
        print("\n[5/6] Calculating review scores...")
        scores_created = 0

        for user in users:
            for trait in traits:
                # Calculate scores from responses
                self_scores = []
                peer_scores = []
                supervisor_scores = []

                # Get all assignments for this user/trait
                user_assignments = [a for a in assignments if a.reviewee_id == user.id]

                for assignment in user_assignments:
                    # Get responses for this trait
                    responses = db.query(ReviewResponseModel).join(
                        ReviewQuestion, ReviewResponseModel.question_id == ReviewQuestion.id
                    ).filter(
                        ReviewResponseModel.assignment_id == assignment.id,
                        ReviewQuestion.trait_id == trait.id
                    ).all()

                    if responses:
                        avg_rating = sum(r.rating for r in responses) / len(responses)

                        if assignment.review_type == 'self':
                            self_scores.append(avg_rating)
                        elif assignment.review_type == 'peer':
                            peer_scores.append(avg_rating)
                        elif assignment.review_type == 'supervisor':
                            supervisor_scores.append(avg_rating)

                # Calculate averages
                self_score = sum(self_scores) / len(self_scores) if self_scores else None
                peer_score = sum(peer_scores) / len(peer_scores) if peer_scores else None
                supervisor_score = sum(supervisor_scores) / len(supervisor_scores) if supervisor_scores else None

                # Weighted score: 20% self, 30% peer, 50% supervisor
                weighted_score = (
                    (self_score or 0) * 0.2 +
                    (peer_score or 0) * 0.3 +
                    (supervisor_score or 0) * 0.5
                ) if (self_score or peer_score or supervisor_score) else None

                if weighted_score:
                    review_score = ReviewScore(
                        cycle_id=cycle.id,
                        user_id=user.id,
                        trait_id=trait.id,
                        self_score=self_score,
                        peer_score=peer_score,
                        supervisor_score=supervisor_score,
                        weighted_score=weighted_score
                    )
                    db.add(review_score)
                    scores_created += 1

        db.flush()
        print(f"   [OK] Created {scores_created} review scores")

        # Step 6: Calculate overall performance scores
        print("\n[6/6] Calculating performance scores...")
        perf_scores_created = 0

        for user in users:
            # Get all review scores for this user
            user_scores = db.query(ReviewScore).filter(
                ReviewScore.cycle_id == cycle.id,
                ReviewScore.user_id == user.id
            ).all()

            if user_scores:
                overall_score = sum(float(s.weighted_score) for s in user_scores) / len(user_scores)

                # Normalize to 1-10 scale
                review_score = (overall_score / 5) * 10

                # Task and goal scores (placeholder - would come from actual data)
                task_score = random.uniform(7.0, 9.0)
                goal_score = random.uniform(7.0, 9.0)

                # Final rating: 50% reviews, 30% tasks, 20% goals
                final_rating = (
                    review_score * 0.5 +
                    task_score * 0.3 +
                    goal_score * 0.2
                )

                perf_score = PerformanceScore(
                    cycle_id=cycle.id,
                    user_id=user.id,
                    task_performance_score=task_score,
                    review_performance_score=review_score,
                    overall_performance_score=final_rating
                )
                db.add(perf_score)
                perf_scores_created += 1

        db.commit()
        print(f"   [OK] Created {perf_scores_created} performance scores")

        print("\n" + "="*60)
        print("[OK] COMPLETE! Summary:")
        print("="*60)
        print(f"  Cycle: {cycle.name}")
        print(f"  Users: {len(users)}")
        print(f"  Traits: {len(traits)}")
        print(f"  Assignments: {assignments_created}")
        print(f"  Responses: {responses_created}")
        print(f"  Review Scores: {scores_created}")
        print(f"  Performance Scores: {perf_scores_created}")
        print("\nYou can now view the performance data in the dashboard!")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_complete_cycle()
