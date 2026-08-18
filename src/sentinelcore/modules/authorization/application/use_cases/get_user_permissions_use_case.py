from sentinelcore.modules.authorization.application.dtos.input.get_user_permissions_input import GetUserPermissionsInput
from sentinelcore.modules.authorization.application.dtos.output.user_permissions_output import UserPermissionsOutput
from sentinelcore.modules.authorization.application.ports.permission_repository import PermissionRepository
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.application.ports.user_role_repository import UserRoleRepository
from sentinelcore.shared.application.use_case import UseCase


class GetUserPermissionsUseCase(UseCase[GetUserPermissionsInput, UserPermissionsOutput]):
    def __init__(
        self,
        user_role_repository: UserRoleRepository,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ) -> None:
        self._user_role_repository = user_role_repository
        self._role_repository = role_repository
        self._permission_repository = permission_repository

    async def execute(self, input_data: GetUserPermissionsInput) -> UserPermissionsOutput:
        role_ids = await self._user_role_repository.list_role_ids_for_user(input_data.user_id)

        permission_ids: set = set()
        for role_id in role_ids:
            role = await self._role_repository.get_by_id(role_id)
            if role is not None:
                permission_ids.update(role.permission_ids)

        codes: list[str] = []
        for permission_id in permission_ids:
            permission = await self._permission_repository.get_by_id(permission_id)
            if permission is not None:
                codes.append(permission.code)

        return UserPermissionsOutput(user_id=input_data.user_id, permission_codes=sorted(codes))
