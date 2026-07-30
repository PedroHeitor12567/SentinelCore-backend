from datetime import timedelta
from secrets import token_urlsafe

from sentinelcore.modules.authentication.application.dtos.input.refresh_token_input import RefreshTokenInput
from sentinelcore.modules.authentication.application.dtos.output.token_pair_output import TokenPairOutput
from sentinelcore.modules.authentication.application.ports.clock import Clock
from sentinelcore.modules.authentication.application.ports.refresh_token_repository import RefreshTokenRepository
from sentinelcore.modules.authentication.application.ports.token_service import TokenService
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.errors.invalid_refresh_token_error import InvalidRefreshTokenError
from sentinelcore.modules.authentication.domain.errors.refresh_token_expired_error import RefreshTokenExpiredError
from sentinelcore.modules.authentication.domain.errors.refresh_token_reuse_detected_error import RefreshTokenReuseDetectedError
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase



class RefreshTokenUseCase(UseCase[RefreshTokenInput, TokenPairOutput]):
    def __init__(self, refresh_token_repository: RefreshTokenRepository, token_service: TokenService, clock: Clock, unit_of_work: UnitOfWork, refresh_token_ttl: timedelta) -> None:
        self._refresh_token_repository = refresh_token_repository
        self._token_service = token_service
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._refresh_token_ttl = refresh_token_ttl

    async def execute(self, input_data: RefreshTokenInput) -> TokenPairOutput:
        token_hash = hash_refresh_token(input_data.refresh_token)
        stored_token = await self._refresh_token_repository.get_by_token_hash(token_hash)
        if stored_token is None:
            raise InvalidRefreshTokenError("Refresh token not recognized")

        now = self._clock.now()

        if stored_token.is_revoked:
            await self._refresh_token_repository.revoke_all_for_user(stored_token.user_id, now)
            await self._unit_of_work.commit()
            raise RefreshTokenReuseDetectedError(
                "Refresh token reuse detected; all sessions have been revoked"
            )

        if stored_token.is_expired(now):
            raise RefreshTokenExpiredError("Refresh token has expired")

        raw_refresh_token = token_urlsafe(32)
        new_refresh_token = RefreshToken.issue(
            user_id=stored_token.user_id,
            token_hash=hash_refresh_token(raw_refresh_token),
            issued_at=now,
            expires_at=now + self._refresh_token_ttl,
        )
        await self._refresh_token_repository.add(new_refresh_token)

        stored_token.revoke(at=now, replaced_by_id=new_refresh_token.id)
        await self._refresh_token_repository.update(stored_token)

        access_token = self._token_service.create_access_token(subject=str(stored_token.user_id))

        await self._unit_of_work.commit()

        return TokenPairOutput(access_token=access_token, refresh_token=raw_refresh_token)
