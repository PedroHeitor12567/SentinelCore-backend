from sentinelcore.modules.authorization.application.dtos.input.create_role_input import CreateRoleInput
from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.domain.entities.role import Role
from sentinelcore.modules.authorization.domain.errors.role_name_already_in_use_error import RoleNameAlreadyInUseError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class CreateRoleUseCase(UseCase[CreateRoleInput, RoleOutput]):
    def __init__(self, role_repository: RoleRepository, unit_of_work: UnitOfWork) -> None:
        self._role_repository = role_repository
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: CreateRoleInput) -> RoleOutput:
        existing = await self._role_repository.get_by_name(input_data.name)
        if existing is not None:
            raise RoleNameAlreadyInUseError(f"Role name '{input_data.name}' is already in use")

        role = Role.create(name=input_data.name, description=input_data.description)
        await self._role_repository.add(role)
        await self._unit_of_work.commit()

        return RoleOutput.from_role(role)
