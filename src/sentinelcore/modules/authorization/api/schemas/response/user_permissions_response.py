from uuid import UUID

from pydantic import BaseModel

from sentinelcore.modules.authorization.application.dtos.output.user_permissions_output import UserPermissionsOutput


class UserPermissionsResponse(BaseModel):
    user_id: UUID
    permission_codes: list[str]

    @classmethod
    def from_output(cls, output: UserPermissionsOutput) -> "UserPermissionsResponse":
        return cls(user_id=output.user_id, permission_codes=output.permission_codes)
