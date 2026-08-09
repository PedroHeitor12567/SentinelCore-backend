from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RevokePermissionInput:
    role_id: UUID
    permission_id: UUID
