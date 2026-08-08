from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from sentinelcore.modules.sessions.application.dtos.output.session_output import SessionOutput


class SessionResponse(BaseModel):
    id: UUID
    created_at: datetime
    last_seen_at: datetime
    is_revoked: bool
    ip_address: str | None
    user_agent: str | None

    @classmethod
    def from_output(cls, output: SessionOutput) -> "SessionResponse":
        return cls(
            id=output.id,
            created_at=output.created_at,
            last_seen_at=output.last_seen_at,
            is_revoked=output.is_revoked,
            ip_address=output.ip_address,
            user_agent=output.user_agent,
        )
