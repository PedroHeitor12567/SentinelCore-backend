from datetime import datetime, UTC
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    ocurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
