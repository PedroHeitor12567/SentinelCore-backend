from datetime import datetime
from uuid import UUID

from sentinelcore.modules.authentication.domain.entities.refresh_token import RefreshToken

class FakeRefreshTokenRepository:
    def __init__(self) -> None:
        self._tokens: dict[str, RefreshToken] = {}

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        return self._tokens.get(token_hash)

    async def add(self, refresh_token: RefreshToken) -> None:
        self._tokens[refresh_token.token_hash] = refresh_token

    async def update(self, refresh_token: RefreshToken) -> None:
        self._tokens[refresh_token.token_hash] = refresh_token

    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None:
        for token in self._tokens.values():
            if token.user_id == user_id and not token.is_revoked:
                token.revoke(at=revoked_at)
