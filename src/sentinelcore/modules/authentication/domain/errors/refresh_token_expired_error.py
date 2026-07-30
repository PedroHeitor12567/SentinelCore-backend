from sentinelcore.shared.domain.errors.unauthorized_error import UnauthorizedError


class RefreshTokenExpiredError(UnauthorizedError):
    code = "refresh_token_expired"
