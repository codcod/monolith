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
```

- **inbox**: only module with a public HTTP API. Accepts a message request,
  validates it minimally, writes an intake row, publishes it to the
  `traffic-in` stream.
- **traffic**: background stream consumer. Reads from `traffic-in`, writes a
  routing row, republishes to `dispatch-in`. No real routing logic — for this
  scaffold the channel is whatever the caller specified in the payload.
- **dispatcher**: background stream consumer. Reads from `dispatch-in`,
  calls a stub `Sender` for the requested channel (logs "would send via
  X"), writes a final status row.

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
built by one shared helper:

```python
# stelo-base
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

```
platform/stelo-base/
  pyproject.toml       # hatchling, PEP 621 [project] table
  src/stelo/base/
    __init__.py
    config.py          # read_config/setup_logging/setup_app
    db.py               # make_engine()
    migrations.py       # shared async Alembic env.py runner
    streams.py          # thin wrapper over rbfly: publish(), consume()
    security.py         # aiohttp middleware: request-id + bearer-token stub
    webapp.py           # make_app()/run_in_background() + typed AppKeys
    channels.py         # Sender protocol + Sms/Email/WhatsApp stub senders
    messages.py         # shared Message TypedDict
  tests/                # unit tests for every module above
```

- **config.py**: `read_config`/`setup_logging`/`setup_app`, no longer
  copy-pasted per module. `setup_logging` logs in UTC and passes
  `force=True` to `logging.basicConfig` (without it, the call is a silent
  no-op whenever something — pytest included — already configured the root
  logger).
- **db.py**: single `make_engine(dsn)` — the "similar way to connect"
  requirement, without forcing identical schemas (schema comes from each
  module's own `Table(..., schema=...)`, not the DSN).
- **migrations.py**: `run_migrations_online(context, target_metadata, dsn)`
  — the async-engine boilerplate every module's Alembic `env.py` calls the
  same way. Creates the module's schema up front (Alembic's own version
  table needs it to exist before it can even check the current revision)
  and configures `version_table_schema=target_metadata.schema` so each
  module's migration history lives inside its own schema instead of every
  module fighting over one shared `public.alembic_version`.
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
- **channels.py**:
  ```python
  class Sender(Protocol):
      async def send(self, recipient: str, body: str) -> None: ...

  class SmsSender: ...      # logs "would send SMS to <recipient>: <body>"
  class EmailSender: ...    # logs "would send email to <recipient>: <body>"
  class WhatsAppSender: ... # logs "would send WhatsApp to <recipient>: <body>"

  SENDERS: dict[str, Sender] = {"sms": SmsSender(), "email": EmailSender(), "whatsapp": WhatsAppSender()}
  ```

## Per-module layout (inbox as example, traffic/dispatcher mirror it)

```
platform/inbox/
  pyproject.toml       # hatchling; dependencies = ["stelo-base"]
  Dockerfile           # builds only this dir + stelo-base, no requirements.txt
  justfile             # install/run/test/perf/migrate/fmt/lint/docker-build
  alembic.ini
  bin/stelo-inbox
  config/config.toml
  migrations/
    env.py             # calls stelo.base.migrations.run_migrations_online
    versions/0001_...  # CREATE SCHEMA + create_table("messages", schema=...)
  src/stelo/inbox/
    app.py             # routes: POST /messages, GET /health
  tests/
    test_app.py        # aiohttp test client, DB/rabbit faked
    performance/k6/script.js
```

- **inbox**: `POST /messages` validates `{channel, recipient, body}`,
  generates `id`/`created_at`, INSERTs into `inbox.messages`, publishes to
  `traffic-in`, returns `202` with the message id.
- **traffic**: on startup, spawns a background task subscribing to
  `traffic-in`; for each message, INSERTs into `traffic.messages`, publishes
  unchanged to `dispatch-in`.
- **dispatcher**: on startup, spawns a background task subscribing to
  `dispatch-in`; for each message, looks up `SENDERS[channel]`, calls
  `.send()`, INSERTs into `dispatcher.messages` with `send_status="sent"`.

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
  `stelo.base.migrations.run_migrations_online` — the one piece of Alembic
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
`pytest` (`asyncio_mode = "auto"` — no `@pytest.mark.asyncio` needed).
Real infrastructure (Postgres, RabbitMQ) is never required to run the
suite: DB/RabbitMQ access is faked at the same seam the app code uses
(`app[DB_KEY]`/`app[RABBIT_KEY]`, or by monkeypatching `publish`/`consume`
in the module under test), so tests stay fast and don't need `docker
compose up` first.

- `stelo-base`: unit tests per helper (`channels`, `config`, `db`,
  `security`, `streams`) — the shared library is the one place with real
  unit-testable logic in isolation.
- `inbox`: an aiohttp test client drives `/health` and `/messages`
  (auth rejection, payload validation, and the happy path — row inserted,
  message published — against fakes).
- `traffic`/`dispatcher`: `/health` over an aiohttp test client, plus their
  consumer function (`process_traffic_in`/`process_dispatch_in`) called
  directly against a fake `consume`/`publish`/DB engine.

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
+ itself, editable), `run`, `test`, `perf` (k6), `migrate`/`migration
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
  manifest. A service module's only declared dependency is
  `"stelo-base"` (unpinned: there's no index to version-match against, so
  any locally-installed copy satisfies it); everything else
  (aiohttp/SQLAlchemy/asyncpg/alembic/rbfly/uvloop) is declared once, in
  `stelo-base`, and flows to every module transitively. Local dev and
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

- No retries, dead-letter handling, or delivery guarantees beyond what
  RabbitMQ Streams gives for free.
- No real SMS/email/WhatsApp provider integration — `channels.py` senders
  only log.
- No real auth/tenancy — `security.py` is a stub seam, not a security
  control.
- No smart routing/channel-selection logic in `traffic` — channel comes from
  the original request.
- No private package index for `stelo-base` — an unpinned local dependency,
  installed explicitly (path, then module) in that order everywhere.
