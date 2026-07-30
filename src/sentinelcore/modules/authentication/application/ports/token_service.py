from typing import Protocol


class TokenDecodeError(Exception):
    pass

class TokenExpiredError(TokenDecodeError):
    pass

class TokenService(Protocol):
    def create_access_token(self, subject: str) -> str: ...

    def decode_access_token(self, token: str) -> str:
        """Returns the token subject. Raises TokenExpiredError or TokenDecodeError."""
        ...
