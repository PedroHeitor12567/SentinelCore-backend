import pytest

from sentinelcore.modules.identity.domain.value_objects.email import Email
from sentinelcore.shared.domain.errors.validation_error import ValidationError


def test_valid_email_is_normalized_to_lowercase() -> None:
    email = Email("User@Example.com")

    assert str(email) == "user@example.com"


@pytest.mark.parametrize("invalid_value", ["not-an-email", "missing-at.com", "user@", "@example.com"])
def test_invalid_email_raises_validation_error(invalid_value: str) -> None:
    with pytest.raises(ValidationError):
        Email(invalid_value)
