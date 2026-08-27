from sentinelcore.modules.audit.application.ports.audit_log_repository import AuditLogRepository
from sentinelcore.modules.audit.domain.entities.audit_log import AuditLog
from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.identity.application.dtos.input.create_user_input import CreateUserInput
from sentinelcore.modules.identity.application.dtos.output.user_output import UserOutput
from sentinelcore.modules.identity.application.ports.password_hasher import PasswordHasher
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.errors.email_already_in_use_error import EmailAlreadyInUseError
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class CreateUserUseCase(UseCase[CreateUserInput, UserOutput]):
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        unit_of_work: UnitOfWork,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._unit_of_work = unit_of_work
        self._audit_log_repository = audit_log_repository

    async def execute(self, input_data: CreateUserInput) -> UserOutput:
        email = Email(input_data.email)

        existing_user = await self._user_repository.get_by_email(email)
        if existing_user is not None:
            raise EmailAlreadyInUseError(f"Email {email} is already in use")

        password_hash = self._password_hasher.hash(input_data.password)
        user = User.create(email=email, password_hash=password_hash)

        await self._user_repository.add(user)

        await self._audit_log_repository.add(
            AuditLog.record(
                event_type=AuditEventType.USER_CREATED,
                actor_id=user.id,
                target_id=user.id,
                metadata={"email": str(email)},
            )
        )

        await self._unit_of_work.commit()

        return UserOutput.from_entity(user)
