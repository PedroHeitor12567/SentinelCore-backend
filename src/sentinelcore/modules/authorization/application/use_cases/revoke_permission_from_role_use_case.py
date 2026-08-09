from sentinelcore.modules.authorization.application.dtos.input.revoke_permission_input import RevokePermissionInput
from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class RevokePermissionFromRoleUseCase(UseCase[RevokePermissionInput, RoleOutput]):
    def __init__(self, role_repository: RoleRepository, unit_of_work: UnitOfWork) -> None:
        self._role_repository = role_repository
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: RevokePermissionInput) -> RoleOutput:
        role = await self._role_repository.get_by_id(input_data.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role {input_data.role_id} not found")

        role.revoke_permission(input_data.permission_id)
        await self._role_repository.update(role)
        await self._unit_of_work.commit()

        return RoleOutput.from_role(role)
