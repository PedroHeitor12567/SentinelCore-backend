from dataclasses import dataclass


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str
