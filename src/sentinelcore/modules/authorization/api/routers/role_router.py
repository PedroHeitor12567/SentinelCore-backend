from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from sentinelcore.modules.authorization.api.dependencies import CreateRoleUseCaseDep,GrantPermissionToRoleUseCaseDep,ListRolesUseCaseDep,RevokePermissionFromRoleUseCaseDep,require_permission
from sentinelcore.modules.authorization.api.schemas.request.create_role_request import CreateRoleRequest
from sentinelcore.modules.authorization.api.schemas.response.role_response import RoleResponse
from sentinelcore.modules.authorization.application.dtos.input.create_role_input import CreateRoleInput
from sentinelcore.modules.authorization.application.dtos.input.grant_permission_input import GrantPermissionInput
from sentinelcore.modules.authorization.application.dtos.input.revoke_permission_input import RevokePermissionInput

router = APIRouter(prefix="/roles", tags=["authorization"])


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: CreateRoleRequest,
    _current_user_id: Annotated[UUID, Depends(require_permission("roles:create"))],
    use_case: CreateRoleUseCaseDep,
) -> RoleResponse:
    output = await use_case.execute(CreateRoleInput(name=body.name, description=body.description))
    return RoleResponse.from_output(output)


@router.get("", response_model=list[RoleResponse])
async def list_roles(
    _current_user_id: Annotated[UUID, Depends(require_permission("roles:read"))],
    use_case: ListRolesUseCaseDep,
) -> list[RoleResponse]:
    outputs = await use_case.execute(None)
    return [RoleResponse.from_output(output) for output in outputs]


@router.post("/{role_id}/permissions/{permission_id}", response_model=RoleResponse)
async def grant_permission(
    role_id: UUID,
    permission_id: UUID,
    _current_user_id: Annotated[UUID, Depends(require_permission("roles:manage_permissions"))],
    use_case: GrantPermissionToRoleUseCaseDep,
) -> RoleResponse:
    output = await use_case.execute(GrantPermissionInput(role_id=role_id, permission_id=permission_id))
    return RoleResponse.from_output(output)


@router.delete("/{role_id}/permissions/{permission_id}", response_model=RoleResponse)
async def revoke_permission(
    role_id: UUID,
    permission_id: UUID,
    _current_user_id: Annotated[UUID, Depends(require_permission("roles:manage_permissions"))],
    use_case: RevokePermissionFromRoleUseCaseDep,
) -> RoleResponse:
    output = await use_case.execute(RevokePermissionInput(role_id=role_id, permission_id=permission_id))
    return RoleResponse.from_output(output)
