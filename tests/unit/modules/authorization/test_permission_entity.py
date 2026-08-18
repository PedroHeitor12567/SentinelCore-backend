from datetime import UTC, datetime

from sentinelcore.modules.authorization.domain.entities.permission import Permission


def test_create_permission_sets_fields() -> None:
    permission = Permission.create(code="roles:create", description="Create roles")

    assert permission.code == "roles:create"
    assert permission.description == "Create roles"
    assert isinstance(permission.created_at, datetime)
    assert permission.created_at.tzinfo == UTC
