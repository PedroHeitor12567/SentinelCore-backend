from typing import Protocol

from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(Protocol):
    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None: ...

    async def add(self, refresh_token: RefreshToken) -> None: ...

    async def update(self, refresh_token: RefreshToken) -> None: ...
