from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar
from uuid import UUID

from sentinelcore.shared.domain.entity import Entity

TEntity = TypeVar("TEntity", bound=Entity)


class Repository(Protocol[TEntity]):
    async def get_by_id(self, entity_id: UUID) -> TEntity | None: ...

    async def add(self, entity: TEntity) -> None: ...

    async def update(self, entity: TEntity) -> None: ...

    async def delete(self, entity_id: UUID) -> None: ...


class UnitOfWork(ABC, Generic[TEntity]):
    async def __aenter__(self) -> "UnitOfWork[TEntity]":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.rollback()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
