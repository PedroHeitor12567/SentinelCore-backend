from typing import Protocol

from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog


class AuditLogRepository(Protocol):
    async def add(self, audit_log: AuditLog) -> None: ...

    async def list_all(selfself, limit: int = 100, offset: int = 0) -> list[AuditLog]: ...
