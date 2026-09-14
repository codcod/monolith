# Packaging

`stelo-platform` is a [uv workspace](pyproject.toml) (one shared lockfile,
`uv.lock`, at the repo root) with four members under `platform/`:

- **`stelo-base`** — shared config/logging/DB/messaging/security helpers.
  Not deployed on its own; every service below depends on it.
- **`stelo-inbox`** — receives communication requests over HTTP. Needs
  Postgres + RabbitMQ.
- **`stelo-traffic`** — routes messages to their dispatch channel. Needs
  Postgres + RabbitMQ.
- **`stelo-dispatcher`** — sends messages over their target channel. Needs
  Postgres + RabbitMQ.

Each service is an independently deployable process, released and versioned
on its own (see [`RELEASING.md`](RELEASING.md)) — there is no single "platform"
version. `stelo-base` is versioned independently too, since more than one
service depends on it.

## Running the stack

```sh
cp .env.example .env   # only needed once
just up                # docker compose up --build
```

This builds all three service images, starts `postgres` + `rabbitmq`, runs
each service's `*-migrate` one-shot (Alembic, against that service's own
schema), then starts `inbox` (published on `$INBOX_PORT`, default 8080),
`traffic`, and `dispatcher`. See [`compose.yaml`](compose.yaml).

## Building a service image standalone

Each service has its own [`Dockerfile`](platform/inbox/Dockerfile), but the
**build context is the repo root**, not the service directory — uv needs to
see the whole workspace (`pyproject.toml` + `uv.lock` + every member's
`pyproject.toml`) to resolve `stelo-base` as a workspace dependency, even
though the resulting image only ships that one service plus `stelo-base`.

```sh
just inbox::docker-build       # docker build -f platform/inbox/Dockerfile -t stelo-inbox <repo root>
```

The image is a two-stage build: a `ghcr.io/astral-sh/uv` builder stage
(compiles `rbfly`'s Cython extension, `uv sync`s just that one package
non-editable) and a `gcr.io/distroless/python3-debian13` runtime stage (no
shell, no package manager, non-root `USER nonroot`) that only receives the
built `site-packages` plus that service's `bin/`/`config/`/`migrations/`.

## Working on one service locally (no Docker)

Each service directory has its own `justfile` (mirroring `stelo-base`'s),
which drives `uv` against the shared workspace venv at the repo root:

```sh
cd platform/inbox
just              # lists this module's recipes (install/run/test/lint/fmt/migrate/...)
just test         # uv run --project <repo root> pytest -q
just run          # needs `just up` at the repo root first, for postgres/rabbitmq
```

The repo-root [`justfile`](justfile) fans `fmt`/`lint`/`test`/`clean` out to
every module (`just fmt`, `just lint`, `just test`, `just clean`).

## Tooling

- **`uv`** for dependency resolution/installs (one lockfile, one shared
  `.venv` at the repo root).
- **`ruff`** for linting and formatting (line length 88, single-quote style —
  see `[tool.ruff]` in the root [`pyproject.toml`](pyproject.toml)).
- **`ty`** for type-checking, scoped to each module's `src/` — test doubles
  under `tests/` use loose fakes that aren't meant to type-check against the
  real classes they stand in for, so `ty` is never pointed at `tests/`.
