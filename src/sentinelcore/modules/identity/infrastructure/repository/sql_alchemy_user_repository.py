from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.modules.identity.infrastructure.models.user_model import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=Email(model.email),
        password_hash=model.password_hash,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        email=str(user.email),
        password_hash=user.password_hash,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> User | None:
        model = await self._session.get(UserModel, entity_id)
        return _to_entity(model) if model is not None else None

    async def get_by_email(self, email: Email) -> User | None:
        statement = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model is not None else None

    async def add(self, entity: User) -> None:
        self._session.add(_to_model(entity))
        await self._session.flush()

    async def update(self, entity: User) -> None:
        model = await self._session.get(UserModel, entity.id)
        if model is None:
            return
        model.email = str(entity.email)
        model.password_hash = entity.password_hash
        model.status = entity.status
        model.updated_at = entity.updated_at
        await self._session.flush()

    async def delete(self, entity_id: UUID) -> None:
        model = await self._session.get(UserModel, entity_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

    async def get_all(self) -> list[User]:
        result = await self._session.execute(
            select(UserModel)
        )

        models = result.scalars().all()

        return [_to_entity(model) for model in models]
