"""increase goal title length

Revision ID: 20260118_title_length
Revises: 20260117_tags_kpis
Create Date: 2026-01-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260118_title_length'
down_revision = '20260117_tags_kpis'
branch_labels = None
depends_on = None


def upgrade():
    # Increase the title column length from 255 to 1000 characters
    op.alter_column('goals', 'title',
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=1000),
                    existing_nullable=False)


def downgrade():
    # Revert back to 255 characters
    op.alter_column('goals', 'title',
                    existing_type=sa.String(length=1000),
                    type_=sa.String(length=255),
                    existing_nullable=False)
