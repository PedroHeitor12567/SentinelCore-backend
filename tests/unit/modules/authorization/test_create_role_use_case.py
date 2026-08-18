import pytest

from sentinelcore.modules.authorization.application.dtos.input.create_role_input import CreateRoleInput
from sentinelcore.modules.authorization.application.use_cases.create_role_use_case import CreateRoleUseCase
from sentinelcore.modules.authorization.domain.errors.role_name_already_in_use_error import RoleNameAlreadyInUseError


async def test_create_role_persists_role(role_repository, unit_of_work) -> None:
    use_case = CreateRoleUseCase(role_repository, unit_of_work)

    output = await use_case.execute(CreateRoleInput(name="admin", description="Administrator"))

    stored_role = await role_repository.get_by_id(output.id)
    assert stored_role is not None
    assert stored_role.name == "admin"
    assert unit_of_work.committed is True


async def test_create_role_with_duplicate_name_raises_error(role_repository, unit_of_work) -> None:
    use_case = CreateRoleUseCase(role_repository, unit_of_work)
    await use_case.execute(CreateRoleInput(name="admin", description="Administrator"))

    with pytest.raises(RoleNameAlreadyInUseError):
        await use_case.execute(CreateRoleInput(name="admin", description="Other description"))
