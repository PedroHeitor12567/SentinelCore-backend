from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.modules.authorization.domain.entities.role import Role
from sentinelcore.modules.authorization.infrastructure.models.role_model import RoleModel
from sentinelcore.modules.authorization.infrastructure.models.role_permission_model import (
    RolePermissionModel,
)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


class SqlAlchemyRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _permission_ids_for_role(self, role_id: UUID) -> set[UUID]:
        statement = select(RolePermissionModel.permission_id).where(
            RolePermissionModel.role_id == role_id
        )
        result = await self._session.execute(statement)
        return set(result.scalars().all())

    async def _to_entity(self, model: RoleModel) -> Role:
        return Role(
            id=model.id,
            name=model.name,
            description=model.description,
            permission_ids=await self._permission_ids_for_role(model.id),
            created_at=_as_utc(model.created_at),
        )

    async def get_by_id(self, role_id: UUID) -> Role | None:
        model = await self._session.get(RoleModel, role_id)
        return await self._to_entity(model) if model is not None else None

    async def get_by_name(self, name: str) -> Role | None:
        statement = select(RoleModel).where(RoleModel.name == name)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return await self._to_entity(model) if model is not None else None

    async def list_all(self) -> list[Role]:
        result = await self._session.execute(select(RoleModel))
        return [await self._to_entity(model) for model in result.scalars().all()]

    async def add(self, role: Role) -> None:
        self._session.add(
            RoleModel(
                id=role.id,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
            )
        )
        await self._session.flush()
        await self._sync_permissions(role)

    async def update(self, role: Role) -> None:
        model = await self._session.get(RoleModel, role.id)
        if model is None:
            return
        model.name = role.name
        model.description = role.description
        await self._session.flush()
        await self._sync_permissions(role)

    async def _sync_permissions(self, role: Role) -> None:
        current_ids = await self._permission_ids_for_role(role.id)

        for permission_id in role.permission_ids - current_ids:
            self._session.add(
                RolePermissionModel(role_id=role.id, permission_id=permission_id)
            )

        for permission_id in current_ids - role.permission_ids:
            link = await self._session.get(
                RolePermissionModel, {"role_id": role.id, "permission_id": permission_id}
            )
            if link is not None:
                await self._session.delete(link)

        await self._session.flush()
