from datetime import datetime
from uuid import UUID, uuid4

from sentinelcore.shared.domain.entity import Entity


class RefreshToken(Entity):
    def __init__(
        self,
        id: UUID,
        session_id: UUID,
        user_id: UUID,
        token_hash: str,
        created_at: datetime,
        expires_at: datetime,
        revoked_at: datetime | None = None,
        replaced_by_id: UUID | None = None,
    ) -> None:
        super().__init__(id)
        self.session_id = session_id
        self.user_id = user_id
        self.token_hash = token_hash
        self.created_at = created_at
        self.expires_at = expires_at
        self.revoked_at = revoked_at
        self.replaced_by_id = replaced_by_id

    @classmethod
    def issue(
        cls,
        session_id: UUID,
        user_id: UUID,
        token_hash: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> "RefreshToken":
        return cls(
            id=uuid4(),
            session_id=session_id,
            user_id=user_id,
            token_hash=token_hash,
            created_at=issued_at,
            expires_at=expires_at,
        )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired(self, at: datetime) -> bool:
        return at >= self.expires_at

    def revoke(self, at: datetime, replaced_by_id: UUID | None = None) -> None:
        self.revoked_at = at
        if replaced_by_id is not None:
            self.replaced_by_id = replaced_by_id
