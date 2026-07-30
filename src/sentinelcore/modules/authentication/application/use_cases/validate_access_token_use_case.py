from uuid import UUID

from sentinelcore.modules.authentication.application.dtos.input.validate_access_token_input import \
    ValidateAccessTokenInput
from sentinelcore.modules.authentication.application.ports.token_service import TokenService, TokenExpiredError, \
    TokenDecodeError
from sentinelcore.modules.authentication.domain.errors.access_token_expired_error import AccessTokenExpiredError
from sentinelcore.modules.authentication.domain.errors.invalid_access_token_error import InvalidAccessTokenError
from sentinelcore.shared.application.use_case import UseCase


class ValidateAccessTokenUseCase(UseCase[ValidateAccessTokenInput, UUID]):
    def __init__(self, token_service: TokenService) -> None:
        self._token_service = token_service

    async def execute(self, input_data: ValidateAccessTokenInput) -> UUID:
        try:
            subject = self._token_service.decode_access_token(input_data.access_token)
        except TokenExpiredError as exc:
            raise AccessTokenExpiredError("Access token has expired") from exc
        except TokenDecodeError as exc:
            raise InvalidAccessTokenError("Access token is invalid") from exc

        try:
            return UUID(subject)
        except ValueError as exc:
            raise InvalidAccessTokenError("Access token subject is invalid") from exc
