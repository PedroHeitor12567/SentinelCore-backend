from sentinelcore.shared.domain.errors.not_found_error import NotFoundError


class RoleNotFoundError(NotFoundError):
    code = "role_not_found"
