# Graph Report - monolith  (2026-09-28)

## Corpus Check
- 94 files · ~17,554 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 35 file(s) not represented in the graph (top: (none) 18, .typed 5, .toml 4)

## Summary
- 559 nodes · 748 edges · 67 communities (23 shown, 16 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 86 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8c85e5a5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TrafficUnitOfWork
- make_app
- SqlAlchemyMessageRepository
- InboxUnitOfWork
- events
- stelo-base shared library (design)
- Reusable Python module CI workflow
- AsyncEngine
- FakeConnection
- Config
- dispatcher/tests/e2e/test_consumer.py
- request_id_middleware
- FakeConnection
- FakeUnitOfWork
- Message
- T
- FakeUnitOfWork
- FakeUnitOfWork
- Message
- channels.py
- build_app
- datastar.js
- stelo-base
- FakeClient
- inbox/tests/performance/k6/script.js
- dispatcher/tests/performance/k6/script.js
- traffic/tests/performance/k6/script.js
- rebuild-sandbox.sh
- MetaData
- stelo-platform
- PublishFn
- AsyncEngine
- AsyncEngine
- Self
- PublishFn
- Any
- _serve
- Self
- Connection

## God Nodes (most connected - your core abstractions)
1. `make_app()` - 16 edges
2. `events()` - 16 edges
3. `FakeConnection` - 13 edges
4. `FakeResult` - 12 edges
5. `stelo-base shared library (design)` - 12 edges
6. `publish()` - 10 edges
7. `InboxUnitOfWork` - 9 edges
8. `run_outbox_relay()` - 9 edges
9. `FakeClient` - 9 edges
10. `TrafficUnitOfWork` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Switch from black/isort/flake8/pylint/pyright to ruff+ty` --semantically_similar_to--> `Reusable Python module CI workflow`  [INFERRED] [semantically similar]
  CHANGELOG.md → .github/workflows/python_reusable.yml
- `src/-only type-check rationale` --semantically_similar_to--> `ty type-checking scoped to src/ only`  [INFERRED] [semantically similar]
  .github/workflows/python_reusable.yml → PACKAGING.md
- `admin module (Relay Console)` --references--> `admin module (design)`  [INFERRED]
  README.md → development/design.md
- `Alembic (per-module migrations)` --references--> `Independent per-module Alembic migration history (own schema, own alembic_version)`  [INFERRED]
  README.md → development/design.md
- `dispatcher module` --references--> `dispatcher module (design)`  [INFERRED]
  README.md → development/design.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Message pipeline: inbox → traffic → dispatcher, observed by admin** — development_design_inbox, development_design_traffic, development_design_dispatcher, development_design_admin [EXTRACTED 1.00]
- **Reusable Python CI workflow pattern shared by every module** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow, _github_workflows_python_reusable_workflow [EXTRACTED 1.00]
- **rbfly Cython build-essential workaround shared by all module CI workflows** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow [EXTRACTED 1.00]
- **Message pipeline: inbox → traffic → dispatcher, observed by admin** — readme_inbox, readme_traffic, readme_dispatcher, readme_admin [EXTRACTED 1.00]
- **Repository/UnitOfWork pattern implementation group** — development_design_stelo_base, development_design_repository_pattern, development_design_unit_of_work_pattern, development_design_sqlalchemy_core [INFERRED 0.85]

## Communities (67 total, 16 thin omitted)

### Community 0 - "TrafficUnitOfWork"
Cohesion: 0.10
Nodes (23): build_app(), health(), process_traffic_in(), Application, Config, get, Request, Response (+15 more)

### Community 1 - "make_app"
Cohesion: 0.07
Nodes (34): AbstractRouteDef, build_app(), Application, Config, `relay=False` leaves the outbox relay out: monobase runs one relay per outbox…, _close_quietly(), connect(), consume() (+26 more)

### Community 2 - "SqlAlchemyMessageRepository"
Cohesion: 0.07
Nodes (30): DispatcherUnitOfWork, AsyncConnection, Message, SqlAlchemyMessageRepository, Message, dispatcher's own send-outcome record — its row in `dispatcher.messages`.…, build_app(), health() (+22 more)

### Community 3 - "InboxUnitOfWork"
Cohesion: 0.11
Nodes (21): Channel, create_message(), health(), get, Request, Response, Message, Store the message and, in the same transaction, enqueue its wire shape for… (+13 more)

### Community 4 - "events"
Cohesion: 0.09
Nodes (33): channel_breakdown(), ChannelCounts, error_rate(), Event, latency_percentiles_ms(), oldest_unprocessed_age_seconds(), AsyncConnection, Age of the oldest inbox row with no matching traffic row yet — how long the… (+25 more)

### Community 5 - "stelo-base shared library (design)"
Cohesion: 0.11
Nodes (39): CHANGELOG.md, admin module (design), Independent per-module Alembic migration history (own schema, own alembic_version), config.py (read_config/setup_logging/setup_app), dispatcher module (design), Two-stage Docker build (compile-image/build-image), Design: inbox / traffic / dispatcher, hatchling over Poetry — plain PEP 621, no requirements.txt (+31 more)

### Community 6 - "Reusable Python module CI workflow"
Cohesion: 0.10
Nodes (32): rbfly transitive Cython build dependency note, CI platform/admin workflow, CI platform/dispatcher workflow, CI platform/inbox workflow, CI platform/stelo-base workflow, CI platform/traffic workflow, src/-only type-check rationale, --project/--package uv sync scoping rationale (+24 more)

### Community 8 - "FakeConnection"
Cohesion: 0.17
Nodes (12): FakeConnection, FakeResult, Stands in for `AsyncConnection`: `scalar()` and `execute()` each pop the next…, Stands in for a SQLAlchemy `Result` — only the bits metrics.py uses., test_channel_breakdown_maps_rows(), test_error_rate_defaults_to_zero_when_no_messages(), test_latency_percentiles_ms(), test_oldest_unprocessed_age_seconds() (+4 more)

### Community 9 - "Config"
Cohesion: 0.12
Nodes (16): get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, Config, A module's own section of its `config.toml` (e.g. `config["traffic"]` after…, Read configuration file and return configuration object, keyed by module name…, Setup logging for an application. (+8 more)

### Community 10 - "dispatcher/tests/e2e/test_consumer.py"
Cohesion: 0.13
Nodes (6): FakeConnection, FakeEngine, FakeResult, FakeSender, FakeTransaction, test_process_dispatch_in_sends_and_records()

### Community 11 - "request_id_middleware"
Cohesion: 0.08
Nodes (20): Handler, middleware, FakeConnection, FakeEngine, FakeTransaction, _make_client(), test_create_message_inserts_row_and_outbox_row(), test_create_message_requires_auth() (+12 more)

### Community 12 - "FakeConnection"
Cohesion: 0.15
Nodes (5): FakeConnection, FakeEngine, FakeResult, FakeTransaction, test_process_traffic_in_records_and_enqueues()

### Community 13 - "FakeUnitOfWork"
Cohesion: 0.15
Nodes (9): FakeMessageRepository, FakeOutbox, FakeUnitOfWork, AbstractUnitOfWork, Message, test_route_message_adds_a_routing_row_and_commits(), test_route_message_enqueues_it_for_dispatch_before_commit(), commit() (+1 more)

### Community 14 - "Message"
Cohesion: 0.27
Nodes (5): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, inbox's own intake record — its row in `inbox.messages`. Distinct from…

### Community 16 - "FakeUnitOfWork"
Cohesion: 0.15
Nodes (8): FakeMessageRepository, FakeOutbox, FakeUnitOfWork, AbstractUnitOfWork, Message, test_submit_message_adds_the_message_and_commits(), test_submit_message_enqueues_the_wire_shape_before_commit(), commit()

### Community 17 - "FakeUnitOfWork"
Cohesion: 0.18
Nodes (8): FakeMessageRepository, FakeSender, FakeUnitOfWork, AbstractUnitOfWork, Message, test_dispatch_message_records_the_outcome_and_commits(), test_dispatch_message_sends_via_the_given_sender(), test_dispatch_message_skips_a_duplicate_id()

### Community 18 - "Message"
Cohesion: 0.27
Nodes (5): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, traffic's own routing record — its row in `traffic.messages`. Distinct from…

### Community 19 - "channels.py"
Cohesion: 0.22
Nodes (4): EmailSender, Sender, SmsSender, WhatsAppSender

### Community 20 - "build_app"
Cohesion: 0.50
Nodes (7): build_app(), Application, _config(), test_health_ok(), test_index_page_is_reachable_without_auth(), test_static_datastar_bundle_is_reachable_without_auth(), TestClient

### Community 21 - "datastar.js"
Cohesion: 0.38
Nodes (3): apply(), get(), has()

### Community 22 - "stelo-base"
Cohesion: 0.40
Nodes (5): stelo-admin, stelo-base, stelo-dispatcher, stelo-inbox, stelo-traffic

### Community 23 - "FakeClient"
Cohesion: 0.11
Nodes (10): BaseException, parametrize, test_sender_logs_the_send(), FakeClient, FakePublisher, Self, Stands in for `rbfly.streams.StreamsClient` so the wrapper's create/…, test_consume_creates_stream_and_decodes_json() (+2 more)

### Community 48 - "_serve"
Cohesion: 0.38
Nodes (5): Config, Run one HTTP worker on its own event loop, bound to a socket shared (via…, Fork `workers` worker processes (see `_serve_one`) and supervise them: forward…, _serve(), _serve_one()

## Knowledge Gaps
- **22 isolated node(s):** `stelo-admin`, `stelo-dispatcher`, `stelo-inbox`, `stelo-traffic`, `CHANNELS` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 242 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_app()` connect `make_app` to `TrafficUnitOfWork`, `SqlAlchemyMessageRepository`, `request_id_middleware`, `build_app`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `build_app()` connect `build_app` to `Config`, `events`, `make_app`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `build_app()` connect `make_app` to `_serve`, `InboxUnitOfWork`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `make_app()` (e.g. with `build_app()` and `build_app()`) actually correct?**
  _`make_app()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `stelo-admin`, `stelo-dispatcher`, `stelo-inbox` to the rest of the system?**
  _22 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TrafficUnitOfWork` be split into smaller, more focused modules?**
  _Cohesion score 0.09852216748768473 - nodes in this community are weakly interconnected._
- **Should `make_app` be split into smaller, more focused modules?**
  _Cohesion score 0.06829268292682927 - nodes in this community are weakly interconnected._