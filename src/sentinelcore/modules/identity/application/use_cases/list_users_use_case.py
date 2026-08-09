from sentinelcore.modules.identity.application.dtos.output.user_output import UserOutput
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.shared.application.use_case import UseCase


class ListUsersUseCase(UseCase[None, list[UserOutput]]):
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, input_data: None = None) -> list[UserOutput]:
        users = await self._user_repository.get_all()

        return [
            UserOutput.from_entity(user)
            for user in users
        ]
