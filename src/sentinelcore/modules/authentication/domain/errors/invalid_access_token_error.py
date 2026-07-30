from sentinelcore.shared.domain.errors.unauthorized_error import UnauthorizedError


class InvalidAccessTokenError(UnauthorizedError):
    code = "invalid_access_token"
