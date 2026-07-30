from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from sentinelcore.infrastructure.database.base import Base
from sentinelcore.infrastructure.database.session import get_db_session
from sentinelcore.main import app


@pytest.fixture
async def client() -> AsyncGenerator[TestClient]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db_session() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    await engine.dispose()


def _create_active_user(client: TestClient, email: str, password: str) -> str:
    create_response = client.post("/api/v1/users", json={"email": email, "password": password})
    user_id = create_response.json()["id"]
    client.post(f"/api/v1/users/{user_id}/activate")
    return user_id


def test_login_with_valid_credentials_returns_token_pair(client: TestClient) -> None:
    _create_active_user(client, "user@example.com", "s3cr3t!!")

    response = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "s3cr3t!!"})

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    _create_active_user(client, "user@example.com", "s3cr3t!!")

    response = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


def test_login_with_pending_user_returns_401(client: TestClient) -> None:
    client.post("/api/v1/users", json={"email": "pending@example.com", "password": "s3cr3t!!"})

    response = client.post(
        "/api/v1/auth/login", json={"email": "pending@example.com", "password": "s3cr3t!!"}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


def test_refresh_rotates_token_and_old_token_becomes_invalid(client: TestClient) -> None:
    _create_active_user(client, "user@example.com", "s3cr3t!!")
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "s3cr3t!!"}
    )
    old_refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

    assert refresh_response.status_code == 200
    new_refresh_token = refresh_response.json()["refresh_token"]
    assert new_refresh_token != old_refresh_token


def test_reusing_rotated_refresh_token_is_rejected(client: TestClient) -> None:
    _create_active_user(client, "user@example.com", "s3cr3t!!")
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "s3cr3t!!"}
    )
    old_refresh_token = login_response.json()["refresh_token"]
    client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

    reuse_response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

    assert reuse_response.status_code == 401
    assert reuse_response.json()["code"] == "refresh_token_reuse_detected"


def test_refresh_with_unknown_token_returns_401(client: TestClient) -> None:
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "unknown-token"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_refresh_token"


def test_logout_revokes_refresh_token(client: TestClient) -> None:
    _create_active_user(client, "user@example.com", "s3cr3t!!")
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "s3cr3t!!"}
    )
    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 204

    refresh_after_logout = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_after_logout.status_code == 401
    assert refresh_after_logout.json()["code"] == "refresh_token_reuse_detected"
