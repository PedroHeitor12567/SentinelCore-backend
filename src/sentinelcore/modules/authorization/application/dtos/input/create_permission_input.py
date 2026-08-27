from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreatePermissionInput:
    code: str
    description: str
    actor_id: UUID | None = None
