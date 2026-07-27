from sentinelcore.shared.domain.errors.domain_error import DomainError


class UnauthorizedError(DomainError):
    code = "unauthorized"
