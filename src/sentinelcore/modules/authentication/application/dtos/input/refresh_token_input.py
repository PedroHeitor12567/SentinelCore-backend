from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshTokenInput:
    refresh_token: str
