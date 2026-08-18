from uuid import uuid4

import pytest

from sentinelcore.modules.authorization.application.dtos.input.grant_permission_input import GrantPermissionInput
from sentinelcore.modules.authorization.application.dtos.input.revoke_permission_input import RevokePermissionInput
from sentinelcore.modules.authorization.application.use_cases.grant_permission_to_role_use_case import (
    GrantPermissionToRoleUseCase,
)
from sentinelcore.modules.authorization.application.use_cases.revoke_permission_from_role_use_case import (
    RevokePermissionFromRoleUseCase,
)
from sentinelcore.modules.authorization.domain.entities.permission import Permission
from sentinelcore.modules.authorization.domain.entities.role import Role
from sentinelcore.modules.authorization.domain.errors.permission_not_found_error import PermissionNotFoundError
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError


async def test_grant_permission_adds_permission_to_role(role_repository, permission_repository, unit_of_work) -> None:
    role = Role.create(name="admin", description="Administrator")
    permission = Permission.create(code="roles:create", description="Create roles")
    await role_repository.add(role)
    await permission_repository.add(permission)
    use_case = GrantPermissionToRoleUseCase(role_repository, permission_repository, unit_of_work)

    output = await use_case.execute(GrantPermissionInput(role_id=role.id, permission_id=permission.id))

    assert permission.id in output.permission_ids
    assert unit_of_work.committed is True


async def test_grant_permission_with_unknown_role_raises_error(role_repository, permission_repository, unit_of_work) -> None:
    permission = Permission.create(code="roles:create", description="Create roles")
    await permission_repository.add(permission)
    use_case = GrantPermissionToRoleUseCase(role_repository, permission_repository, unit_of_work)

    with pytest.raises(RoleNotFoundError):
        await use_case.execute(GrantPermissionInput(role_id=uuid4(), permission_id=permission.id))


async def test_grant_permission_with_unknown_permission_raises_error(role_repository, permission_repository, unit_of_work) -> None:
    role = Role.create(name="admin", description="Administrator")
    await role_repository.add(role)
    use_case = GrantPermissionToRoleUseCase(role_repository, permission_repository, unit_of_work)

    with pytest.raises(PermissionNotFoundError):
        await use_case.execute(GrantPermissionInput(role_id=role.id, permission_id=uuid4()))


async def test_revoke_permission_removes_permission_from_role(role_repository, unit_of_work) -> None:
    role = Role.create(name="admin", description="Administrator")
    permission_id = uuid4()
    role.grant_permission(permission_id)
    await role_repository.add(role)
    use_case = RevokePermissionFromRoleUseCase(role_repository, unit_of_work)

    output = await use_case.execute(RevokePermissionInput(role_id=role.id, permission_id=permission_id))

    assert permission_id not in output.permission_ids
    assert unit_of_work.committed is True


async def test_revoke_permission_with_unknown_role_raises_error(role_repository, unit_of_work) -> None:
    use_case = RevokePermissionFromRoleUseCase(role_repository, unit_of_work)

    with pytest.raises(RoleNotFoundError):
        await use_case.execute(RevokePermissionInput(role_id=uuid4(), permission_id=uuid4()))
