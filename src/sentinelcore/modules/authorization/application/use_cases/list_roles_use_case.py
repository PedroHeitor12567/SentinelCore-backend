from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.shared.application.use_case import UseCase


class ListRolesUseCase(UseCase[None, list[RoleOutput]]):
    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repository = role_repository

    async def execute(self, input_data: None = None) -> list[RoleOutput]:
        roles = await self._role_repository.list_all()
        return [RoleOutput.from_role(role) for role in roles]
