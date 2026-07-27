import re
from dataclasses import dataclass

from sentinelcore.shared.domain.errors.validation_error import ValidationError
from sentinelcore.shared.domain.value_object import ValueObject

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_PATTERN.match(self.value):
            raise ValidationError(f"Invalid email address: {self.value}")
        object.__setattr__(self, "value", self.value.lower())

    def __str__(self) -> str:
        return self.value
