from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authorization.application.dtos.input.create_permission_input import CreatePermissionInput
from sentinelcore.modules.authorization.application.dtos.output.permission_output import PermissionOutput
from sentinelcore.modules.authorization.application.ports.permission_repository import PermissionRepository
from sentinelcore.modules.authorization.domain.entities.permission import Permission
from sentinelcore.modules.authorization.domain.errors.permission_code_already_in_use_error import (
    PermissionCodeAlreadyInUseError,
)
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class CreatePermissionUseCase(UseCase[CreatePermissionInput, PermissionOutput]):
    def __init__(
        self,
        permission_repository: PermissionRepository,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._permission_repository = permission_repository
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: CreatePermissionInput) -> PermissionOutput:
        existing = await self._permission_repository.get_by_code(input_data.code)
        if existing is not None:
            raise PermissionCodeAlreadyInUseError(f"Permission code '{input_data.code}' is already in use.")

        permission = Permission.create(code=input_data.code, description=input_data.description)
        await self._permission_repository.add(permission)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.SENSITIVE_OPERATION,
                actor_id=input_data.actor_id,
                target_id=permission.id,
                metadata={
                    "action": "permission_created",
                    "permission_id": str(permission.id),
                    "permission_code": permission.code,
                },
            )
        )

        await self._unit_of_work.commit()

        return PermissionOutput.from_permission(permission)
