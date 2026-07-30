from datetime import datetime
from typing import Protocol
from uuid import UUID

from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(Protocol):
    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None: ...

    async def add(self, refresh_token: RefreshToken) -> None: ...

    async def update(self, refresh_token: RefreshToken) -> None: ...

    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None: ...
