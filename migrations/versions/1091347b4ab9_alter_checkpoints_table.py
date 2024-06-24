"""
migrations/script.py.mako
----------------------------


Alembic Migration Script Template

This script serves as a template for Alembic migrations. When Alembic auto-generates migration scripts, it uses
this template to structure the content. The generated script then gets saved in the 'versions' directory under 'migrations'.
Each script defines actions to be taken for both 'upgrade' (applying the migration) and 'downgrade' (reverting the migration).

"""

"""Alter checkpoints table

Revision ID: 1091347b4ab9
Revises: e1338e81c83d
Create Date: 2024-06-23 13:00:52.486715

"""
from alembic import op
import sqlalchemy as sa

# Import additional modules dynamically based on the migration's needs.

# Revision identifiers, used by Alembic to identify the migration script.
revision = "1091347b4ab9"  # The ID of this revision (migration).
down_revision = (
    "e1338e81c83d"  # The ID of the previous revision. Specifies ordering of migrations.
)
branch_labels = None  # Labels that can group revisions together.
depends_on = None  # If this revision depends on another one, it is referenced here.


def upgrade() -> None:
    # Add new columns
    op.add_column(
        "checkpoints",
        sa.Column("thread_ts", sa.DateTime(timezone=True), nullable=True),
        schema="personaflow",
    )
    op.add_column(
        "checkpoints",
        sa.Column("parent_ts", sa.DateTime(timezone=True), nullable=True),
        schema="personaflow",
    )

    # Update existing rows to set thread_ts
    op.execute(
        "UPDATE personaflow.checkpoints SET thread_ts = CURRENT_TIMESTAMP AT TIME ZONE 'UTC' WHERE thread_ts IS NULL"
    )

    # Drop the existing index on thread_id
    op.drop_index(
        "ix_personaflow_checkpoints_thread_id",
        table_name="checkpoints",
        schema="personaflow",
    )

    # Drop the existing primary key
    op.drop_constraint(
        "checkpoints_pkey", "checkpoints", schema="personaflow", type_="primary"
    )

    # Add new primary key
    op.create_primary_key(
        "checkpoints_pkey",
        "checkpoints",
        ["thread_id", "thread_ts"],
        schema="personaflow",
    )

    # Make thread_ts not nullable after setting values
    op.alter_column("checkpoints", "thread_ts", nullable=False, schema="personaflow")

    # Make user_id nullable
    op.alter_column("checkpoints", "user_id", nullable=True, schema="personaflow")


def downgrade() -> None:
    # Make user_id not nullable again
    op.alter_column("checkpoints", "user_id", nullable=False, schema="personaflow")

    # Drop the new primary key
    op.drop_constraint(
        "checkpoints_pkey", "checkpoints", schema="personaflow", type_="primary"
    )

    # Recreate the original primary key
    op.create_primary_key(
        "checkpoints_pkey", "checkpoints", ["id"], schema="personaflow"
    )

    # Recreate the index on thread_id
    op.create_index(
        "ix_personaflow_checkpoints_thread_id",
        "checkpoints",
        ["thread_id"],
        unique=False,
        schema="personaflow",
    )

    # Drop the new columns
    op.drop_column("checkpoints", "thread_ts", schema="personaflow")
    op.drop_column("checkpoints", "parent_ts", schema="personaflow")
