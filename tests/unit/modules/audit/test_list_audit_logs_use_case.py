from sentinelcore.modules.audit.application.dtos.input.list_audit_logs_input import ListAuditLogsInput
from sentinelcore.modules.audit.application.use_cases.list_audit_logs_use_case import ListAuditLogsUseCase
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType


async def test_list_audit_logs_returns_all_recorded_logs(audit_log_repository) -> None:
    await audit_log_repository.add(AuditLog.record(event_type=AuditEventType.LOGIN_SUCCESS))
    await audit_log_repository.add(AuditLog.record(event_type=AuditEventType.USER_CREATED))
    use_case = ListAuditLogsUseCase(audit_log_repository)

    outputs = await use_case.execute(ListAuditLogsInput())

    assert {output.event_type for output in outputs} == {"login_success", "user_created"}


async def test_list_audit_logs_respects_limit(audit_log_repository) -> None:
    for _ in range(5):
        await audit_log_repository.add(AuditLog.record(event_type=AuditEventType.LOGIN_SUCCESS))
    use_case = ListAuditLogsUseCase(audit_log_repository)

    outputs = await use_case.execute(ListAuditLogsInput(limit=2))

    assert len(outputs) == 2


async def test_list_audit_logs_for_empty_repository_returns_empty_list(audit_log_repository) -> None:
    use_case = ListAuditLogsUseCase(audit_log_repository)

    outputs = await use_case.execute(ListAuditLogsInput())

    assert outputs == []
