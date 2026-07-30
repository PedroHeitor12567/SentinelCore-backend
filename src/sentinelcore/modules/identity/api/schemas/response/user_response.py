from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from sentinelcore.modules.identity.application.dtos.output.user_output import UserOutput


class UserResponse(BaseModel):
    id: UUID
    email: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_output(cls, output: UserOutput) -> "UserResponse":
        return cls(
            id=output.id,
            email=output.email,
            status=output.status,
            created_at=output.created_at,
            updated_at=output.updated_at,
        )

