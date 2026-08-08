from datetime import datetime
from uuid import UUID

from sentinelcore.modules.authentication.domain.entities.session import Session


class FakeSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}

    async def get_by_id(self, session_id: UUID) -> Session | None:
        return self._sessions.get(session_id)

    async def list_by_user_id(self, user_id: UUID) -> list[Session]:
        return sorted(
            (session for session in self._sessions.values() if session.user_id == user_id),
            key=lambda session: session.last_seen_at,
            reverse=True,
        )

    async def add(self, session: Session) -> None:
        self._sessions[session.id] = session

    async def update(self, session: Session) -> None:
        self._sessions[session.id] = session

    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None:
        for session in self._sessions.values():
            if session.user_id == user_id and not session.is_revoked:
                session.revoke(at=revoked_at)

