from datetime import UTC, datetime
from uuid import uuid4

from sentinelcore.modules.authorization.domain.entities.role import Role


def test_create_role_has_no_permissions() -> None:
    role = Role.create(name="admin", description="Administrator role")

    assert role.name == "admin"
    assert role.description == "Administrator role"
    assert role.permission_ids == set()
    assert isinstance(role.created_at, datetime)
    assert role.created_at.tzinfo == UTC


def test_grant_permission_adds_permission_id() -> None:
    role = Role.create(name="admin", description="Administrator role")
    permission_id = uuid4()

    role.grant_permission(permission_id)

    assert permission_id in role.permission_ids


def test_grant_permission_is_idempotent() -> None:
    role = Role.create(name="admin", description="Administrator role")
    permission_id = uuid4()

    role.grant_permission(permission_id)
    role.grant_permission(permission_id)

    assert role.permission_ids == {permission_id}


def test_revoke_permission_removes_permission_id() -> None:
    role = Role.create(name="admin", description="Administrator role")
    permission_id = uuid4()
    role.grant_permission(permission_id)

    role.revoke_permission(permission_id)

    assert permission_id not in role.permission_ids


def test_revoke_permission_not_granted_is_noop() -> None:
    role = Role.create(name="admin", description="Administrator role")
    permission_id = uuid4()

    role.revoke_permission(permission_id)

    assert role.permission_ids == set()


def test_role_equality_is_based_on_id() -> None:
    role_id = uuid4()
    first = Role(id=role_id, name="admin", description="d", permission_ids=set(), created_at=datetime.now(UTC))
    second = Role(id=role_id, name="other", description="d2", permission_ids=set(), created_at=datetime.now(UTC))

    assert first == second
    assert hash(first) == hash(second)
