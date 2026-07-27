from sentinelcore.shared.domain.errors.domain_error import DomainError


class ConflictError(DomainError):
    code = "conflict"
