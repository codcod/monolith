# stelo-platform

A scaffold for independent, multi-module microservice development — not a
real communications platform. The scenario (receive, route, and send a
message over SMS/email/WhatsApp) exists only to give the scaffolding
something concrete to hang off. See [`development/design.md`](development/design.md)
for the full design rationale.

```
client
  |  HTTP POST /messages
  v
inbox        --publish--> [traffic-in stream]
  |
  v (own schema)
inbox DB

traffic      --consume--> [traffic-in stream]
  |
  |--publish--> [dispatch-in stream]
  v (own schema)
traffic DB

dispatcher   --consume--> [dispatch-in stream]
  |
  |--stub send via channel (sms/email/whatsapp)
  v (own schema)
dispatcher DB

admin        --read-only--> inbox DB, traffic DB, dispatcher DB
```

Four independently deployable [aiohttp](https://docs.aiohttp.org/) services
plus a shared library, chained through RabbitMQ Streams:

- **`inbox`** — the only module with a public HTTP API. Accepts a message
  request, writes an intake row, publishes it to the `traffic-in` stream.
- **`traffic`** — background stream consumer. Routes each message (no real
  routing logic in this scaffold) and republishes to `dispatch-in`.
- **`dispatcher`** — background stream consumer. Sends each message over a
  stub `Sender` for its channel and records the outcome.
- **`admin`** — read-only dashboard ("Relay Console") over Server-Sent
  Events, showing pipeline throughput/latency/errors across the other
  three modules' data. Owns no schema of its own.
- **`stelo-base`** — shared streams/messaging/web-app/security helpers, the
  `Config` type and `setup_app`. Not deployed on its own; every service
  above depends on it. The persistence and config helpers (`make_engine`,
  the Alembic runner, the Repository/Unit-of-Work bases,
  `read_config`/`setup_logging`) come from [`monobase`](https://github.com/codcod/monobase), pinned by tag.

## Architecture

Data access goes through the **Repository** and **Unit of Work** patterns
(Percival & Gregory, *Architecture Patterns with Python*), kept on plain
SQLAlchemy Core rather than the ORM — `monobase` provides
`AbstractRepository`/`AbstractUnitOfWork`/`SqlAlchemyUnitOfWork`; each
service builds its own concrete repository/UoW on top. `inbox`, `traffic`,
and `dispatcher` follow the book's layout:

```
src/stelo/<module>/
  domain/         # the module's own persisted entity (not the wire-format Message)
  service_layer/  # orchestration: build the domain object, run it through a UnitOfWork
  adapters/        # the Core table + a Repository converting to/from the domain type
  entrypoints/      # aiohttp routes / stream-consumer loop, thin
```

`admin` is read-only and owns no schema, so it skips `domain`/`service_layer`
and Repository/UoW entirely (Repository/UoW model transactional writes to
an aggregate) — it keeps `adapters/` (read-only table refs + query
functions) and `entrypoints/` only.

## Repo layout

```
platform/
  stelo-base/     # shared library — every service depends on this
  inbox/          # HTTP entrypoint
  traffic/        # stream consumer
  dispatcher/     # stream consumer
  admin/          # read-only dashboard
compose.yaml      # postgres + rabbitmq + migrations + all four services
justfile          # repo-wide up/down/logs/fmt/lint/test, fanning out to every module
```

Each service directory has its own `pyproject.toml`, `Dockerfile`,
`justfile`, `config/config.toml`, and (except `admin`, which owns no
schema) its own independent Alembic migration history under `migrations/`.

## Quickstart

```sh
cp .env.example .env   # only needed once
just up                # docker compose up --build
```

This builds all four service images, starts `postgres` + `rabbitmq`, runs
each service's `*-migrate` one-shot, then starts `inbox` (published on
`$INBOX_PORT`, default `8080`), `traffic`, `dispatcher`, and `admin`
(published on `$ADMIN_PORT`, default `8081`).

```sh
curl -XPOST localhost:8080/messages \
  -H 'Authorization: Bearer dev-token' \
  -H 'Content-Type: application/json' \
  -d '{"channel":"sms","recipient":"+1","body":"hi"}'
```

Then open `localhost:8081` to watch it flow through the pipeline.

## Working on one module locally (no Docker)

```sh
cd platform/inbox
just              # lists this module's recipes
just test         # unit + e2e tiers — fast, no docker needed
just run          # needs `just up` at the repo root first, for postgres/rabbitmq
```

The repo-root [`justfile`](justfile) fans `fmt`/`lint`/`test`/`clean` out to
every module (`just fmt`, `just lint`, `just test`, `just clean`).

## Testing

`inbox`/`traffic`/`dispatcher` split their tests into three tiers
(`tests/unit`, `tests/integration`, `tests/e2e`); `stelo-base`/`admin` keep
a flatter `unit`/`e2e` split. The default `just <module>::test` never needs
real infrastructure. The one tier that does — `tests/integration`,
exercising a module's repository/UoW against a real Postgres — is skipped
unless explicitly requested:

```sh
just up                       # postgres needs to be running
just inbox::test-integration  # RUN_INTEGRATION_TESTS=1 pytest tests/integration
```

## More docs

- [`PACKAGING.md`](PACKAGING.md) — the uv workspace, Docker image build, tooling.
- [`RELEASING.md`](RELEASING.md) — cutting a release per service.
- [`CHANGELOG.md`](CHANGELOG.md) — notable changes, per service.
- [`development/design.md`](development/design.md) — full design rationale,
  including what's explicitly out of scope for this scaffold.
