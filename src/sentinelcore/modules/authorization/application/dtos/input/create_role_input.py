from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateRoleInput:
    name: str
    description: str
    actor_id: UUID | None = None
