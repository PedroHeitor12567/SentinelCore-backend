from sentinelcore.shared.domain.errors.domain_error import DomainError


class NotFoundError(DomainError):
    code = "not_found"
