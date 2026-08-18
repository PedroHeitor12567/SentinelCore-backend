from sentinelcore.modules.authorization.application.dtos.input.create_permission_input import CreatePermissionInput
from sentinelcore.modules.authorization.application.dtos.output.permission_output import PermissionOutput
from sentinelcore.modules.authorization.application.ports.permission_repository import PermissionRepository
from sentinelcore.modules.authorization.domain.entities.permission import Permission
from sentinelcore.modules.authorization.domain.errors.permission_code_already_in_use_error import \
    PermissionCodeAlreadyInUseError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class CreatePermissionUseCase(UseCase[CreatePermissionInput, PermissionOutput]):
    def __init__(self, permission_repository: PermissionRepository, unit_of_work: UnitOfWork) -> None:
        self._permission_repository = permission_repository
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: CreatePermissionInput) -> PermissionOutput:
        existing = await self._permission_repository.get_by_code(input_data.code)
        if existing is not None:
            raise PermissionCodeAlreadyInUseError(f"Permission code '{input_data.code}' is already in use.")

        permission = Permission.create(code=input_data.code, description=input_data.description)
        await self._permission_repository.add(permission)
        await self._unit_of_work.commit()

        return PermissionOutput.from_permission(permission)
