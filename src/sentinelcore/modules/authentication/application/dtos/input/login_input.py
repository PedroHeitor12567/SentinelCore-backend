from dataclasses import dataclass


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str
    ip_address: str | None = None
    user_agent: str | None = None
