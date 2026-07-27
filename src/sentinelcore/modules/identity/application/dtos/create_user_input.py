from dataclasses import dataclass


@dataclass(frozen=True)
class CreateUserInput:
    email: str
    password: str
