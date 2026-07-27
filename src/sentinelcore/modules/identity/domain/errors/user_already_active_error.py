from sentinelcore.shared.domain.errors.conflict_error import ConflictError


class UserAlreadyActiveError(ConflictError):
    code = "user_already_active"
