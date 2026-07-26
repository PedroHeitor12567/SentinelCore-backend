from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from sentinelcore.shared.domain.errors import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    RateLimitedError,
    UnauthorizedError,
    ValidationError,
)

_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ValidationError: status.HTTP_400_BAD_REQUEST,
    ConflictError: status.HTTP_409_CONFLICT,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    RateLimitedError: status.HTTP_429_TOO_MANY_REQUESTS,
}


def _resolve_status_code(error: DomainError) -> int:
    for error_type, status_code in _STATUS_BY_ERROR.items():
        if isinstance(error, error_type):
            return status_code
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = _resolve_status_code(exc)
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "detail": exc.message},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
