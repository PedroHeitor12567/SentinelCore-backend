from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListSessionsInput:
    user_id: UUID
