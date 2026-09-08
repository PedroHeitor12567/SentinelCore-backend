from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authorization.application.dtos.input.assign_role_input import AssignRoleInput
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.application.ports.user_role_repository import UserRoleRepository
from sentinelcore.modules.authorization.domain.errors.role_not_found_error import RoleNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class AssignRoleToUserUseCase(UseCase[AssignRoleInput, None]):
    def __init__(
        self,
        role_repository: RoleRepository,
        user_role_repository: UserRoleRepository,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._role_repository = role_repository
        self._user_role_repository = user_role_repository
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: AssignRoleInput) -> None:
        role = await self._role_repository.get_by_id(input_data.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role {input_data.role_id} not found")

        await self._user_role_repository.assign(input_data.user_id, input_data.role_id)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.ROLE_ASSIGNED,
                actor_id=input_data.actor_id,
                target_id=input_data.user_id,
                metadata={
                    "action": "role_assigned",
                    "user_id": str(input_data.user_id),
                    "role_id": str(role.id),
                    "role_name": role.name,
                },
            )
        )

        await self._unit_of_work.commit()
