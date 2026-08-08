"""introduce sessions table, decouple from refresh_tokens

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-01

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)

    with op.batch_alter_table("refresh_tokens") as batch_op:
        batch_op.drop_column("ip_address")
        batch_op.drop_column("user_agent")
        batch_op.add_column(sa.Column("session_id", sa.Uuid(), nullable=True))
        batch_op.create_index("ix_refresh_tokens_session_id", ["session_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_refresh_tokens_session_id", "sessions", ["session_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("refresh_tokens") as batch_op:
        batch_op.drop_constraint("fk_refresh_tokens_session_id", type_="foreignkey")
        batch_op.drop_index("ix_refresh_tokens_session_id")
        batch_op.drop_column("session_id")
        batch_op.add_column(sa.Column("user_agent", sa.String(length=512), nullable=True))
        batch_op.add_column(sa.Column("ip_address", sa.String(length=45), nullable=True))

    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
