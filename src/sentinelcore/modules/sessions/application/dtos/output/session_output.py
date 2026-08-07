from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sentinelcore.modules.authentication.domain.entities.session import Session


@dataclass(frozen=True)
class SessionOutput:
    id: UUID
    created_at: datetime
    last_seen_at: datetime
    is_revoked: bool
    ip_address: str | None
    user_agent: str | None

    @classmethod
    def from_session(cls, session: Session) -> "SessionOutput":
        return cls(
            id=session.id,
            created_at=session.created_at,
            last_seen_at=session.last_seen_at,
            is_revoked=session.is_revoked,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
        )
