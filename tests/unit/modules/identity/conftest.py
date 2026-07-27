from uuid import UUID

import pytest

from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email


class FakeUserRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def get_by_id(self, entity_id: UUID) -> User | None:
        return self._users.get(entity_id)

    async def get_by_email(self, email: Email) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def add(self, entity: User) -> None:
        self._users[entity.id] = entity

    async def update(self, entity: User) -> None:
        self._users[entity.id] = entity

    async def delete(self, entity_id: UUID) -> None:
        self._users.pop(entity_id, None)


class FakePasswordHasher:
    def hash(self, plain_password: str) -> str:
        return f"hashed::{plain_password}"

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return password_hash == f"hashed::{plain_password}"


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()
