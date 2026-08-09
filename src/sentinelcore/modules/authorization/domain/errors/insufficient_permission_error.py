from sentinelcore.shared.domain.errors.forbidden_error import ForbiddenError


class InsufficientPermissionError(ForbiddenError):
    code = "insufficient_permission"
