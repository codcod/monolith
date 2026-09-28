mod stelo_base 'platform/stelo-base'
mod inbox 'platform/inbox'
mod traffic 'platform/traffic'
mod dispatcher 'platform/dispatcher'
mod admin 'platform/admin'

MODULES := "stelo_base inbox traffic dispatcher admin"

# List available recipes (default when running `just` with no args)
list:
    @just --list

# Build images and start the full stack: postgres, rabbitmq, migrations, all services
[group('compose')]
up:
    docker compose up -d --build

# Stop and remove all containers and volumes (full reset — deletes postgres/rabbitmq data)
[group('compose')]
down:
    docker compose down -v

# Tail logs from every running service
[group('compose')]
logs:
    docker compose logs -f

# Auto-fix and reformat every module (ruff)
[group('quality')]
fmt:
    uv lock -q
    for m in {{ MODULES }}; do UV_FROZEN=1 just $m::fmt; done

# Lint + format-check + type-check every module (ruff + ty)
[group('quality')]
lint:
    uv lock -q
    for m in {{ MODULES }}; do UV_FROZEN=1 just $m::lint; done

# Run every module's test suite
[group('test')]
test:
    uv lock -q
    for m in {{ MODULES }}; do UV_FROZEN=1 just $m::test; done

# Mirror the top-level GHA integration job: build, boot stack, check inbox health, tear down
[group('ci')]
integration:
    #!/usr/bin/env bash
    set -euo pipefail
    trap 'docker compose down -v' EXIT
    docker compose build
    docker compose up -d
    for _ in $(seq 1 30); do
        curl -sf http://localhost:8080/health && exit 0
        sleep 1
    done
    echo "inbox never became healthy" >&2
    docker compose logs
    exit 1

# Mirror the top-level GHA actionlint job
[group('ci')]
lint-workflows:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v actionlint >/dev/null 2>&1; then
        curl -s https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash | bash -s -- latest .
        ./actionlint -color
    else
        actionlint -color
    fi

# Remove caches/build artifacts from every module
[group('dev')]
clean:
    for m in {{ MODULES }}; do just $m::clean; done
