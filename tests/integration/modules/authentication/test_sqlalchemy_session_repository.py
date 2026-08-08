from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sentinelcore.infrastructure.database.base import Base
from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.authentication.infrastructure.repository.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from sentinelcore.modules.identity.infrastructure.models.user_model import UserModel  # noqa: F401


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as db_session:
        yield db_session

    await engine.dispose()


def _new_session(user_id, now: datetime, **kwargs) -> Session:
    return Session.start(user_id=user_id, started_at=now, **kwargs)


async def test_add_and_get_by_id_round_trip(session: AsyncSession) -> None:
    repository = SqlAlchemySessionRepository(session)
    now = datetime.now(UTC)
    device_session = _new_session(uuid4(), now, ip_address="203.0.113.1", user_agent="curl/8.0")

    await repository.add(device_session)
    await session.commit()

    fetched = await repository.get_by_id(device_session.id)

    assert fetched is not None
    assert fetched.ip_address == "203.0.113.1"
    assert fetched.user_agent == "curl/8.0"
    assert fetched.is_revoked is False


async def test_list_by_user_id_returns_only_that_users_sessions(session: AsyncSession) -> None:
    repository = SqlAlchemySessionRepository(session)
    now = datetime.now(UTC)
    user_id = uuid4()
    other_user_id = uuid4()

    own_session = _new_session(user_id, now)
    other_session = _new_session(other_user_id, now)
    await repository.add(own_session)
    await repository.add(other_session)
    await session.commit()

    result = await repository.list_by_user_id(user_id)

    assert len(result) == 1
    assert result[0].id == own_session.id


async def test_update_persists_touch_and_revocation(session: AsyncSession) -> None:
    repository = SqlAlchemySessionRepository(session)
    now = datetime.now(UTC)
    device_session = _new_session(uuid4(), now)
    await repository.add(device_session)
    await session.commit()

    device_session.touch(at=now + timedelta(hours=1), ip_address="198.51.100.7")
    await repository.update(device_session)
    await session.commit()

    fetched = await repository.get_by_id(device_session.id)
    assert fetched.last_seen_at == now + timedelta(hours=1)
    assert fetched.ip_address == "198.51.100.7"

    device_session.revoke(at=now + timedelta(hours=2))
    await repository.update(device_session)
    await session.commit()

    fetched_after_revoke = await repository.get_by_id(device_session.id)
    assert fetched_after_revoke.is_revoked is True


async def test_revoke_all_for_user_revokes_only_active_sessions_of_that_user(session: AsyncSession) -> None:
    repository = SqlAlchemySessionRepository(session)
    now = datetime.now(UTC)
    user_id = uuid4()
    other_user_id = uuid4()

    session_1 = _new_session(user_id, now)
    session_2 = _new_session(user_id, now)
    other_user_session = _new_session(other_user_id, now)

    await repository.add(session_1)
    await repository.add(session_2)
    await repository.add(other_user_session)
    await session.commit()

    await repository.revoke_all_for_user(user_id, now + timedelta(minutes=5))
    await session.commit()

    fetched_1 = await repository.get_by_id(session_1.id)
    fetched_2 = await repository.get_by_id(session_2.id)
    fetched_other = await repository.get_by_id(other_user_session.id)

    assert fetched_1.is_revoked is True
    assert fetched_2.is_revoked is True
    assert fetched_other.is_revoked is False
