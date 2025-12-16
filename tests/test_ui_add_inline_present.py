import pathlib


def test_inline_add_button_present_in_js():
    js_path = pathlib.Path('static/js/main.js')
    assert js_path.exists()
    js = js_path.read_text(encoding='utf-8')
    assert 'btn-add-inline' in js
    assert 'add-inline-label' in js
