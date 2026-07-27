import pytest

from sentinelcore.modules.identity.domain.enums.user_status import UserStatus
from sentinelcore.modules.identity.domain.errors.user_already_active_error import UserAlreadyActiveError
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.errors.user_already_inactive_error import UserAlreadyInactiveError
from sentinelcore.modules.identity.domain.value_objects.email import Email


def test_new_user_is_created_as_pending() -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")

    assert user.status == UserStatus.PENDING


def test_activate_pending_user_sets_status_to_active() -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")

    user.activate()

    assert user.status == UserStatus.ACTIVE


def test_activate_already_active_user_raises_error() -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    user.activate()

    with pytest.raises(UserAlreadyActiveError):
        user.activate()


def test_deactivate_active_user_sets_status_to_inactive() -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    user.activate()

    user.deactivate()

    assert user.status == UserStatus.INACTIVE


def test_deactivate_already_inactive_user_raises_error() -> None:
    user = User.create(email=Email("user@example.com"), password_hash="hashed")
    user.deactivate()

    with pytest.raises(UserAlreadyInactiveError):
        user.deactivate()
