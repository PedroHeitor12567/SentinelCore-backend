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
    "audit:read",
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


async def test_list_audit_logs_without_permission_returns_403(client: TestClient) -> None:
    tokens = _create_and_login(client)

    response = client.get("/api/v1/audit-logs", headers=_auth_headers(tokens["access_token"]))

    assert response.status_code == 403
    assert response.json()["code"] == "insufficient_permission"


async def test_list_audit_logs_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/v1/audit-logs")

    assert response.status_code == 401


async def test_user_creation_and_login_are_recorded_and_listable(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client, email="admin@example.com")
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))
    headers = _auth_headers(tokens["access_token"])

    response = client.get("/api/v1/audit-logs", headers=headers)

    assert response.status_code == 200
    event_types = [entry["event_type"] for entry in response.json()]
    assert "user_created" in event_types
    assert "login_success" in event_types


async def test_failed_login_is_recorded(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client, email="admin@example.com")
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))
    headers = _auth_headers(tokens["access_token"])

    client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "wrong-password"})

    response = client.get("/api/v1/audit-logs", headers=headers)
    event_types = [entry["event_type"] for entry in response.json()]
    assert "login_failure" in event_types


async def test_role_creation_and_permission_grant_are_recorded(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client, email="admin@example.com")
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))
    headers = _auth_headers(tokens["access_token"])

    role_id = client.post(
        "/api/v1/roles", json={"name": "editor", "description": "Editor"}, headers=headers
    ).json()["id"]
    permission_id = client.post(
        "/api/v1/permissions", json={"code": "posts:write", "description": "Write posts"}, headers=headers
    ).json()["id"]
    client.post(f"/api/v1/roles/{role_id}/permissions/{permission_id}", headers=headers)

    response = client.get("/api/v1/audit-logs", headers=headers)
    event_types = [entry["event_type"] for entry in response.json()]
    assert "sensitive_operation" in event_types
    assert "permission_changed" in event_types

    actors = [entry["actor_id"] for entry in response.json() if entry["event_type"] == "permission_changed"]
    assert tokens["user_id"] in actors


async def test_audit_logs_respect_limit_query_param(
    client: TestClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    tokens = _create_and_login(client, email="admin@example.com")
    await _grant_all_permissions_to_user(session_factory, UUID(tokens["user_id"]))
    headers = _auth_headers(tokens["access_token"])

    response = client.get("/api/v1/audit-logs?limit=1", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
