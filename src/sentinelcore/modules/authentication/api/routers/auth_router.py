from fastapi import APIRouter
from starlette import status

from sentinelcore.modules.authentication.api.dependencies import LoginUseCaseDep, LogoutUseCaseDep, RefreshTokenUseCaseDep
from sentinelcore.modules.authentication.api.schemas.request.login_request import LoginRequest
from sentinelcore.modules.authentication.api.schemas.request.logout_request import LogoutRequest
from sentinelcore.modules.authentication.api.schemas.request.refresh_token_request import RefreshTokenRequest
from sentinelcore.modules.authentication.api.schemas.response.token_response import TokenResponse
from sentinelcore.modules.authentication.application.dtos.input.login_input import LoginInput
from sentinelcore.modules.authentication.application.dtos.input.logout_input import LogoutInput
from sentinelcore.modules.authentication.application.dtos.input.refresh_token_input import RefreshTokenInput

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, use_case: LoginUseCaseDep) -> TokenResponse:
    output = await use_case.execute(LoginInput(email=request.email, password=request.password))
    return TokenResponse.from_output(output)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest, use_case: RefreshTokenUseCaseDep) -> TokenResponse:
    output = await use_case.execute(RefreshTokenInput(refresh_token=request.refresh_token))
    return TokenResponse.from_output(output)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: LogoutRequest, use_case: LogoutUseCaseDep) -> None:
    await use_case.execute(LogoutInput(refresh_token=request.refresh_token))
