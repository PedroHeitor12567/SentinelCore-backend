import pytest

from sentinelcore.modules.authorization.application.dtos.input.create_permission_input import CreatePermissionInput
from sentinelcore.modules.authorization.application.use_cases.create_permission_use_case import CreatePermissionUseCase
from sentinelcore.modules.authorization.domain.errors.permission_code_already_in_use_error import (
    PermissionCodeAlreadyInUseError,
)


async def test_create_permission_persists_permission(permission_repository, unit_of_work) -> None:
    use_case = CreatePermissionUseCase(permission_repository, unit_of_work)

    output = await use_case.execute(CreatePermissionInput(code="roles:create", description="Create roles"))

    stored_permission = await permission_repository.get_by_id(output.id)
    assert stored_permission is not None
    assert stored_permission.code == "roles:create"
    assert unit_of_work.committed is True


async def test_create_permission_with_duplicate_code_raises_error(permission_repository, unit_of_work) -> None:
    use_case = CreatePermissionUseCase(permission_repository, unit_of_work)
    await use_case.execute(CreatePermissionInput(code="roles:create", description="Create roles"))

    with pytest.raises(PermissionCodeAlreadyInUseError):
        await use_case.execute(CreatePermissionInput(code="roles:create", description="Other"))
