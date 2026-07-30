import pytest

from tests.unit.modules.identity.fakes.fake_password_hasher import FakePasswordHasher
from tests.unit.modules.identity.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.unit.modules.identity.fakes.fake_user_repository import FakeUserRepository


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()
