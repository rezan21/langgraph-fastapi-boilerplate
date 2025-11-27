FROM python:3.10-slim-bookworm

# update
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /uvx /bin/

# set and change to working directory
WORKDIR /app

# optimisation
ENV UV_CACHE_DIR=/root/.cache/uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# install dependencies from uv.lock
RUN --mount=type=cache,target=${UV_CACHE_DIR} \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

# copy the rest of the project
COPY . .

# place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
