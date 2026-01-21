"""fix_existing_kpis_format

Revision ID: d9f7e6a5b4c3
Revises: fa8897f1132c
Create Date: 2026-01-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select
from sqlalchemy import String, Text
import json


# revision identifiers, used by Alembic.
revision = 'd9f7e6a5b4c3'
down_revision = 'fa8897f1132c'
branch_labels = None
depends_on = None


def upgrade():
    """
    Fix existing KPIs in the goals table.
    Converts:
    - Empty strings '' to NULL
    - Invalid JSON to NULL
    - Valid JSON strings to remain unchanged
    """
    # Create a reference to the goals table for data operations
    connection = op.get_bind()

    # Get all goals with kpis that are empty strings or potentially invalid
    result = connection.execute(
        sa.text("SELECT id, kpis FROM goals WHERE kpis IS NOT NULL")
    )

    goals_to_update = []
    for row in result:
        goal_id = row[0]
        kpis = row[1]

        # Check if kpis is an empty string
        if kpis == '':
            goals_to_update.append((goal_id, None))
            continue

        # Check if kpis is valid JSON
        if isinstance(kpis, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(kpis)
                # If it parses successfully and is a list, keep it
                if isinstance(parsed, list):
                    continue
                else:
                    # If it's not a list, set to NULL
                    goals_to_update.append((goal_id, None))
            except (json.JSONDecodeError, ValueError):
                # Invalid JSON, set to NULL
                goals_to_update.append((goal_id, None))

    # Update all goals with invalid kpis
    for goal_id, new_kpis in goals_to_update:
        connection.execute(
            sa.text("UPDATE goals SET kpis = :kpis WHERE id = :id"),
            {"kpis": new_kpis, "id": goal_id}
        )

    if goals_to_update:
        print(f"Fixed {len(goals_to_update)} goals with invalid KPIs format")
    else:
        print("No goals with invalid KPIs found")


def downgrade():
    """
    No downgrade needed for data cleaning migration.
    Cannot restore invalid data that was cleaned up.
    """
    pass
