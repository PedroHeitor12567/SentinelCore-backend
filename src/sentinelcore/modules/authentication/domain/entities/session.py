from datetime import datetime
from uuid import UUID, uuid4

from sentinelcore.shared.domain.entity import Entity


class Session(Entity):
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        created_at: datetime,
        last_seen_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
        revoked_at: datetime | None = None,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.created_at = created_at
        self.last_seen_at = last_seen_at
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.revoked_at = revoked_at

    @classmethod
    def start(
        cls,
        user_id: UUID,
        started_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> "Session":
        return cls(
            id=uuid4(),
            user_id=user_id,
            created_at=started_at,
            last_seen_at=started_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def touch(self, at: datetime, ip_address: str | None = None, user_agent: str | None = None) -> None:
        self.last_seen_at = at
        if ip_address is not None:
            self.ip_address = ip_address
        if user_agent is not None:
            self.user_agent = user_agent

    def revoke(self, at: datetime) -> None:
        self.revoked_at = at
