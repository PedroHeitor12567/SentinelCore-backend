from uuid import uuid4

from sentinelcore.modules.authorization.application.dtos.input.get_user_permissions_input import (
    GetUserPermissionsInput,
)
from sentinelcore.modules.authorization.application.use_cases.get_user_permissions_use_case import (
    GetUserPermissionsUseCase,
)
from sentinelcore.modules.authorization.domain.entities.permission import Permission
from sentinelcore.modules.authorization.domain.entities.role import Role


async def test_get_user_permissions_aggregates_codes_from_all_roles(
    role_repository, permission_repository, user_role_repository
) -> None:
    create_permission = Permission.create(code="roles:create", description="Create roles")
    read_permission = Permission.create(code="roles:read", description="Read roles")
    await permission_repository.add(create_permission)
    await permission_repository.add(read_permission)

    editor_role = Role.create(name="editor", description="Editor")
    editor_role.grant_permission(create_permission.id)
    viewer_role = Role.create(name="viewer", description="Viewer")
    viewer_role.grant_permission(read_permission.id)
    await role_repository.add(editor_role)
    await role_repository.add(viewer_role)

    user_id = uuid4()
    await user_role_repository.assign(user_id, editor_role.id)
    await user_role_repository.assign(user_id, viewer_role.id)

    use_case = GetUserPermissionsUseCase(user_role_repository, role_repository, permission_repository)
    output = await use_case.execute(GetUserPermissionsInput(user_id=user_id))

    assert output.permission_codes == ["roles:create", "roles:read"]


async def test_get_user_permissions_for_user_without_roles_returns_empty(
    role_repository, permission_repository, user_role_repository
) -> None:
    use_case = GetUserPermissionsUseCase(user_role_repository, role_repository, permission_repository)

    output = await use_case.execute(GetUserPermissionsInput(user_id=uuid4()))

    assert output.permission_codes == []
