from uuid import uuid4

import pytest

from sentinelcore.modules.identity.application.use_cases.activate_user_use_case import ActivateUserUseCase
from sentinelcore.modules.identity.application.use_cases.deactive_user_use_case import DeactiveUserUseCase
from sentinelcore.modules.identity.application.dtos.user_id_input import UserIdInput
from sentinelcore.modules.identity.domain.enums.user_status import UserStatus
from sentinelcore.modules.identity.domain.errors.user_not_found_error import UserNotFoundError
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email


async def test_activate_user_sets_status_to_active(user_repository, unit_of_work) -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    await user_repository.add(user)
    use_case = ActivateUserUseCase(user_repository, unit_of_work)

    output = await use_case.execute(UserIdInput(user_id=user.id))

    assert output.status == UserStatus.ACTIVE
    assert unit_of_work.committed is True


async def test_activate_unknown_user_raises_not_found(user_repository, unit_of_work) -> None:
    use_case = ActivateUserUseCase(user_repository, unit_of_work)

    with pytest.raises(UserNotFoundError):
        await use_case.execute(UserIdInput(user_id=uuid4()))


async def test_deactivate_user_sets_status_to_inactive(user_repository, unit_of_work) -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    user.activate()
    await user_repository.add(user)
    use_case = DeactiveUserUseCase(user_repository, unit_of_work)

    output = await use_case.execute(UserIdInput(user_id=user.id))

    assert output.status == UserStatus.INACTIVE
    assert unit_of_work.committed is True


async def test_deactivate_unknown_user_raises_not_found(user_repository, unit_of_work) -> None:
    use_case = DeactiveUserUseCase(user_repository, unit_of_work)

    with pytest.raises(UserNotFoundError):
        await use_case.execute(UserIdInput(user_id=uuid4()))
