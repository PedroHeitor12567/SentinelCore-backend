from dataclasses import dataclass


@dataclass(frozen=True)
class ValidateAccessTokenInput:
    access_token: str
