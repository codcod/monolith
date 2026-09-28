# Design: inbox / traffic / dispatcher

## Purpose

This is a **scaffold for independent, multi-module microservice development**,
not a real communications platform. The scenario (receive, route, and send a
message over SMS/email/WhatsApp) exists only to give the scaffolding
something concrete to hang off. Features are kept to the minimum needed to
prove the pattern: independent versioning/release per module, a shared
approach to logging/config/security/DB access, and a realistic
queue-based hand-off between modules.

Everything under "Explicitly out of scope" is a deliberate cut, not an
oversight.

## System overview

Three independently deployable aiohttp services, chained through RabbitMQ
Streams:

```
client
  |  HTTP POST /messages
  v
inbox        --outbox relay--> [traffic-in stream]
  |
  v (own schema: messages + outbox, one transaction)
inbox DB

traffic      --consume--> [traffic-in stream]
  |
  |--outbox relay--> [dispatch-in stream]
  v (own schema: messages + outbox, one transaction)
traffic DB

dispatcher   --consume--> [dispatch-in stream]
  |
  |--stub send via channel (sms/email/whatsapp)
  v (own schema)
dispatcher DB
```

- **inbox**: only module with a public HTTP API. Accepts a message request,
  validates it minimally, writes an intake row and an outbox row in one
  transaction; a relay publishes it to the `traffic-in` stream.
- **traffic**: background stream consumer. Reads from `traffic-in`, writes a
  routing row and an outbox row for `dispatch-in` in one transaction, and
  skips an id it has already routed. No real routing logic — for this
  scaffold the channel is whatever the caller specified in the payload.
- **dispatcher**: background stream consumer. Reads from `dispatch-in`,
  calls a stub `Sender` for the requested channel (logs "would send via
  X"), writes a final status row. Skips an id it has already sent.

**Outbox.** inbox and traffic never publish straight after a commit: a
crash in between would lose a stored message. Each has an `outbox` table in
its own schema (`monobase.outbox.outbox_table`, created by its own Alembic
revision), and the service adds the wire message to it (`event_id` = message
id, `destination` = stream name, `payload` = the JSON wire message) in the
same transaction as its own row. `stelo.base.webapp.run_outbox_relay` runs
monobase's `run_relay` for the app's lifetime and publishes each row to its
`destination`. monobase allows one relay per table, so inbox, which forks
`workers` processes, runs it in the first worker only. Delivery into the
stream is at-least-once, and consumers subscribe at `Offset.NEXT`, so a
message published before a consumer first subscribes is not consumed. traffic
and dispatcher look the id up first and skip one they have already recorded
(a redelivered id would otherwise hit the primary key and kill the consumer
task). A failed or cancelled stream send (the relay's `deliver_timeout`)
drops and closes the cached rbfly publisher, so the next send starts a fresh
one.

Each module also exposes `GET /health` over aiohttp so it can run as a normal
web service in compose/k8s even though inbox is the only one with real
business routes.

## Message shape

One minimal shape flows through both streams, as plain JSON (AMQP 1.0 body
via rbfly's `amqp=True` default):

```json
{
  "id": "uuid4 string",
  "channel": "sms | email | whatsapp",
  "recipient": "string (phone/email/handle)",
  "body": "string",
  "status": "received | routed | sent",
  "created_at": "ISO 8601"
}
```

Defined once as a `TypedDict` in `stelo-base` (`stelo.base.messages`), reused
by all three modules — this is the one piece of "domain" shape shared across
schema boundaries; everything else per-module is free to differ.

## Database

One Postgres instance, one schema per module — same connection pattern,
different tables/columns per module's own concern:

| schema       | table          | columns (minimal)                                   |
|--------------|----------------|------------------------------------------------------|
| `inbox`      | `messages`     | id, channel, recipient, body, received_at             |
| `traffic`    | `messages`     | id, channel, recipient, routed_at                      |
| `dispatcher` | `messages`     | id, channel, recipient, send_status, sent_at           |

Connection: SQLAlchemy **core** (no ORM), async engine via `asyncpg`,
built by one shared helper. Writes go through the Repository and Unit of
Work patterns (Percival & Gregory, *Architecture Patterns with Python*) —
see "Shared library: `stelo-base`" and "Per-module layout" below — kept
Core-only rather than pulling in the SQLAlchemy ORM: Repository/UoW don't
require a mapper, only a place to put "one transaction, one collection of
domain objects."

```python
# monobase.db
def make_engine(dsn: str) -> AsyncEngine:
    return create_async_engine(dsn, pool_pre_ping=True)
```

Every module uses the *same* DSN (`postgresql+asyncpg://stelo:stelo@postgres/stelo`)
— the schema split happens in code, not in the connection string: each
module's `sqlalchemy.Table` objects pass `schema="<module>"` explicitly, so
one engine-construction pattern works for all three regardless of which
schema they own.

Schema/table creation is managed by **Alembic**, one independent migration
history per module (see "Migrations" below) — there is no init-SQL script
seeded into the `postgres` container.

## Shared library: `stelo-base`

New module at `platform/stelo-base`, versioned and released independently,
depended on by the other three as an unpinned local dependency (a real
package index would replace this later, out of scope now — see
"Versioning / release").

The persistence and config helpers that used to live here — `make_engine`,
the async Alembic `env.py` runner, `AbstractRepository`,
`AbstractUnitOfWork`/`SqlAlchemyUnitOfWork` and `read_config`/`setup_logging`
— moved to [`monobase`](https://github.com/codcod/monobase) (`monobase.db`, `.migrations`, `.repository`, `.uow`,
`.config`), which every module depends on, pinned by tag in the root
`pyproject.toml`. What follows is what stays in stelo-base.

```
platform/stelo-base/
  pyproject.toml       # hatchling, PEP 621 [project] table
  src/stelo/base/
    __init__.py
    config.py          # Config TypedDict + setup_app (logging via monobase, uvloop)
    streams.py          # thin wrapper over rbfly: publish(), consume()
    security.py         # aiohttp middleware: request-id + bearer-token stub
    webapp.py           # make_app()/run_in_background()/run_outbox_relay() + typed AppKeys
    channels.py         # Sender protocol + Sms/Email/WhatsApp stub senders
    messages.py         # shared Message TypedDict
  tests/                # unit tests for every module above
```

- **config.py**: the `Config` TypedDict and `setup_app`, which calls
  `monobase.config.setup_logging(config.get("log_level"))` (UTC timestamps,
  `force=True`) and installs uvloop.
- **streams.py**: wraps `rbfly.streams.streams_client` — connects using the
  `rabbitmq-stream://` URL from config (`RABBITMQ_BROKER_URL` in
  `compose.yaml`). `connect()` just builds the client (connection itself is
  lazy); `publish()`/`consume()` JSON-encode/decode messages and create
  their stream on first use.
- **security.py**: minimal aiohttp middleware — stamps a request id on every
  request (`REQUEST_ID_KEY`, an aiohttp `RequestKey`) and a stub
  bearer-token check (reads a static token from config; real auth is out of
  scope but the seam is there).
- **webapp.py**: `make_app(config, *, routes, db_dsn) -> web.Application`
  wires the middleware plus typed `web.AppKey`s (`CONFIG_KEY`, `DB_KEY`,
  `RABBIT_KEY`) via `cleanup_ctx`, so the DB engine/RabbitMQ client connect
  on startup and dispose on shutdown the same way in every module.
  `run_in_background(app, factory)` runs a coroutine (traffic/dispatcher's
  consumer loop) for the app's lifetime alongside its `/health` route.
  `run_outbox_relay(app, table)` uses it to run monobase's outbox relay,
  publishing each row to the stream in its `destination` (see "Outbox").
- **channels.py**:
  ```python
  class Sender(Protocol):
      async def send(self, recipient: str, body: str) -> None: ...

  class SmsSender: ...      # logs "would send SMS to <recipient>: <body>"
  class EmailSender: ...    # logs "would send email to <recipient>: <body>"
  class WhatsAppSender: ... # logs "would send WhatsApp to <recipient>: <body>"

  SENDERS: dict[str, Sender] = {"sms": SmsSender(), "email": EmailSender(), "whatsapp": WhatsAppSender()}
  ```
- **repository.py**: `AbstractRepository[T]` — `add(item)`/`get(id)`, no
  DB-specific code. Concrete repositories (converting between a module's own
  domain dataclass and its Core table) live in that module's own
  `adapters/repository.py`, not here — there's no shared row shape to build
  a generic SQLAlchemy implementation against.
- **unit_of_work.py**: `AbstractUnitOfWork` (async context manager;
  `__aexit__` rolls back unless `commit()` was called) plus
  `SqlAlchemyUnitOfWork`, which owns one `AsyncConnection`/transaction for
  the `async with` block's lifetime. Each module's own
  `service_layer/unit_of_work.py` subclasses it, attaching its repositories
  in `__aenter__`.

## Per-module layout (inbox as example, traffic/dispatcher mirror it)

Each of inbox/traffic/dispatcher follows the layered structure from
*Architecture Patterns with Python* (Percival & Gregory): `domain` (the
module's own persisted entity — distinct from the wire-format `Message`
crossing stream boundaries), `service_layer` (orchestration: builds the
domain object, runs it through a Unit of Work, adding the outgoing message to
the UoW's outbox (inbox, traffic) or calling an injected `sender`
(dispatcher)), `adapters` (the Core table + a Repository converting to/from
the domain dataclass), `entrypoints` (thin aiohttp route handlers /
stream-consumer loop, wiring a concrete `UnitOfWork` per request/message from
`app[DB_KEY]`):

```
platform/inbox/
  pyproject.toml       # hatchling; dependencies = ["monobase", "stelo-base"]
  Dockerfile           # builds only this dir + stelo-base, no requirements.txt
  justfile             # install/run/test/test-integration/perf/migrate/fmt/lint/docker-build
  alembic.ini
  bin/stelo-inbox
  config/config.toml
  migrations/
    env.py             # calls monobase.migrations.run_migrations_online
    versions/0001_...  # CREATE SCHEMA + create_table("messages", schema=...)
  src/stelo/inbox/
    domain/
      model.py          # Message dataclass (id, channel, recipient, body, received_at)
    service_layer/
      services.py         # submit_message(channel, recipient, body, uow)
      unit_of_work.py       # InboxUnitOfWork(SqlAlchemyUnitOfWork), binds messages + outbox
    adapters/
      tables.py            # messages_table (plain Core sa.table(), not an ORM mapping) + outbox
      repository.py          # SqlAlchemyMessageRepository(AbstractRepository[Message])
    entrypoints/
      app.py                 # routes: POST /messages, GET /health; build_app()
  tests/
    unit/test_services.py     # service_layer against an in-memory fake UoW/repository
    integration/test_repository.py  # repository/UoW against a real Postgres, skipped by default
    e2e/test_api.py             # aiohttp test client, DB/rabbit faked at app[DB_KEY]/[RABBIT_KEY]
    performance/k6/script.js
```

- **inbox**: `POST /messages` validates `{channel, recipient, body}`,
  builds a domain `Message`, adds it via `InboxUnitOfWork.messages` and its
  wire-format shape via `InboxUnitOfWork.outbox`, and commits; returns `202`
  with the message id. The relay publishes it to `traffic-in`.
- **traffic**: on startup, spawns a background task subscribing to
  `traffic-in`; for each message not already routed, records a routing row
  and an outbox row for `dispatch-in` via `TrafficUnitOfWork`. A second task
  runs the outbox relay.
- **dispatcher**: on startup, spawns a background task subscribing to
  `dispatch-in`; for each message not already sent, looks up
  `SENDERS[channel]`, calls `.send()`, then records the outcome via
  `DispatcherUnitOfWork` with `send_status="sent"`.

`admin` is read-only (owns no schema, only queries the other three
modules') and skips `domain`/`service_layer`/Repository/UoW — Repository/UoW
model transactional writes to an aggregate, which doesn't apply to a pure
read view. It keeps `adapters/` (its own read-only table refs in
`read_model.py`, plus `metrics.py`'s query functions taking a plain
`AsyncConnection`) and `entrypoints/app.py`; `render.py`/`datastar.py` stay
at the package root as presentation helpers, not data access.

## Migrations

Each module owns an independent Alembic history under its own
`migrations/`, generated the normal way (`alembic init`, then
`alembic revision --autogenerate`) and customized only in `env.py`:

- The DSN comes from the module's own `config.toml` (via `-x config=<path>`,
  default `./config/config.toml`) — not from `alembic.ini` — so there is one
  place the DB connection is configured, not two.
- `target_metadata = sa.MetaData(schema="<module>")` plus one
  `sa.Table("messages", ...)` — hand-declared to match the app's own table,
  not reflected from a shared model layer (there isn't one; this is
  SQLAlchemy core).
- Online-mode migration running (the async engine dance) is delegated to
  `monobase.migrations.run_migrations_online` — the one piece of Alembic
  boilerplate that's genuinely identical across modules.

Verified end-to-end against a real Postgres for all three modules: each
module's `upgrade head` creates its schema + table + its own
`<schema>.alembic_version`, and `downgrade base` cleanly reverses it
(without dropping the schema itself, since Alembic's own version table
still needs to live there).

Containers run their own migration on startup (`alembic upgrade head`, see
each `Dockerfile`'s `CMD`) before starting the app — no separate init-SQL
step in `compose.yaml`.

## Tests

Every module (`stelo-base` included) has a `tests/` directory run with
`pytest` (`asyncio_mode = "auto"` — no `@pytest.mark.asyncio` needed). The
default `just <module>::test` never requires real infrastructure (Postgres,
RabbitMQ) — inbox/traffic/dispatcher split their tests into three tiers,
mirroring *Architecture Patterns with Python*'s layout:

- `unit/`: `service_layer` exercised directly against an in-memory fake
  `UnitOfWork`/repository — no DB, no aiohttp.
- `integration/`: the real `SqlAlchemyMessageRepository`/`UnitOfWork`
  against a live Postgres — the one tier that isn't free, so it's skipped
  unless `RUN_INTEGRATION_TESTS=1` (run it via `just <module>::test-integration`,
  after `just up`).
- `e2e/`: aiohttp test client (inbox) / consumer function called directly
  (traffic, dispatcher), with DB/RabbitMQ faked at the same seam the app
  code uses (`app[DB_KEY]`/`app[RABBIT_KEY]`, or by monkeypatching
  `consume` in the entrypoints module under test).

`stelo-base` and `admin` keep a flatter split (no `integration/` tier):

- `stelo-base`: unit tests per helper (`channels`, `config`, `security`,
  `streams`, `webapp`) — the shared library is the one place with real
  unit-testable logic in isolation. The moved persistence helpers are tested
  in `monobase`.
- `admin`: `unit/` covers `render.py`/`datastar.py`/`adapters/metrics.py`
  (pure functions and query builders against fake connections); `e2e/`
  drives its routes over an aiohttp test client.

## Performance testing

Each *service* module (not `stelo-base`, which has no runtime surface) has
a `tests/performance/k6/script.js`, run against a live instance
(`docker compose up`, or a module's own `just run`):

- **inbox**: the only module with a real endpoint worth load-testing —
  `POST /messages` across the three channels, with p95 latency and error
  rate thresholds.
- **traffic**/**dispatcher**: exercise `/health` only, since their real
  work (consuming a stream) isn't something k6 drives — documented in the
  script itself as a liveness/latency check, not a throughput test of what
  the service actually does.

## Justfiles

Every module has its own `justfile` (recipes grouped with `[group(...)]`
into `dev`/`test`/`db`/`quality`/`docker`): `install` (venv + `stelo-base`
+ itself, editable), `run`, `test`, `test-integration` (inbox/traffic/
dispatcher only — repository/UoW against a real Postgres, needs `just up`
first), `perf` (k6), `migrate`/`migration
<name>`/`downgrade`, `fmt`/`lint`, `docker-build`. The repo root `justfile`
pulls every module in as a `mod` (`just inbox::test`, `just
stelo_base::lint`, …) and adds repo-wide `up`/`down`/`logs` (Docker
Compose) and `fmt`/`lint`/`test`/`clean` that fan out across all four
modules.

## Packaging

- **hatchling**, not Poetry — plain PEP 621 `[project]` tables, no
  `[tool.poetry]` section. `src/` layout in every module
  (`src/stelo/<name>/`, an implicit PEP 420 namespace package — no
  `stelo/__init__.py` — so `stelo-base`, `inbox`, `traffic` and
  `dispatcher` all install side by side under one `stelo.*` namespace).
- No `requirements.txt` anywhere — `pyproject.toml` is the only dependency
  manifest. A service module declares `"stelo-base"` (unpinned: there's no
  index to version-match against, so any locally-installed copy satisfies
  it) and `"monobase"` (pinned by tag in the root `pyproject.toml`'s
  `[tool.uv.sources]`); everything else (aiohttp/SQLAlchemy/rbfly/uvloop in
  `stelo-base`, asyncpg/alembic in `monobase`) flows to every module
  transitively. Local dev and
  Docker builds both install `stelo-base` first, then the module itself,
  so pip is never asked to fetch `stelo-base` from an index that doesn't
  have it.
- No `setup.cfg` — that file only existed for old-setuptools
  pyproject-detection, which hatchling doesn't need.
- `[tool.pyright]` sets `venvPath`/`venv` per module so `pyright` resolves
  imports against that module's own `.venv` instead of erroring on every
  third-party import.

## Versioning / release

Each of the four packages (`stelo-base`, `inbox`, `traffic`, `dispatcher`)
keeps its own `pyproject.toml` with its own semantic version, its own
Dockerfile, its own migration history, and can be released independently.
Bumping `stelo-base` means bumping the version in its own `pyproject.toml`;
because the other modules depend on it unpinned, they pick up the change
the next time their environment is (re)installed — the same "bump and
re-resolve" motion a private package index would require later, just
without the index.

## Docker images

Two-stage build (`compile-image`/`build-image`) per module, all on
`python:3.13-alpine`:

- `compile-image` builds a venv with build tools (`gcc`/`build-base`,
  dropped from the final image), `pip install`s `stelo-base` then the
  module itself (`PIP_NO_CACHE_DIR=1`, `PIP_NO_COMPILE=1` — no pip cache,
  no bytecode baked into the image).
- `build-image` copies only the finished venv plus the module's own
  `bin/`, `config/`, `migrations/`, `alembic.ini` — never `tests/` or a
  sibling *service* directory. `platform/.dockerignore` keeps `tests/`,
  `.venv`, `__pycache__` and similar out of the build context entirely.
- No `tzdata`/`TZ` — logging is UTC (see `config.py`), so the timezone
  package that shipped in the original scaffold is dropped.
- Build context is `platform/` for every module (unified — the original
  scaffold had `inbox` and `traffic` using two different, inconsistent
  contexts), so each Dockerfile can `COPY stelo-base` in alongside its own
  module directory.

Not verified in this environment: this sandbox's network intercepts TLS to
Alpine's package CDN, so `docker build` itself couldn't be run start to
finish here. The pip-install sequence each Dockerfile uses (`pip install
./stelo-base && pip install ./inbox`, no `requirements.txt`) is the same
one verified directly against real venvs throughout development.

## Explicitly out of scope (scaffold cuts)

- No dead-letter handling, and no delivery guarantee beyond the outbox
  relay's at-least-once publish into each stream (retried with backoff) and
  what RabbitMQ Streams gives for free.
- No real SMS/email/WhatsApp provider integration — `channels.py` senders
  only log.
- No real auth/tenancy — `security.py` is a stub seam, not a security
  control.
- No smart routing/channel-selection logic in `traffic` — channel comes from
  the original request.
- No private package index for `stelo-base` — an unpinned local dependency,
  installed explicitly (path, then module) in that order everywhere.
