from typing import Annotated

from fastapi import Depends

from sentinelcore.core.dependencies import UoW
from sentinelcore.modules.audit.api.dependencies import AuditLogRepositoryDep
from sentinelcore.modules.authentication.api.dependencies import ClockDep, SessionRepositoryDep
from sentinelcore.modules.sessions.application.use_cases.list_sessions_use_case import (
    ListSessionsUseCase,
)
from sentinelcore.modules.sessions.application.use_cases.revoke_session_use_case import (
    RevokeSessionUseCase,
)


def get_list_sessions_use_case(session_repository: SessionRepositoryDep) -> ListSessionsUseCase:
    return ListSessionsUseCase(session_repository)


def get_revoke_session_use_case(
    session_repository: SessionRepositoryDep,
    clock: ClockDep,
    unit_of_work: UoW,
    audit_log_repository: AuditLogRepositoryDep,
) -> RevokeSessionUseCase:
    return RevokeSessionUseCase(session_repository, clock, unit_of_work, audit_log_repository)


ListSessionsUseCaseDep = Annotated[ListSessionsUseCase, Depends(get_list_sessions_use_case)]
RevokeSessionUseCaseDep = Annotated[RevokeSessionUseCase, Depends(get_revoke_session_use_case)]
