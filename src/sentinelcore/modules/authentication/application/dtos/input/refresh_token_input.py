from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshTokenInput:
    refresh_token: str
    ip_address: str | None = None
    user_agent: str | None = None
