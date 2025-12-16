from app import app


def test_tracked_badge_exists():
    with app.test_client() as c:
        r = c.get('/')
        assert r.status_code == 200
        html = r.get_data(as_text=True)
        # badge has been removed; ensure it's not in the server-rendered HTML
        assert 'id="tracked-badge"' not in html
    # ensure client-side JS will show the tracked-wrapper area
    import pathlib
    js_path = pathlib.Path('static/js/main.js')
    assert js_path.exists()
    js = js_path.read_text(encoding='utf-8')
    assert 'tracked-wrapper' in js
