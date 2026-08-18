from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from sentinelcore.modules.authorization.application.dtos.output.permission_output import PermissionOutput


class PermissionResponse(BaseModel):
    id: UUID
    code: str
    description: str
    created_at: datetime

    @classmethod
    def from_output(cls, output: PermissionOutput) -> "PermissionResponse":
        return cls(
            id=output.id,
            code=output.code,
            description=output.description,
            created_at=output.created_at,
        )
