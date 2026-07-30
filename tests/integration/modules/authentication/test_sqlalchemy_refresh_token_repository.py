from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken
from sentinelcore.modules.authentication.infrastructure.models.refresh_token_model import RefreshTokenModel


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _to_entity(model: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        created_at=_as_utc(model.created_at),
        expires_at=_as_utc(model.expires_at),
        revoked_at=_as_utc(model.revoked_at),
        replaced_by_id=model.replaced_by_id,
    )


def _to_model(refresh_token: RefreshToken) -> RefreshTokenModel:
    return RefreshTokenModel(
        id=refresh_token.id,
        user_id=refresh_token.user_id,
        token_hash=refresh_token.token_hash,
        created_at=refresh_token.created_at,
        expires_at=refresh_token.expires_at,
        revoked_at=refresh_token.revoked_at,
        replaced_by_id=refresh_token.replaced_by_id,
    )


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        statement = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model is not None else None

    async def add(self, refresh_token: RefreshToken) -> None:
        self._session.add(_to_model(refresh_token))
        await self._session.flush()

    async def update(self, refresh_token: RefreshToken) -> None:
        model = await self._session.get(RefreshTokenModel, refresh_token.id)
        if model is None:
            return
        model.revoked_at = refresh_token.revoked_at
        model.replaced_by_id = refresh_token.replaced_by_id
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None:
        statement = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        await self._session.execute(statement)
        await self._session.flush()
