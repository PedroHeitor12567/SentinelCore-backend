from pydantic import BaseModel, Field
from pydantic.v1 import EmailStr


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
