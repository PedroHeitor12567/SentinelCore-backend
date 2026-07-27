from sentinelcore.modules.identity.application.dtos.create_user_input import CreateUserInput
from sentinelcore.modules.identity.application.dtos.user_output import UserOutput
from sentinelcore.modules.identity.application.ports.password_hasher import PasswordHasher
from sentinelcore.modules.identity.application.ports.user_repository import UserRepository
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.errors.email_already_in_use_error import EmailAlreadyInUseError
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.shared.application.ports import UnitOfWork
from sentinelcore.shared.application.use_case import UseCase


class CreateUserUseCase(UseCase[CreateUserInput, UserOutput]):
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher, unit_of_work: UnitOfWork) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._unit_of_work = unit_of_work

    async def execute(self, input_data: CreateUserInput) -> UserOutput:
        email = Email(input_data.email)

        existing_user = await self._user_repository.get_by_email(email)
        if existing_user is not None:
            raise EmailAlreadyInUseError(f"Email {email} is already in use")

        password_hash = self._password_hasher.hash(input_data.password)
        user = User.create(email=email, password_hash=password_hash)

        await self._user_repository.add(user)
        await self._unit_of_work.commit()

        return UserOutput.from_entity(user)
