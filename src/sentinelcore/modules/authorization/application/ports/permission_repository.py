from typing import Protocol
from uuid import UUID

from sentinelcore.modules.authorization.domain.entities.permission import Permission


class PermissionRepository(Protocol):
    async def get_by_id(self, permission_id: UUID) -> Permission | None: ...

    async def get_by_code(self, code: str) -> Permission | None: ...

    async def list_all(self) -> list[Permission]: ...

    async def add (self, permission: Permission) -> None: ...
