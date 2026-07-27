from sentinelcore.shared.domain.errors.domain_error import DomainError


class ForbiddenError(DomainError):
    code = "forbidden"
