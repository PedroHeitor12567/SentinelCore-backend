from datetime import timedelta
from uuid import uuid4

import pytest

from sentinelcore.modules.authentication.application.dtos.input.logout_input import LogoutInput
from sentinelcore.modules.authentication.application.use_cases.logout_use_case import LogoutUseCase
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.errors.invalid_refresh_token_error import InvalidRefreshTokenError
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token

_TTL = timedelta(days=7)


async def test_logout_with_valid_token_revokes_it(refresh_token_repository, clock, unit_of_work) -> None:
    raw_token = "raw-refresh-token"
    stored = RefreshToken.issue(
        user_id=uuid4(),
        token_hash=hash_refresh_token(raw_token),
        issued_at=clock.now(),
        expires_at=clock.now() + _TTL,
    )
    await refresh_token_repository.add(stored)
    use_case = LogoutUseCase(refresh_token_repository, clock, unit_of_work)

    await use_case.execute(LogoutInput(refresh_token=raw_token))

    revoked = await refresh_token_repository.get_by_token_hash(hash_refresh_token(raw_token))
    assert revoked.is_revoked is True
    assert unit_of_work.committed is True


async def test_logout_with_unknown_token_raises_invalid_refresh_token(
    refresh_token_repository, clock, unit_of_work
) -> None:
    use_case = LogoutUseCase(refresh_token_repository, clock, unit_of_work)

    with pytest.raises(InvalidRefreshTokenError):
        await use_case.execute(LogoutInput(refresh_token="unknown-token"))


async def test_logout_with_already_revoked_token_is_idempotent(
    refresh_token_repository, clock, unit_of_work
) -> None:
    raw_token = "raw-refresh-token"
    stored = RefreshToken.issue(
        user_id=uuid4(),
        token_hash=hash_refresh_token(raw_token),
        issued_at=clock.now(),
        expires_at=clock.now() + _TTL,
    )
    stored.revoke(at=clock.now())
    await refresh_token_repository.add(stored)
    use_case = LogoutUseCase(refresh_token_repository, clock, unit_of_work)

    await use_case.execute(LogoutInput(refresh_token=raw_token))

    assert unit_of_work.committed is False
