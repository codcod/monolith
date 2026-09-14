# Graph Report - monolith  (2026-09-14)

## Corpus Check
- Corpus is ~12,767 words - fits in a single context window. You may not need a graph.

## Summary
- 358 nodes · 519 edges · 28 communities (17 shown, 6 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 67 edges (avg confidence: 0.86)
- Token cost: 107,924 input · 0 output

## Community Hubs (Navigation)
- Auth Middleware & Request Security
- Admin App Routes
- CI Workflow & Build Rationale
- Admin Metrics Tests
- Inbox Worker Process Management
- Database DSN Config
- Dispatcher App Tests
- Full-Stack CI & Compose Deployment
- Admin App Bootstrap & Tests
- Async DB Test Fakes
- Traffic App Tests
- Database Engine & Migrations
- RabbitMQ Streams Test Fakes
- Dispatcher App Routes
- Notification Channel Senders
- Datastar Reactive JS Library
- Stelo Service Package Graph
- Channel Sender Tests
- Admin Frontend Channel Config
- Frontend Script Options A
- Frontend Script Options B
- Sandbox Rebuild Script
- Stelo Platform Root

## God Nodes (most connected - your core abstractions)
1. `make_app()` - 17 edges
2. `events()` - 16 edges
3. `FakeConnection` - 13 edges
4. `stelo-base shared library` - 13 edges
5. `FakeResult` - 12 edges
6. `traffic service (design)` - 12 edges
7. `_make_client()` - 10 edges
8. `dispatcher service (design)` - 10 edges
9. `_make_client()` - 9 edges
10. `CHANGELOG.md Unreleased section` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Switch from black/isort/flake8/pylint/pyright to ruff+ty` --semantically_similar_to--> `Reusable Python module CI workflow`  [INFERRED] [semantically similar]
  CHANGELOG.md → .github/workflows/python_reusable.yml
- `src/-only type-check rationale` --semantically_similar_to--> `ty type-checking scoped to src/ only`  [INFERRED] [semantically similar]
  .github/workflows/python_reusable.yml → PACKAGING.md
- `traffic Dockerfile COPY ../inbox path-not-found error log` --semantically_similar_to--> `Repo-root Docker build context rationale`  [INFERRED] [semantically similar]
  README.md → PACKAGING.md
- `traffic Dockerfile COPY ../inbox path-not-found error log` --semantically_similar_to--> `Unified platform/ Docker build context`  [INFERRED] [semantically similar]
  README.md → development/design.md
- `admin service (compose)` --references--> `Relay Console admin dashboard`  [INFERRED]
  compose.yaml → platform/admin/static/index.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reusable Python CI workflow pattern shared by every module** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow, _github_workflows_python_reusable_workflow [EXTRACTED 1.00]
- **Inbox -> Traffic -> Dispatcher message pipeline over RabbitMQ Streams** — development_design_stelo_inbox_service, development_design_stelo_traffic_service, development_design_stelo_dispatcher_service, development_design_traffic_in_stream, development_design_dispatch_in_stream [EXTRACTED 1.00]
- **rbfly Cython build-essential workaround shared by all module CI workflows** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow [EXTRACTED 1.00]

## Communities (28 total, 6 thin omitted)

### Community 0 - "Auth Middleware & Request Security"
Cohesion: 0.06
Nodes (36): AbstractRouteDef, middleware, auth_middleware(), Request, Stamp every request with an id (reusing an inbound one if present) so it can be…, Build a bearer-token check middleware. `token` comes from module config. This…, request_id_middleware(), connect() (+28 more)

### Community 1 - "Admin App Routes"
Cohesion: 0.09
Nodes (33): AsyncConnection, FileResponse, events(), health(), index(), get, Request, Response (+25 more)

### Community 2 - "CI Workflow & Build Rationale"
Cohesion: 0.12
Nodes (35): rbfly transitive Cython build dependency note, CI platform/dispatcher workflow, CI platform/inbox workflow, CI platform/stelo-base workflow, CI platform/traffic workflow, src/-only type-check rationale, --project/--package uv sync scoping rationale, Reusable Python module CI workflow (+27 more)

### Community 3 - "Admin Metrics Tests"
Cohesion: 0.11
Nodes (12): FakeConnection, FakeResult, Stands in for `AsyncConnection`: `scalar()` and `execute()` each pop the next…, Stands in for a SQLAlchemy `Result` — only the bits metrics.py uses., test_channel_breakdown_maps_rows(), test_error_rate_defaults_to_zero_when_no_messages(), test_latency_percentiles_ms(), test_oldest_unprocessed_age_seconds() (+4 more)

### Community 4 - "Inbox Worker Process Management"
Cohesion: 0.12
Nodes (16): Config, Run one HTTP worker on its own event loop, bound to a socket shared (via…, Fork `workers` worker processes (see `_serve_one`) and supervise them: forward…, _serve(), _serve_one(), build_app(), create_message(), health() (+8 more)

### Community 5 - "Database DSN Config"
Cohesion: 0.12
Nodes (15): get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, Config, Read configuration file and return configuration object., Setup logging for an application., Setup Stelo application. 1. Setup logging. 2. Install uvloop based asyncio loop. (+7 more)

### Community 6 - "Dispatcher App Tests"
Cohesion: 0.15
Nodes (6): FakeConnection, FakeEngine, FakeSender, Self, test_health_ok(), test_process_dispatch_in_sends_and_records()

### Community 7 - "Full-Stack CI & Compose Deployment"
Cohesion: 0.23
Nodes (16): CI platform/admin workflow, actionlint workflow-lint job, Full-stack compose smoke-test job (integration), Top-level CI workflow, Alpine+pip to distroless image, one-shot migrations, admin service (compose), dispatcher-migrate one-shot job (compose), dispatcher service (compose) (+8 more)

### Community 8 - "Admin App Bootstrap & Tests"
Cohesion: 0.19
Nodes (14): build_app(), Application, Config, _config(), test_health_ok(), test_index_page_is_reachable_without_auth(), test_static_datastar_bundle_is_reachable_without_auth(), get (+6 more)

### Community 9 - "Async DB Test Fakes"
Cohesion: 0.18
Nodes (8): FakeConnection, FakeEngine, _make_client(), Self, test_create_message_inserts_row_and_publishes(), test_create_message_requires_auth(), test_create_message_validates_payload(), test_health_ok()

### Community 10 - "Traffic App Tests"
Cohesion: 0.15
Nodes (5): FakeConnection, FakeEngine, Self, test_health_ok(), test_process_traffic_in_inserts_and_republishes()

### Community 11 - "Database Engine & Migrations"
Cohesion: 0.21
Nodes (12): Connection, MetaData, make_engine(), AsyncEngine, Build an async SQLAlchemy core engine for a module's database. All modules…, _do_run_migrations(), Any, AsyncEngine (+4 more)

### Community 12 - "RabbitMQ Streams Test Fakes"
Cohesion: 0.16
Nodes (6): FakeClient, FakePublisher, Self, Stands in for `rbfly.streams.StreamsClient` so the wrapper's create/…, test_consume_creates_stream_and_decodes_json(), test_publish_creates_stream_and_sends_json()

### Community 13 - "Dispatcher App Routes"
Cohesion: 0.24
Nodes (9): build_app(), health(), process_dispatch_in(), Application, Config, get, Request, Response (+1 more)

### Community 14 - "Notification Channel Senders"
Cohesion: 0.22
Nodes (4): EmailSender, Sender, SmsSender, WhatsAppSender

### Community 15 - "Datastar Reactive JS Library"
Cohesion: 0.38
Nodes (3): apply(), get(), has()

### Community 16 - "Stelo Service Package Graph"
Cohesion: 0.40
Nodes (5): stelo-admin, stelo-base, stelo-dispatcher, stelo-inbox, stelo-traffic

## Knowledge Gaps
- **14 isolated node(s):** `stelo-admin`, `stelo-dispatcher`, `options`, `stelo-inbox`, `options` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 146 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_app()` connect `Auth Middleware & Request Security` to `Admin App Bootstrap & Tests`, `Database Engine & Migrations`, `Inbox Worker Process Management`, `Dispatcher App Routes`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `build_app()` connect `Admin App Bootstrap & Tests` to `Auth Middleware & Request Security`, `Admin App Routes`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `_make_client()` connect `Async DB Test Fakes` to `Auth Middleware & Request Security`, `Admin App Bootstrap & Tests`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `make_app()` (e.g. with `build_app()` and `build_app()`) actually correct?**
  _`make_app()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `stelo-admin`, `stelo-dispatcher`, `options` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth Middleware & Request Security` be split into smaller, more focused modules?**
  _Cohesion score 0.06183574879227053 - nodes in this community are weakly interconnected._
- **Should `Admin App Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.08780487804878048 - nodes in this community are weakly interconnected._