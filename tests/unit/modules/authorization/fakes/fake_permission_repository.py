from uuid import UUID

from sentinelcore.modules.authorization.domain.entities.permission import Permission


class FakePermissionRepository:
    def __init__(self) -> None:
        self._permissions: dict[UUID, Permission] = {}

    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        return self._permissions.get(permission_id)

    async def get_by_code(self, code: str) -> Permission | None:
        for permission in self._permissions.values():
            if permission.code == code:
                return permission
        return None

    async def list_all(self) -> list[Permission]:
        return list(self._permissions.values())

    async def add(self, permission: Permission) -> None:
        self._permissions[permission.id] = permission
