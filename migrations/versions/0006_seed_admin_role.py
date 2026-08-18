"""seed admin role with all permissions and assign to first user

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-16

"""
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
PERMISSION_CODES = [
    "roles:create",
    "roles:read",
    "roles:manage_permissions",
    "permissions:create",
    "permissions:read",
    "users:manage_roles",
    "users:read_permissions",
]


def upgrade() -> None:
    connection = op.get_bind()
    now = datetime.now(UTC)

    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("description", sa.String()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
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
    user_roles_table = sa.table(
        "user_roles",
        sa.column("user_id", sa.Uuid()),
        sa.column("role_id", sa.Uuid()),
    )
    users_table = sa.table(
        "users",
        sa.column("id", sa.Uuid()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )

    connection.execute(
        roles_table.insert().values(
            id=ADMIN_ROLE_ID,
            name="admin",
            description="Full access administrator role",
            created_at=now,
        )
    )

    permission_ids: list[uuid.UUID] = []
    for code in PERMISSION_CODES:
        permission_id = uuid.uuid4()
        permission_ids.append(permission_id)
        connection.execute(
            permissions_table.insert().values(
                id=permission_id,
                code=code,
                description=code,
                created_at=now,
            )
        )

    connection.execute(
        role_permissions_table.insert(),
        [{"role_id": ADMIN_ROLE_ID, "permission_id": permission_id} for permission_id in permission_ids],
    )

    first_user_id = connection.execute(
        sa.select(users_table.c.id).order_by(users_table.c.created_at.asc()).limit(1)
    ).scalar()

    if first_user_id is not None:
        connection.execute(
            user_roles_table.insert().values(user_id=first_user_id, role_id=ADMIN_ROLE_ID)
        )


def downgrade() -> None:
    connection = op.get_bind()

    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Uuid()),
        sa.column("permission_id", sa.Uuid()),
    )
    user_roles_table = sa.table(
        "user_roles",
        sa.column("user_id", sa.Uuid()),
        sa.column("role_id", sa.Uuid()),
    )
    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Uuid()),
        sa.column("code", sa.String()),
    )
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Uuid()),
    )

    connection.execute(user_roles_table.delete().where(user_roles_table.c.role_id == ADMIN_ROLE_ID))
    connection.execute(
        role_permissions_table.delete().where(role_permissions_table.c.role_id == ADMIN_ROLE_ID)
    )
    connection.execute(
        permissions_table.delete().where(permissions_table.c.code.in_(PERMISSION_CODES))
    )
    connection.execute(roles_table.delete().where(roles_table.c.id == ADMIN_ROLE_ID))
