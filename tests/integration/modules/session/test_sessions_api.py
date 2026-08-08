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


def _login(client: TestClient, email: str = "user@example.com", password: str = "s3cr3t!!") -> dict:
    create_response = client.post("/api/v1/users", json={"email": email, "password": password})
    user_id = create_response.json()["id"]
    client.post(f"/api/v1/users/{user_id}/activate")
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return login_response.json()


def _auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


def test_list_sessions_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/v1/sessions")

    assert response.status_code == 401


def test_list_sessions_returns_the_session_created_by_login(client: TestClient) -> None:
    tokens = _login(client)

    response = client.get("/api/v1/sessions", headers=_auth_headers(tokens["access_token"]))

    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) == 1
    assert sessions[0]["is_revoked"] is False
    assert sessions[0]["user_agent"] is not None


def test_login_records_ip_and_user_agent(client: TestClient) -> None:
    tokens = _login(client)

    response = client.get(
        "/api/v1/sessions",
        headers={**_auth_headers(tokens["access_token"]), "User-Agent": "IntegrationTestClient/1.0"},
    )

    sessions = response.json()
    assert len(sessions) == 1
    assert sessions[0]["ip_address"] is not None


def test_revoke_session_makes_it_appear_revoked_in_listing(client: TestClient) -> None:
    tokens = _login(client)
    sessions_before = client.get(
        "/api/v1/sessions", headers=_auth_headers(tokens["access_token"])
    ).json()
    session_id = sessions_before[0]["id"]

    revoke_response = client.post(
        f"/api/v1/sessions/{session_id}/revoke", headers=_auth_headers(tokens["access_token"])
    )
    assert revoke_response.status_code == 204

    sessions_after = client.get(
        "/api/v1/sessions", headers=_auth_headers(tokens["access_token"])
    ).json()
    assert sessions_after[0]["is_revoked"] is True


def test_revoked_session_can_no_longer_be_used_to_refresh(client: TestClient) -> None:
    tokens = _login(client)
    sessions = client.get("/api/v1/sessions", headers=_auth_headers(tokens["access_token"])).json()
    session_id = sessions[0]["id"]

    client.post(f"/api/v1/sessions/{session_id}/revoke", headers=_auth_headers(tokens["access_token"]))

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 401
    assert refresh_response.json()["code"] == "session_revoked"


def test_revoke_unknown_session_returns_404(client: TestClient) -> None:
    tokens = _login(client)

    response = client.post(
        "/api/v1/sessions/00000000-0000-0000-0000-000000000000/revoke",
        headers=_auth_headers(tokens["access_token"]),
    )

    assert response.status_code == 404
    assert response.json()["code"] == "session_not_found"


def test_user_cannot_revoke_another_users_session(client: TestClient) -> None:
    victim_tokens = _login(client, email="victim@example.com")
    attacker_tokens = _login(client, email="attacker@example.com")
    victim_sessions = client.get(
        "/api/v1/sessions", headers=_auth_headers(victim_tokens["access_token"])
    ).json()
    victim_session_id = victim_sessions[0]["id"]

    response = client.post(
        f"/api/v1/sessions/{victim_session_id}/revoke",
        headers=_auth_headers(attacker_tokens["access_token"]),
    )

    assert response.status_code == 404
    victim_sessions_after = client.get(
        "/api/v1/sessions", headers=_auth_headers(victim_tokens["access_token"])
    ).json()
    assert victim_sessions_after[0]["is_revoked"] is False


def test_session_stays_stable_across_token_rotation(client: TestClient) -> None:
    tokens = _login(client)
    sessions_before = client.get("/api/v1/sessions", headers=_auth_headers(tokens["access_token"])).json()
    assert len(sessions_before) == 1
    session_id_before = sessions_before[0]["id"]
    last_seen_before = sessions_before[0]["last_seen_at"]

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    new_access_token = refresh_response.json()["access_token"]

    sessions_after = client.get("/api/v1/sessions", headers=_auth_headers(new_access_token)).json()

    assert len(sessions_after) == 1
    assert sessions_after[0]["id"] == session_id_before
    assert sessions_after[0]["is_revoked"] is False
    assert sessions_after[0]["last_seen_at"] >= last_seen_before


def test_two_logins_from_same_user_create_two_distinct_sessions(client: TestClient) -> None:
    tokens_1 = _login(client)
    client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "s3cr3t!!"})

    sessions = client.get("/api/v1/sessions", headers=_auth_headers(tokens_1["access_token"])).json()

    assert len(sessions) == 2
