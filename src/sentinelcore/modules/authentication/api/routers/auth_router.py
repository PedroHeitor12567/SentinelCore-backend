from fastapi import APIRouter, Request
from starlette import status

from sentinelcore.modules.authentication.api.dependencies import (
    LoginUseCaseDep,
    LogoutUseCaseDep,
    RefreshTokenUseCaseDep,
)
from sentinelcore.modules.authentication.api.schemas.request.login_request import LoginRequest
from sentinelcore.modules.authentication.api.schemas.request.logout_request import LogoutRequest
from sentinelcore.modules.authentication.api.schemas.request.refresh_token_request import (
    RefreshTokenRequest,
)
from sentinelcore.modules.authentication.api.schemas.response.token_response import TokenResponse
from sentinelcore.modules.authentication.application.dtos.input.login_input import LoginInput
from sentinelcore.modules.authentication.application.dtos.input.logout_input import LogoutInput
from sentinelcore.modules.authentication.application.dtos.input.refresh_token_input import (
    RefreshTokenInput,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def _client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, body: LoginRequest, use_case: LoginUseCaseDep) -> TokenResponse:
    output = await use_case.execute(
        LoginInput(
            email=body.email,
            password=body.password,
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
    )
    return TokenResponse.from_output(output)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request, body: RefreshTokenRequest, use_case: RefreshTokenUseCaseDep
) -> TokenResponse:
    output = await use_case.execute(
        RefreshTokenInput(
            refresh_token=body.refresh_token,
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
    )
    return TokenResponse.from_output(output)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: LogoutRequest, use_case: LogoutUseCaseDep) -> None:
    await use_case.execute(LogoutInput(refresh_token=body.refresh_token))
