from stelo.admin import render


def test_spark_carries_its_own_target_id():
    svg = render.spark([1.0, 2.0, 3.0], "var(--received)", "spark-received")
    assert svg.startswith('<svg id="spark-received"')
    assert "var(--received)" in svg


def test_spark_handles_empty_history():
    svg = render.spark([], "var(--received)", "spark-received")
    assert svg == '<svg id="spark-received" viewBox="0 0 240 34"></svg>'


def test_chart_embeds_series_as_json_for_the_hover_script():
    svg = render.chart(
        {"received": [1.0, 2.0], "routed": [0.5, 1.5], "sent": [0.1, 0.2]}
    )
    assert svg.startswith('<svg id="chart"')
    assert 'data-series="' in svg
    assert "&#34;received&#34;:[1.0,2.0]" in svg


def test_channel_bars_renders_sent_and_failed_counts():
    html = render.channel_bars([{"channel": "sms", "sent": 82340, "failed": 214}])
    assert "<b>82,340</b>" in html
    assert "/ 214" in html
    assert "sms" in html


def test_channel_bars_handles_no_rows():
    assert render.channel_bars([]) == '<div id="channels"></div>'


def test_feed_rows_renders_stage_badge_and_id():
    events = [
        {
            "id": "abc-1",
            "stage": "failed",
            "channel": "whatsapp",
            "at": "2026-01-01T12:34:56",
        }
    ]
    html = render.feed_rows(events)
    assert "failed" in html
    assert "abc-1" in html
    assert "whatsapp" in html
    assert "12:34:56" in html
