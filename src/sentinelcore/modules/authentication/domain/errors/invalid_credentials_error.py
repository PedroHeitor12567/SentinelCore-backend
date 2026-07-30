from sentinelcore.shared.domain.errors.unauthorized_error import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    code = "invalid_credentials"
