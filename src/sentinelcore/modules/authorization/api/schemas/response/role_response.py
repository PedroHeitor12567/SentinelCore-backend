from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from sentinelcore.modules.authorization.application.dtos.output.role_output import RoleOutput


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str
    permission_ids: list[UUID]
    created_at: datetime

    @classmethod
    def from_output(cls, output: RoleOutput) -> "RoleResponse":
        return cls(
            id=output.id,
            name=output.name,
            description=output.description,
            permission_ids=output.permission_ids,
            created_at=output.created_at,
        )
