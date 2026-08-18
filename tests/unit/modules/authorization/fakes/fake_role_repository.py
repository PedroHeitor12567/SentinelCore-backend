from uuid import UUID

from sentinelcore.modules.authorization.domain.entities.role import Role


class FakeRoleRepository:
    def __init__(self) -> None:
        self._roles: dict[UUID, Role] = {}

    async def get_by_id(self, role_id: UUID) -> Role | None:
        return self._roles.get(role_id)

    async def get_by_name(self, name: str) -> Role | None:
        for role in self._roles.values():
            if role.name == name:
                return role
        return None

    async def list_all(self) -> list[Role]:
        return list(self._roles.values())

    async def add(self, role: Role) -> None:
        self._roles[role.id] = role

    async def update(self, role: Role) -> None:
        self._roles[role.id] = role
