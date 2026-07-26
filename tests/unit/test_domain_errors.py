from fastapi import FastAPI
from fastapi.testclient import TestClient

from sentinelcore.core.errors.handlers import register_exception_handlers
from sentinelcore.shared.domain.errors import ConflictError, NotFoundError, ValidationError


def _build_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    async def raise_not_found() -> None:
        raise NotFoundError("resource missing")

    @app.get("/conflict")
    async def raise_conflict() -> None:
        raise ConflictError("already exists")

    @app.get("/validation")
    async def raise_validation() -> None:
        raise ValidationError("invalid field")

    return app


client = TestClient(_build_app())


def test_not_found_error_maps_to_404() -> None:
    response = client.get("/not-found")
    assert response.status_code == 404
    assert response.json() == {"code": "not_found", "detail": "resource missing"}


def test_conflict_error_maps_to_409() -> None:
    response = client.get("/conflict")
    assert response.status_code == 409
    assert response.json() == {"code": "conflict", "detail": "already exists"}


def test_validation_error_maps_to_400() -> None:
    response = client.get("/validation")
    assert response.status_code == 400
    assert response.json() == {"code": "validation_error", "detail": "invalid field"}
