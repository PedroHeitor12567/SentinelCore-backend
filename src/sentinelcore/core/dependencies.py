from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.infrastructure.database.session import get_db_session
from sentinelcore.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_unit_of_work(session: DbSession) -> AsyncGenerator[SqlAlchemyUnitOfWork]:
    yield SqlAlchemyUnitOfWork(session)


UoW = Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)]
