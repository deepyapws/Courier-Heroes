import pathlib


def test_update_wrapper_present():
    js_path = pathlib.Path('static/js/main.js')
    assert js_path.exists()
    js = js_path.read_text(encoding='utf-8')
    # the tracked-update-wrapper should be present in the rendered control markup
    assert 'tracked-update-wrapper' in js
    # and ensure the code binds the button by re-querying the DOM
    assert "document.getElementById('update-all-btn')" in js or 'getElementById("update-all-btn")' in js
    # ensure fetch uses cache: 'no-store' for tracked list so updates are not cached
    assert "cache: 'no-store'" in js or 'cache: "no-store"' in js
