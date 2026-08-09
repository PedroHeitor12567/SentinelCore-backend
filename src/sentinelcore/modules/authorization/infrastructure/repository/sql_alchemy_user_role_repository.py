from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.modules.authorization.infrastructure.models.user_role_model import UserRoleModel


class SqlAlchemyUserRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def assign(self, user_id: UUID, role_id: UUID) -> None:
        existing = await self._session.get(UserRoleModel, {"user_id": user_id, "role_id": role_id})
        if existing is not None:
            return
        self._session.add(UserRoleModel(user_id=user_id, role_id=role_id))
        await self._session.flush()

    async def unassign(self, user_id: UUID, role_id: UUID) -> None:
        existing = await self._session.get(UserRoleModel, {"user_id": user_id, "role_id": role_id})
        if existing is not None:
            await self._session.delete(existing)
            await self._session.flush()

    async def list_role_ids_for_user(self, user_id: UUID) -> list[UUID]:
        statement = select(UserRoleModel.role_id).where(UserRoleModel.user_id == user_id)
        result = await self._session.execute(statement)
        return list(result.scalars().all())
