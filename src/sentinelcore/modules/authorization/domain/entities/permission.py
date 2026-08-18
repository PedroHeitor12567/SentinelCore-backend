from datetime import datetime, UTC
from uuid import UUID, uuid4

from sentinelcore.shared.domain.entity import Entity


class Permission(Entity):
    def __init__(self, id: UUID, code: str, description: str, created_at: datetime) -> None:
        super().__init__(id)
        self.code = code
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, code: str, description: str) -> "Permission":
        return cls(id=uuid4(), code=code, description=description, created_at=datetime.now(UTC))
