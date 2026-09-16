# Graph Report - monolith  (2026-09-16)

## Corpus Check
- 61 files · ~16,326 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 606 nodes · 798 edges · 83 communities (23 shown, 32 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 90 edges (avg confidence: 0.9)
- Token cost: 69,998 input · 0 output

## Community Hubs (Navigation)
- Traffic module (repo/UoW/service)
- stelo-base web & security
- Dispatcher module (repo/UoW/service)
- Inbox module (repo/UoW/service)
- Admin metrics & rendering
- Docs: architecture & rationale
- CI/CD & Compose infra
- Unit of Work pattern
- Admin metrics tests
- Config & DB migration env
- Dispatcher e2e tests
- Inbox e2e tests
- Traffic e2e tests
- stelo-base DB & Alembic
- stelo-base streams tests
- Repository pattern
- Inbox service unit tests
- Dispatcher service unit tests
- Inbox entrypoint & bin script
- Channel senders (SMS/Email/WhatsApp)
- Admin e2e tests
- Admin Datastar proxy adapter
- stelo package registry
- stelo-base channel tests
- Admin Datastar SSE module
- Inbox k6 performance script
- Message TypedDict (wire format)
- Dispatcher k6 performance script
- Traffic k6 performance script
- Sandbox rebuild script
- AsyncConnection type reference
- stelo-platform workspace package
- Admin app.py (legacy) application
- Admin app.py (legacy) config
- Admin app.py (legacy) get
- Admin app.py (legacy) request
- Admin app.py (legacy) response
- Dispatcher app.py (legacy) application
- Dispatcher app.py (legacy) config
- Dispatcher app.py (legacy) get
- Dispatcher app.py (legacy) request
- Dispatcher app.py (legacy) response
- Dispatcher test_app self ref
- Inbox app.py (legacy) application
- Inbox app.py (legacy) config
- Inbox app.py (legacy) get
- Inbox app.py (legacy) request
- Inbox app.py (legacy) response
- Inbox test_app self ref
- Traffic app.py (legacy) application
- Traffic app.py (legacy) config
- Traffic app.py (legacy) get
- Traffic app.py (legacy) request
- Traffic app.py (legacy) response
- Traffic test_app self ref

## God Nodes (most connected - your core abstractions)
1. `SqlAlchemyUnitOfWork` - 15 edges
2. `events()` - 14 edges
3. `make_app()` - 13 edges
4. `FakeConnection` - 13 edges
5. `FakeResult` - 12 edges
6. `Message` - 12 edges
7. `Message` - 12 edges
8. `Message` - 12 edges
9. `stelo-base shared library (design)` - 12 edges
10. `AbstractUnitOfWork` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Switch from black/isort/flake8/pylint/pyright to ruff+ty` --semantically_similar_to--> `Reusable Python module CI workflow`  [INFERRED] [semantically similar]
  CHANGELOG.md → .github/workflows/python_reusable.yml
- `src/-only type-check rationale` --semantically_similar_to--> `ty type-checking scoped to src/ only`  [INFERRED] [semantically similar]
  .github/workflows/python_reusable.yml → PACKAGING.md
- `CI platform/admin workflow` --references--> `admin service (compose)`  [EXTRACTED]
  .github/workflows/ci_admin.yml → compose.yaml
- `admin service (compose)` --references--> `Relay Console admin dashboard`  [INFERRED]
  compose.yaml → platform/admin/static/index.html
- `inbox module` --references--> `inbox module (design)`  [INFERRED]
  README.md → development/design.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reusable Python CI workflow pattern shared by every module** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow, _github_workflows_python_reusable_workflow [EXTRACTED 1.00]
- **rbfly Cython build-essential workaround shared by all module CI workflows** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow [EXTRACTED 1.00]
- **Message pipeline: inbox → traffic → dispatcher, observed by admin** — readme_inbox, readme_traffic, readme_dispatcher, readme_admin [EXTRACTED 1.00]
- **Message pipeline: inbox → traffic → dispatcher, observed by admin** — development_design_inbox, development_design_traffic, development_design_dispatcher, development_design_admin [EXTRACTED 1.00]
- **Repository/UnitOfWork pattern implementation group** — development_design_stelo_base, development_design_repository_pattern, development_design_unit_of_work_pattern, development_design_sqlalchemy_core [INFERRED 0.85]

## Communities (83 total, 32 thin omitted)

### Community 0 - "Traffic module (repo/UoW/service)"
Cohesion: 0.06
Nodes (32): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, traffic's own routing record — its row in `traffic.messages`. Distinct from…, build_app(), health(), process_traffic_in() (+24 more)

### Community 1 - "stelo-base web & security"
Cohesion: 0.06
Nodes (34): AbstractRouteDef, middleware, auth_middleware(), Request, Stamp every request with an id (reusing an inbound one if present) so it can be…, Build a bearer-token check middleware. `token` comes from module config. This…, request_id_middleware(), connect() (+26 more)

### Community 2 - "Dispatcher module (repo/UoW/service)"
Cohesion: 0.07
Nodes (29): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, dispatcher's own send-outcome record — its row in `dispatcher.messages`.…, build_app(), health(), process_dispatch_in() (+21 more)

### Community 3 - "Inbox module (repo/UoW/service)"
Cohesion: 0.08
Nodes (26): Channel, AsyncConnection, Message, SqlAlchemyMessageRepository, Message, inbox's own intake record — its row in `inbox.messages`. Distinct from…, create_message(), health() (+18 more)

### Community 4 - "Admin metrics & rendering"
Cohesion: 0.08
Nodes (27): FileResponse, channel_breakdown(), ChannelCounts, error_rate(), Event, latency_percentiles_ms(), oldest_unprocessed_age_seconds(), AsyncConnection (+19 more)

### Community 5 - "Docs: architecture & rationale"
Cohesion: 0.11
Nodes (39): CHANGELOG.md, admin module (design), Independent per-module Alembic migration history (own schema, own alembic_version), config.py (read_config/setup_logging/setup_app), dispatcher module (design), Two-stage Docker build (compile-image/build-image), Design: inbox / traffic / dispatcher, hatchling over Poetry — plain PEP 621, no requirements.txt (+31 more)

### Community 6 - "CI/CD & Compose infra"
Cohesion: 0.09
Nodes (35): rbfly transitive Cython build dependency note, CI platform/admin workflow, CI platform/dispatcher workflow, CI platform/inbox workflow, CI platform/stelo-base workflow, CI platform/traffic workflow, src/-only type-check rationale, --project/--package uv sync scoping rationale (+27 more)

### Community 7 - "Unit of Work pattern"
Cohesion: 0.09
Nodes (14): AbstractUnitOfWork, AsyncEngine, Self, Owns one `AsyncConnection` + transaction for the lifetime of the `async with`…, One business transaction: `async with uow: ...; await uow.commit()`. Exiting…, SqlAlchemyUnitOfWork, FakeConnection, FakeEngine (+6 more)

### Community 8 - "Admin metrics tests"
Cohesion: 0.17
Nodes (12): FakeConnection, FakeResult, Stands in for `AsyncConnection`: `scalar()` and `execute()` each pop the next…, Stands in for a SQLAlchemy `Result` — only the bits metrics.py uses., test_channel_breakdown_maps_rows(), test_error_rate_defaults_to_zero_when_no_messages(), test_latency_percentiles_ms(), test_oldest_unprocessed_age_seconds() (+4 more)

### Community 9 - "Config & DB migration env"
Cohesion: 0.12
Nodes (15): get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, Config, Read configuration file and return configuration object., Setup logging for an application., Setup Stelo application. 1. Setup logging. 2. Install uvloop based asyncio loop. (+7 more)

### Community 10 - "Dispatcher e2e tests"
Cohesion: 0.14
Nodes (5): FakeConnection, FakeEngine, FakeSender, FakeTransaction, test_process_dispatch_in_sends_and_records()

### Community 11 - "Inbox e2e tests"
Cohesion: 0.16
Nodes (8): FakeConnection, FakeEngine, FakeTransaction, _make_client(), test_create_message_inserts_row_and_publishes(), test_create_message_requires_auth(), test_create_message_validates_payload(), test_health_ok()

### Community 12 - "Traffic e2e tests"
Cohesion: 0.15
Nodes (4): FakeConnection, FakeEngine, FakeTransaction, test_process_traffic_in_inserts_and_republishes()

### Community 13 - "stelo-base DB & Alembic"
Cohesion: 0.21
Nodes (12): Connection, MetaData, make_engine(), AsyncEngine, Build an async SQLAlchemy core engine for a module's database. All modules…, _do_run_migrations(), Any, AsyncEngine (+4 more)

### Community 14 - "stelo-base streams tests"
Cohesion: 0.16
Nodes (6): FakeClient, FakePublisher, Self, Stands in for `rbfly.streams.StreamsClient` so the wrapper's create/…, test_consume_creates_stream_and_decodes_json(), test_publish_creates_stream_and_sends_json()

### Community 15 - "Repository pattern"
Cohesion: 0.19
Nodes (7): AbstractRepository, A collection-like façade over one aggregate's storage. Concrete repositories…, InMemoryRepository, test_abstract_repository_cannot_be_instantiated(), test_add_then_get_returns_the_same_item(), test_get_missing_id_returns_none(), T

### Community 16 - "Inbox service unit tests"
Cohesion: 0.24
Nodes (7): FakeUnitOfWork, _noop_publish(), test_submit_message_adds_the_message_and_commits(), test_submit_message_publishes_only_after_commit(), commit(), test_submit_message_publishes_the_wire_shape_after_commit(), publish()

### Community 17 - "Dispatcher service unit tests"
Cohesion: 0.29
Nodes (4): FakeSender, FakeUnitOfWork, test_dispatch_message_records_the_outcome_and_commits(), test_dispatch_message_sends_via_the_given_sender()

### Community 18 - "Inbox entrypoint & bin script"
Cohesion: 0.24
Nodes (8): Config, Run one HTTP worker on its own event loop, bound to a socket shared (via…, Fork `workers` worker processes (see `_serve_one`) and supervise them: forward…, _serve(), _serve_one(), build_app(), Application, Config

### Community 19 - "Channel senders (SMS/Email/WhatsApp)"
Cohesion: 0.22
Nodes (4): EmailSender, Sender, SmsSender, WhatsAppSender

### Community 20 - "Admin e2e tests"
Cohesion: 0.43
Nodes (7): build_app(), Application, Config, _config(), test_health_ok(), test_index_page_is_reachable_without_auth(), test_static_datastar_bundle_is_reachable_without_auth()

### Community 21 - "Admin Datastar proxy adapter"
Cohesion: 0.38
Nodes (3): apply(), get(), has()

### Community 22 - "stelo package registry"
Cohesion: 0.40
Nodes (5): stelo-admin, stelo-base, stelo-dispatcher, stelo-inbox, stelo-traffic

## Knowledge Gaps
- **23 isolated node(s):** `stelo-admin`, `stelo-dispatcher`, `stelo-inbox`, `stelo-traffic`, `CHANNELS` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 273 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SqlAlchemyUnitOfWork` connect `Unit of Work pattern` to `Traffic module (repo/UoW/service)`, `Dispatcher module (repo/UoW/service)`, `Inbox module (repo/UoW/service)`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `InboxUnitOfWork` connect `Inbox module (repo/UoW/service)` to `Unit of Work pattern`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `AbstractUnitOfWork` connect `Unit of Work pattern` to `Inbox service unit tests`, `Dispatcher service unit tests`, `Traffic module (repo/UoW/service)`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `SqlAlchemyUnitOfWork` (e.g. with `test_commit_marks_transaction_committed_and_closes_connection()` and `test_exception_in_block_rolls_back_and_still_closes()`) actually correct?**
  _`SqlAlchemyUnitOfWork` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `make_app()` (e.g. with `request_id_middleware()` and `db_ctx()`) actually correct?**
  _`make_app()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `stelo-admin`, `stelo-dispatcher`, `stelo-inbox` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Traffic module (repo/UoW/service)` be split into smaller, more focused modules?**
  _Cohesion score 0.058823529411764705 - nodes in this community are weakly interconnected._