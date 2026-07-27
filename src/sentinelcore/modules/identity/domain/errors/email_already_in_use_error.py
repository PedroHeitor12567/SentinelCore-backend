from sentinelcore.shared.domain.errors.conflict_error import ConflictError


class EmailAlreadyInUseError(ConflictError):
    code = "email_already_in_use"
