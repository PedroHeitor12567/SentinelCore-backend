from sentinelcore.modules.authentication.application.dtos.input.logout_input import LogoutInput
from sentinelcore.modules.authentication.application.ports.clock import Clock
from sentinelcore.modules.authentication.application.ports.refresh_token_repository import RefreshTokenRepository
from sentinelcore.modules.authentication.domain.errors.invalid_refresh_token_error import InvalidRefreshTokenError
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class LogoutUseCase(UseCase[LogoutInput, None]):
    def __init__(self, refresh_token_repository: RefreshTokenRepository, clock: Clock, unit_of_work: UnitOfWork) -> None:
        self._refresh_token_repository = refresh_token_repository
        self._clock = clock
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: LogoutInput) -> None:
        token_hash = hash_refresh_token(input_data.refresh_token)
        stored_token = await self._refresh_token_repository.get_by_token_hash(token_hash)
        if stored_token is None:
            raise InvalidRefreshTokenError("Refresh token not recognized")

        if not stored_token.is_revoked:
            stored_token.revoke(at=self._clock.now())
            await self._refresh_token_repository.update(stored_token)
            await self._unit_of_work.commit()
