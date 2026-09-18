# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY app ./app

RUN useradd --uid 1000 --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
