from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authorization.application.dtos.input.revoke_permission_input import RevokePermissionInput
from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class RevokePermissionFromRoleUseCase(UseCase[RevokePermissionInput, RoleOutput]):
    def __init__(
        self,
        role_repository: RoleRepository,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._role_repository = role_repository
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: RevokePermissionInput) -> RoleOutput:
        role = await self._role_repository.get_by_id(input_data.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role {input_data.role_id} not found")

        role.revoke_permission(input_data.permission_id)
        await self._role_repository.update(role)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.PERMISSION_CHANGED,
                actor_id=input_data.actor_id,
                target_id=role.id,
                metadata={
                    "action": "permission_revoked",
                    "role_id": str(role.id),
                    "permission_id": str(input_data.permission_id),
                },
            )
        )

        await self._unit_of_work.commit()

        return RoleOutput.from_role(role)
