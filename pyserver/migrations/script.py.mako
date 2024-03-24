"""
migrations/script.py.mako
----------------------------


Alembic Migration Script Template

This script serves as a template for Alembic migrations. When Alembic auto-generates migration scripts, it uses
this template to structure the content. The generated script then gets saved in the 'versions' directory under 'migrations'.
Each script defines actions to be taken for both 'upgrade' (applying the migration) and 'downgrade' (reverting the migration).

"""

"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}  # Import additional modules dynamically based on the migration's needs.

# Revision identifiers, used by Alembic to identify the migration script.
revision = ${repr(up_revision)}  # The ID of this revision (migration).
down_revision = ${repr(down_revision)}  # The ID of the previous revision. Specifies ordering of migrations.
branch_labels = ${repr(branch_labels)}  # Labels that can group revisions together.
depends_on = ${repr(depends_on)}  # If this revision depends on another one, it is referenced here.

# Function to handle the 'upgrade' operation.
# This contains the operations to be performed when moving to this version from the previous version.
def upgrade() -> None:
    ${upgrades if upgrades else "pass"}  # Operations to upgrade the database schema.

# Function to handle the 'downgrade' operation.
# This contains the operations to revert the changes introduced in the 'upgrade' function.
def downgrade() -> None:
    ${downgrades if downgrades else "pass"}  # Operations to downgrade the database schema.
