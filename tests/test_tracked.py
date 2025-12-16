import json
import unified
from app import app


def test_tracked_flow(tmp_path, monkeypatch):
    # Use temp DB by pointing DB_PATH to temp file
    import db
    db.DB_PATH = tmp_path / 'tracked_test.db'
    db.init_db()

    with app.test_client() as c:
        # add
        r = c.post('/api/tracked', json={'tracking': '363136094640', 'label': 'Mattress'})
        assert r.status_code == 200
        data = r.get_json()
        assert 'id' in data

        # list
        rl = c.get('/api/tracked')
        assert rl.status_code == 200
        items = rl.get_json().get('items', [])
        assert any(i['tracking'] == '363136094640' and i.get('label') == 'Mattress' for i in items)

        # check (mock unified.track so the test is hermetic)
        item_id = items[0]['id']
        monkeypatch.setattr(unified, 'track', lambda tracking: {'courier': 'Mock', 'tracking_number': tracking, 'status': 'In transit', 'history': [], 'latest_event': {}})
        rc = c.post(f'/api/tracked/{item_id}/check')
        assert rc.status_code == 200

        # Ensure the last_result is saved and returned by the list endpoint
        rl2 = c.get('/api/tracked')
        items2 = rl2.get_json().get('items', [])
        it = next((it for it in items2 if it['id'] == item_id), None)
        assert it is not None
        assert isinstance(it.get('last_result'), dict)

        # delete
        rd = c.delete(f'/api/tracked/{item_id}')
        assert rd.status_code == 200
