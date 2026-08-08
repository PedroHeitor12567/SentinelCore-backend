from datetime import UTC, datetime

import pytest

from tests.unit.modules.authentication.fakes.fixed_clock import FixedClock
from tests.unit.modules.identity.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.unit.modules.sessions.fakes.fake_session_repository import FakeSessionRepository


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(now=datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC))

@pytest.fixture
def session_repository() -> FakeSessionRepository:
    return FakeSessionRepository()

@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()
