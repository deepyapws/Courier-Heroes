from app import app


def test_search_input_present():
    # The tracked search input is injected by client-side JS when the tracked list
    # is rendered. Server-side HTML won't contain it, so assert that the
    # client-side JS contains the creation code for the input instead.
    import pathlib
    js_path = pathlib.Path('static/js/main.js')
    assert js_path.exists(), "main.js is missing"
    js = js_path.read_text(encoding='utf-8')
    assert 'id="tracked-search"' in js
