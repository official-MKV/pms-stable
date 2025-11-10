"""Fix enums for taskstatus and taskurgency

Revision ID: 3bd8a85daf51
Revises: 309b649ccb3b
Create Date: 2025-09-30 11:26:00.831173
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3bd8a85daf51"
down_revision: Union[str, None] = "309b649ccb3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Clean up existing data (make uppercase) ---
    op.execute("UPDATE tasks SET urgency = UPPER(urgency) WHERE urgency IS NOT NULL;")
    op.execute("UPDATE tasks SET status = UPPER(status) WHERE status IS NOT NULL;")

    # --- Drop old enums (if they exist) ---
    op.execute("DROP TYPE IF EXISTS taskurgency CASCADE;")
    op.execute("DROP TYPE IF EXISTS taskstatus CASCADE;")

    # --- Create new enums ---
    op.execute("CREATE TYPE taskurgency AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');")
    op.execute(
        "CREATE TYPE taskstatus AS ENUM ('PENDING', 'ONGOING', 'COMPLETED', 'APPROVED', 'OVERDUE');"
    )

    # --- Rebind urgency column ---
    op.alter_column(
        "tasks",
        "urgency",
        type_=sa.Enum("LOW", "MEDIUM", "HIGH", "URGENT", name="taskurgency"),
        existing_type=sa.VARCHAR(length=20),
        postgresql_using="urgency::text::taskurgency",
        existing_nullable=True,
        server_default="MEDIUM",
    )

    # --- Rebind status column ---
    op.alter_column(
        "tasks",
        "status",
        type_=sa.Enum(
            "PENDING", "ONGOING", "COMPLETED", "APPROVED", "OVERDUE", name="taskstatus"
        ),
        existing_type=sa.VARCHAR(length=20),
        postgresql_using="status::text::taskstatus",
        existing_nullable=False,
    )


def downgrade() -> None:
    # Convert back to VARCHAR in case of rollback
    op.alter_column("tasks", "urgency", type_=sa.VARCHAR(length=20), postgresql_using="urgency::text")
    op.alter_column("tasks", "status", type_=sa.VARCHAR(length=20), postgresql_using="status::text")

    op.execute("DROP TYPE IF EXISTS taskurgency CASCADE;")
    op.execute("DROP TYPE IF EXISTS taskstatus CASCADE;")
