from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SentinelCore"
    app_env: str = "development"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://sentinelcore:sentinelcore@localhost:5432/sentinelcore"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://sentinelcore:sentinelcore@localhost:5672/"

    jwt_secret_key: str = "change-me-to-a-random-secret-with-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


@lru_cache
def get_settings() -> Settings:
    return Settings()
