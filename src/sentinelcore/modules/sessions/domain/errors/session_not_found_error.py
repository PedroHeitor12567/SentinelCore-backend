from sentinelcore.shared.domain.errors.not_found_error import NotFoundError


class SessionNotFoundError(NotFoundError):
    code = "session_not_found"
