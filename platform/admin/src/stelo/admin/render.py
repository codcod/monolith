"""
Tiny f-string HTML/SVG builders for the fragments pushed over SSE — no
templating engine anywhere in this codebase, so this follows suit rather
than introducing jinja2 for four small snippets.
"""

import html

import orjson

from .metrics import ChannelCounts, Event

STAGE_COLORS = {
    'received': 'var(--received)',
    'routed': 'var(--processed)',
    'sent': 'var(--dispatched)',
}
FEED_STAGE_LABEL = {
    'received': 'received',
    'routed': 'routed',
    'sent': 'sent',
    'failed': 'failed',
}
FEED_STAGE_COLOR = {
    'received': 'var(--received)',
    'routed': 'var(--processed)',
    'sent': 'var(--dispatched)',
    'failed': 'var(--critical)',
}


def spark(
    values: list[float], color: str, elem_id: str, width: int = 240, height: int = 34
) -> str:
    """
    The returned <svg> carries `elem_id` so Datastar's default fragment merge
    (match by the fragment's own id) replaces the right element without
    needing an explicit selector.
    """
    if not values:
        return f'<svg id="{elem_id}" viewBox="0 0 {width} {height}"></svg>'
    hi = max(values) * 1.15 or 1.0
    step = width / max(len(values) - 1, 1)
    pts = ' '.join(
        f'{i * step:.1f},{height - (v / hi) * height:.1f}' for i, v in enumerate(values)
    )
    lx, ly = width, height - (values[-1] / hi) * height
    return (
        f'<svg id="{elem_id}" viewBox="0 0 {width} {height}" preserveAspectRatio="none">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{lx}" cy="{ly:.1f}" r="3" fill="{color}"/>'
        f'</svg>'
    )


def chart(history: dict[str, list[float]], width: int = 560, height: int = 220) -> str:
    pad_l, pad_r, pad_t, pad_b = 34, 8, 10, 22
    inner_w, inner_h = width - pad_l - pad_r, height - pad_t - pad_b
    n = max((len(v) for v in history.values()), default=0)
    all_vals = [v for series in history.values() for v in series] or [1.0]
    hi = max(1.0, ((max(all_vals) * 1.15) // 5 + 1) * 5)
    step = inner_w / max(n - 1, 1)

    def y_of(v: float) -> float:
        return pad_t + inner_h - (v / hi) * inner_h

    parts = []
    for g in range(5):
        gv = hi * g / 4
        gy = y_of(gv)
        parts.append(
            f'<line x1="{pad_l}" x2="{width - pad_r}" y1="{gy:.1f}" y2="{gy:.1f}" '
            f'stroke="var(--grid)" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="4" y="{gy + 3:.1f}" font-size="9" fill="var(--text-muted)" '
            f'font-family="IBM Plex Mono, monospace">{round(gv)}</text>'
        )
    parts.append(
        f'<line x1="{pad_l}" x2="{width - pad_r}" y1="{pad_t + inner_h}" '
        f'y2="{pad_t + inner_h}" stroke="var(--axis)" stroke-width="1"/>'
    )
    for stage, values in history.items():
        pts = ' '.join(
            f'{pad_l + i * step:.1f},{y_of(v):.1f}' for i, v in enumerate(values)
        )
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{STAGE_COLORS[stage]}" '
            f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        )

    series_json = html.escape(orjson.dumps(history).decode(), quote=True)
    return (
        f'<svg id="chart" viewBox="0 0 {width} {height}" preserveAspectRatio="none" '
        f'data-series="{series_json}" data-step="{step:.4f}" data-pad-l="{pad_l}" '
        f'data-pad-t="{pad_t}" data-inner-h="{inner_h}" data-hi="{hi}">'
        f'{"".join(parts)}</svg>'
    )


def channel_bars(rows: list[ChannelCounts]) -> str:
    if not rows:
        return '<div id="channels"></div>'
    max_total = max((r['sent'] + r['failed'] for r in rows), default=1) or 1
    body = []
    for r in rows:
        sent_pct = r['sent'] / max_total * 100
        fail_pct = r['failed'] / max_total * 100
        body.append(
            '<div class="chan-row">'
            f'<div class="chan-name">{html.escape(r["channel"])}</div>'
            '<div class="chan-bar-track">'
            f'<div class="chan-bar-seg" style="width:{sent_pct:.2f}%;background:var(--good)"></div>'
            f'<div class="chan-bar-seg" style="width:{fail_pct:.2f}%;background:var(--critical)"></div>'
            '</div>'
            f'<div class="chan-count"><b>{r["sent"]:,}</b> '
            f'<span class="fail-text">/ {r["failed"]:,}</span></div>'
            '</div>'
        )
    return f'<div id="channels">{"".join(body)}</div>'


def feed_rows(events: list[Event]) -> str:
    rows = []
    for e in events:
        color = FEED_STAGE_COLOR[e['stage']]
        label = FEED_STAGE_LABEL[e['stage']]
        rows.append(
            '<div class="feed-row">'
            f'<div class="feed-time">{html.escape(e["at"][11:19])}</div>'
            f'<div class="badge" style="background:color-mix(in srgb, {color} 16%, transparent); '
            f'color:{color}"><span class="bdot" style="background:{color}"></span>{label}</div>'
            f'<div class="feed-id">{html.escape(e["id"])}</div>'
            f'<div class="feed-chan">{html.escape(e["channel"])}</div>'
            '</div>'
        )
    return f'<div id="feed">{"".join(rows)}</div>'
