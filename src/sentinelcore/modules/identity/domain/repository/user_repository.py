from typing import Protocol

from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.shared.application.ports import Repository


class UserRepository(Repository[User], Protocol):
    async def get_by_email(self, email: Email) -> User | None: ...
