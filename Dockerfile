FROM python:3.13-alpine AS builder
WORKDIR /app
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    apk update &&  \
    pip install uv && \
    uv sync --locked --no-dev
COPY src /app/src/

FROM python:3.13-alpine
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"
CMD ["python"]
