from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.audit.infrastructure.models.audit_log_model import AuditLogModel


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _to_entity(model: AuditLogModel) -> AuditLog:
    return AuditLog(
        id=model.id,
        event_type=AuditEventType(model.event_type),
        actor_id=model.actor_id,
        target_id=model.target_id,
        ip_address=model.ip_address,
        user_agent=model.user_agent,
        metadata=model.log_metadata,
        created_at=_as_utc(model.created_at),
    )


class SqlAlchemyAuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, audit_log: AuditLog) -> None:
        self._session.add(
            AuditLogModel(
                id=audit_log.id,
                event_type=audit_log.event_type.value,
                actor_id=audit_log.actor_id,
                target_id=audit_log.target_id,
                ip_address=audit_log.ip_address,
                user_agent=audit_log.user_agent,
                log_metadata=audit_log.metadata,
                created_at=audit_log.created_at,
            )
        )
        await self._session.flush()

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        statement = (
            select(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(limit).offset(offset)
        )
        result = await self._session.execute(statement)
        return [_to_entity(model) for model in result.scalars().all()]
