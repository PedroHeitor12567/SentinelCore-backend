from sentinelcore.modules.authorization.application.dtos.input.assign_role_input import AssignRoleInput
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.application.ports.user_role_repository import UserRoleRepository
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class AssignRoleToUserUseCase(UseCase[AssignRoleInput, None]):
    def __init__(
        self,
        role_repository: RoleRepository,
        user_role_repository: UserRoleRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._role_repository = role_repository
        self._user_role_repository = user_role_repository
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: AssignRoleInput) -> None:
        role = await self._role_repository.get_by_id(input_data.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role {input_data.role_id} not found")

        await self._user_role_repository.assign(input_data.user_id, input_data.role_id)
        await self._unit_of_work.commit()
