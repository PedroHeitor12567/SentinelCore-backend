class DomainError(Exception):
    code: str = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

class NotFoundError(DomainError):
    code = "not_found"

class ValidationError(DomainError):
    code = "validation_error"

class ConflictError(DomainError):
    code = "conflict"

class UnauthorizedError(DomainError):
    code = "unauthorized"

class ForbiddenError(DomainError):
    code = "forbidden"

class RateLimitedError(DomainError):
    code = "rate_limited"
    
