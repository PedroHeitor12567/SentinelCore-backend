from datetime import timedelta, datetime, UTC

import jwt

from sentinelcore.modules.authentication.application.ports.token_service import TokenDecodeError, TokenExpiredError


class JwtTokenService:
    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(self, subject: str) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._access_token_expire_minutes),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredError from exc
        except jwt.InvalidTokenError as exc:
            raise TokenDecodeError from exc

        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise TokenDecodeError

        return subject
