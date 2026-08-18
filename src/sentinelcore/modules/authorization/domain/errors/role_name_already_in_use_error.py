from sentinelcore.shared.domain.errors.conflict_error import ConflictError


class RoleNameAlreadyInUseError(ConflictError):
    code = "role_name_already_in_use"
