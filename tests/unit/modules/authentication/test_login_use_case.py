from datetime import timedelta

import pytest

from sentinelcore.modules.authentication.application.dtos.input.login_input import LoginInput
from sentinelcore.modules.authentication.application.use_cases.login_use_case import LoginUseCase
from sentinelcore.modules.authentication.domain.errors.invalid_credentials_error import (
    InvalidCredentialsError,
)
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email

_TTL = timedelta(days=7)


def _build_use_case(
    user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
) -> LoginUseCase:
    return LoginUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        session_repository=session_repository,
        refresh_token_repository=refresh_token_repository,
        token_service=token_service,
        clock=clock,
        unit_of_work=unit_of_work,
        refresh_token_ttl=_TTL,
    )


async def test_login_with_valid_credentials_returns_token_pair(
    user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    user = User.create(email=Email("user@example.com"), password_hash=password_hasher.hash("s3cr3t!!"))
    user.activate()
    await user_repository.add(user)
    use_case = _build_use_case(
        user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
    )

    output = await use_case.execute(
        LoginInput(email="user@example.com", password="s3cr3t!!", ip_address="203.0.113.1", user_agent="curl/8.0")
    )

    assert output.access_token == f"access-token::{user.id}"
    assert output.token_type == "bearer"
    assert unit_of_work.committed is True

    sessions = await session_repository.list_by_user_id(user.id)
    assert len(sessions) == 1
    assert sessions[0].ip_address == "203.0.113.1"
    assert sessions[0].user_agent == "curl/8.0"


async def test_login_with_wrong_password_raises_invalid_credentials(
    user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    user = User.create(email=Email("user@example.com"), password_hash=password_hasher.hash("s3cr3t!!"))
    user.activate()
    await user_repository.add(user)
    use_case = _build_use_case(
        user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(LoginInput(email="user@example.com", password="wrong-password"))


async def test_login_with_unknown_email_raises_invalid_credentials(
    user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    use_case = _build_use_case(
        user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(LoginInput(email="missing@example.com", password="s3cr3t!!"))


async def test_login_with_pending_user_raises_invalid_credentials(
    user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    user = User.create(email=Email("pending@example.com"), password_hash=password_hasher.hash("s3cr3t!!"))
    await user_repository.add(user)
    use_case = _build_use_case(
        user_repository, password_hasher, session_repository, refresh_token_repository, token_service, clock, unit_of_work
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(LoginInput(email="pending@example.com", password="s3cr3t!!"))
