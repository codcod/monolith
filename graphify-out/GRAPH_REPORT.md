# Graph Report - monolith  (2026-09-28)

## Corpus Check
- 92 files · ~16,038 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 35 file(s) not represented in the graph (top: (none) 18, .typed 5, .toml 4)

## Summary
- 513 nodes · 727 edges · 57 communities (19 shown, 9 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 102 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85153772`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Message
- make_app
- Message
- Message
- events
- stelo-base shared library (design)
- Reusable Python module CI workflow
- test_channels.py
- FakeConnection
- get_dsn
- FakeConnection
- _make_client
- FakeConnection
- FakeUnitOfWork
- get_dsn
- get_dsn
- FakeUnitOfWork
- FakeUnitOfWork
- channels.py
- datastar.js
- stelo-base
- FakeClient
- inbox/tests/performance/k6/script.js
- dispatcher/tests/performance/k6/script.js
- traffic/tests/performance/k6/script.js
- rebuild-sandbox.sh
- stelo-platform
- Config

## God Nodes (most connected - your core abstractions)
1. `events()` - 16 edges
2. `make_app()` - 16 edges
3. `FakeConnection` - 13 edges
4. `FakeResult` - 12 edges
5. `Message` - 12 edges
6. `Message` - 12 edges
7. `Message` - 12 edges
8. `stelo-base shared library (design)` - 12 edges
9. `Config` - 11 edges
10. `DispatcherUnitOfWork` - 10 edges

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

## Communities (57 total, 9 thin omitted)

### Community 0 - "Message"
Cohesion: 0.07
Nodes (30): Message, The one shared shape that flows through the traffic-in / dispatch-in streams.…, AsyncConnection, Message, SqlAlchemyMessageRepository, Message, traffic's own routing record — its row in `traffic.messages`. Distinct from…, build_app() (+22 more)

### Community 1 - "make_app"
Cohesion: 0.06
Nodes (41): AbstractRouteDef, Handler, middleware, build_app(), Application, _config(), test_health_ok(), test_index_page_is_reachable_without_auth() (+33 more)

### Community 2 - "Message"
Cohesion: 0.08
Nodes (27): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, dispatcher's own send-outcome record — its row in `dispatcher.messages`.…, build_app(), health(), process_dispatch_in() (+19 more)

### Community 3 - "Message"
Cohesion: 0.08
Nodes (27): Channel, AsyncConnection, Message, SqlAlchemyMessageRepository, Message, inbox's own intake record — its row in `inbox.messages`. Distinct from…, create_message(), health() (+19 more)

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

### Community 10 - "FakeConnection"
Cohesion: 0.14
Nodes (6): FakeConnection, FakeEngine, FakeSender, FakeTransaction, test_health_ok(), test_process_dispatch_in_sends_and_records()

### Community 11 - "_make_client"
Cohesion: 0.16
Nodes (8): FakeConnection, FakeEngine, FakeTransaction, _make_client(), test_create_message_inserts_row_and_publishes(), test_create_message_requires_auth(), test_create_message_validates_payload(), test_health_ok()

### Community 12 - "FakeConnection"
Cohesion: 0.15
Nodes (5): FakeConnection, FakeEngine, FakeTransaction, test_health_ok(), test_process_traffic_in_inserts_and_republishes()

### Community 13 - "FakeUnitOfWork"
Cohesion: 0.27
Nodes (5): FakeUnitOfWork, _noop_publish(), AbstractUnitOfWork, test_route_message_adds_a_routing_row_and_commits(), test_route_message_republishes_with_status_routed()

### Community 16 - "FakeUnitOfWork"
Cohesion: 0.22
Nodes (8): FakeUnitOfWork, _noop_publish(), AbstractUnitOfWork, test_submit_message_adds_the_message_and_commits(), test_submit_message_publishes_only_after_commit(), commit(), test_submit_message_publishes_the_wire_shape_after_commit(), publish()

### Community 17 - "FakeUnitOfWork"
Cohesion: 0.25
Nodes (5): FakeSender, FakeUnitOfWork, AbstractUnitOfWork, test_dispatch_message_records_the_outcome_and_commits(), test_dispatch_message_sends_via_the_given_sender()

### Community 19 - "channels.py"
Cohesion: 0.22
Nodes (4): EmailSender, Sender, SmsSender, WhatsAppSender

### Community 21 - "datastar.js"
Cohesion: 0.38
Nodes (3): apply(), get(), has()

### Community 22 - "stelo-base"
Cohesion: 0.40
Nodes (5): stelo-admin, stelo-base, stelo-dispatcher, stelo-inbox, stelo-traffic

### Community 23 - "FakeClient"
Cohesion: 0.16
Nodes (6): FakeClient, FakePublisher, Self, Stands in for `rbfly.streams.StreamsClient` so the wrapper's create/…, test_consume_creates_stream_and_decodes_json(), test_publish_creates_stream_and_sends_json()

### Community 48 - "Config"
Cohesion: 0.21
Nodes (10): Run one HTTP worker on its own event loop, bound to a socket shared (via…, Fork `workers` worker processes (see `_serve_one`) and supervise them: forward…, _serve(), _serve_one(), build_app(), Application, Config, Setup Stelo application. 1. Setup logging. 2. Install uvloop based asyncio loop. (+2 more)

## Knowledge Gaps
- **22 isolated node(s):** `stelo-admin`, `stelo-dispatcher`, `options`, `stelo-inbox`, `options` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 219 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_app()` connect `make_app` to `Config`, `Message`, `Message`?**
  _High betweenness centrality (0.187) - this node is a cross-community bridge._
- **Why does `build_app()` connect `make_app` to `Config`, `events`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `Message` connect `Message` to `Message`, `Message`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `make_app()` (e.g. with `build_app()` and `build_app()`) actually correct?**
  _`make_app()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Message` (e.g. with `SqlAlchemyMessageRepository` and `_a_message()`) actually correct?**
  _`Message` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `stelo-admin`, `stelo-dispatcher`, `options` to the rest of the system?**
  _22 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Message` be split into smaller, more focused modules?**
  _Cohesion score 0.06767676767676768 - nodes in this community are weakly interconnected._