from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPairOutput:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
