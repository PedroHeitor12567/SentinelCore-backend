from sentinelcore.modules.authorization.application.dtos.input.unassign_role_input import UnassignRoleInput
from sentinelcore.modules.authorization.application.ports.user_role_repository import UserRoleRepository
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class UnassignRoleFromUserUseCase(UseCase[UnassignRoleInput, None]):
    def __init__(self, user_role_repository: UserRoleRepository, unit_of_work: UnitOfWork) -> None:
        self._user_role_repository = user_role_repository
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: UnassignRoleInput) -> None:
        await self._user_role_repository.unassign(input_data.user_id, input_data.role_id)
        await self._unit_of_work.commit()
