import pytest

from tests.unit.modules.authorization.fakes.fake_permission_repository import FakePermissionRepository
from tests.unit.modules.authorization.fakes.fake_role_repository import FakeRoleRepository
from tests.unit.modules.authorization.fakes.fake_user_role_repository import FakeUserRoleRepository


@pytest.fixture
def role_repository() -> FakeRoleRepository:
    return FakeRoleRepository()


@pytest.fixture
def permission_repository() -> FakePermissionRepository:
    return FakePermissionRepository()


@pytest.fixture
def user_role_repository() -> FakeUserRoleRepository:
    return FakeUserRoleRepository()
