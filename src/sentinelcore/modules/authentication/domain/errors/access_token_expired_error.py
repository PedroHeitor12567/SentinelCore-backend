from sentinelcore.shared.domain.errors.unauthorized_error import UnauthorizedError


class AccessTokenExpiredError(UnauthorizedError):
    code = "access_token_expired"
