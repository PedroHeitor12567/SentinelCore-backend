from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from sentinelcore.infrastructure.database.base import Base
from sentinelcore.infrastructure.database.session import get_db_session
from sentinelcore.main import app
from sentinelcore.modules.authorization.infrastructure.models.permission_model import PermissionModel
from sentinelcore.modules.authorization.infrastructure.models.role_model import RoleModel
from sentinelcore.modules.authorization.infrastructure.models.role_permission_model import RolePermissionModel
from sentinelcore.modules.authorization.infrastructure.models.user_role_model import UserRoleModel

ALL_PERMISSION_CODES = [
    "roles:create",
    "roles:read",
    "roles:manage_permissions",
    "permissions:create",
    "permissions:read",
    "users:manage_roles",
    "users:read_permissions",
]


@pytest.fixture
async def session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.fixture
async def client(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[TestClient]:
    async def override_get_db_session() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


async def _grant_all_permissions_to_user(
    session_factory: async_sessionmaker[AsyncSession], user_id: UUID
) -> None:
    async with session_factory() as session:
        role_id = uuid4()
        session.add(RoleModel(id=role_id, name="test-admin", description="Full access", created_at=datetime.now(UTC)))

        for code in ALL_PERMISSION_CODES:
            permission_id = uuid4()
            session.add(
                PermissionModel(id=permission_id, code=code, description=code, created_at=datetime.now(UTC))
            )
            session.add(RolePermissionModel(role_id=role_id, permission_id=permission_id))

        session.add(UserRoleModel(user_id=user_id, role_id=role_id))
        await session.commit()


def _create_and_login(
    client: TestClient, email: str = "user@example.com", password: str = "s3cr3t!!"
) -> dict:
    create_response = client.post("/api/v1/users", json={"email": email, "password": password})
    user_id = create_response.json()["id"]
    client.post(f"/api/v1/users/{user_id}/activate")
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    tokens = login_response.json()
    tokens["user_id"] = user_id
    return tokens


def _auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


async def test_create_role_without_permission_returns_403(client: TestClient) -> None:
    tokens = _create_and_login(client)

    response = client.post(
        "/api/v1/roles",
        json={"name": "admin", "description": "Administrator"},
        headers=_auth_headers(tokens["access_token"]),
    )

    assert response.status_code == 403
    assert response.json()["code"] == "insufficient_permission"


async def test_create_role_without_token_returns_401(client: TestClient) -> None:
    response = client.post("/api/v1/roles", json={"name": "admin", "description": "Administrator"})

    assert response.status_code == 401


async def test_create_role_with_permission_returns_201(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client)
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))

    response = client.post(
        "/api/v1/roles",
        json={"name": "admin", "description": "Administrator"},
        headers=_auth_headers(tokens["access_token"]),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "admin"
    assert body["permission_ids"] == []


async def test_create_role_with_duplicate_name_returns_409(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client)
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))
    client.post(
        "/api/v1/roles",
        json={"name": "admin", "description": "Administrator"},
        headers=_auth_headers(tokens["access_token"]),
    )

    response = client.post(
        "/api/v1/roles",
        json={"name": "admin", "description": "Other"},
        headers=_auth_headers(tokens["access_token"]),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "role_name_already_in_use"


async def test_create_permission_and_list_permissions(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client)
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))

    create_response = client.post(
        "/api/v1/permissions",
        json={"code": "reports:read", "description": "Read reports"},
        headers=_auth_headers(tokens["access_token"]),
    )
    assert create_response.status_code == 201
    assert create_response.json()["code"] == "reports:read"

    list_response = client.get("/api/v1/permissions", headers=_auth_headers(tokens["access_token"]))
    codes = [item["code"] for item in list_response.json()]
    assert "reports:read" in codes


async def test_create_permission_with_duplicate_code_returns_409(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client)
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))
    client.post(
        "/api/v1/permissions",
        json={"code": "reports:read", "description": "Read reports"},
        headers=_auth_headers(tokens["access_token"]),
    )

    response = client.post(
        "/api/v1/permissions",
        json={"code": "reports:read", "description": "Other"},
        headers=_auth_headers(tokens["access_token"]),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "permission_code_already_in_use"


async def test_grant_and_revoke_permission_on_role(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client)
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))
    headers = _auth_headers(tokens["access_token"])

    role_id = client.post(
        "/api/v1/roles", json={"name": "editor", "description": "Editor"}, headers=headers
    ).json()["id"]
    permission_id = client.post(
        "/api/v1/permissions", json={"code": "posts:write", "description": "Write posts"}, headers=headers
    ).json()["id"]

    grant_response = client.post(f"/api/v1/roles/{role_id}/permissions/{permission_id}", headers=headers)
    assert grant_response.status_code == 200
    assert permission_id in grant_response.json()["permission_ids"]

    revoke_response = client.delete(f"/api/v1/roles/{role_id}/permissions/{permission_id}", headers=headers)
    assert revoke_response.status_code == 200
    assert permission_id not in revoke_response.json()["permission_ids"]


async def test_assign_role_grants_permission_to_target_user(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    admin_tokens = _create_and_login(client, email="admin@example.com")
    await _grant_all_permissions_to_user(session_factory, UUID(admin_tokens["user_id"]))
    admin_headers = _auth_headers(admin_tokens["access_token"])

    target_tokens = _create_and_login(client, email="target@example.com")
    target_headers = _auth_headers(target_tokens["access_token"])

    role_id = client.post(
        "/api/v1/roles", json={"name": "editor", "description": "Editor"}, headers=admin_headers
    ).json()["id"]
    permission_id = client.post(
        "/api/v1/permissions", json={"code": "posts:write", "description": "Write posts"}, headers=admin_headers
    ).json()["id"]
    client.post(f"/api/v1/roles/{role_id}/permissions/{permission_id}", headers=admin_headers)

    assign_response = client.post(
        f"/api/v1/users/{target_tokens['user_id']}/roles/{role_id}", headers=admin_headers
    )
    assert assign_response.status_code == 204

    permissions_response = client.get(
        f"/api/v1/users/{target_tokens['user_id']}/permissions", headers=target_headers
    )
    assert permissions_response.status_code == 200
    assert permissions_response.json()["permission_codes"] == ["posts:write"]

    unassign_response = client.delete(
        f"/api/v1/users/{target_tokens['user_id']}/roles/{role_id}", headers=admin_headers
    )
    assert unassign_response.status_code == 204

    permissions_after_response = client.get(
        f"/api/v1/users/{target_tokens['user_id']}/permissions", headers=target_headers
    )
    assert permissions_after_response.json()["permission_codes"] == []


async def test_user_can_read_own_permissions_without_extra_permission(client: TestClient) -> None:
    tokens = _create_and_login(client)

    response = client.get(
        f"/api/v1/users/{tokens['user_id']}/permissions", headers=_auth_headers(tokens["access_token"])
    )

    assert response.status_code == 200
    assert response.json()["permission_codes"] == []


async def test_user_cannot_read_another_users_permissions_without_permission(client: TestClient) -> None:
    victim_tokens = _create_and_login(client, email="victim@example.com")
    attacker_tokens = _create_and_login(client, email="attacker@example.com")

    response = client.get(
        f"/api/v1/users/{victim_tokens['user_id']}/permissions",
        headers=_auth_headers(attacker_tokens["access_token"]),
    )

    assert response.status_code == 403
    assert response.json()["code"] == "insufficient_permission"
