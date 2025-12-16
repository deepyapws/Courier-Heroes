import db
import unified
from app import app


def test_update_all_endpoint(tmp_path, monkeypatch):
    # Use temp DB
    db.DB_PATH = tmp_path / 'tracked_update_all.db'
    db.init_db()

    with app.test_client() as c:
        # add two items
        r1 = c.post('/api/tracked', json={'tracking': 'AAA'})
        r2 = c.post('/api/tracked', json={'tracking': 'BBB'})
        assert r1.status_code == 200 and r2.status_code == 200

        # monkeypatch unified.track to return predictable results
        def fake_track(tracking):
            return {'courier': 'Mock', 'tracking_number': tracking, 'status': f'OK-{tracking}', 'history': [], 'latest_event': {}}

        monkeypatch.setattr(unified, 'track', fake_track)

        # call update all
        resp = c.post('/api/tracked/check_all')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'results' in data and len(data['results']) == 2

        # ensure DB entries were updated with last_result and last_checked present in response
        for res in data['results']:
            assert 'last_checked' in res
            assert 'result' in res

        # ensure DB entries reflect updated status
        list_resp = c.get('/api/tracked')
        items = list_resp.get_json().get('items', [])
        assert any(it.get('last_result', {}).get('status','').startswith('OK-') for it in items)


def test_update_all_shows_per_item_overlay_in_js():
    import pathlib
    js_path = pathlib.Path('static/js/main.js')
    js = js_path.read_text(encoding='utf-8')
    assert "spinner-overlay" in js
    assert ".classList.add('checking')" in js
