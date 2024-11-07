"""
migrations/script.py.mako
----------------------------


Alembic Migration Script Template

This script serves as a template for Alembic migrations. When Alembic auto-generates migration scripts, it uses
this template to structure the content. The generated script then gets saved in the 'versions' directory under 'migrations'.
Each script defines actions to be taken for both 'upgrade' (applying the migration) and 'downgrade' (reverting the migration).

"""

"""remove_checkpoints_table

Revision ID: fd264e716c5d
Revises: af0a5f3e2816
Create Date: 2024-10-28 16:11:58.088012

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import (
    postgresql,
)  # Import additional modules dynamically based on the migration's needs.

# Revision identifiers, used by Alembic to identify the migration script.
revision = "fd264e716c5d"  # The ID of this revision (migration).
down_revision = (
    "af0a5f3e2816"  # The ID of the previous revision. Specifies ordering of migrations.
)
branch_labels = None  # Labels that can group revisions together.
depends_on = None  # If this revision depends on another one, it is referenced here.


# Function to handle the 'upgrade' operation.
# This contains the operations to be performed when moving to this version from the previous version.
def upgrade() -> None:
    op.execute('DROP TABLE IF EXISTS "personaflow".checkpoints')


# Function to handle the 'downgrade' operation.
# This contains the operations to revert the changes introduced in the 'upgrade' function.
def downgrade() -> None:
    pass
