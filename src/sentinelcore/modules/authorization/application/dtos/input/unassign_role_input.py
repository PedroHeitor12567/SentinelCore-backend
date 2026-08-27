from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UnassignRoleInput:
    user_id: UUID
    role_id: UUID
    actor_id: UUID | None = None
