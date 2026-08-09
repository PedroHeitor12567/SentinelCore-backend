from pydantic import BaseModel, Field


class CreatePermissionRequest(BaseModel):
    code: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=255)
