from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RevokeSessionInput:
    user_id: UUID
    session_id: UUID
