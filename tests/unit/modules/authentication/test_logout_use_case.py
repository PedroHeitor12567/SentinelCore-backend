from datetime import timedelta
from uuid import uuid4

import pytest

from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authentication.application.dtos.input.logout_input import LogoutInput
from sentinelcore.modules.authentication.application.use_cases.logout_use_case import LogoutUseCase
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.authentication.domain.errors.invalid_refresh_token_error import (
    InvalidRefreshTokenError,
)
from sentinelcore.modules.authentication.domain.errors.refresh_token_reuse_detected_error import (
    RefreshTokenReuseDetectedError,
)
from sentinelcore.modules.authentication.domain.services.token_hasher import hash_refresh_token

_TTL = timedelta(days=7)


async def _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token: str):
    user_id = uuid4()
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


async def test_logout_with_valid_token_revokes_the_session(
    refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository
) -> None:
    raw_token = "raw-refresh-token"
    session, _ = await _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token)
    use_case = LogoutUseCase(refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository)

    await use_case.execute(LogoutInput(refresh_token=raw_token))

    reloaded_session = await session_repository.get_by_id(session.id)
    assert reloaded_session.is_revoked is True
    assert unit_of_work.committed is True
    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.LOGOUT
    assert log.actor_id == session.user_id
    assert log.target_id == session.id


async def test_logout_with_unknown_token_raises_invalid_refresh_token(
    refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository
) -> None:
    use_case = LogoutUseCase(refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository)

    with pytest.raises(InvalidRefreshTokenError):
        await use_case.execute(LogoutInput(refresh_token="unknown-token"))

    assert len(audit_log_repository.logs) == 0


async def test_logout_with_already_revoked_session_is_idempotent(
    refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository
) -> None:
    raw_token = "raw-refresh-token"
    session, _ = await _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token)
    session.revoke(at=clock.now())
    await session_repository.update(session)
    use_case = LogoutUseCase(refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository)

    await use_case.execute(LogoutInput(refresh_token=raw_token))

    assert unit_of_work.committed is False
    assert len(audit_log_repository.logs) == 0


async def test_logout_with_rotated_out_token_detects_reuse_and_revokes_session(
    refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository
) -> None:
    raw_token = "raw-refresh-token"
    session, token = await _start_session_with_token(session_repository, refresh_token_repository, clock, raw_token)
    token.revoke(at=clock.now(), replaced_by_id=uuid4())
    await refresh_token_repository.update(token)
    use_case = LogoutUseCase(refresh_token_repository, session_repository, clock, unit_of_work, audit_log_repository)

    with pytest.raises(RefreshTokenReuseDetectedError):
        await use_case.execute(LogoutInput(refresh_token=raw_token))

    reloaded_session = await session_repository.get_by_id(session.id)
    assert reloaded_session.is_revoked is True
    assert len(audit_log_repository.logs) == 0
