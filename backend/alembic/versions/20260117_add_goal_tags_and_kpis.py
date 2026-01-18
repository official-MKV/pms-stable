"""add goal tags and kpis

Revision ID: 20260117_tags_kpis
Revises:
Create Date: 2026-01-17 21:12:04.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260117_tags_kpis'
down_revision = 'f8a2b1c3d4e5'
branch_labels = None
depends_on = None


def upgrade():
    # Create goal_tags table
    op.create_table('goal_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False, server_default='#6B7280'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_goal_tags_id'), 'goal_tags', ['id'], unique=False)

    # Create goal_tag_assignments association table
    op.create_table('goal_tag_assignments',
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['goal_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('goal_id', 'tag_id')
    )

    # Add kpis column to goals table
    op.add_column('goals', sa.Column('kpis', sa.Text(), nullable=True))

    # Insert default tags
    op.execute("""
        INSERT INTO goal_tags (id, name, color, created_by)
        SELECT
            gen_random_uuid(),
            'Infrastructure',
            '#3B82F6',
            (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng' LIMIT 1)
        WHERE NOT EXISTS (SELECT 1 FROM goal_tags WHERE name = 'Infrastructure')
    """)

    op.execute("""
        INSERT INTO goal_tags (id, name, color, created_by)
        SELECT
            gen_random_uuid(),
            'Strategy',
            '#8B5CF6',
            (SELECT id FROM users WHERE email = 'admin@nigcomsat.gov.ng' LIMIT 1)
        WHERE NOT EXISTS (SELECT 1 FROM goal_tags WHERE name = 'Strategy')
    """)


def downgrade():
    # Remove kpis column
    op.drop_column('goals', 'kpis')

    # Drop association table
    op.drop_table('goal_tag_assignments')

    # Drop goal_tags table
    op.drop_index(op.f('ix_goal_tags_id'), table_name='goal_tags')
    op.drop_table('goal_tags')
