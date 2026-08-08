from sentinelcore.shared.domain.errors.unauthorized_error import UnauthorizedError


class SessionRevokedError(UnauthorizedError):
    code = "session_revoked"
