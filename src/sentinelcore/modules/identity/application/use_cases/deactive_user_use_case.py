from sentinelcore.modules.identity.application.dtos.input.user_id_input import UserIdInput
from sentinelcore.modules.identity.application.dtos.output.user_output import UserOutput
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.modules.identity.domain.errors.user_not_found_error import UserNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class DeactiveUserUseCase(UseCase[UserIdInput, UserOutput]):
    def __init__(self, user_repository: UserRepository, unit_of_work: UnitOfWork):
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: UserIdInput) -> UserOutput:
        user = await self._user_repository.get_by_id(input_data.user_id)
        if user is None:
            raise UserNotFoundError(f"User {input_data.user_id} not found")

        user.deactivate()

        await self._user_repository.update(user)
        await self._unit_of_work.commit()

        return UserOutput.from_entity(user)
