from sentinelcore.shared.domain.errors.conflict_error import ConflictError


class PermissionCodeAlreadyInUseError(ConflictError):
    code = "permission_code_already_in_use"
