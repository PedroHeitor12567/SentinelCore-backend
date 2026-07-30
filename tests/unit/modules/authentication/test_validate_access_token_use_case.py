from uuid import uuid4

import pytest

from sentinelcore.modules.authentication.application.dtos.input.validate_access_token_input import ValidateAccessTokenInput
from sentinelcore.modules.authentication.application.ports.token_service import (
    TokenDecodeError,
    TokenExpiredError,
)
from sentinelcore.modules.authentication.application.use_cases.validate_access_token_use_case import (
    ValidateAccessTokenUseCase,
)
from sentinelcore.modules.authentication.domain.errors.access_token_expired_error import (
    AccessTokenExpiredError,
)
from sentinelcore.modules.authentication.domain.errors.invalid_access_token_error import (
    InvalidAccessTokenError,
)


class _ExpiredTokenService:
    def create_access_token(self, subject: str) -> str:
        raise NotImplementedError

    def decode_access_token(self, token: str) -> str:
        raise TokenExpiredError


class _InvalidTokenService:
    def create_access_token(self, subject: str) -> str:
        raise NotImplementedError

    def decode_access_token(self, token: str) -> str:
        raise TokenDecodeError


class _NonUuidSubjectTokenService:
    def create_access_token(self, subject: str) -> str:
        raise NotImplementedError

    def decode_access_token(self, token: str) -> str:
        return "not-a-uuid"


async def test_validate_access_token_returns_user_id(token_service) -> None:
    user_id = uuid4()
    token = token_service.create_access_token(subject=str(user_id))
    use_case = ValidateAccessTokenUseCase(token_service)

    result = await use_case.execute(ValidateAccessTokenInput(access_token=token))

    assert result == user_id


async def test_validate_expired_access_token_raises_expired_error() -> None:
    use_case = ValidateAccessTokenUseCase(_ExpiredTokenService())

    with pytest.raises(AccessTokenExpiredError):
        await use_case.execute(ValidateAccessTokenInput(access_token="expired"))


async def test_validate_invalid_access_token_raises_invalid_error() -> None:
    use_case = ValidateAccessTokenUseCase(_InvalidTokenService())

    with pytest.raises(InvalidAccessTokenError):
        await use_case.execute(ValidateAccessTokenInput(access_token="garbage"))


async def test_validate_access_token_with_non_uuid_subject_raises_invalid_error() -> None:
    use_case = ValidateAccessTokenUseCase(_NonUuidSubjectTokenService())

    with pytest.raises(InvalidAccessTokenError):
        await use_case.execute(ValidateAccessTokenInput(access_token="whatever"))
