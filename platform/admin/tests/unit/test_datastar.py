from stelo.admin.datastar import patch_elements, patch_signals


def test_patch_signals_encodes_one_json_line():
    out = patch_signals({"a": 1, "b": "x"})
    assert out == 'event: datastar-patch-signals\ndata: signals {"a":1,"b":"x"}\n\n'


def test_patch_elements_encodes_each_line_and_ends_with_blank_line():
    out = patch_elements('<div id="x">\n  <span>hi</span>\n</div>')
    assert out == (
        "event: datastar-patch-elements\n"
        'data: elements <div id="x">\n'
        "data: elements   <span>hi</span>\n"
        "data: elements </div>\n"
        "\n"
    )


def test_patch_elements_includes_optional_selector_and_mode():
    out = patch_elements("<b>x</b>", selector="#target", mode="append")
    assert "data: selector #target\n" in out
    assert "data: mode append\n" in out
