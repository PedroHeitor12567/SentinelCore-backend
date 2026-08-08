from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sentinelcore.modules.authentication.domain.entities.session import Session

_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def test_new_session_is_not_revoked() -> None:
    session = Session.start(user_id=uuid4(), started_at=_NOW, ip_address="203.0.113.1", user_agent="curl/8.0")

    assert session.is_revoked is False
    assert session.last_seen_at == _NOW
    assert session.ip_address == "203.0.113.1"


def test_touch_updates_last_seen_at() -> None:
    session = Session.start(user_id=uuid4(), started_at=_NOW)
    later = _NOW + timedelta(hours=2)

    session.touch(at=later)

    assert session.last_seen_at == later


def test_touch_updates_ip_and_user_agent_when_provided() -> None:
    session = Session.start(user_id=uuid4(), started_at=_NOW, ip_address="203.0.113.1", user_agent="old-ua")

    session.touch(at=_NOW, ip_address="198.51.100.7", user_agent="new-ua")

    assert session.ip_address == "198.51.100.7"
    assert session.user_agent == "new-ua"


def test_touch_without_new_device_info_keeps_previous_values() -> None:
    session = Session.start(user_id=uuid4(), started_at=_NOW, ip_address="203.0.113.1", user_agent="old-ua")

    session.touch(at=_NOW + timedelta(minutes=5))

    assert session.ip_address == "203.0.113.1"
    assert session.user_agent == "old-ua"


def test_revoke_sets_revoked_at() -> None:
    session = Session.start(user_id=uuid4(), started_at=_NOW)

    session.revoke(at=_NOW + timedelta(hours=1))

    assert session.is_revoked is True
    assert session.revoked_at == _NOW + timedelta(hours=1)
