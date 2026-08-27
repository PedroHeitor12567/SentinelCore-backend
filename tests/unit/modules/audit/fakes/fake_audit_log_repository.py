from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.logs: list[AuditLog] = []

    async def add(self, audit_log: AuditLog) -> None:
        self.logs.append(audit_log)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        ordered = sorted(self.logs, key=lambda log: log.created_at, reverse=True)
        return ordered[offset : offset + limit]
