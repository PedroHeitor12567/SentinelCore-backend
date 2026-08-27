from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from sentinelcore.modules.authorization.api.dependencies import CreatePermissionUseCaseDep,ListPermissionsUseCaseDep,require_permission
from sentinelcore.modules.authorization.api.schemas.request.create_permission_request import CreatePermissionRequest
from sentinelcore.modules.authorization.api.schemas.response.permission_response import PermissionResponse
from sentinelcore.modules.authorization.application.dtos.input.create_permission_input import CreatePermissionInput

router = APIRouter(prefix="/permissions", tags=["authorization"])


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    body: CreatePermissionRequest,
    current_user_id: Annotated[UUID, Depends(require_permission("permissions:create"))],
    use_case: CreatePermissionUseCaseDep,
) -> PermissionResponse:
    output = await use_case.execute(
        CreatePermissionInput(code=body.code, description=body.description, actor_id=current_user_id)
    )
    return PermissionResponse.from_output(output)


@router.get("", response_model=list[PermissionResponse])
async def list_permissions(
    _current_user_id: Annotated[UUID, Depends(require_permission("permissions:read"))],
    use_case: ListPermissionsUseCaseDep,
) -> list[PermissionResponse]:
    outputs = await use_case.execute(None)
    return [PermissionResponse.from_output(output) for output in outputs]
