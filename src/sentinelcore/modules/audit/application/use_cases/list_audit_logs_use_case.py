from sentinelcore.modules.audit.application.dtos.input.list_audit_logs_input import ListAuditLogsInput
from sentinelcore.modules.audit.application.dtos.output.audit_log_output import AuditLogOutput
from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.shared.application.use_case import UseCase


class ListAuditLogsUseCase(UseCase[ListAuditLogsInput, list[AuditLogOutput]]):
    def __init__(self, audit_log_repository: AuditLogRepository) -> None:
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: ListAuditLogsInput) -> list[AuditLogOutput]:
        audit_logs = await self._audit_log_repository.list_all(
            limit=input_data.limit,
            offset=input_data.offset,
        )
        return [AuditLogOutput.from_entity(audit_log) for audit_log in audit_logs]
