from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from sentinelcore.modules.audit.application.dtos.output.audit_log_output import AuditLogOutput


class AuditLogResponse(BaseModel):
    id: UUID
    event_type: str
    actor_id: UUID | None
    target_id: UUID | None
    ip_address: str | None
    user_agent: str | None
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_output(cls, output: AuditLogOutput) -> "AuditLogResponse":
        return cls(
            id=output.id,
            event_type=output.event_type,
            actor_id=output.actor_id,
            target_id=output.target_id,
            ip_address=output.ip_address,
            user_agent=output.user_agent,
            metadata=output.metadata,
            created_at=output.created_at,
        )
