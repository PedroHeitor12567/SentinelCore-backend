from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authorization.application.dtos.input.create_role_input import CreateRoleInput
from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput
from sentinelcore.modules.authorization.application.ports.role_repository import RoleRepository
from sentinelcore.modules.authorization.domain.entities.role import Role
from sentinelcore.modules.authorization.domain.errors.role_name_already_in_use_error import RoleNameAlreadyInUseError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class CreateRoleUseCase(UseCase[CreateRoleInput, RoleOutput]):
    def __init__(
        self,
        role_repository: RoleRepository,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._role_repository = role_repository
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: CreateRoleInput) -> RoleOutput:
        existing = await self._role_repository.get_by_name(input_data.name)
        if existing is not None:
            raise RoleNameAlreadyInUseError(f"Role name '{input_data.name}' is already in use")

        role = Role.create(name=input_data.name, description=input_data.description)
        await self._role_repository.add(role)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.SENSITIVE_OPERATION,
                actor_id=input_data.actor_id,
                target_id=role.id,
                metadata={"action": "role_created", "role_id": str(role.id), "role_name": role.name},
            )
        )

        await self._unit_of_work.commit()

        return RoleOutput.from_role(role)
