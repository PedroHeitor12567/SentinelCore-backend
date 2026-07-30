from datetime import datetime, UTC

import pytest

from tests.unit.modules.authentication.fakes.fake_refresh_token_repository import FakeRefreshTokenRepository
from tests.unit.modules.authentication.fakes.fake_token_service import FakeTokenService
from tests.unit.modules.authentication.fakes.fixed_clock import FixedClock
from tests.unit.modules.identity.fakes.fake_password_hasher import FakePasswordHasher
from tests.unit.modules.identity.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.unit.modules.identity.fakes.fake_user_repository import FakeUserRepository


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(now=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC))

@pytest.fixture
def refresh_token_repository() -> FakeRefreshTokenRepository:
    return FakeRefreshTokenRepository()

@pytest.fixture
def token_service() -> FakeTokenService:
    return FakeTokenService()

@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()

@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()

@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()
