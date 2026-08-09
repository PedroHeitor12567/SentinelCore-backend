from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserPermissionsOutput:
    user_id: UUID
    permission_codes: list[str]
