from uuid import uuid4

from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.sessions.application.dtos.input.list_sessions_input import (
    ListSessionsInput,
)
from sentinelcore.modules.sessions.application.use_cases.list_sessions_use_case import (
    ListSessionsUseCase,
)


async def test_list_sessions_returns_only_sessions_of_the_given_user(session_repository, clock) -> None:
    user_id = uuid4()
    other_user_id = uuid4()

    own_session = Session.start(
        user_id=user_id, started_at=clock.now(), ip_address="203.0.113.10", user_agent="Mozilla/5.0"
    )
    other_session = Session.start(user_id=other_user_id, started_at=clock.now())
    await session_repository.add(own_session)
    await session_repository.add(other_session)
    use_case = ListSessionsUseCase(session_repository)

    result = await use_case.execute(ListSessionsInput(user_id=user_id))

    assert len(result) == 1
    assert result[0].id == own_session.id
    assert result[0].ip_address == "203.0.113.10"
    assert result[0].user_agent == "Mozilla/5.0"
    assert result[0].is_revoked is False


async def test_list_sessions_returns_empty_list_for_user_without_sessions(session_repository) -> None:
    use_case = ListSessionsUseCase(session_repository)

    result = await use_case.execute(ListSessionsInput(user_id=uuid4()))

    assert result == []


async def test_list_sessions_includes_revoked_sessions(session_repository, clock) -> None:
    user_id = uuid4()
    session = Session.start(user_id=user_id, started_at=clock.now())
    session.revoke(at=clock.now())
    await session_repository.add(session)
    use_case = ListSessionsUseCase(session_repository)

    result = await use_case.execute(ListSessionsInput(user_id=user_id))

    assert len(result) == 1
    assert result[0].is_revoked is True
