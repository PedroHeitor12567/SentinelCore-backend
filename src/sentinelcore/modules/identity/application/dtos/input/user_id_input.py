from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserIdInput:
    user_id: UUID
