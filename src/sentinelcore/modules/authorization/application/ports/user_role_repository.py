from typing import Protocol
from uuid import UUID


class UserRoleRepository(Protocol):
    async def assign(self, user_id: UUID, role_id: UUID) -> None: ...

    async def unassign(self, user_id: UUID, role_id: UUID) -> None: ...

    async def list_role_ids_for_user(self, user_id: UUID) -> list[UUID]: ...
