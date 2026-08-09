from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sentinelcore.modules.authorization.domain.entities.permission import Permission


@dataclass(frozen=True)
class PermissionOutput:
    id: UUID
    code: str
    description: str
    created_at: datetime

    @classmethod
    def from_permission(cls, permission: Permission) -> "PermissionOutput":
        return cls(
            id=permission.id,
            code=permission.code,
            description=permission.description,
            created_at=permission.created_at,
        )
