from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from sentinelcore.modules.authentication.api.dependencies import CurrentUserId
from sentinelcore.modules.authorization.api.dependencies import AssignRoleToUserUseCaseDep,GetUserPermissionsUseCaseDep,UnassignRoleFromUserUseCaseDep,require_permission
from sentinelcore.modules.authorization.api.schemas.response.user_permissions_response import UserPermissionsResponse
from sentinelcore.modules.authorization.application.dtos.input.assign_role_input import AssignRoleInput
from sentinelcore.modules.authorization.application.dtos.input.get_user_permissions_input import GetUserPermissionsInput
from sentinelcore.modules.authorization.application.dtos.input.unassign_role_input import UnassignRoleInput


router = APIRouter(prefix="/users", tags=["authorization"])


@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role(
    user_id: UUID,
    role_id: UUID,
    current_user_id: Annotated[UUID, Depends(require_permission("users:manage_roles"))],
    use_case: AssignRoleToUserUseCaseDep,
) -> None:
    await use_case.execute(AssignRoleInput(user_id=user_id, role_id=role_id, actor_id=current_user_id))


@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_role(
    user_id: UUID,
    role_id: UUID,
    current_user_id: Annotated[UUID, Depends(require_permission("users:manage_roles"))],
    use_case: UnassignRoleFromUserUseCaseDep,
) -> None:
    await use_case.execute(UnassignRoleInput(user_id=user_id, role_id=role_id, actor_id=current_user_id))


@router.get("/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: UUID,
    current_user_id: CurrentUserId,
    use_case: GetUserPermissionsUseCaseDep,
) -> UserPermissionsResponse:
    if user_id != current_user_id:
        checker = require_permission("users:read_permissions")
        await checker(current_user_id, use_case)
    output = await use_case.execute(GetUserPermissionsInput(user_id=user_id))
    return UserPermissionsResponse.from_output(output)
