from datetime import timedelta
from uuid import uuid4

from sentinelcore.modules.audit.domain.enums.audit_event_type import AuditEventType
from sentinelcore.modules.authentication.application.dtos.input.login_input import LoginInput
from sentinelcore.modules.authentication.application.use_cases.login_use_case import LoginUseCase
from sentinelcore.modules.authentication.domain.errors.invalid_credentials_error import (
    InvalidCredentialsError,
)
from sentinelcore.modules.authorization.application.dtos.input.assign_role_input import AssignRoleInput
from sentinelcore.modules.authorization.application.dtos.input.create_permission_input import (
    CreatePermissionInput,
)
from sentinelcore.modules.authorization.application.dtos.input.create_role_input import CreateRoleInput
from sentinelcore.modules.authorization.application.dtos.input.grant_permission_input import (
    GrantPermissionInput,
)
from sentinelcore.modules.authorization.application.use_cases.assign_role_to_user_use_case import (
    AssignRoleToUserUseCase,
)
from sentinelcore.modules.authorization.application.use_cases.create_permission_use_case import (
    CreatePermissionUseCase,
)
from sentinelcore.modules.authorization.application.use_cases.create_role_use_case import CreateRoleUseCase
from sentinelcore.modules.authorization.application.use_cases.grant_permission_to_role_use_case import (
    GrantPermissionToRoleUseCase,
)
from sentinelcore.modules.authorization.domain.entities.role import Role
from sentinelcore.modules.identity.application.dtos.input.create_user_input import CreateUserInput
from sentinelcore.modules.identity.application.use_cases.create_user_use_case import CreateUserUseCase
from sentinelcore.modules.identity.domain.entities.user import User
from sentinelcore.modules.identity.domain.value_objects.email import Email

_TTL = timedelta(days=7)


async def test_successful_login_records_login_success_event(
    user_repository,
    password_hasher,
    session_repository,
    refresh_token_repository,
    token_service,
    clock,
    unit_of_work,
    audit_log_repository,
) -> None:
    user = User.create(email=Email("user@example.com"), password_hash=password_hasher.hash("s3cr3t!!"))
    user.activate()
    await user_repository.add(user)
    use_case = LoginUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        session_repository=session_repository,
        refresh_token_repository=refresh_token_repository,
        token_service=token_service,
        clock=clock,
        unit_of_work=unit_of_work,
        refresh_token_ttl=_TTL,
        audit_log_repository=audit_log_repository,
    )

    await use_case.execute(
        LoginInput(email="user@example.com", password="s3cr3t!!", ip_address="203.0.113.1")
    )

    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.LOGIN_SUCCESS
    assert log.actor_id == user.id
    assert log.ip_address == "203.0.113.1"


async def test_failed_login_records_login_failure_event(
    user_repository,
    password_hasher,
    session_repository,
    refresh_token_repository,
    token_service,
    clock,
    unit_of_work,
    audit_log_repository,
) -> None:
    use_case = LoginUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        session_repository=session_repository,
        refresh_token_repository=refresh_token_repository,
        token_service=token_service,
        clock=clock,
        unit_of_work=unit_of_work,
        refresh_token_ttl=_TTL,
        audit_log_repository=audit_log_repository,
    )

    try:
        await use_case.execute(LoginInput(email="missing@example.com", password="s3cr3t!!"))
    except InvalidCredentialsError:
        pass

    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.LOGIN_FAILURE
    assert log.actor_id is None
    assert log.metadata["email"] == "missing@example.com"


async def test_create_user_records_user_created_event(
    user_repository, password_hasher, unit_of_work, audit_log_repository
) -> None:
    use_case = CreateUserUseCase(user_repository, password_hasher, unit_of_work, audit_log_repository)

    output = await use_case.execute(CreateUserInput(email="new@example.com", password="s3cr3t!!"))

    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.USER_CREATED
    assert log.target_id == output.id


async def test_create_role_records_sensitive_operation_event(role_repository, unit_of_work, audit_log_repository) -> None:
    actor_id = uuid4()
    use_case = CreateRoleUseCase(role_repository, unit_of_work, audit_log_repository)

    await use_case.execute(CreateRoleInput(name="admin", description="Administrator", actor_id=actor_id))

    assert len(audit_log_repository.logs) == 1
    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.SENSITIVE_OPERATION
    assert log.actor_id == actor_id


async def test_create_permission_records_sensitive_operation_event(
    permission_repository, unit_of_work, audit_log_repository
) -> None:
    use_case = CreatePermissionUseCase(permission_repository, unit_of_work, audit_log_repository)

    await use_case.execute(CreatePermissionInput(code="roles:create", description="Create roles"))

    assert audit_log_repository.logs[0].event_type == AuditEventType.SENSITIVE_OPERATION


async def test_grant_permission_records_permission_changed_event(
    role_repository, permission_repository, unit_of_work, audit_log_repository
) -> None:
    role = Role.create(name="admin", description="Administrator")
    await role_repository.add(role)
    from sentinelcore.modules.authorization.domain.entities.permission import Permission

    permission = Permission.create(code="roles:create", description="Create roles")
    await permission_repository.add(permission)
    actor_id = uuid4()
    use_case = GrantPermissionToRoleUseCase(role_repository, permission_repository, unit_of_work, audit_log_repository)

    await use_case.execute(
        GrantPermissionInput(role_id=role.id, permission_id=permission.id, actor_id=actor_id)
    )

    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.PERMISSION_CHANGED
    assert log.actor_id == actor_id
    assert log.metadata["action"] == "permission_granted"


async def test_assign_role_records_permission_changed_event(
    role_repository, user_role_repository, unit_of_work, audit_log_repository
) -> None:
    role = Role.create(name="admin", description="Administrator")
    await role_repository.add(role)
    user_id = uuid4()
    actor_id = uuid4()
    use_case = AssignRoleToUserUseCase(role_repository, user_role_repository, unit_of_work, audit_log_repository)

    await use_case.execute(AssignRoleInput(user_id=user_id, role_id=role.id, actor_id=actor_id))

    log = audit_log_repository.logs[0]
    assert log.event_type == AuditEventType.PERMISSION_CHANGED
    assert log.actor_id == actor_id
    assert log.target_id == user_id
    assert log.metadata["action"] == "role_assigned"
