#!/usr/bin/env python3
"""
Populate database with review and performance data for demo
Run this script to create realistic performance data for all employees
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from models import (
    User, ReviewCycle, ReviewTrait, ReviewQuestion, ReviewCycleTrait,
    ReviewAssignment, Review, ReviewScore, ReviewResponse, Task, TaskStatus,
    TraitScopeType, ReviewCycleStatus, UserStatus
)
import uuid
import random

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost/pms_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def populate_performance_data():
    db = SessionLocal()
    try:
        print("[*] Starting database population for performance demo...")

        # Get all active users
        users = db.query(User).filter(User.status == UserStatus.ACTIVE).all()
        print(f"[OK] Found {len(users)} active users")

        # 1. Create Global Review Traits
        print("\n[*] Creating global review traits...")
        traits_data = [
            {"name": "Communication", "description": "Ability to communicate effectively with team members and stakeholders"},
            {"name": "Leadership", "description": "Demonstrates leadership qualities and ability to guide others"},
            {"name": "Technical Skills", "description": "Proficiency in technical areas relevant to the role"},
            {"name": "Teamwork", "description": "Collaborates effectively with team members"},
            {"name": "Problem Solving", "description": "Ability to identify and solve complex problems"},
            {"name": "Initiative", "description": "Takes proactive steps to improve processes and outcomes"},
            {"name": "Quality of Work", "description": "Consistently delivers high-quality work"},
            {"name": "Time Management", "description": "Manages time effectively and meets deadlines"}
        ]

        traits = []
        for i, trait_data in enumerate(traits_data):
            # Check if trait already exists
            existing = db.query(ReviewTrait).filter(
                ReviewTrait.name == trait_data["name"],
                ReviewTrait.scope_type == TraitScopeType.GLOBAL
            ).first()

            if existing:
                traits.append(existing)
                print(f"  - Using existing trait: {trait_data['name']}")
            else:
                trait = ReviewTrait(
                    name=trait_data["name"],
                    description=trait_data["description"],
                    scope_type=TraitScopeType.GLOBAL,
                    display_order=i + 1,
                    is_active=True,
                    created_by=users[0].id
                )
                db.add(trait)
                db.flush()
                traits.append(trait)
                print(f"  [OK] Created trait: {trait_data['name']}")

        db.commit()

        # 2. Create Review Questions for each trait
        print("\n[*] Creating review questions...")
        for trait in traits:
            # Check if questions already exist for this trait
            existing_questions = db.query(ReviewQuestion).filter(
                ReviewQuestion.trait_id == trait.id
            ).count()

            if existing_questions > 0:
                print(f"  - Trait '{trait.name}' already has {existing_questions} questions")
                continue

            questions = [
                f"How would you rate this person's {trait.name.lower()}?",
                f"Provide specific examples of {trait.name.lower()} demonstrated.",
                f"What improvements could be made in {trait.name.lower()}?"
            ]

            for q_text in questions:
                question = ReviewQuestion(
                    trait_id=trait.id,
                    question_text=q_text,
                    applies_to_self=True,
                    applies_to_peer=True,
                    applies_to_supervisor=True,
                    is_active=True,
                    created_by=users[0].id
                )
                db.add(question)

            print(f"  [OK] Created 3 questions for trait: {trait.name}")

        db.commit()

        # 3. Create Review Cycles
        print("\n[*] Creating review cycles...")

        # Q1 2024 Cycle
        q1_cycle = db.query(ReviewCycle).filter(
            ReviewCycle.name == "Q1 2024 Performance Review"
        ).first()

        if not q1_cycle:
            q1_cycle = ReviewCycle(
                name="Q1 2024 Performance Review",
                type="quarterly",
                period="Q1-2024",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 3, 31),
                status=ReviewCycleStatus.COMPLETED,
                participants_count=len(users),
                completion_rate=85.0,
                created_by=users[0].id
            )
            db.add(q1_cycle)
            db.flush()
            print("  [OK] Created Q1 2024 cycle")
        else:
            print("  - Using existing Q1 2024 cycle")

        # Current Q4 2024 Cycle
        q4_cycle = db.query(ReviewCycle).filter(
            ReviewCycle.name == "Q4 2024 Performance Review"
        ).first()

        if not q4_cycle:
            q4_cycle = ReviewCycle(
                name="Q4 2024 Performance Review",
                type="quarterly",
                period="Q4-2024",
                start_date=datetime(2024, 10, 1),
                end_date=datetime(2024, 12, 31),
                status=ReviewCycleStatus.ACTIVE,
                participants_count=len(users),
                completion_rate=45.0,
                created_by=users[0].id
            )
            db.add(q4_cycle)
            db.flush()
            print("  [OK] Created Q4 2024 cycle")
        else:
            print("  - Using existing Q4 2024 cycle")

        db.commit()

        # 4. Link Traits to Cycles
        print("\n[*] Linking traits to review cycles...")
        for cycle in [q1_cycle, q4_cycle]:
            for trait in traits:
                existing_link = db.query(ReviewCycleTrait).filter(
                    ReviewCycleTrait.cycle_id == cycle.id,
                    ReviewCycleTrait.trait_id == trait.id
                ).first()

                if not existing_link:
                    link = ReviewCycleTrait(
                        cycle_id=cycle.id,
                        trait_id=trait.id,
                        is_active=True
                    )
                    db.add(link)

            print(f"  [OK] Linked {len(traits)} traits to {cycle.name}")

        db.commit()

        # 5. Create Review Assignments and Reviews (for Q1 - completed)
        print("\n[*] Creating review assignments and reviews for Q1 2024...")
        review_count = 0

        for user in users[:min(10, len(users))]:  # Create reviews for first 10 users
            # Check if assignment already exists
            existing = db.query(ReviewAssignment).filter(
                ReviewAssignment.cycle_id == q1_cycle.id,
                ReviewAssignment.reviewee_id == user.id,
                ReviewAssignment.review_type == 'self'
            ).first()

            if existing:
                print(f"  - User {user.name} already has Q1 review")
                continue

            # Create self-review assignment
            assignment = ReviewAssignment(
                cycle_id=q1_cycle.id,
                reviewer_id=user.id,
                reviewee_id=user.id,
                review_type='self',
                status='completed',
                completed_at=datetime(2024, 3, 25) + timedelta(days=random.randint(0, 5))
            )
            db.add(assignment)
            db.flush()

            # Create review
            review = Review(
                cycle_id=q1_cycle.id,
                reviewer_id=user.id,
                reviewee_id=user.id,
                type='self',
                status='submitted',
                submitted_at=assignment.completed_at
            )
            db.add(review)
            db.flush()

            # Create scores for each trait
            for trait in traits:
                # Check if score already exists
                existing_score = db.query(ReviewScore).filter(
                    ReviewScore.cycle_id == q1_cycle.id,
                    ReviewScore.user_id == user.id,
                    ReviewScore.trait_id == trait.id
                ).first()

                if not existing_score:
                    # Random score between 3.0 and 5.0 with some variation
                    base_score = random.uniform(3.0, 5.0)
                    score = round(base_score, 1)

                    review_score = ReviewScore(
                        cycle_id=q1_cycle.id,
                        user_id=user.id,
                        trait_id=trait.id,
                        self_score=score,
                        weighted_score=score
                    )
                    db.add(review_score)

            review_count += 1
            print(f"  [OK] Created review for {user.name}")

        db.commit()
        print(f"[OK] Created {review_count} completed reviews for Q1 2024")

        # 6. Create Tasks with Scores for Performance Data
        print("\n[*] Creating completed tasks with scores...")
        task_count = 0

        task_titles = [
            "Complete Monthly Report",
            "Update System Documentation",
            "Code Review for Feature X",
            "Client Presentation Preparation",
            "Data Analysis Project",
            "Team Training Session",
            "Process Improvement Initiative",
            "Quality Assurance Testing",
            "Project Planning Session",
            "Technical Research Report"
        ]

        for user in users[:min(10, len(users))]:
            # Create 5-8 completed tasks per user with random scores
            num_tasks = random.randint(5, 8)

            for i in range(num_tasks):
                title = random.choice(task_titles)

                # Create task with approved status and score
                task = Task(
                    title=f"{title} - {user.first_name}",
                    description=f"Task assigned to {user.name}",
                    type="individual",
                    status=TaskStatus.APPROVED,
                    due_date=datetime.now() - timedelta(days=random.randint(30, 90)),
                    score=random.randint(6, 10),  # Score between 6 and 10
                    feedback=random.choice([
                        "Excellent work, well done!",
                        "Good job, met expectations",
                        "Outstanding performance",
                        "Very good, minor improvements needed",
                        "Satisfactory completion"
                    ]),
                    created_by=users[0].id,
                    reviewed_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.add(task)
                db.flush()

                # Create task assignment
                from models import TaskAssignment
                assignment = TaskAssignment(
                    task_id=task.id,
                    user_id=user.id
                )
                db.add(assignment)

                task_count += 1

            print(f"  [OK] Created {num_tasks} tasks for {user.name}")

        db.commit()
        print(f"[OK] Created {task_count} completed tasks with scores")

        # 7. Summary
        print("\n" + "="*60)
        print("[SUCCESS] DATABASE POPULATION COMPLETE!")
        print("="*60)
        print(f"[*] Summary:")
        print(f"  - Review Traits: {len(traits)}")
        print(f"  - Review Questions: {len(traits) * 3}")
        print(f"  - Review Cycles: 2 (Q1 & Q4 2024)")
        print(f"  - Completed Reviews: {review_count}")
        print(f"  - Completed Tasks with Scores: {task_count}")
        print(f"  - Users with Performance Data: {min(10, len(users))}")
        print("\n[*] Your performance data is ready for the demo!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = populate_performance_data()
    sys.exit(0 if success else 1)
