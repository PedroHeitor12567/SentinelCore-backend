from uuid import uuid4

import pytest

from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.identity.application.use_cases.activate_user_use_case import ActivateUserUseCase
from sentinelcore.modules.identity.application.use_cases.deactive_user_use_case import DeactiveUserUseCase
from sentinelcore.modules.identity.application.dtos.input.user_id_input import UserIdInput
from sentinelcore.modules.identity.domain.enums.user_status import UserStatus
from sentinelcore.modules.identity.domain.errors.user_already_active_error import UserAlreadyActiveError
from sentinelcore.modules.identity.domain.errors.user_already_inactive_error import UserAlreadyInactiveError
from sentinelcore.modules.identity.domain.errors.user_not_found_error import UserNotFoundError
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email


async def test_activate_user_sets_status_to_active(user_repository, unit_of_work, audit_log_repository) -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    await user_repository.add(user)
    actor_id = uuid4()
    use_case = ActivateUserUseCase(user_repository, unit_of_work, audit_log_repository)

    output = await use_case.execute(UserIdInput(user_id=user.id, actor_id=actor_id))

    assert output.status == UserStatus.ACTIVE
    assert unit_of_work.committed is True
    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.USER_ACTIVATED
    assert log.actor_id == actor_id
    assert log.target_id == user.id


async def test_activate_unknown_user_raises_not_found(user_repository, unit_of_work, audit_log_repository) -> None:
    use_case = ActivateUserUseCase(user_repository, unit_of_work, audit_log_repository)

    with pytest.raises(UserNotFoundError):
        await use_case.execute(UserIdInput(user_id=uuid4()))

    assert len(audit_log_repository.logs) == 0


async def test_activate_already_active_user_does_not_record_event(
    user_repository, unit_of_work, audit_log_repository
) -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    user.activate()
    await user_repository.add(user)
    use_case = ActivateUserUseCase(user_repository, unit_of_work, audit_log_repository)

    with pytest.raises(UserAlreadyActiveError):
        await use_case.execute(UserIdInput(user_id=user.id))

    assert len(audit_log_repository.logs) == 0


async def test_deactivate_user_sets_status_to_inactive(user_repository, unit_of_work, audit_log_repository) -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    user.activate()
    await user_repository.add(user)
    actor_id = uuid4()
    use_case = DeactiveUserUseCase(user_repository, unit_of_work, audit_log_repository)

    output = await use_case.execute(UserIdInput(user_id=user.id, actor_id=actor_id))

    assert output.status == UserStatus.INACTIVE
    assert unit_of_work.committed is True
    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.USER_DEACTIVATED
    assert log.actor_id == actor_id
    assert log.target_id == user.id


async def test_deactivate_unknown_user_raises_not_found(user_repository, unit_of_work, audit_log_repository) -> None:
    use_case = DeactiveUserUseCase(user_repository, unit_of_work, audit_log_repository)

    with pytest.raises(UserNotFoundError):
        await use_case.execute(UserIdInput(user_id=uuid4()))

    assert len(audit_log_repository.logs) == 0


async def test_deactivate_already_inactive_user_does_not_record_event(
    user_repository, unit_of_work, audit_log_repository
) -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    user.activate()
    user.deactivate()
    await user_repository.add(user)
    use_case = DeactiveUserUseCase(user_repository, unit_of_work, audit_log_repository)

    with pytest.raises(UserAlreadyInactiveError):
        await use_case.execute(UserIdInput(user_id=user.id))

    assert len(audit_log_repository.logs) == 0
