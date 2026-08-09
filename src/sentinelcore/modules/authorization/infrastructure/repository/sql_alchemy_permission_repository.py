from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.modules.authorization.domain.entities.permission import Permission
from sentinelcore.modules.authorization.infrastructure.models.permission_model import (
    PermissionModel,
)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _to_entity(model: PermissionModel) -> Permission:
    return Permission(
        id=model.id,
        code=model.code,
        description=model.description,
        created_at=_as_utc(model.created_at),
    )


class SqlAlchemyPermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        model = await self._session.get(PermissionModel, permission_id)
        return _to_entity(model) if model is not None else None

    async def get_by_code(self, code: str) -> Permission | None:
        statement = select(PermissionModel).where(PermissionModel.code == code)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model is not None else None

    async def list_all(self) -> list[Permission]:
        result = await self._session.execute(select(PermissionModel))
        return [_to_entity(model) for model in result.scalars().all()]

    async def add(self, permission: Permission) -> None:
        self._session.add(
            PermissionModel(
                id=permission.id,
                code=permission.code,
                description=permission.description,
                created_at=permission.created_at,
            )
        )
        await self._session.flush()
