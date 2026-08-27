from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from tests.unit.modules.audit.fakes.fake_audit_log_repository import FakeAuditLogRepository
from tests.unit.modules.authentication.fakes.fake_refresh_token_repository import FakeRefreshTokenRepository
from tests.unit.modules.authentication.fakes.fake_token_service import FakeTokenService
from tests.unit.modules.authentication.fakes.fixed_clock import FixedClock
from tests.unit.modules.identity.fakes.fake_password_hasher import FakePasswordHasher
from tests.unit.modules.identity.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.unit.modules.identity.fakes.fake_user_repository import FakeUserRepository
from tests.unit.modules.sessions.fakes.fake_session_repository import FakeSessionRepository


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(now=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC))


@pytest.fixture
def refresh_token_repository() -> FakeRefreshTokenRepository:
    return FakeRefreshTokenRepository()


@pytest.fixture
def session_repository() -> FakeSessionRepository:
    return FakeSessionRepository()


@pytest.fixture
def token_service() -> FakeTokenService:
    return FakeTokenService()


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()

@pytest.fixture
def audit_log_repository() -> FakeAuditLogRepository:
    return FakeAuditLogRepository()
