from sentinelcore.shared.domain.errors.unauthorized_error import UnauthorizedError


class InvalidRefreshTokenError(UnauthorizedError):
    code = "invalid_refresh_token" 
