"""
Fragment builders for the markup pushed over SSE. Math (coordinates, colors,
percentages) stays in Python — Jinja templates just lay out the markup.
"""

import jinja2
import orjson

from .adapters.metrics import ChannelCounts, Event

_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates/fragments'),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)

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
    ly = height - (values[-1] / hi) * height
    return _env.get_template('spark.html').render(
        elem_id=elem_id,
        width=width,
        height=height,
        points=pts,
        color=color,
        lx=width,
        ly=f'{ly:.1f}',
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

    gridlines = []
    for g in range(5):
        gv = hi * g / 4
        gy = y_of(gv)
        gridlines.append(
            {'y': f'{gy:.1f}', 'label_y': f'{gy + 3:.1f}', 'label': round(gv)}
        )
    series = [
        {
            'points': ' '.join(
                f'{pad_l + i * step:.1f},{y_of(v):.1f}' for i, v in enumerate(values)
            ),
            'color': STAGE_COLORS[stage],
        }
        for stage, values in history.items()
    ]

    return _env.get_template('chart.html').render(
        width=width,
        height=height,
        pad_l=pad_l,
        pad_r=pad_r,
        pad_t=pad_t,
        inner_h=inner_h,
        axis_y=pad_t + inner_h,
        step=f'{step:.4f}',
        hi=hi,
        series_json=orjson.dumps(history).decode(),
        gridlines=gridlines,
        series=series,
    )


def channel_bars(rows: list[ChannelCounts]) -> str:
    if not rows:
        return '<div id="channels"></div>'
    max_total = max((r['sent'] + r['failed'] for r in rows), default=1) or 1
    return _env.get_template('channel_bars.html').render(
        rows=[
            {
                'channel': r['channel'],
                'sent_pct': f'{r["sent"] / max_total * 100:.2f}',
                'fail_pct': f'{r["failed"] / max_total * 100:.2f}',
                'sent_fmt': f'{r["sent"]:,}',
                'failed_fmt': f'{r["failed"]:,}',
            }
            for r in rows
        ]
    )


def feed_rows(events: list[Event]) -> str:
    return _env.get_template('feed_rows.html').render(
        events=[
            {
                'time': e['at'][11:19],
                'color': FEED_STAGE_COLOR[e['stage']],
                'label': FEED_STAGE_LABEL[e['stage']],
                'id': e['id'],
                'channel': e['channel'],
            }
            for e in events
        ]
    )
