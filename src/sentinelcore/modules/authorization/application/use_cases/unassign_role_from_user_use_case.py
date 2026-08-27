from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authorization.application.dtos.input.unassign_role_input import UnassignRoleInput
from sentinelcore.modules.authorization.application.ports.user_role_repository import UserRoleRepository
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class UnassignRoleFromUserUseCase(UseCase[UnassignRoleInput, None]):
    def __init__(
        self,
        user_role_repository: UserRoleRepository,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._user_role_repository = user_role_repository
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: UnassignRoleInput) -> None:
        await self._user_role_repository.unassign(input_data.user_id, input_data.role_id)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.PERMISSION_CHANGED,
                actor_id=input_data.actor_id,
                target_id=input_data.user_id,
                metadata={
                    "action": "role_unassigned",
                    "user_id": str(input_data.user_id),
                    "role_id": str(input_data.role_id),
                },
            )
        )

        await self._unit_of_work.commit()
