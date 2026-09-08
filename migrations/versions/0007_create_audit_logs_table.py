"""create audit_logs table and audit:read permission

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-23

"""
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
AUDIT_READ_PERMISSION_CODE = "audit:read"


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"], unique=False)
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"], unique=False)
    op.create_index("ix_audit_logs_target_id", "audit_logs", ["target_id"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)

    connection = op.get_bind()
    now = datetime.now(UTC)

    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Uuid()),
        sa.column("code", sa.String()),
        sa.column("description", sa.String()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Uuid()),
        sa.column("permission_id", sa.Uuid()),
    )

    permission_id = uuid.uuid4()
    connection.execute(
        permissions_table.insert().values(
            id=permission_id,
            code=AUDIT_READ_PERMISSION_CODE,
            description=AUDIT_READ_PERMISSION_CODE,
            created_at=now,
        )
    )
    connection.execute(
        role_permissions_table.insert().values(role_id=ADMIN_ROLE_ID, permission_id=permission_id)
    )


def downgrade() -> None:
    connection = op.get_bind()

    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Uuid()),
        sa.column("code", sa.String()),
    )
    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Uuid()),
        sa.column("permission_id", sa.Uuid()),
    )

    permission_id = connection.execute(
        sa.select(permissions_table.c.id).where(permissions_table.c.code == AUDIT_READ_PERMISSION_CODE)
    ).scalar()
    if permission_id is not None:
        connection.execute(
            role_permissions_table.delete().where(
                role_permissions_table.c.permission_id == permission_id
            )
        )
        connection.execute(permissions_table.delete().where(permissions_table.c.id == permission_id))

    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_target_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    op.drop_table("audit_logs")
