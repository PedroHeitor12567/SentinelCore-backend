from datetime import timedelta
from secrets import token_urlsafe

from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authentication.application.dtos.input.refresh_token_input import (
    RefreshTokenInput,
)
from sentinelcore.modules.authentication.application.dtos.output.token_pair_output import TokenPairOutput
from sentinelcore.modules.authentication.application.ports.clock import Clock
from sentinelcore.modules.authentication.application.ports.refresh_token_repository import (
    RefreshTokenRepository,
)
from sentinelcore.modules.authentication.application.ports.session_repository import SessionRepository
from sentinelcore.modules.authentication.application.ports.token_service import TokenService
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.errors.invalid_refresh_token_error import (
    InvalidRefreshTokenError,
)
from sentinelcore.modules.authentication.domain.errors.refresh_token_expired_error import (
    RefreshTokenExpiredError,
)
from sentinelcore.modules.authentication.domain.errors.refresh_token_reuse_detected_error import (
    RefreshTokenReuseDetectedError,
)
from sentinelcore.modules.authentication.domain.errors.session_revoked_error import SessionRevokedError
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class RefreshTokenUseCase(UseCase[RefreshTokenInput, TokenPairOutput]):
    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
        session_repository: SessionRepository,
        token_service: TokenService,
        clock: Clock,
        unit_of_work: UnitOfWork,
        refresh_token_ttl: timedelta,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._refresh_token_repository = refresh_token_repository
        self._session_repository = session_repository
        self._token_service = token_service
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._refresh_token_ttl = refresh_token_ttl
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: RefreshTokenInput) -> TokenPairOutput:
        token_hash = hash_refresh_token(input_data.refresh_token)
        stored_token = await self._refresh_token_repository.get_by_token_hash(token_hash)
        if stored_token is None:
            raise InvalidRefreshTokenError("Refresh token not recognized")

        now = self._clock.now()

        session = await self._session_repository.get_by_id(stored_token.session_id)
        if session is None or session.is_revoked:
            raise SessionRevokedError("Session has been revoked")

        if stored_token.is_revoked:
            await self._session_repository.revoke_all_for_user(session.user_id, now)
            await self._unit_of_work.commit()
            raise RefreshTokenReuseDetectedError(
                "Refresh token reuse detected; all sessions have been revoked"
            )

        if stored_token.is_expired(now):
            raise RefreshTokenExpiredError("Refresh token has expired")

        raw_refresh_token = token_urlsafe(32)
        new_refresh_token = RefreshToken.issue(
            session_id=session.id,
            user_id=session.user_id,
            token_hash=hash_refresh_token(raw_refresh_token),
            issued_at=now,
            expires_at=now + self._refresh_token_ttl,
        )
        await self._refresh_token_repository.add(new_refresh_token)

        stored_token.revoke(at=now, replaced_by_id=new_refresh_token.id)
        await self._refresh_token_repository.update(stored_token)

        session.touch(at=now, ip_address=input_data.ip_address, user_agent=input_data.user_agent)
        await self._session_repository.update(session)

        access_token = self._token_service.create_access_token(subject=str(session.user_id))

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.TOKEN_REFRESHED,
                actor_id=session.user_id,
                target_id=session.id,
                metadata={"session_id": str(session.id)},
            )
        )

        await self._unit_of_work.commit()

        return TokenPairOutput(access_token=access_token, refresh_token=raw_refresh_token)
