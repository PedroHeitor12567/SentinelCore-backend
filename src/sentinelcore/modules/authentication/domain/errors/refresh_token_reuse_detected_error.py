from sentinelcore.shared.domain.errors.unauthorized_error import UnauthorizedError


class RefreshTokenReuseDetectedError(UnauthorizedError):
    code = "refresh_token_reuse_detected"
