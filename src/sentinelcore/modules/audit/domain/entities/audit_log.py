from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.shared.domain.entity import Entity


class AuditLog(Entity):
    def __init__(
        self,
        id: UUID,
        event_type: AuditEventType,
        actor_id: UUID | None,
        target_id: UUID | None,
        ip_address: str | None,
        user_agent: str | None,
        metadata: dict[str, Any],
        created_at: datetime,
    ) -> None:
        super().__init__(id)
        self.event_type = event_type
        self.actor_id = actor_id
        self.target_id = target_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.metadata = metadata
        self.created_at = created_at

    @classmethod
    def record(
        cls,
        event_type: AuditEventType,
        actor_id: UUID | None = None,
        target_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "AuditLog":
        return cls(
            id=uuid4(),
            event_type=event_type,
            actor_id=actor_id,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            created_at=datetime.now(UTC),
        )
