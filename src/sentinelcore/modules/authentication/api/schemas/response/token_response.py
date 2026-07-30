from pydantic import BaseModel

from sentinelcore.modules.authentication.application.dtos.output.token_pair_output import TokenPairOutput


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    @classmethod
    def from_output(cls, output: TokenPairOutput) -> "TokenResponse":
        return cls(
            access_token=output.access_token,
            refresh_token=output.refresh_token,
            token_type=output.token_type,
        )
