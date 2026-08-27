from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sentinelcore.core.config.settings import get_settings
from sentinelcore.core.dependencies import UoW
from sentinelcore.modules.audit.api.dependencies import AuditLogRepositoryDep
from sentinelcore.modules.authentication.application.dtos.input.validate_access_token_input import (
    ValidateAccessTokenInput,
)
from sentinelcore.modules.authentication.application.ports.clock import Clock
from sentinelcore.modules.authentication.application.ports.refresh_token_repository import (
    RefreshTokenRepository,
)
from sentinelcore.modules.authentication.application.ports.session_repository import SessionRepository
from sentinelcore.modules.authentication.application.ports.token_service import TokenService
from sentinelcore.modules.authentication.application.use_cases.login_use_case import LoginUseCase
from sentinelcore.modules.authentication.application.use_cases.logout_use_case import LogoutUseCase
from sentinelcore.modules.authentication.application.use_cases.refresh_token_use_case import (
    RefreshTokenUseCase,
)
from sentinelcore.modules.authentication.application.use_cases.validate_access_token_use_case import (
    ValidateAccessTokenUseCase,
)
from sentinelcore.modules.authentication.infrastructure.clock.system_clock import SystemClock
from sentinelcore.modules.authentication.infrastructure.repository.sql_alchemy_refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
from sentinelcore.modules.authentication.infrastructure.repository.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from sentinelcore.modules.authentication.infrastructure.security.jwt_token_service import JwtTokenService
from sentinelcore.modules.identity.api.dependencies import PasswordHasherDep, UserRepositoryDep

_clock = SystemClock()
_bearer_scheme = HTTPBearer()


def get_clock() -> Clock:
    return _clock


def get_token_service() -> TokenService:
    settings = get_settings()
    return JwtTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes,
    )


def get_refresh_token_repository(unit_of_work: UoW) -> RefreshTokenRepository:
    return SqlAlchemyRefreshTokenRepository(unit_of_work.session)


def get_session_repository(unit_of_work: UoW) -> SessionRepository:
    return SqlAlchemySessionRepository(unit_of_work.session)


def get_refresh_token_ttl() -> timedelta:
    settings = get_settings()
    return timedelta(days=settings.refresh_token_expire_days)


ClockDep = Annotated[Clock, Depends(get_clock)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
RefreshTokenRepositoryDep = Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)]
SessionRepositoryDep = Annotated[SessionRepository, Depends(get_session_repository)]
RefreshTokenTtlDep = Annotated[timedelta, Depends(get_refresh_token_ttl)]


def get_login_use_case(
    user_repository: UserRepositoryDep,
    password_hasher: PasswordHasherDep,
    session_repository: SessionRepositoryDep,
    refresh_token_repository: RefreshTokenRepositoryDep,
    token_service: TokenServiceDep,
    clock: ClockDep,
    unit_of_work: UoW,
    refresh_token_ttl: RefreshTokenTtlDep,
    audit_log_repository: AuditLogRepositoryDep,
) -> LoginUseCase:
    return LoginUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        session_repository=session_repository,
        refresh_token_repository=refresh_token_repository,
        token_service=token_service,
        clock=clock,
        unit_of_work=unit_of_work,
        refresh_token_ttl=refresh_token_ttl,
        audit_log_repository=audit_log_repository,
    )


def get_refresh_token_use_case(
    refresh_token_repository: RefreshTokenRepositoryDep,
    session_repository: SessionRepositoryDep,
    token_service: TokenServiceDep,
    clock: ClockDep,
    unit_of_work: UoW,
    refresh_token_ttl: RefreshTokenTtlDep,
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        refresh_token_repository=refresh_token_repository,
        session_repository=session_repository,
        token_service=token_service,
        clock=clock,
        unit_of_work=unit_of_work,
        refresh_token_ttl=refresh_token_ttl,
    )


def get_logout_use_case(
    refresh_token_repository: RefreshTokenRepositoryDep,
    session_repository: SessionRepositoryDep,
    clock: ClockDep,
    unit_of_work: UoW,
) -> LogoutUseCase:
    return LogoutUseCase(
        refresh_token_repository=refresh_token_repository,
        session_repository=session_repository,
        clock=clock,
        unit_of_work=unit_of_work,
    )


def get_validate_access_token_use_case(token_service: TokenServiceDep) -> ValidateAccessTokenUseCase:
    return ValidateAccessTokenUseCase(token_service)


LoginUseCaseDep = Annotated[LoginUseCase, Depends(get_login_use_case)]
RefreshTokenUseCaseDep = Annotated[RefreshTokenUseCase, Depends(get_refresh_token_use_case)]
LogoutUseCaseDep = Annotated[LogoutUseCase, Depends(get_logout_use_case)]
ValidateAccessTokenUseCaseDep = Annotated[
    ValidateAccessTokenUseCase, Depends(get_validate_access_token_use_case)
]


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
    use_case: ValidateAccessTokenUseCaseDep,
) -> UUID:
    return await use_case.execute(ValidateAccessTokenInput(access_token=credentials.credentials))


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
