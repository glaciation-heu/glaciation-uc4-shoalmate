FROM python:3.13-alpine AS builder
WORKDIR /app
COPY src /app/src
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip install uv && \
    uv sync --locked --no-dev && \
    find . -type d -name "__pycache__" -exec rm -r {} +

FROM python:3.13-alpine
COPY --from=builder --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src"
CMD ["python", "-m", "shoalmate.main"]