from datetime import timedelta
from uuid import uuid4

import pytest

from sentinelcore.modules.authentication.application.dtos.input.refresh_token_input import RefreshTokenInput
from sentinelcore.modules.authentication.application.use_cases.refresh_token_use_case import RefreshTokenUseCase
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
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token

_TTL = timedelta(days=7)


def _build_use_case(refresh_token_repository, token_service, clock, unit_of_work) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        refresh_token_repository=refresh_token_repository,
        token_service=token_service,
        clock=clock,
        unit_of_work=unit_of_work,
        refresh_token_ttl=_TTL,
    )


async def test_refresh_with_unknown_token_raises_invalid_refresh_token(
    refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    use_case = _build_use_case(refresh_token_repository, token_service, clock, unit_of_work)

    with pytest.raises(InvalidRefreshTokenError):
        await use_case.execute(RefreshTokenInput(refresh_token="unknown-token"))


async def test_refresh_with_valid_token_rotates_and_revokes_old_token(
    refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    raw_token = "raw-refresh-token"
    stored = RefreshToken.issue(
        user_id=uuid4(),
        token_hash=hash_refresh_token(raw_token),
        issued_at=clock.now(),
        expires_at=clock.now() + _TTL,
    )
    await refresh_token_repository.add(stored)
    use_case = _build_use_case(refresh_token_repository, token_service, clock, unit_of_work)

    output = await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    assert output.refresh_token != raw_token
    old_token = await refresh_token_repository.get_by_token_hash(hash_refresh_token(raw_token))
    assert old_token.is_revoked is True
    new_token = await refresh_token_repository.get_by_token_hash(hash_refresh_token(output.refresh_token))
    assert new_token is not None
    assert new_token.is_revoked is False
    assert old_token.replaced_by_id == new_token.id


async def test_refresh_with_expired_token_raises_expired_error(
    refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    raw_token = "raw-refresh-token"
    stored = RefreshToken.issue(
        user_id=uuid4(),
        token_hash=hash_refresh_token(raw_token),
        issued_at=clock.now() - _TTL - timedelta(days=1),
        expires_at=clock.now() - timedelta(days=1),
    )
    await refresh_token_repository.add(stored)
    use_case = _build_use_case(refresh_token_repository, token_service, clock, unit_of_work)

    with pytest.raises(RefreshTokenExpiredError):
        await use_case.execute(RefreshTokenInput(refresh_token=raw_token))


async def test_reusing_an_already_rotated_token_revokes_all_sessions(
    refresh_token_repository, token_service, clock, unit_of_work
) -> None:
    raw_token = "raw-refresh-token"
    user_id = uuid4()
    stored = RefreshToken.issue(
        user_id=user_id,
        token_hash=hash_refresh_token(raw_token),
        issued_at=clock.now(),
        expires_at=clock.now() + _TTL,
    )
    await refresh_token_repository.add(stored)
    use_case = _build_use_case(refresh_token_repository, token_service, clock, unit_of_work)

    first_output = await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    with pytest.raises(RefreshTokenReuseDetectedError):
        await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    new_token = await refresh_token_repository.get_by_token_hash(
        hash_refresh_token(first_output.refresh_token)
    )
    assert new_token.is_revoked is True
