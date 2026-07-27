from sentinelcore.shared.domain.errors.domain_error import DomainError


class RateLimitedError(DomainError):
    code = "rate_limited"
