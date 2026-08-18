from uuid import UUID


class FakeUserRoleRepository:
    def __init__(self) -> None:
        self._links: set[tuple[UUID, UUID]] = set()

    async def assign(self, user_id: UUID, role_id: UUID) -> None:
        self._links.add((user_id, role_id))

    async def unassign(self, user_id: UUID, role_id: UUID) -> None:
        self._links.discard((user_id, role_id))

    async def list_role_ids_for_user(self, user_id: UUID) -> list[UUID]:
        return [
            role_id
            for (uid, role_id) in self._links
            if uid == user_id
        ]
