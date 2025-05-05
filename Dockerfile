FROM ghcr.io/astral-sh/uv:python3.13-alpine

ADD . /formodoro
WORKDIR /formodoro
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

CMD [".venv/bin/uvicorn", "formodoro.main:app", "--host", "0.0.0.0", "--port", "8000"]