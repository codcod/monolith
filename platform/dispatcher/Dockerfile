# syntax=docker/dockerfile:1
#
# Build context is the repo root (see compose.yaml) — uv needs the workspace
# root (pyproject.toml + uv.lock) plus every platform/* member's pyproject.toml
# to resolve the workspace, even though this image only installs
# stelo-dispatcher and its dependency closure.
#

#
# BUILD
#
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
# build-essential for libc6-dev headers — rbfly (a stelo-base dependency)
# compiles a Cython extension from source, no manylinux wheel available for it.
RUN apt-get update && apt-get install --no-install-recommends -y build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY platform/stelo-base ./platform/stelo-base
COPY platform/dispatcher/pyproject.toml ./platform/dispatcher/pyproject.toml
COPY platform/dispatcher/src ./platform/dispatcher/src
# Sibling members' pyproject.toml only (no src) — uv needs to see the whole
# workspace to resolve, but this image doesn't build or ship their code.
COPY platform/inbox/pyproject.toml ./platform/inbox/pyproject.toml
COPY platform/traffic/pyproject.toml ./platform/traffic/pyproject.toml
COPY platform/admin/pyproject.toml ./platform/admin/pyproject.toml

# --no-editable: workspace members install as regular wheels, so the final
# stage can run off a copied site-packages dir instead of needing /app/platform
# (and its editable-install .pth redirects) around at runtime.
# Strip debug symbols from compiled extensions (rbfly, uvloop, asyncpg, ...) —
# unstripped .so files run ~5-10x larger than they need to for a runtime image.
RUN uv sync --locked --no-dev --no-editable --package stelo-dispatcher \
    && find .venv/lib/python3.13/site-packages -name '*.so' -exec strip -s {} +

#
# RUNTIME
#
# distroless debian13 ships Python 3.13 (3.14 has no distroless build yet) with
# no shell/package manager — smallest, lowest attack surface. Only the venv's
# site-packages are copied over (not the whole venv), so no shell is needed to
# activate it; PYTHONPATH does the same job.
FROM gcr.io/distroless/python3-debian13
WORKDIR /opt/stelo
COPY --from=builder /app/.venv/lib/python3.13/site-packages /opt/site-packages
COPY platform/dispatcher/bin ./bin
COPY platform/dispatcher/config ./config
COPY platform/dispatcher/migrations ./migrations
COPY platform/dispatcher/alembic.ini .
ENV PYTHONPATH=/opt/site-packages

USER nonroot
EXPOSE 8080

# Entrypoint is plain `python` (no shell) so compose can override CMD to run
# migrations instead of the app — see the `*-migrate` services in compose.yaml.
ENTRYPOINT ["python"]
CMD ["bin/stelo-dispatcher", "config/config.toml"]
