from dataclasses import dataclass


@dataclass(frozen=True)
class CreateRoleInput:
    name: str
    description: str
