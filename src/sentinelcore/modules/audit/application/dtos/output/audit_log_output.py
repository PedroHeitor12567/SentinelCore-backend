from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog

@dataclass(frozen=True)
class AuditLogOutput:
    id: UUID
    event_type: str
    actor_id: UUID | None
    target_id: UUID | None
    ip_address: str | None
    user_agent: str | None
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_entity(cls, audit_log: AuditLog) -> "AuditLogOutput":
        return cls(
            id=audit_log.id,
            event_type=audit_log.event_type.value,
            actor_id=audit_log.actor_id,
            target_id=audit_log.target_id,
            ip_address=audit_log.ip_address,
            user_agent=audit_log.user_agent,
            metadata=audit_log.metadata,
            created_at=audit_log.created_at,
        )
