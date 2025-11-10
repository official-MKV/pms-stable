"""Add INDIVIDUAL to goaltype enum

Revision ID: 6992f5f4979f
Revises: 1edccf6e74f0
Create Date: 2025-11-05 08:43:27.301636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6992f5f4979f'
down_revision: Union[str, None] = '1edccf6e74f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'individual' to the goaltype enum
    op.execute("ALTER TYPE goaltype ADD VALUE IF NOT EXISTS 'individual'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values
    # This would require recreating the enum which is complex
    pass
