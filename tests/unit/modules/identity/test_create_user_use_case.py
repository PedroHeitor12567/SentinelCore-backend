import pytest

from sentinelcore.modules.identity.application.use_cases.create_user_use_case import CreateUserUseCase
from sentinelcore.modules.identity.application.dtos.input.create_user_input import CreateUserInput
from sentinelcore.modules.identity.domain.errors.email_already_in_use_error import EmailAlreadyInUseError
from sentinelcore.modules.identity.domain.enums.user_status import UserStatus


async def test_create_user_persists_user_with_hashed_password(user_repository, password_hasher, unit_of_work) -> None:
    use_case = CreateUserUseCase(user_repository, password_hasher, unit_of_work)

    output = await use_case.execute(CreateUserInput(email="user@example.com", password="s3cr3t!!"))

    stored_user = await user_repository.get_by_id(output.id)
    assert stored_user is not None
    assert stored_user.password_hash == "hashed::s3cr3t!!"
    assert output.status == UserStatus.PENDING
    assert unit_of_work.committed is True


async def test_create_user_with_duplicate_email_raises_error(user_repository, password_hasher, unit_of_work) -> None:
    use_case = CreateUserUseCase(user_repository, password_hasher, unit_of_work)
    await use_case.execute(CreateUserInput(email="user@example.com", password="s3cr3t!!"))

    with pytest.raises(EmailAlreadyInUseError):
        await use_case.execute(CreateUserInput(email="user@example.com", password="other-pass"))
