from uuid import UUID

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
