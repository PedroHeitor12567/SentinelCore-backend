FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY src ./src

RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "sentinelcore.main:app", "--host", "0.0.0.0", "--port", "8000"]
