"""Add profile_image_path to users

Revision ID: d2628fc28d59
Revises: 3bd8a85daf51
Create Date: 2025-10-08 08:10:45.697811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2628fc28d59'
down_revision: Union[str, None] = '3bd8a85daf51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('profile_image_path', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'profile_image_path')
