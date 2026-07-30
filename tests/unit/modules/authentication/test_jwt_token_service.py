from datetime import UTC, datetime, timedelta

import jwt
import pytest

from sentinelcore.modules.authentication.infrastructure.security.jwt_token_service import JwtTokenService
from sentinelcore.modules.authentication.application.ports.token_service import TokenDecodeError, TokenExpiredError
_SECRET = "0123456789abcdef0123456789abcdef"
_ALGORITHM = "HS256"


def _service() -> JwtTokenService:
    return JwtTokenService(secret_key=_SECRET, algorithm=_ALGORITHM, access_token_expire_minutes=15)


def test_create_and_decode_round_trip_returns_subject() -> None:
    service = _service()
    token = service.create_access_token(subject="user-123")

    subject = service.decode_access_token(token)

    assert subject == "user-123"


def test_decode_expired_token_raises_token_expired_error() -> None:
    service = _service()
    now = datetime.now(UTC)
    expired_payload = {"sub": "user-123", "iat": now - timedelta(minutes=30), "exp": now - timedelta(minutes=15)}
    expired_token = jwt.encode(expired_payload, _SECRET, algorithm=_ALGORITHM)

    with pytest.raises(TokenExpiredError):
        service.decode_access_token(expired_token)


def test_decode_token_with_wrong_secret_raises_token_decode_error() -> None:
    service = _service()
    now = datetime.now(UTC)
    payload = {"sub": "user-123", "iat": now, "exp": now + timedelta(minutes=15)}
    token_signed_with_other_secret = jwt.encode(payload, "another_secret_key_with_more_than_32_chars", algorithm=_ALGORITHM)

    with pytest.raises(TokenDecodeError):
        service.decode_access_token(token_signed_with_other_secret)


def test_decode_malformed_token_raises_token_decode_error() -> None:
    service = _service()

    with pytest.raises(TokenDecodeError):
        service.decode_access_token("not-a-jwt")


def test_decode_token_without_subject_raises_token_decode_error() -> None:
    service = _service()
    now = datetime.now(UTC)
    payload = {"iat": now, "exp": now + timedelta(minutes=15)}
    token_without_subject = jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)

    with pytest.raises(TokenDecodeError):
        service.decode_access_token(token_without_subject)
