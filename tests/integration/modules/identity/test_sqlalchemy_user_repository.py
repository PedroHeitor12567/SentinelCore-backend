from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sentinelcore.infrastructure.database.base import Base
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.modules.identity.infrastructure.repository.sql_alchemy_user_repository import SqlAlchemyUserRepository


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_factory() as db_session:
        yield db_session

    await engine.dispose()


async def test_add_and_get_by_id_round_trip(session: AsyncSession) -> None:
    repository = SqlAlchemyUserRepository(session)
    user = User.create(email=Email("user@example.com"), password_hash="hashed")

    await repository.add(user)
    await session.commit()

    fetched = await repository.get_by_id(user.id)

    assert fetched is not None
    assert str(fetched.email) == "user@example.com"
    assert fetched.status == user.status


async def test_get_by_email_finds_existing_user(session: AsyncSession) -> None:
    repository = SqlAlchemyUserRepository(session)
    user = User.create(email=Email("findme@example.com"), password_hash="hashed")
    await repository.add(user)
    await session.commit()

    fetched = await repository.get_by_email(Email("findme@example.com"))

    assert fetched is not None
    assert fetched.id == user.id


async def test_get_by_email_returns_none_when_not_found(session: AsyncSession) -> None:
    repository = SqlAlchemyUserRepository(session)

    fetched = await repository.get_by_email(Email("missing@example.com"))

    assert fetched is None


async def test_update_persists_status_change(session: AsyncSession) -> None:
    repository = SqlAlchemyUserRepository(session)
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    await repository.add(user)
    await session.commit()

    user.activate()
    await repository.update(user)
    await session.commit()

    fetched = await repository.get_by_id(user.id)
    assert fetched is not None
    assert fetched.status == user.status


async def test_delete_removes_user(session: AsyncSession) -> None:
    repository = SqlAlchemyUserRepository(session)
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    await repository.add(user)
    await session.commit()

    await repository.delete(user.id)
    await session.commit()

    fetched = await repository.get_by_id(user.id)
    assert fetched is None
