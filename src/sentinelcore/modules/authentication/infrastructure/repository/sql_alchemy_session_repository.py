from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.modules.authentication.domain.entities.session import Session
from sentinelcore.modules.authentication.infrastructure.models.session_model import SessionModel


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _to_entity(model: SessionModel) -> Session:
    return Session(
        id=model.id,
        user_id=model.user_id,
        created_at=_as_utc(model.created_at),
        last_seen_at=_as_utc(model.last_seen_at),
        ip_address=model.ip_address,
        user_agent=model.user_agent,
        revoked_at=_as_utc(model.revoked_at),
    )


def _to_model(session: Session) -> SessionModel:
    return SessionModel(
        id=session.id,
        user_id=session.user_id,
        created_at=session.created_at,
        last_seen_at=session.last_seen_at,
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        revoked_at=session.revoked_at,
    )


class SqlAlchemySessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, session_id: UUID) -> Session | None:
        model = await self._session.get(SessionModel, session_id)
        return _to_entity(model) if model is not None else None

    async def list_by_user_id(self, user_id: UUID) -> list[Session]:
        statement = (
            select(SessionModel)
            .where(SessionModel.user_id == user_id)
            .order_by(SessionModel.last_seen_at.desc())
        )
        result = await self._session.execute(statement)
        return [_to_entity(model) for model in result.scalars().all()]

    async def add(self, session: Session) -> None:
        self._session.add(_to_model(session))
        await self._session.flush()

    async def update(self, session: Session) -> None:
        model = await self._session.get(SessionModel, session.id)
        if model is None:
            return
        model.last_seen_at = session.last_seen_at
        model.ip_address = session.ip_address
        model.user_agent = session.user_agent
        model.revoked_at = session.revoked_at
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None:
        statement = (
            update(SessionModel)
            .where(SessionModel.user_id == user_id)
            .where(SessionModel.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        await self._session.execute(statement)
        await self._session.flush()
