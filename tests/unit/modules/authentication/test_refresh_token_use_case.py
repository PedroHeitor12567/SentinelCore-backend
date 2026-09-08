from datetime import timedelta
from uuid import uuid4

import pytest

from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authentication.application.dtos.input.refresh_token_input import (
    RefreshTokenInput,
)
from sentinelcore.modules.authentication.application.use_cases.refresh_token_use_case import (
    RefreshTokenUseCase,
)
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.authentication.domain.errors.invalid_refresh_token_error import (
    InvalidRefreshTokenError,
)
from sentinelcore.modules.authentication.domain.errors.refresh_token_expired_error import (
    RefreshTokenExpiredError,
)
from sentinelcore.modules.authentication.domain.errors.refresh_token_reuse_detected_error import (
    RefreshTokenReuseDetectedError,
)
from sentinelcore.modules.authentication.domain.errors.session_revoked_error import (
    SessionRevokedError,
)
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token

_TTL = timedelta(days=7)


def _build_use_case(
    refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        refresh_token_repository=refresh_token_repository,
        session_repository=session_repository,
        token_service=token_service,
        clock=clock,
        unit_of_work=unit_of_work,
        refresh_token_ttl=_TTL,
        audit_log_repository=audit_log_repository,
    )


async def _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token: str, user_id=None):
    user_id = user_id or uuid4()
    session = Session.start(user_id=user_id, started_at=clock.now())
    await session_repository.add(session)
    token = RefreshToken.issue(
        session_id=session.id,
        user_id=user_id,
        token_hash=hash_refresh_token(raw_token),
        issued_at=clock.now(),
        expires_at=clock.now() + _TTL,
    )
    await refresh_token_repository.add(token)
    return session, token


async def test_refresh_with_unknown_token_raises_invalid_refresh_token(
    refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
) -> None:
    use_case = _build_use_case(
        refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
    )

    with pytest.raises(InvalidRefreshTokenError):
        await use_case.execute(RefreshTokenInput(refresh_token="unknown-token"))

    assert len(audit_log_repository.logs) == 0


async def test_refresh_with_valid_token_rotates_and_revokes_old_token(
    refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
) -> None:
    raw_token = "raw-refresh-token"
    session, _old_token = await _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token)
    use_case = _build_use_case(
        refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
    )

    output = await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    assert output.refresh_token != raw_token
    reloaded_old = await refresh_token_repository.get_by_token_hash(hash_refresh_token(raw_token))
    assert reloaded_old.is_revoked is True
    new_token = await refresh_token_repository.get_by_token_hash(hash_refresh_token(output.refresh_token))
    assert new_token is not None
    assert new_token.is_revoked is False
    assert new_token.session_id == session.id
    assert reloaded_old.replaced_by_id == new_token.id

    reloaded_session = await session_repository.get_by_id(session.id)
    assert reloaded_session.is_revoked is False
    assert reloaded_session.last_seen_at == clock.now()

    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.TOKEN_REFRESHED
    assert log.actor_id == session.user_id
    assert log.target_id == session.id


async def test_refresh_with_expired_token_raises_expired_error(
    refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
) -> None:
    raw_token = "raw-refresh-token"
    user_id = uuid4()
    session = Session.start(user_id=user_id, started_at=clock.now() - _TTL - timedelta(days=1))
    await session_repository.add(session)
    token = RefreshToken.issue(
        session_id=session.id,
        user_id=user_id,
        token_hash=hash_refresh_token(raw_token),
        issued_at=clock.now() - _TTL - timedelta(days=1),
        expires_at=clock.now() - timedelta(days=1),
    )
    await refresh_token_repository.add(token)
    use_case = _build_use_case(
        refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
    )

    with pytest.raises(RefreshTokenExpiredError):
        await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    assert len(audit_log_repository.logs) == 0


async def test_reusing_an_already_rotated_token_revokes_the_session(
    refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
) -> None:
    raw_token = "raw-refresh-token"
    session, _ = await _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token)
    use_case = _build_use_case(
        refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
    )

    await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    with pytest.raises(RefreshTokenReuseDetectedError):
        await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    reloaded_session = await session_repository.get_by_id(session.id)
    assert reloaded_session.is_revoked is True
    assert len(audit_log_repository.logs) == 1
    assert audit_log_repository.logs[0].event_type == AuditEventType.TOKEN_REFRESHED


async def test_refresh_with_token_from_revoked_session_raises_session_revoked(
    refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
) -> None:
    raw_token = "raw-refresh-token"
    session, _ = await _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token)
    session.revoke(at=clock.now())
    await session_repository.update(session)
    use_case = _build_use_case(
        refresh_token_repository, session_repository, token_service, clock, unit_of_work, audit_log_repository
    )

    with pytest.raises(SessionRevokedError):
        await use_case.execute(RefreshTokenInput(refresh_token=raw_token))

    assert len(audit_log_repository.logs) == 0
