class FakeTokenService:
    def __init__(self) -> None:
        self.issued_subjects: list[str] = []

    def create_access_token(self, subject: str) -> str:
        self.issued_subjects.append(subject)
        return f"access-token::{subject}"

    def decode_access_token(self, token: str) -> str:
        if not token.startswith("access-token::"):
            from sentinelcore.modules.authentication.application.ports.token_service import (
                TokenDecodeError,
            )

            raise TokenDecodeError
        return token.removeprefix("access-token::")
