# Graph Report - monolith  (2026-09-14)

## Corpus Check
- 99 files · ~15,720 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 30 file(s) not represented in the graph (top: (none) 18, .toml 4, .ini 3)

## Summary
- 584 nodes · 796 edges · 81 communities (22 shown, 31 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 102 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `061cb8b1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_app
- events
- stelo-base shared library
- _serve
- read_config
- Message
- Application
- Self
- make_engine
- FakeClient
- Application
- channels.py
- datastar.js
- stelo-base
- test_channels.py
- inbox/tests/performance/k6/script.js
- dispatcher/tests/performance/k6/script.js
- traffic/tests/performance/k6/script.js
- rebuild-sandbox.sh
- stelo-platform
- Message
- Message
- SqlAlchemyUnitOfWork
- FakeConnection
- FakeConnection
- _make_client
- FakeConnection
- AbstractRepository
- FakeUnitOfWork
- FakeUnitOfWork
- FakeUnitOfWork
- Message
- AsyncConnection
- Config
- get
- Request
- Response
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
- Application
- Config
- get
- Request
- Response
- Self

## God Nodes (most connected - your core abstractions)
1. `make_app()` - 17 edges
2. `events()` - 16 edges
3. `SqlAlchemyUnitOfWork` - 15 edges
4. `FakeConnection` - 13 edges
5. `stelo-base shared library` - 13 edges
6. `FakeResult` - 12 edges
7. `Message` - 12 edges
8. `Message` - 12 edges
9. `Message` - 12 edges
10. `traffic service (design)` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Switch from black/isort/flake8/pylint/pyright to ruff+ty` --semantically_similar_to--> `Reusable Python module CI workflow`  [INFERRED] [semantically similar]
  CHANGELOG.md → .github/workflows/python_reusable.yml
- `traffic Dockerfile COPY ../inbox path-not-found error log` --semantically_similar_to--> `Unified platform/ Docker build context`  [INFERRED] [semantically similar]
  README.md → development/design.md
- `traffic Dockerfile COPY ../inbox path-not-found error log` --semantically_similar_to--> `Repo-root Docker build context rationale`  [INFERRED] [semantically similar]
  README.md → PACKAGING.md
- `src/-only type-check rationale` --semantically_similar_to--> `ty type-checking scoped to src/ only`  [INFERRED] [semantically similar]
  .github/workflows/python_reusable.yml → PACKAGING.md
- `admin service (compose)` --references--> `Relay Console admin dashboard`  [INFERRED]
  compose.yaml → platform/admin/static/index.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reusable Python CI workflow pattern shared by every module** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow, _github_workflows_python_reusable_workflow [EXTRACTED 1.00]
- **Inbox -> Traffic -> Dispatcher message pipeline over RabbitMQ Streams** — development_design_stelo_inbox_service, development_design_stelo_traffic_service, development_design_stelo_dispatcher_service, development_design_traffic_in_stream, development_design_dispatch_in_stream [EXTRACTED 1.00]
- **rbfly Cython build-essential workaround shared by all module CI workflows** — _github_workflows_ci_admin_workflow, _github_workflows_ci_dispatcher_workflow, _github_workflows_ci_inbox_workflow, _github_workflows_ci_stelo_base_workflow, _github_workflows_ci_traffic_workflow [EXTRACTED 1.00]

## Communities (81 total, 31 thin omitted)

### Community 0 - "make_app"
Cohesion: 0.06
Nodes (35): AbstractRouteDef, middleware, build_app(), Application, Config, _config(), test_health_ok(), test_index_page_is_reachable_without_auth() (+27 more)

### Community 1 - "events"
Cohesion: 0.09
Nodes (33): FileResponse, channel_breakdown(), ChannelCounts, error_rate(), Event, latency_percentiles_ms(), oldest_unprocessed_age_seconds(), AsyncConnection (+25 more)

### Community 2 - "stelo-base shared library"
Cohesion: 0.08
Nodes (51): rbfly transitive Cython build dependency note, CI platform/admin workflow, CI platform/dispatcher workflow, CI platform/inbox workflow, CI platform/stelo-base workflow, CI platform/traffic workflow, src/-only type-check rationale, --project/--package uv sync scoping rationale (+43 more)

### Community 4 - "_serve"
Cohesion: 0.24
Nodes (8): Config, Run one HTTP worker on its own event loop, bound to a socket shared (via…, Fork `workers` worker processes (see `_serve_one`) and supervise them: forward…, _serve(), _serve_one(), build_app(), Application, Config

### Community 5 - "read_config"
Cohesion: 0.12
Nodes (15): get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, get_dsn(), The DSN comes from the module's own config.toml (same file the app reads), not…, Config, Read configuration file and return configuration object., Setup logging for an application., Setup Stelo application. 1. Setup logging. 2. Install uvloop based asyncio loop. (+7 more)

### Community 7 - "Message"
Cohesion: 0.07
Nodes (29): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, traffic's own routing record — its row in `traffic.messages`. Distinct from…, build_app(), health(), process_traffic_in() (+21 more)

### Community 11 - "make_engine"
Cohesion: 0.21
Nodes (12): Connection, MetaData, make_engine(), AsyncEngine, Build an async SQLAlchemy core engine for a module's database. All modules…, _do_run_migrations(), Any, AsyncEngine (+4 more)

### Community 12 - "FakeClient"
Cohesion: 0.11
Nodes (12): consume(), publish(), Any, Publish a message (as JSON) to `stream`, creating it and its publisher on first…, Consume JSON messages from `stream` from the point of subscription onward,…, FakeClient, FakePublisher, Self (+4 more)

### Community 14 - "channels.py"
Cohesion: 0.22
Nodes (4): EmailSender, Sender, SmsSender, WhatsAppSender

### Community 15 - "datastar.js"
Cohesion: 0.38
Nodes (3): apply(), get(), has()

### Community 16 - "stelo-base"
Cohesion: 0.40
Nodes (5): stelo-admin, stelo-base, stelo-dispatcher, stelo-inbox, stelo-traffic

### Community 28 - "Message"
Cohesion: 0.07
Nodes (29): AsyncConnection, Message, SqlAlchemyMessageRepository, Message, dispatcher's own send-outcome record — its row in `dispatcher.messages`.…, build_app(), health(), process_dispatch_in() (+21 more)

### Community 29 - "Message"
Cohesion: 0.08
Nodes (26): Channel, AsyncConnection, Message, SqlAlchemyMessageRepository, Message, inbox's own intake record — its row in `inbox.messages`. Distinct from…, create_message(), health() (+18 more)

### Community 30 - "SqlAlchemyUnitOfWork"
Cohesion: 0.09
Nodes (14): AbstractUnitOfWork, AsyncEngine, Self, Owns one `AsyncConnection` + transaction for the lifetime of the `async with`…, One business transaction: `async with uow: ...; await uow.commit()`. Exiting…, SqlAlchemyUnitOfWork, FakeConnection, FakeEngine (+6 more)

### Community 31 - "FakeConnection"
Cohesion: 0.17
Nodes (12): FakeConnection, FakeResult, Stands in for `AsyncConnection`: `scalar()` and `execute()` each pop the next…, Stands in for a SQLAlchemy `Result` — only the bits metrics.py uses., test_channel_breakdown_maps_rows(), test_error_rate_defaults_to_zero_when_no_messages(), test_latency_percentiles_ms(), test_oldest_unprocessed_age_seconds() (+4 more)

### Community 32 - "FakeConnection"
Cohesion: 0.14
Nodes (5): FakeConnection, FakeEngine, FakeSender, FakeTransaction, test_process_dispatch_in_sends_and_records()

### Community 33 - "_make_client"
Cohesion: 0.16
Nodes (8): FakeConnection, FakeEngine, FakeTransaction, _make_client(), test_create_message_inserts_row_and_publishes(), test_create_message_requires_auth(), test_create_message_validates_payload(), test_health_ok()

### Community 34 - "FakeConnection"
Cohesion: 0.15
Nodes (4): FakeConnection, FakeEngine, FakeTransaction, test_process_traffic_in_inserts_and_republishes()

### Community 35 - "AbstractRepository"
Cohesion: 0.19
Nodes (7): AbstractRepository, A collection-like façade over one aggregate's storage. Concrete repositories…, InMemoryRepository, test_abstract_repository_cannot_be_instantiated(), test_add_then_get_returns_the_same_item(), test_get_missing_id_returns_none(), T

### Community 36 - "FakeUnitOfWork"
Cohesion: 0.24
Nodes (7): FakeUnitOfWork, _noop_publish(), test_submit_message_adds_the_message_and_commits(), test_submit_message_publishes_only_after_commit(), commit(), test_submit_message_publishes_the_wire_shape_after_commit(), publish()

### Community 37 - "FakeUnitOfWork"
Cohesion: 0.29
Nodes (4): FakeSender, FakeUnitOfWork, test_dispatch_message_records_the_outcome_and_commits(), test_dispatch_message_sends_via_the_given_sender()

### Community 38 - "FakeUnitOfWork"
Cohesion: 0.31
Nodes (4): FakeUnitOfWork, _noop_publish(), test_route_message_adds_a_routing_row_and_commits(), test_route_message_republishes_with_status_routed()

## Knowledge Gaps
- **14 isolated node(s):** `stelo-admin`, `stelo-dispatcher`, `stelo-inbox`, `stelo-traffic`, `CHANNELS` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 257 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_app()` connect `make_app` to `make_engine`, `Message`, `_serve`, `Message`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `SqlAlchemyUnitOfWork` connect `SqlAlchemyUnitOfWork` to `Message`, `Message`, `Message`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Why does `build_app()` connect `make_app` to `events`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `make_app()` (e.g. with `build_app()` and `build_app()`) actually correct?**
  _`make_app()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `events()` (e.g. with `patch_elements()` and `patch_signals()`) actually correct?**
  _`events()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SqlAlchemyUnitOfWork` (e.g. with `test_commit_marks_transaction_committed_and_closes_connection()` and `test_exception_in_block_rolls_back_and_still_closes()`) actually correct?**
  _`SqlAlchemyUnitOfWork` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `stelo-admin`, `stelo-dispatcher`, `stelo-inbox` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._