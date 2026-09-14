# Releasing

`monolith` ships three independently deployable services
(`stelo-inbox`, `stelo-traffic`, `stelo-dispatcher`) as container images.
Each is versioned and released on its own — there is no single "platform"
version. `stelo-base` (the shared library they all depend on) is versioned
too, but only ever ships bundled inside a service's image, never on its own.

> There is no release automation (no GitHub Actions release workflow, no
> registry push on tag) wired up yet — this is a fully manual process today.
> If/when that's added, this doc is where it should be documented (see
> [petstore's `RELEASING.md`](https://github.com/codcod/petstore/blob/main/RELEASING.md)
> for the shape a tag-driven version of this could take).

## Cutting a release for one service

Cutting a release is a deliberate human action.

**1. Decide what changed.** A service's release includes its own commits
since its last tag, plus any `stelo-base` changes since then (every service
image bundles whatever `stelo-base` version is current at build time —
there's no separate `stelo-base` release to pin to).

```sh
git log "$(git describe --tags --match 'inbox-v*' --abbrev=0)..HEAD" --oneline -- platform/inbox platform/stelo-base
```

**2. Stamp the changelog and bump the version.** In
[`CHANGELOG.md`](CHANGELOG.md), move the relevant `[Unreleased]` entries under
a new `## [inbox-X.Y.Z] - YYYY-MM-DD`-style heading (adjust the prefix for
whichever service you're releasing). Then bump `version = "..."` in that
service's `platform/<service>/pyproject.toml` (and in
`platform/stelo-base/pyproject.toml` too, if this release includes a
`stelo-base` change). Commit both together.

**3. Tag.** Prefix the tag with the service name so the three services don't
collide on the same tag namespace:

```sh
git tag inbox-vX.Y.Z
git push origin inbox-vX.Y.Z
```

**4. Build and publish the image manually:**

```sh
just inbox::docker-build
docker tag stelo-inbox ghcr.io/umbrella-org/monolith/stelo-inbox:X.Y.Z
docker push ghcr.io/umbrella-org/monolith/stelo-inbox:X.Y.Z
```

Repeat step 4 with `:latest` too if this tag should move the floating tag.

## Validating locally before tagging

```sh
just lint
just test
docker compose build
docker compose up -d   # runs each *-migrate one-shot, then all three services
docker compose down
```

This exercises the same lint/type-check/test/build/migrate path a CI release
gate would run, if one existed.

## Versioning

Semantic versioning, independently per service (and for `stelo-base`). While
a service's version is below `1.0.0`, breaking changes may land in a minor
release — they must be labelled `### Breaking` in the changelog entry.
