"""refactor_tasks_to_initiatives_with_approval_workflow

Revision ID: d7f139b94d7f
Revises: d2628fc28d59
Create Date: 2025-11-04 19:05:49.318637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7f139b94d7f'
down_revision: Union[str, None] = 'd2628fc28d59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Refactor tasks to initiatives with new approval workflow
    New workflow: Staff creates → Supervisor approves → Assigned → Started → Completed → Approved
    """

    # Step 1: Drop existing task-related tables (in reverse dependency order)
    op.drop_table('task_extensions')
    op.drop_table('task_documents')
    op.drop_table('task_submissions')
    op.drop_table('task_assignments')
    op.drop_table('tasks')

    # Step 2: Drop old task enums
    op.execute("DROP TYPE IF EXISTS extensionstatus")
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS taskurgency")
    op.execute("DROP TYPE IF EXISTS tasktype")

    # Step 3: Create new initiative enums (drop first if they exist from previous attempts)
    op.execute("DROP TYPE IF EXISTS initiativestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS initiativetype CASCADE")
    op.execute("DROP TYPE IF EXISTS initiativeurgency CASCADE")

    initiative_status = sa.Enum(
        'PENDING_APPROVAL',  # Initial state when staff creates initiative
        'ASSIGNED',          # Supervisor approved and assigned
        'REJECTED',          # Supervisor rejected the initiative
        'STARTED',           # Assignee started working
        'COMPLETED',         # Assignee completed work
        'APPROVED',          # Supervisor reviewed and approved with score
        'OVERDUE',           # Past due date
        name='initiativestatus'
    )
    initiative_status.create(op.get_bind())

    initiative_type = sa.Enum('INDIVIDUAL', 'GROUP', name='initiativetype')
    initiative_type.create(op.get_bind())

    initiative_urgency = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='initiativeurgency')
    initiative_urgency.create(op.get_bind())

    # Extension status enum may still exist, so drop and recreate
    op.execute("DROP TYPE IF EXISTS extensionstatus CASCADE")
    extension_status = sa.Enum('PENDING', 'APPROVED', 'DENIED', name='extensionstatus')
    extension_status.create(op.get_bind())

    # Step 4: Create new initiatives table with approval workflow
    # Note: We reference the enum types by name instead of creating them inline
    op.execute("""
        CREATE TABLE initiatives (
            id UUID PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            type initiativetype NOT NULL,
            urgency initiativeurgency DEFAULT 'MEDIUM',
            due_date TIMESTAMP NOT NULL,
            status initiativestatus DEFAULT 'PENDING_APPROVAL',
            score INTEGER,
            feedback TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            approved_at TIMESTAMP WITH TIME ZONE,
            rejected_at TIMESTAMP WITH TIME ZONE,
            reviewed_at TIMESTAMP WITH TIME ZONE,
            created_by UUID NOT NULL REFERENCES users(id),
            assigned_by UUID REFERENCES users(id),
            team_head_id UUID REFERENCES users(id),
            goal_id UUID REFERENCES goals(id)
        )
    """)
    op.create_index('ix_initiatives_id', 'initiatives', ['id'])
    op.create_index('ix_initiatives_status', 'initiatives', ['status'])
    op.create_index('ix_initiatives_created_by', 'initiatives', ['created_by'])
    op.create_index('ix_initiatives_assigned_by', 'initiatives', ['assigned_by'])

    # Step 5: Create initiative_assignments table
    op.create_table(
        'initiative_assignments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('initiative_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['initiative_id'], ['initiatives.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_initiative_assignments_id', 'initiative_assignments', ['id'])
    op.create_index('ix_initiative_assignments_initiative_user', 'initiative_assignments',
                    ['initiative_id', 'user_id'])

    # Step 6: Create initiative_submissions table
    op.create_table(
        'initiative_submissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('initiative_id', sa.UUID(), nullable=False),
        sa.Column('submitted_by', sa.UUID(), nullable=False),
        sa.Column('report', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['initiative_id'], ['initiatives.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_initiative_submissions_id', 'initiative_submissions', ['id'])
    op.create_index('ix_initiative_submissions_initiative', 'initiative_submissions', ['initiative_id'])

    # Step 7: Create initiative_documents table
    op.create_table(
        'initiative_documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('initiative_id', sa.UUID(), nullable=True),  # Nullable for pre-upload
        sa.Column('uploaded_by', sa.UUID(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['initiative_id'], ['initiatives.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_initiative_documents_id', 'initiative_documents', ['id'])
    op.create_index('ix_initiative_documents_initiative', 'initiative_documents', ['initiative_id'])

    # Step 8: Create initiative_extensions table
    op.execute("""
        CREATE TABLE initiative_extensions (
            id UUID PRIMARY KEY,
            initiative_id UUID NOT NULL REFERENCES initiatives(id) ON DELETE CASCADE,
            requested_by UUID NOT NULL REFERENCES users(id),
            reviewed_by UUID REFERENCES users(id),
            new_due_date TIMESTAMP NOT NULL,
            reason TEXT NOT NULL,
            status extensionstatus DEFAULT 'PENDING',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    op.create_index('ix_initiative_extensions_id', 'initiative_extensions', ['id'])
    op.create_index('ix_initiative_extensions_initiative', 'initiative_extensions', ['initiative_id'])


def downgrade() -> None:
    """
    Revert initiatives back to tasks
    WARNING: This will delete all initiative data!
    """

    # Drop initiative tables
    op.drop_table('initiative_extensions')
    op.drop_table('initiative_documents')
    op.drop_table('initiative_submissions')
    op.drop_table('initiative_assignments')
    op.drop_table('initiatives')

    # Drop initiative enums
    op.execute("DROP TYPE IF EXISTS extensionstatus")
    op.execute("DROP TYPE IF EXISTS initiativestatus")
    op.execute("DROP TYPE IF EXISTS initiativeurgency")
    op.execute("DROP TYPE IF EXISTS initiativetype")

    # Recreate old task enums
    task_status = sa.Enum(
        'PENDING', 'ONGOING', 'COMPLETED', 'PENDING_REVIEW', 'APPROVED', 'OVERDUE',
        name='taskstatus'
    )
    task_status.create(op.get_bind())

    task_type = sa.Enum('INDIVIDUAL', 'GROUP', name='tasktype')
    task_type.create(op.get_bind())

    task_urgency = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='taskurgency')
    task_urgency.create(op.get_bind())

    extension_status = sa.Enum('PENDING', 'APPROVED', 'DENIED', name='extensionstatus')
    extension_status.create(op.get_bind())

    # Recreate old tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('INDIVIDUAL', 'GROUP', name='tasktype'), nullable=False),
        sa.Column('urgency', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='taskurgency'),
                  server_default='MEDIUM'),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ONGOING', 'COMPLETED', 'PENDING_REVIEW',
                                    'APPROVED', 'OVERDUE', name='taskstatus'),
                  server_default='PENDING'),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('team_head_id', sa.UUID(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=True),

        sa.ForeignKeyConstraint(['team_head_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_id', 'tasks', ['id'])

    # Recreate task_assignments
    op.create_table(
        'task_assignments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_assignments_id', 'task_assignments', ['id'])

    # Recreate task_submissions
    op.create_table(
        'task_submissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('submitted_by', sa.UUID(), nullable=False),
        sa.Column('report', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_submissions_id', 'task_submissions', ['id'])

    # Recreate task_documents
    op.create_table(
        'task_documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=True),
        sa.Column('uploaded_by', sa.UUID(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),

        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_documents_id', 'task_documents', ['id'])

    # Recreate task_extensions
    op.create_table(
        'task_extensions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('requested_by', sa.UUID(), nullable=False),
        sa.Column('reviewed_by', sa.UUID(), nullable=True),
        sa.Column('new_due_date', sa.DateTime(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'DENIED', name='extensionstatus'),
                  server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_extensions_id', 'task_extensions', ['id'])
