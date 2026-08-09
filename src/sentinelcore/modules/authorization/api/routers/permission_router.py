from fastapi import APIRouter
from starlette import status

from sentinelcore.modules.authentication.api.dependencies import CurrentUserId
from sentinelcore.modules.authorization.api.dependencies import CreatePermissionUseCaseDep,ListPermissionsUseCaseDep
from sentinelcore.modules.authorization.api.schemas.request.create_permission_request import CreatePermissionRequest
from sentinelcore.modules.authorization.api.schemas.response.permission_response import PermissionResponse
from sentinelcore.modules.authorization.application.dtos.input.create_permission_input import CreatePermissionInput

router = APIRouter(prefix="/permissions", tags=["authorization"])


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    body: CreatePermissionRequest,
    _current_user_id: CurrentUserId,
    use_case: CreatePermissionUseCaseDep,
) -> PermissionResponse:
    output = await use_case.execute(CreatePermissionInput(code=body.code, description=body.description))
    return PermissionResponse.from_output(output)


@router.get("", response_model=list[PermissionResponse])
async def list_permissions(
    _current_user_id: CurrentUserId, use_case: ListPermissionsUseCaseDep
) -> list[PermissionResponse]:
    outputs = await use_case.execute(None)
    return [PermissionResponse.from_output(output) for output in outputs]
