from dataclasses import dataclass


@dataclass(frozen=True)
class CreatePermissionInput:
    code: str
    description: str
