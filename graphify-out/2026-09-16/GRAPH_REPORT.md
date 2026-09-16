# Graph Report - monolith  (2026-09-16)

## Corpus Check
- 99 files · ~16,909 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 35 file(s) not represented in the graph (top: (none) 18, .typed 5, .toml 4)

## Summary
- 617 nodes · 816 edges · 94 communities (22 shown, 44 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `08957f3e`
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
- SqlAlchemyUnitOfWork
- FakeConnection
- Config
- FakeConnection
- _make_client
- FakeConnection
- make_engine
- FakeClient
- InMemoryRepository
- FakeUnitOfWork
- FakeUnitOfWork
- Config
- channels.py
- Config
- datastar.js
- stelo-base
- test_channels.py
- _serve
- inbox/tests/performance/k6/script.js
- Message
- dispatcher/tests/performance/k6/script.js
- traffic/tests/performance/k6/script.js
- rebuild-sandbox.sh
- AsyncConnection
- stelo-platform
- Application
- Config
- get
- Request
- Response
- Application
- Config
- get
- Request
- Response
- Self
- Application
- Config
- get
- Request
- Response
- Self
- Application
- Config
- get
- Request
- Response
- Self
- FileResponse
- Config
- Config
- Any
- Config
- Config
- Application
- get
- Request
- Response
- StreamResponse

## God Nodes (most connected - your core abstractions)
1. `make_app()` - 17 edges
2. `events()` - 16 edges
3. `SqlAlchemyUnitOfWork` - 15 edges
4. `FakeConnection` - 13 edges
5. `Message` - 12 edges
6. `Message` - 12 edges
7. `Message` - 12 edges
8. `FakeResult` - 12 edges
9. `stelo-base shared library (design)` - 12 edges
10. `AbstractUnitOfWork` - 11 edges

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

## Communities (94 total, 44 thin omitted)

### Community 0 - "Message"
Cohesion: 0.06
Nodes (32): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, traffic's own routing record — its row in `traffic.messages`. Distinct from…, build_app(), health(), process_traffic_in() (+24 more)

### Community 1 - "make_app"
Cohesion: 0.06
Nodes (42): AbstractRouteDef, Application, Config, Handler, middleware, build_app(), _config(), test_health_ok() (+34 more)

### Community 2 - "Message"
Cohesion: 0.08
Nodes (28): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, dispatcher's own send-outcome record — its row in `dispatcher.messages`.…, build_app(), health(), process_dispatch_in() (+20 more)

### Community 3 - "Message"
Cohesion: 0.07
Nodes (28): Channel, AsyncConnection, Message, SqlAlchemyMessageRepository, Message, inbox's own intake record — its row in `inbox.messages`. Distinct from…, build_app(), create_message() (+20 more)

### Community 4 - "events"
Cohesion: 0.07
Nodes (32): ChannelCounts, Event, get, channel_breakdown(), ChannelCounts, error_rate(), Event, latency_percentiles_ms() (+24 more)

### Community 5 - "stelo-base shared library (design)"
Cohesion: 0.11
Nodes (39): CHANGELOG.md, admin module (design), Independent per-module Alembic migration history (own schema, own alembic_version), config.py (read_config/setup_logging/setup_app), dispatcher module (design), Two-stage Docker build (compile-image/build-image), Design: inbox / traffic / dispatcher, hatchling over Poetry — plain PEP 621, no requirements.txt (+31 more)

### Community 6 - "Reusable Python module CI workflow"
Cohesion: 0.09
Nodes (32): rbfly transitive Cython build dependency note, CI platform/admin workflow, CI platform/dispatcher workflow, CI platform/inbox workflow, CI platform/stelo-base workflow, CI platform/traffic workflow, src/-only type-check rationale, --project/--package uv sync scoping rationale (+24 more)

### Community 7 - "SqlAlchemyUnitOfWork"
Cohesion: 0.09
Nodes (14): AbstractUnitOfWork, AsyncEngine, Self, Owns one `AsyncConnection` + transaction for the lifetime of the `async with`…, One business transaction: `async with uow: ...; await uow.commit()`. Exiting…, SqlAlchemyUnitOfWork, FakeConnection, FakeEngine (+6 more)

### Community 8 - "FakeConnection"
Cohesion: 0.17
Nodes (12): FakeConnection, FakeResult, Stands in for `AsyncConnection`: `scalar()` and `execute()` each pop the next…, Stands in for a SQLAlchemy `Result` — only the bits metrics.py uses., test_channel_breakdown_maps_rows(), test_error_rate_defaults_to_zero_when_no_messages(), test_latency_percentiles_ms(), test_oldest_unprocessed_age_seconds() (+4 more)

### Community 9 - "Config"
Cohesion: 0.12
Nodes (16): get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, Config, A module's own section of its `config.toml` (e.g. `config["traffic"]` after…, Read configuration file and return configuration object, keyed by module name…, Setup logging for an application. (+8 more)

### Community 10 - "FakeConnection"
Cohesion: 0.14
Nodes (6): FakeConnection, FakeEngine, FakeSender, FakeTransaction, test_health_ok(), test_process_dispatch_in_sends_and_records()

### Community 11 - "_make_client"
Cohesion: 0.16
Nodes (8): FakeConnection, FakeEngine, FakeTransaction, _make_client(), test_create_message_inserts_row_and_publishes(), test_create_message_requires_auth(), test_create_message_validates_payload(), test_health_ok()

### Community 12 - "FakeConnection"
Cohesion: 0.15
Nodes (5): FakeConnection, FakeEngine, FakeTransaction, test_health_ok(), test_process_traffic_in_inserts_and_republishes()

### Community 13 - "make_engine"
Cohesion: 0.20
Nodes (11): Connection, MetaData, make_engine(), AsyncEngine, Build an async SQLAlchemy core engine for a module's database. All modules…, _do_run_migrations(), AsyncEngine, Standard Alembic `env.py` online-mode entry point for an async SQLAlchemy… (+3 more)

### Community 14 - "FakeClient"
Cohesion: 0.16
Nodes (6): FakeClient, FakePublisher, Self, Stands in for `rbfly.streams.StreamsClient` so the wrapper's create/…, test_consume_creates_stream_and_decodes_json(), test_publish_creates_stream_and_sends_json()

### Community 15 - "InMemoryRepository"
Cohesion: 0.18
Nodes (7): AbstractRepository, A collection-like façade over one aggregate's storage. Concrete repositories…, InMemoryRepository, test_abstract_repository_cannot_be_instantiated(), test_add_then_get_returns_the_same_item(), test_get_missing_id_returns_none(), T

### Community 16 - "FakeUnitOfWork"
Cohesion: 0.27
Nodes (7): FakeUnitOfWork, _noop_publish(), test_submit_message_adds_the_message_and_commits(), test_submit_message_publishes_only_after_commit(), commit(), test_submit_message_publishes_the_wire_shape_after_commit(), publish()

### Community 17 - "FakeUnitOfWork"
Cohesion: 0.29
Nodes (4): FakeSender, FakeUnitOfWork, test_dispatch_message_records_the_outcome_and_commits(), test_dispatch_message_sends_via_the_given_sender()

### Community 19 - "channels.py"
Cohesion: 0.22
Nodes (4): EmailSender, Sender, SmsSender, WhatsAppSender

### Community 21 - "datastar.js"
Cohesion: 0.38
Nodes (3): apply(), get(), has()

### Community 22 - "stelo-base"
Cohesion: 0.40
Nodes (5): stelo-admin, stelo-base, stelo-dispatcher, stelo-inbox, stelo-traffic

### Community 24 - "_serve"
Cohesion: 0.38
Nodes (5): Config, Run one HTTP worker on its own event loop, bound to a socket shared (via…, Fork `workers` worker processes (see `_serve_one`) and supervise them: forward…, _serve(), _serve_one()

## Knowledge Gaps
- **23 isolated node(s):** `stelo-admin`, `stelo-dispatcher`, `stelo-inbox`, `stelo-traffic`, `CHANNELS` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 281 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_app()` connect `make_app` to `Message`, `Message`, `Message`, `Config`, `make_engine`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Why does `SqlAlchemyUnitOfWork` connect `SqlAlchemyUnitOfWork` to `Message`, `Message`, `Message`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `build_app()` connect `make_app` to `events`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `make_app()` (e.g. with `build_app()` and `build_app()`) actually correct?**
  _`make_app()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `events()` (e.g. with `patch_elements()` and `patch_signals()`) actually correct?**
  _`events()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SqlAlchemyUnitOfWork` (e.g. with `test_commit_marks_transaction_committed_and_closes_connection()` and `test_exception_in_block_rolls_back_and_still_closes()`) actually correct?**
  _`SqlAlchemyUnitOfWork` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Message` (e.g. with `SqlAlchemyMessageRepository` and `_a_message()`) actually correct?**
  _`Message` has 3 INFERRED edges - model-reasoned connections that need verification._