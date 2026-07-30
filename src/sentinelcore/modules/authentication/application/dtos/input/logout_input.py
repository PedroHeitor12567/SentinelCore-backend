from dataclasses import dataclass


@dataclass(frozen=True)
class LogoutInput:
    refresh_token: str
