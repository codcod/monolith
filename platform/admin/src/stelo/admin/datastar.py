"""
Minimal encoders for Datastar v1's two SSE event types
(`datastar-patch-elements` / `datastar-patch-signals`). `datastar-py` isn't a
dependency anywhere in this workspace and the wire format is small enough to
hand-encode here rather than pull in a new package for one caller. Verified
against the vendored `static/datastar.js` (v1.0.3) bundle: each event carries
`data:` lines named after the action's own field names (`elements`/`signals`,
plus optional `selector`/`mode`), and the default `mode` ("outer", no
`selector` needed) replaces whichever existing element shares the id already
present on the fragment's own root tag.
"""

import typing as tp

import orjson


def patch_signals(signals: dict[str, tp.Any]) -> str:
    payload = orjson.dumps(signals).decode()
    return f"event: datastar-patch-signals\ndata: signals {payload}\n\n"


def patch_elements(
    html: str, *, selector: str | None = None, mode: str | None = None
) -> str:
    lines = ["event: datastar-patch-elements"]
    if selector:
        lines.append(f"data: selector {selector}")
    if mode:
        lines.append(f"data: mode {mode}")
    lines += [f"data: elements {line}" for line in html.splitlines()]
    return "\n".join(lines) + "\n\n"
