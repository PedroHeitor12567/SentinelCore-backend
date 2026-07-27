from sentinelcore.shared.domain.errors.conflict_error import ConflictError


class UserAlreadyInactiveError(ConflictError):
    code = "user_already_inactive"
