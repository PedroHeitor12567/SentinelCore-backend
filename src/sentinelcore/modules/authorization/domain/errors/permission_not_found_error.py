from sentinelcore.shared.domain.errors.not_found_error import NotFoundError


class PermissionNotFoundError(NotFoundError):
    code = "permission_not_found"
