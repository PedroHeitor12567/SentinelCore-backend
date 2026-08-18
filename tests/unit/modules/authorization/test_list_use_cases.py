from sentinelcore.modules.authorization.application.use_cases.list_permissions_use_case import (
    ListPermissionsUseCase,
)
from sentinelcore.modules.authorization.application.use_cases.list_roles_use_case import ListRolesUseCase
from sentinelcore.modules.authorization.domain.entities.permission import Permission
from sentinelcore.modules.authorization.domain.entities.role import Role


async def test_list_roles_returns_all_roles(role_repository) -> None:
    await role_repository.add(Role.create(name="admin", description="Administrator"))
    await role_repository.add(Role.create(name="viewer", description="Viewer"))
    use_case = ListRolesUseCase(role_repository)

    outputs = await use_case.execute(None)

    assert {output.name for output in outputs} == {"admin", "viewer"}


async def test_list_permissions_returns_all_permissions(permission_repository) -> None:
    await permission_repository.add(Permission.create(code="roles:create", description="Create roles"))
    await permission_repository.add(Permission.create(code="roles:read", description="Read roles"))
    use_case = ListPermissionsUseCase(permission_repository)

    outputs = await use_case.execute(None)

    assert {output.code for output in outputs} == {"roles:create", "roles:read"}
