from uuid import uuid4

import pytest

from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.sessions.application.dtos.input.revoke_session_input import (
    RevokeSessionInput,
)
from sentinelcore.modules.sessions.application.use_cases.revoke_session_use_case import (
    RevokeSessionUseCase,
)
from sentinelcore.modules.sessions.domain.errors.session_not_found_error import SessionNotFoundError


async def test_revoke_session_marks_it_as_revoked(session_repository, clock, unit_of_work, audit_log_repository) -> None:
    user_id = uuid4()
    session = Session.start(user_id=user_id, started_at=clock.now())
    await session_repository.add(session)
    use_case = RevokeSessionUseCase(session_repository, clock, unit_of_work, audit_log_repository)

    await use_case.execute(RevokeSessionInput(user_id=user_id, session_id=session.id))

    reloaded = await session_repository.get_by_id(session.id)
    assert reloaded.is_revoked is True
    assert unit_of_work.committed is True


async def test_revoke_unknown_session_raises_not_found(session_repository, clock, unit_of_work, audit_log_repository) -> None:
    use_case = RevokeSessionUseCase(session_repository, clock, unit_of_work, audit_log_repository)

    with pytest.raises(SessionNotFoundError):
        await use_case.execute(RevokeSessionInput(user_id=uuid4(), session_id=uuid4()))


async def test_revoke_session_belonging_to_another_user_raises_not_found(
    session_repository, clock, unit_of_work, audit_log_repository
) -> None:
    owner_id = uuid4()
    attacker_id = uuid4()
    session = Session.start(user_id=owner_id, started_at=clock.now())
    await session_repository.add(session)
    use_case = RevokeSessionUseCase(session_repository, clock, unit_of_work, audit_log_repository)

    with pytest.raises(SessionNotFoundError):
        await use_case.execute(RevokeSessionInput(user_id=attacker_id, session_id=session.id))

    reloaded = await session_repository.get_by_id(session.id)
    assert reloaded.is_revoked is False


async def test_revoke_already_revoked_session_is_idempotent(session_repository, clock, unit_of_work, audit_log_repository) -> None:
    user_id = uuid4()
    session = Session.start(user_id=user_id, started_at=clock.now())
    session.revoke(at=clock.now())
    await session_repository.add(session)
    use_case = RevokeSessionUseCase(session_repository, clock, unit_of_work, audit_log_repository)

    await use_case.execute(RevokeSessionInput(user_id=user_id, session_id=session.id))

    assert unit_of_work.committed is False
