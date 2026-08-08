from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken

_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


def _issue() -> RefreshToken:
    return RefreshToken.issue(
        session_id=uuid4(),
        user_id=uuid4(),
        token_hash="hash",
        issued_at=_NOW,
        expires_at=_NOW + timedelta(days=7),
    )


def test_new_token_is_not_revoked() -> None:
    token = _issue()

    assert token.is_revoked is False


def test_token_is_expired_when_current_time_reaches_expiry() -> None:
    token = _issue()

    assert token.is_expired(_NOW + timedelta(days=7)) is True
    assert token.is_expired(_NOW + timedelta(days=6)) is False


def test_revoke_sets_revoked_at() -> None:
    token = _issue()

    token.revoke(at=_NOW + timedelta(hours=1))

    assert token.is_revoked is True
    assert token.revoked_at == _NOW + timedelta(hours=1)


def test_revoke_with_replacement_sets_replaced_by_id() -> None:
    token = _issue()
    replacement_id = uuid4()

    token.revoke(at=_NOW, replaced_by_id=replacement_id)

    assert token.replaced_by_id == replacement_id
