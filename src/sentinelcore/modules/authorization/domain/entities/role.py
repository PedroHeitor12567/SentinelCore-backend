from datetime import datetime, UTC
from uuid import UUID, uuid4

from sentinelcore.shared.domain.entity import Entity


class Role(Entity):
    def __init__(self, id: UUID, name: str, description: str, permission_ids: set[UUID], created_at: datetime) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.permission_ids = set(permission_ids)
        self.created_at = created_at

    @classmethod
    def create(cls, name: str, description: str) -> "Role":
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            permission_ids=set(),
            created_at=datetime.now(UTC)
        )

    def grant_permission(self, permission_id: UUID) -> None:
        self.permission_ids.add(permission_id)

    def revoke_permission(self, permission_id: UUID) -> None:
        self.permission_ids.discard(permission_id)
