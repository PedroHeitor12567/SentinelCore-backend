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


def test_create_user_returns_201_with_pending_status(client: TestClient) -> None:
    response = client.post("/api/v1/users", json={"email": "user@example.com", "password": "s3cr3t!!"})

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert body["status"] == "pending"


def test_create_user_with_duplicate_email_returns_409(client: TestClient) -> None:
    client.post("/api/v1/users", json={"email": "user@example.com", "password": "s3cr3t!!"})

    response = client.post("/api/v1/users", json={"email": "user@example.com", "password": "other-pass"})

    assert response.status_code == 409
    assert response.json()["code"] == "email_already_in_use"


def test_create_user_with_invalid_email_returns_422(client: TestClient) -> None:
    response = client.post("/api/v1/users", json={"email": "not-an-email", "password": "s3cr3t!!"})

    assert response.status_code == 422


def test_get_unknown_user_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["code"] == "user_not_found"


def test_full_lifecycle_create_activate_deactivate(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/users", json={"email": "lifecycle@example.com", "password": "s3cr3t!!"}
    )
    user_id = create_response.json()["id"]

    activate_response = client.post(f"/api/v1/users/{user_id}/activate")
    assert activate_response.status_code == 200
    assert activate_response.json()["status"] == "active"

    deactivate_response = client.post(f"/api/v1/users/{user_id}/deactivate")
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["status"] == "inactive"

    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "inactive"


def test_activate_already_active_user_returns_409(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/users", json={"email": "double-activate@example.com", "password": "s3cr3t!!"}
    )
    user_id = create_response.json()["id"]
    client.post(f"/api/v1/users/{user_id}/activate")

    response = client.post(f"/api/v1/users/{user_id}/activate")

    assert response.status_code == 409
    assert response.json()["code"] == "user_already_active"
