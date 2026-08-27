from datetime import timedelta
from secrets import token_urlsafe
from uuid import UUID

from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authentication.application.dtos.input.login_input import LoginInput
from sentinelcore.modules.authentication.application.dtos.output.token_pair_output import TokenPairOutput
from sentinelcore.modules.authentication.application.ports.clock import Clock
from sentinelcore.modules.authentication.application.ports.refresh_token_repository import (
    RefreshTokenRepository,
)
from sentinelcore.modules.authentication.application.ports.session_repository import SessionRepository
from sentinelcore.modules.authentication.application.ports.token_service import TokenService
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.authentication.domain.errors.invalid_credentials_error import (
    InvalidCredentialsError,
)
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token
from sentinelcore.modules.identity.application.ports.password_hasher import PasswordHasher
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.modules.identity.domain.enums.user_status import UserStatus
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase
from sentinelcore.shared.domain.errors.validation_error import ValidationError


class LoginUseCase(UseCase[LoginInput, TokenPairOutput]):
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        session_repository: SessionRepository,
        refresh_token_repository: RefreshTokenRepository,
        token_service: TokenService,
        clock: Clock,
        unit_of_work: UnitOfWork,
        refresh_token_ttl: timedelta,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._session_repository = session_repository
        self._refresh_token_repository = refresh_token_repository
        self._token_service = token_service
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._refresh_token_ttl = refresh_token_ttl
        self._audit_log_repository = audit_log_repository

    async def _record_login_failure(self, user_id: UUID | None, input_data: LoginInput) -> None:
        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.LOGIN_FAILURE,
                actor_id=user_id,
                target_id=user_id,
                ip_address=input_data.ip_address,
                user_agent=input_data.user_agent,
                metadata={"email": input_data.email},
            )
        )
        await self._unit_of_work.commit()

    async def execute(self, input_data: LoginInput) -> TokenPairOutput:
        try:
            email = Email(input_data.email)
        except ValidationError as exc:
            await self._record_login_failure(None, input_data)
            raise InvalidCredentialsError("Invalid email or password") from exc

        user = await self._user_repository.get_by_email(email)
        if user is None or not self._password_hasher.verify(input_data.password, user.password_hash):
            await self._record_login_failure(user.id if user is not None else None, input_data)
            raise InvalidCredentialsError("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            await self._record_login_failure(user.id, input_data)
            raise InvalidCredentialsError("Invalid email or password")

        now = self._clock.now()

        session = Session.start(
            user_id=user.id,
            started_at=now,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
        )
        await self._session_repository.add(session)

        access_token = self._token_service.create_access_token(subject=str(user.id))
        raw_refresh_token = token_urlsafe(32)

        refresh_token = RefreshToken.issue(
            session_id=session.id,
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh_token),
            issued_at=now,
            expires_at=now + self._refresh_token_ttl,
        )
        await self._refresh_token_repository.add(refresh_token)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.LOGIN_SUCCESS,
                actor_id=user.id,
                target_id=user.id,
                ip_address=input_data.ip_address,
                user_agent=input_data.user_agent,
            )
        )

        await self._unit_of_work.commit()

        return TokenPairOutput(access_token=access_token, refresh_token=raw_refresh_token)
