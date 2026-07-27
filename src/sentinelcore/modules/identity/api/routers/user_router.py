from uuid import UUID

from fastapi import APIRouter, status

from sentinelcore.modules.identity.api.dependencies import (
    ActivateUserUseCaseDep,
    CreateUserUseCaseDep,
    DeactivateUserUseCaseDep,
    GetUserUseCaseDep,
)
from sentinelcore.modules.identity.api.schemas.create_user_request import CreateUserRequest
from sentinelcore.modules.identity.api.schemas.user_response import UserResponse
from sentinelcore.modules.identity.application.dtos.create_user_input import CreateUserInput
from sentinelcore.modules.identity.application.dtos.user_id_input import UserIdInput

router = APIRouter(prefix="/users", tags=["identity"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest, use_case: CreateUserUseCaseDep) -> UserResponse:
    output = await use_case.execute(CreateUserInput(email=request.email, password=request.password))
    return UserResponse.from_output(output)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, use_case: GetUserUseCaseDep) -> UserResponse:
    output = await use_case.execute(UserIdInput(user_id=user_id))
    return UserResponse.from_output(output)


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(user_id: UUID, use_case: ActivateUserUseCaseDep) -> UserResponse:
    output = await use_case.execute(UserIdInput(user_id=user_id))
    return UserResponse.from_output(output)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(user_id: UUID, use_case: DeactivateUserUseCaseDep) -> UserResponse:
    output = await use_case.execute(UserIdInput(user_id=user_id))
    return UserResponse.from_output(output)
