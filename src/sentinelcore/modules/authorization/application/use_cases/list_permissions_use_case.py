from sentinelcore.modules.authorization.application.dtos.output.permission_output import PermissionOutput
from sentinelcore.modules.authorization.application.ports.permission_repository import PermissionRepository
from sentinelcore.shared.application.use_case import UseCase


class ListPermissionsUseCase(UseCase[None, list[PermissionOutput]]):
    def __init__(self, permission_repository: PermissionRepository) -> None:
        self._permission_repository = permission_repository

    async def execute(self, input_data: None) -> list[PermissionOutput]:
        permissions = await self._permission_repository.list_all()
        return [PermissionOutput.from_permission(permission) for permission in permissions]
