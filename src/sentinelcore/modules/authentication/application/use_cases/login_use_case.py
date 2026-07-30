from datetime import timedelta
from secrets import token_urlsafe

from sentinelcore.modules.authentication.application.dtos.input.login_input import LoginInput
from sentinelcore.modules.authentication.application.dtos.output.token_pair_output import TokenPairOutput
from sentinelcore.modules.authentication.application.ports.clock import Clock
from sentinelcore.modules.authentication.application.ports.refresh_token_repository import RefreshTokenRepository
from sentinelcore.modules.authentication.application.ports.token_service import TokenService
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.errors.invalid_credentials_error import InvalidCredentialsError
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token
from sentinelcore.modules.identity.application.ports.password_hasher import PasswordHasher
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.modules.identity.domain.enums.user_status import UserStatus
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase
from sentinelcore.shared.domain.errors.validation_error import ValidationError


class LoginUseCase(UseCase[LoginInput, TokenPairOutput]):
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher, refresh_token_repository: RefreshTokenRepository, token_service: TokenService, clock: Clock, unit_of_work: UnitOfWork, refresh_token_ttl: timedelta) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._refresh_token_repository = refresh_token_repository
        self._token_service = token_service
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._refresh_token_ttl = refresh_token_ttl

    async def execute(self, input_data: LoginInput) -> TokenPairOutput:
        try:
            email = Email(input_data.email)
        except ValidationError as exc:
            raise InvalidCredentialsError("Invalid email or password") from exc

        user = await self._user_repository.get_by_email(email)
        if user is None or not self._password_hasher.verify(input_data.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsError("Invalid email or password")

        now = self._clock.now()
        access_token = self._token_service.create_access_token(subject=str(user.id))
        raw_refresh_token = token_urlsafe(32)

        refresh_token = RefreshToken.issue(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh_token),
            issued_at=now,
            expires_at=now + self._refresh_token_ttl,
        )
        await self._refresh_token_repository.add(refresh_token)
        await self._unit_of_work.commit()

        return TokenPairOutput(access_token=access_token, refresh_token=raw_refresh_token)
