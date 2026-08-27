from uuid import uuid4

import pytest

from sentinelcore.modules.authorization.application.dtos.input.assign_role_input import AssignRoleInput
from sentinelcore.modules.authorization.application.dtos.input.unassign_role_input import UnassignRoleInput
from sentinelcore.modules.authorization.application.use_cases.assign_role_to_user_use_case import (
    AssignRoleToUserUseCase,
)
from sentinelcore.modules.authorization.application.use_cases.unassign_role_from_user_use_case import (
    UnassignRoleFromUserUseCase,
)
from sentinelcore.modules.authorization.domain.entities.role import Role
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError


async def test_assign_role_links_user_and_role(role_repository, user_role_repository, unit_of_work, audit_log_repository) -> None:
    role = Role.create(name="admin", description="Administrator")
    await role_repository.add(role)
    user_id = uuid4()
    use_case = AssignRoleToUserUseCase(role_repository, user_role_repository, unit_of_work, audit_log_repository)

    await use_case.execute(AssignRoleInput(user_id=user_id, role_id=role.id))

    assert role.id in await user_role_repository.list_role_ids_for_user(user_id)
    assert unit_of_work.committed is True


async def test_assign_role_with_unknown_role_raises_error(role_repository, user_role_repository, unit_of_work, audit_log_repository) -> None:
    use_case = AssignRoleToUserUseCase(role_repository, user_role_repository, unit_of_work, audit_log_repository)

    with pytest.raises(RoleNotFoundError):
        await use_case.execute(AssignRoleInput(user_id=uuid4(), role_id=uuid4()))


async def test_unassign_role_removes_link(user_role_repository, unit_of_work, audit_log_repository) -> None:
    user_id = uuid4()
    role_id = uuid4()
    await user_role_repository.assign(user_id, role_id)
    use_case = UnassignRoleFromUserUseCase(user_role_repository, unit_of_work, audit_log_repository)

    await use_case.execute(UnassignRoleInput(user_id=user_id, role_id=role_id))

    assert role_id not in await user_role_repository.list_role_ids_for_user(user_id)
    assert unit_of_work.committed is True
