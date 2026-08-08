from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sentinelcore.infrastructure.database.base import Base
from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.authentication.infrastructure.repository.sql_alchemy_refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
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


async def _new_session_and_token(db_session: AsyncSession, now: datetime) -> tuple[Session, RefreshToken]:
    session_repository = SqlAlchemySessionRepository(db_session)
    user_id = uuid4()
    device_session = Session.start(user_id=user_id, started_at=now)
    await session_repository.add(device_session)

    token = RefreshToken.issue(
        session_id=device_session.id,
        user_id=user_id,
        token_hash=f"hash-{uuid4()}",
        issued_at=now,
        expires_at=now + timedelta(days=7),
    )
    return device_session, token


async def test_add_and_get_by_token_hash_round_trip(session: AsyncSession) -> None:
    repository = SqlAlchemyRefreshTokenRepository(session)
    now = datetime.now(UTC)
    device_session, token = await _new_session_and_token(session, now)

    await repository.add(token)
    await session.commit()

    fetched = await repository.get_by_token_hash(token.token_hash)

    assert fetched is not None
    assert fetched.id == token.id
    assert fetched.session_id == device_session.id
    assert fetched.is_revoked is False


async def test_get_by_token_hash_returns_none_when_not_found(session: AsyncSession) -> None:
    repository = SqlAlchemyRefreshTokenRepository(session)

    fetched = await repository.get_by_token_hash("missing-hash")

    assert fetched is None


async def test_update_persists_revocation_and_replacement(session: AsyncSession) -> None:
    repository = SqlAlchemyRefreshTokenRepository(session)
    now = datetime.now(UTC)
    _, token = await _new_session_and_token(session, now)
    await repository.add(token)
    await session.commit()

    replacement_id = uuid4()
    token.revoke(at=now + timedelta(minutes=1), replaced_by_id=replacement_id)
    await repository.update(token)
    await session.commit()

    fetched = await repository.get_by_token_hash(token.token_hash)
    assert fetched is not None
    assert fetched.is_revoked is True
    assert fetched.replaced_by_id == replacement_id
