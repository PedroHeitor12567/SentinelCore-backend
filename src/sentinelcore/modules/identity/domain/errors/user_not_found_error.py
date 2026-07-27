from sentinelcore.shared.domain.errors.not_found_error import NotFoundError

class UserNotFoundError(NotFoundError):
    code = "user_not_found"
