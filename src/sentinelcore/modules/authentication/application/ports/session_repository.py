from datetime import datetime
from typing import Protocol
from uuid import UUID

from sentinelcore.modules.authentication.domain.entities.session import Session


class SessionRepository(Protocol):
    async def get_by_id(self, session_id: UUID) -> Session | None: ...

    async def list_by_user_id(self, user_id: UUID) -> list[Session]: ...

    async def add(self, session: Session) -> None: ...

    async def update(self, session: Session) -> None: ...

    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None: ...
