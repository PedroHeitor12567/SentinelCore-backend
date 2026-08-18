from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AssignRoleInput:
    user_id: UUID
    role_id: UUID
