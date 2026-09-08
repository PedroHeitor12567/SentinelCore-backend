from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authorization.application.dtos.input.grant_permission_input import GrantPermissionInput
from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput
from sentinelcore.modules.authorization.application.ports.permission_repository import PermissionRepository
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.domain.errors.permission_not_found_error import PermissionNotFoundError
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class GrantPermissionToRoleUseCase(UseCase[GrantPermissionInput, RoleOutput]):
    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._role_repository = role_repository
        self._permission_repository = permission_repository
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: GrantPermissionInput) -> RoleOutput:
        role = await self._role_repository.get_by_id(input_data.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role {input_data.role_id} not found")

        permission = await self._permission_repository.get_by_id(input_data.permission_id)
        if permission is None:
            raise PermissionNotFoundError(f"Permission {input_data.permission_id} not found")

        role.grant_permission(permission.id)
        await self._role_repository.update(role)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.PERMISSION_GRANTED,
                actor_id=input_data.actor_id,
                target_id=role.id,
                metadata={
                    "action": "permission_granted",
                    "role_id": str(role.id),
                    "permission_id": str(permission.id),
                    "permission_code": permission.code,
                },
            )
        )

        await self._unit_of_work.commit()

        return RoleOutput.from_role(role)
