"""
migrations/script.py.mako
----------------------------


Alembic Migration Script Template

This script serves as a template for Alembic migrations. When Alembic auto-generates migration scripts, it uses
this template to structure the content. The generated script then gets saved in the 'versions' directory under 'migrations'.
Each script defines actions to be taken for both 'upgrade' (applying the migration) and 'downgrade' (reverting the migration).

"""

"""init

Revision ID: 42cb7889f092
Revises:
Create Date: 2024-03-02 16:24:40.170953

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import (
    postgresql,
)  # Import additional modules dynamically based on the migration's needs.

# Revision identifiers, used by Alembic to identify the migration script.
revision = "42cb7889f092"  # The ID of this revision (migration).
down_revision = (
    None  # The ID of the previous revision. Specifies ordering of migrations.
)
branch_labels = None  # Labels that can group revisions together.
depends_on = None  # If this revision depends on another one, it is referenced here.


# Function to handle the 'upgrade' operation.
# This contains the operations to be performed when moving to this version from the previous version.
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "assistants",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="A unique identifier for the assistant. It's a UUID type and is automatically generated by the database.",
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=True,
            comment="The ID of the user who created the assistant.",
        ),
        sa.Column(
            "name", sa.String(), nullable=False, comment="The name of the assistant."
        ),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="The assistant config, containing specific configuration parameters.",
        ),
        sa.Column(
            "public",
            sa.Boolean(),
            nullable=False,
            comment="Whether the assistant is public (i.e., customer-facing) or internal (i.e., used by staff or developers).",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Created date",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Last updated date",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pyserver",
    )
    op.create_table(
        "messages",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="A unique identifier for the message. It's a UUID type and is automatically generated by the database.",
        ),
        sa.Column(
            "thread_id",
            sa.String(),
            nullable=False,
            comment="The ID of the thread to which this message belongs.",
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=False,
            comment="The ID of the user who sent the message.",
        ),
        sa.Column(
            "assistant_id",
            sa.String(),
            nullable=False,
            comment="The ID of the assistant that processed the message.",
        ),
        sa.Column(
            "content",
            sa.String(),
            nullable=False,
            comment="The content of the message.",
        ),
        sa.Column(
            "type",
            sa.String(),
            nullable=False,
            comment="The type of message (e.g., text, image, etc.).",
        ),
        sa.Column(
            "additional_kwargs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Additional metadata associated with the message.",
        ),
        sa.Column(
            "example",
            sa.Boolean(),
            nullable=True,
            comment="Indicates whether the message is an example message for training or demonstration purposes.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Created date",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Last updated date",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pyserver",
    )
    op.create_table(
        "request_logs",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="A unique identifier for the log entry. It's a UUID type and is automatically generated by the database.",
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="The time when the log entry was created. Defaults to the current time.",
        ),
        sa.Column(
            "host",
            sa.String(),
            nullable=True,
            comment="The host (i.e., IP address) from which the request originated.",
        ),
        sa.Column(
            "request_id",
            sa.String(),
            nullable=True,
            comment="An identifier for the request, used for correlating logs.",
        ),
        sa.Column(
            "endpoint",
            sa.String(),
            nullable=True,
            comment="The API endpoint that was accessed.",
        ),
        sa.Column(
            "method",
            sa.String(),
            nullable=True,
            comment="The HTTP method (e.g., GET, POST) used for the request.",
        ),
        sa.Column(
            "headers",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="The HTTP headers associated with the request.",
        ),
        sa.Column(
            "query_parameters",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="The query parameters from the request URL.",
        ),
        sa.Column(
            "request_body",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="The body of the request, stored as JSON.",
        ),
        sa.Column(
            "response_body",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="The body of the response, stored as JSON.",
        ),
        sa.Column(
            "status_code",
            sa.Integer(),
            nullable=True,
            comment="The HTTP status code returned by the API for the request.",
        ),
        sa.Column(
            "response_time",
            sa.Float(),
            nullable=True,
            comment="The time it took for the API to process the request.",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pyserver",
    )
    op.create_table(
        "threads",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="A unique identifier for the thread. It's a UUID type and is automatically generated by the database.",
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=False,
            comment="The ID of the user who initiated the thread.",
        ),
        sa.Column(
            "assistant_id",
            sa.String(),
            nullable=True,
            comment="The ID of the assistant that is associated with the thread.",
        ),
        sa.Column(
            "name", sa.String(), nullable=True, comment="The title of the thread."
        ),
        sa.Column(
            "additional_kwargs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Additional metadata associated with the thread.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Created date",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Last updated date",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pyserver",
    )
    op.create_index(
        op.f("ix_pyserver_threads_user_id"),
        "threads",
        ["user_id"],
        unique=False,
        schema="pyserver",
    )
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="A unique identifier for the user. It's a UUID type and is automatically generated by the database.",
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=False,
            comment="A unique identifier for the user, used for tracking and referencing purposes so as to not expose the internal db user ID and allow for correlating the user with external systems.",
        ),
        sa.Column(
            "username",
            sa.String(),
            nullable=True,
            comment="The username chosen by the user. It's a string type and is expected to be unique across the userbase.",
        ),
        sa.Column(
            "password",
            sa.String(),
            nullable=True,
            comment="The hashed password associated with the user's account.",
        ),
        sa.Column(
            "email",
            sa.String(),
            nullable=True,
            comment="The email address associated with the user's account. It's a string type and is expected to be unique across the userbase.",
        ),
        sa.Column(
            "first_name",
            sa.String(),
            nullable=True,
            comment="The first name of the user.",
        ),
        sa.Column(
            "last_name",
            sa.String(),
            nullable=True,
            comment="The last name of the user.",
        ),
        sa.Column(
            "additional_kwargs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Additional metadata associated with the user.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Created date",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Last updated date",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pyserver",
    )
    op.create_index(
        op.f("ix_pyserver_users_user_id"),
        "users",
        ["user_id"],
        unique=True,
        schema="pyserver",
    )
    # ### end Alembic commands ###  # Operations to upgrade the database schema.


# Function to handle the 'downgrade' operation.
# This contains the operations to revert the changes introduced in the 'upgrade' function.
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_pyserver_users_user_id"), table_name="users", schema="pyserver"
    )
    op.drop_table("users", schema="pyserver")
    op.drop_index(
        op.f("ix_pyserver_threads_user_id"), table_name="threads", schema="pyserver"
    )
    op.drop_table("threads", schema="pyserver")
    op.drop_table("request_logs", schema="pyserver")
    op.drop_table("messages", schema="pyserver")
    op.drop_index(
        op.f("ix_pyserver_assistants_name"), table_name="assistants", schema="pyserver"
    )
    op.drop_table("assistants", schema="pyserver")
    # ### end Alembic commands ###  # Operations to downgrade the database schema.
