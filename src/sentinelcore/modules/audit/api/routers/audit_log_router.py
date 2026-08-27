from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from sentinelcore.modules.audit.api.dependencies import ListAuditLogsUseCaseDep
from sentinelcore.modules.audit.api.schemas.response.audit_log_response import AuditLogResponse
from sentinelcore.modules.audit.application.dtos.input.list_audit_logs_input import ListAuditLogsInput
from sentinelcore.modules.authorization.api.dependencies import require_permission

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(
    _current_user_id: Annotated[UUID, Depends(require_permission("audit:read"))],
    use_case: ListAuditLogsUseCaseDep,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AuditLogResponse]:
    outputs = await use_case.execute(ListAuditLogsInput(limit=limit, offset=offset))
    return [AuditLogResponse.from_output(output) for output in outputs]
