"""add device info to refresh_tokens

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-01

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("refresh_tokens", sa.Column("ip_address", sa.String(length=45), nullable=True))
    op.add_column("refresh_tokens", sa.Column("user_agent", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("refresh_tokens", "user_agent")
    op.drop_column("refresh_tokens", "ip_address")
