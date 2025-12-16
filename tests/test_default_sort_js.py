import pathlib


def test_default_sort_in_js():
    js_path = pathlib.Path('static/js/main.js')
    assert js_path.exists()
    js = js_path.read_text(encoding='utf-8')
    assert "if (!sortVal) sortVal = 'first_event:desc'" in js
