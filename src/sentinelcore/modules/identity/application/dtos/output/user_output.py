from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sentinelcore.modules.identity.domain.entities.user import User


@dataclass(frozen=True)
class UserOutput:
    id: UUID
    email: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserOutput":
        return cls(
            id=user.id,
            email=str(user.email),
            status=str(user.status),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
