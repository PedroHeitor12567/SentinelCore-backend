from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetUserPermissionsInput:
    user_id: UUID
