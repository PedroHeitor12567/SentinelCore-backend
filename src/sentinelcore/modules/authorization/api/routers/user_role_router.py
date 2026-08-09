from uuid import UUID

from fastapi import APIRouter
from starlette import status

from sentinelcore.modules.authentication.api.dependencies import CurrentUserId
from sentinelcore.modules.authorization.api.dependencies import AssignRoleToUserUseCaseDep,GetUserPermissionsUseCaseDep,UnassignRoleFromUserUseCaseDep
from sentinelcore.modules.authorization.api.schemas.response.user_permissions_response import UserPermissionsResponse
from sentinelcore.modules.authorization.application.dtos.input.assign_role_input import AssignRoleInput
from sentinelcore.modules.authorization.application.dtos.input.get_user_permissions_input import GetUserPermissionsInput
from sentinelcore.modules.authorization.application.dtos.input.unassign_role_input import UnassignRoleInput

router = APIRouter(prefix="/users", tags=["authorization"])


@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role(
    user_id: UUID,
    role_id: UUID,
    _current_user_id: CurrentUserId,
    use_case: AssignRoleToUserUseCaseDep,
) -> None:
    await use_case.execute(AssignRoleInput(user_id=user_id, role_id=role_id))


@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_role(
    user_id: UUID,
    role_id: UUID,
    _current_user_id: CurrentUserId,
    use_case: UnassignRoleFromUserUseCaseDep,
) -> None:
    await use_case.execute(UnassignRoleInput(user_id=user_id, role_id=role_id))


@router.get("/{user_id}/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    user_id: UUID,
    _current_user_id: CurrentUserId,
    use_case: GetUserPermissionsUseCaseDep,
) -> UserPermissionsResponse:
    output = await use_case.execute(GetUserPermissionsInput(user_id=user_id))
    return UserPermissionsResponse.from_output(output)
