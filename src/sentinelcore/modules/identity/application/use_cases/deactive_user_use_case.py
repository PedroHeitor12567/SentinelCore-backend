from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.identity.application.dtos.input.user_id_input import UserIdInput
from sentinelcore.modules.identity.application.dtos.output.user_output import UserOutput
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.modules.identity.domain.errors.user_not_found_error import UserNotFoundError
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class DeactiveUserUseCase(UseCase[UserIdInput, UserOutput]):
    def __init__(
        self,
        user_repository: UserRepository,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ):
        self._user_repository = user_repository
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: UserIdInput) -> UserOutput:
        user = await self._user_repository.get_by_id(input_data.user_id)
        if user is None:
            raise UserNotFoundError(f"User {input_data.user_id} not found")

        user.deactivate()

        await self._user_repository.update(user)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.USER_DEACTIVATED,
                actor_id=input_data.actor_id,
                target_id=user.id,
                metadata={"email": str(user.email)},
            )
        )

        await self._unit_of_work.commit()

        return UserOutput.from_entity(user)
