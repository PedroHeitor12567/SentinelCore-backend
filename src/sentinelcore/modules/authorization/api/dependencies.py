from typing import Annotated
from uuid import UUID

from fastapi import Depends

from sentinelcore.core.dependencies import UoW
from sentinelcore.modules.authentication.api.dependencies import CurrentUserId
from sentinelcore.modules.authorization.application.dtos.input.get_user_permissions_input import GetUserPermissionsInput
from sentinelcore.modules.authorization.application.ports.permission_repository import PermissionRepository
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.application.ports.user_role_repository import UserRoleRepository
from sentinelcore.modules.authorization.application.use_cases.assign_role_to_user_use_case import AssignRoleToUserUseCase
from sentinelcore.modules.authorization.application.use_cases.create_permission_use_case import CreatePermissionUseCase
from sentinelcore.modules.authorization.application.use_cases.create_role_use_case import CreateRoleUseCase
from sentinelcore.modules.authorization.application.use_cases.get_user_permissions_use_case import GetUserPermissionsUseCase
from sentinelcore.modules.authorization.application.use_cases.grant_permission_to_role_use_case import GrantPermissionToRoleUseCase
from sentinelcore.modules.authorization.application.use_cases.list_permissions_use_case import ListPermissionsUseCase
from sentinelcore.modules.authorization.application.use_cases.list_roles_use_case import ListRolesUseCase
from sentinelcore.modules.authorization.application.use_cases.revoke_permission_from_role_use_case import RevokePermissionFromRoleUseCase
from sentinelcore.modules.authorization.application.use_cases.unassign_role_from_user_use_case import UnassignRoleFromUserUseCase
from sentinelcore.modules.authorization.domain.errors.insufficient_permission_error import InsufficientPermissionError
from sentinelcore.modules.authorization.infrastructure.repository.sql_alchemy_permission_repository import (
    SqlAlchemyPermissionRepository,
)
from sentinelcore.modules.authorization.infrastructure.repository.sql_alchemy_role_repository import (
    SqlAlchemyRoleRepository,
)
from sentinelcore.modules.authorization.infrastructure.repository.sql_alchemy_user_role_repository import (
    SqlAlchemyUserRoleRepository,
)


def get_role_repository(unit_of_work: UoW) -> RoleRepository:
    return SqlAlchemyRoleRepository(unit_of_work.session)


def get_permission_repository(unit_of_work: UoW) -> PermissionRepository:
    return SqlAlchemyPermissionRepository(unit_of_work.session)


def get_user_role_repository(unit_of_work: UoW) -> UserRoleRepository:
    return SqlAlchemyUserRoleRepository(unit_of_work.session)


RoleRepositoryDep = Annotated[RoleRepository, Depends(get_role_repository)]
PermissionRepositoryDep = Annotated[PermissionRepository, Depends(get_permission_repository)]
UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends(get_user_role_repository)]


def get_create_role_use_case(role_repository: RoleRepositoryDep, unit_of_work: UoW) -> CreateRoleUseCase:
    return CreateRoleUseCase(role_repository, unit_of_work)


def get_create_permission_use_case(
    permission_repository: PermissionRepositoryDep, unit_of_work: UoW
) -> CreatePermissionUseCase:
    return CreatePermissionUseCase(permission_repository, unit_of_work)


def get_grant_permission_to_role_use_case(
    role_repository: RoleRepositoryDep,
    permission_repository: PermissionRepositoryDep,
    unit_of_work: UoW,
) -> GrantPermissionToRoleUseCase:
    return GrantPermissionToRoleUseCase(role_repository, permission_repository, unit_of_work)


def get_revoke_permission_from_role_use_case(
    role_repository: RoleRepositoryDep, unit_of_work: UoW
) -> RevokePermissionFromRoleUseCase:
    return RevokePermissionFromRoleUseCase(role_repository, unit_of_work)


def get_assign_role_to_user_use_case(
    role_repository: RoleRepositoryDep,
    user_role_repository: UserRoleRepositoryDep,
    unit_of_work: UoW,
) -> AssignRoleToUserUseCase:
    return AssignRoleToUserUseCase(role_repository, user_role_repository, unit_of_work)


def get_unassign_role_from_user_use_case(
    user_role_repository: UserRoleRepositoryDep, unit_of_work: UoW
) -> UnassignRoleFromUserUseCase:
    return UnassignRoleFromUserUseCase(user_role_repository, unit_of_work)


def get_list_roles_use_case(role_repository: RoleRepositoryDep) -> ListRolesUseCase:
    return ListRolesUseCase(role_repository)


def get_list_permissions_use_case(
    permission_repository: PermissionRepositoryDep,
) -> ListPermissionsUseCase:
    return ListPermissionsUseCase(permission_repository)


def get_get_user_permissions_use_case(
    user_role_repository: UserRoleRepositoryDep,
    role_repository: RoleRepositoryDep,
    permission_repository: PermissionRepositoryDep,
) -> GetUserPermissionsUseCase:
    return GetUserPermissionsUseCase(user_role_repository, role_repository, permission_repository)


CreateRoleUseCaseDep = Annotated[CreateRoleUseCase, Depends(get_create_role_use_case)]
CreatePermissionUseCaseDep = Annotated[CreatePermissionUseCase, Depends(get_create_permission_use_case)]
GrantPermissionToRoleUseCaseDep = Annotated[
    GrantPermissionToRoleUseCase, Depends(get_grant_permission_to_role_use_case)
]
RevokePermissionFromRoleUseCaseDep = Annotated[
    RevokePermissionFromRoleUseCase, Depends(get_revoke_permission_from_role_use_case)
]
AssignRoleToUserUseCaseDep = Annotated[
    AssignRoleToUserUseCase, Depends(get_assign_role_to_user_use_case)
]
UnassignRoleFromUserUseCaseDep = Annotated[
    UnassignRoleFromUserUseCase, Depends(get_unassign_role_from_user_use_case)
]
ListRolesUseCaseDep = Annotated[ListRolesUseCase, Depends(get_list_roles_use_case)]
ListPermissionsUseCaseDep = Annotated[ListPermissionsUseCase, Depends(get_list_permissions_use_case)]
GetUserPermissionsUseCaseDep = Annotated[
    GetUserPermissionsUseCase, Depends(get_get_user_permissions_use_case)
]


def require_permission(required_code: str):
    async def _check(
        current_user_id: CurrentUserId, use_case: GetUserPermissionsUseCaseDep
    ) -> UUID:
        output = await use_case.execute(GetUserPermissionsInput(user_id=current_user_id))
        if required_code not in output.permission_codes:
            raise InsufficientPermissionError(
                f"Missing required permission '{required_code}'"
            )
        return current_user_id

    return _check
