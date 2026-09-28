# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); each service under
`platform/` is versioned independently (see [`PACKAGING.md`](PACKAGING.md) and
[`RELEASING.md`](RELEASING.md)), following [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `stelo-base`: shared streams/messaging/web-app/security helpers, as a uv
  workspace package other services depend on.
- `stelo-inbox`: receives communication requests over HTTP, persists them, and
  publishes them onto the `traffic-in` RabbitMQ stream.
- `stelo-traffic`: consumes `traffic-in`, routes each message to its dispatch
  channel, and republishes onto `dispatch-in`.
- `stelo-dispatcher`: consumes `dispatch-in` and sends each message over its
  target channel.
- Docker Compose stack (`postgres` + `rabbitmq` + one `*-migrate` one-shot and
  one deployable service per app) and a per-service production `Dockerfile`.
- Settings externalized to `.env` (`POSTGRES_*`, `INBOX_PORT`) — see
  [`.env.example`](.env.example).

### Changed

- Every service and `stelo-base` now take `make_engine`, the Alembic runner,
  the Repository/Unit-of-Work bases and `read_config`/`setup_logging` from
  [`monobase`](https://github.com/codcod/monobase) v0.1.0, pinned by archive
  URL in the root `pyproject.toml`. Those modules and their tests leave
  `stelo-base`, and `setup_app` passes the log level to `setup_logging`.
- Converted `platform/` to a [uv workspace](pyproject.toml) (`stelo-base`,
  `stelo-inbox`, `stelo-traffic`, `stelo-dispatcher`) with one shared lockfile,
  replacing the previous per-module `pip`/`venv` setup.
- Switched linting/formatting from black+isort+flake8+pylint+pyright to
  `ruff` (line length 88, single quotes) and `ty`.
- Production images: alpine + pip → `python:3.13-slim-bookworm`/`ghcr.io/astral-sh/uv`
  builder stage + `gcr.io/distroless/python3-debian13` runtime stage (no shell,
  no package manager, non-root). Migrations run as their own one-shot
  (`*-migrate` in `compose.yaml`) instead of being chained onto the app's
  startup command, since the runtime image has no shell to chain `&&` with.

[Unreleased]: https://github.com/umbrella-org/monolith/commits/main
