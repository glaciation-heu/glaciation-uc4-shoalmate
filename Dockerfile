# The code below is inspired by https://github.com/astral-sh/uv-docker-example

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /app
COPY src /app/src
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev && \
    find . -type d -name "__pycache__" -exec rm -r {} +

FROM python:3.13-slim-bookworm
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"
CMD ["python", "-m", "shoalmate.main"]