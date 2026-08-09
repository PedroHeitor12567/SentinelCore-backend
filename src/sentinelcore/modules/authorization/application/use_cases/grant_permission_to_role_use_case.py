from sentinelcore.modules.authorization.application.dtos.input.grant_permission_input import GrantPermissionInput
from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput
from sentinelcore.modules.authorization.application.ports.permission_repository import PermissionRepository
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.domain.errors.permission_not_found_error import PermissionNotFoundError
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class GrantPermissionToRoleUseCase(UseCase[GrantPermissionInput, RoleOutput]):
    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._role_repository = role_repository
        self._permission_repository = permission_repository
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: GrantPermissionInput) -> RoleOutput:
        role = await self._role_repository.get_by_id(input_data.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role {input_data.role_id} not found")

        permission = await self._permission_repository.get_by_id(input_data.permission_id)
        if permission is None:
            raise PermissionNotFoundError(f"Permission {input_data.permission_id} not found")

        role.grant_permission(permission.id)
        await self._role_repository.update(role)
        await self._unit_of_work.commit()

        return RoleOutput.from_role(role)
