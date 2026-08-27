from typing import Annotated

from fastapi import Depends

from sentinelcore.core.dependencies import UoW
from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.application.use_cases.list_audit_logs_use_case import ListAuditLogsUseCase
from sentinelcore.modules.audit.infrastructure.repository.sql_alchemy_audit_log_repository import (
    SqlAlchemyAuditLogRepository,
)


def get_audit_log_repository(unit_of_work: UoW) -> AuditLogRepository:
    return SqlAlchemyAuditLogRepository(unit_of_work.session)


AuditLogRepositoryDep = Annotated[AuditLogRepository, Depends(get_audit_log_repository)]


def get_list_audit_logs_use_case(audit_log_repository: AuditLogRepositoryDep) -> ListAuditLogsUseCase:
    return ListAuditLogsUseCase(audit_log_repository)


ListAuditLogsUseCaseDep = Annotated[ListAuditLogsUseCase, Depends(get_list_audit_logs_use_case)]
