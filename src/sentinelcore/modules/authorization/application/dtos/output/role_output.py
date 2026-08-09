from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sentinelcore.modules.authorization.domain.entities.role import Role


@dataclass(frozen=True)
class RoleOutput:
    id: UUID
    name: str
    description: str
    permission_ids: list[UUID]
    created_at: datetime

    @classmethod
    def from_role(cls, role: Role) -> "RoleOutput":
        return cls(
            id=role.id,
            name=role.name,
            description=role.description,
            permission_ids=sorted(role.permission_ids, key=str),
            created_at=role.created_at,
        )
