from datetime import datetime, UTC
from uuid import UUID, uuid4

from sentinelcore.modules.identity.domain.enums.user_status import UserStatus
from sentinelcore.modules.identity.domain.errors.user_already_active_error import UserAlreadyActiveError
from sentinelcore.modules.identity.domain.errors.user_already_inactive_error import UserAlreadyInactiveError
from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.shared.domain.entity import Entity


class User(Entity):
    def __init__(self, id: UUID, email: Email, password_hash: str, status: UserStatus, created_at: datetime, updated_at: datetime) -> None:
        super().__init__(id)
        self.email = email
        self.password_hash = password_hash
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create(cls, email: Email, password_hash: str) -> "User":
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            status=UserStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

    def activate(self) -> None:
        if self.status == UserStatus.ACTIVE:
            raise UserAlreadyActiveError(f"User {self.id} is already active")
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        if self.status == UserStatus.INACTIVE:
            raise UserAlreadyInactiveError(f"User {self.id} is already inactive")
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now(UTC)

    def change_password(self, new_password_hash: str) -> None:
        self.password_hash = new_password_hash
        self.updated_at = datetime.now(UTC)
