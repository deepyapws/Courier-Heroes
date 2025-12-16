import unified
from app import app


def test_search_by_tracking_and_label(tmp_path):
    import db
    db.DB_PATH = tmp_path / 'tracked_search.db'
    db.init_db()

    with app.test_client() as c:
        # add several tracked items
        r1 = c.post('/api/tracked', json={'tracking': 'ABC123', 'label': 'Mattress'})
        r2 = c.post('/api/tracked', json={'tracking': 'XYZ999', 'label': 'Shoes'})
        r3 = c.post('/api/tracked', json={'tracking': '12345', 'label': 'Parcel'})
        assert r1.status_code == 200 and r2.status_code == 200 and r3.status_code == 200

        # search by label (case-insensitive)
        s = c.get('/api/tracked?q=matTress')
        assert s.status_code == 200
        items = s.get_json().get('items', [])
        assert len(items) == 1 and items[0]['tracking'] == 'ABC123'

        # search by part of tracking number
        s2 = c.get('/api/tracked?q=123')
        assert s2.status_code == 200
        items2 = s2.get_json().get('items', [])
        # ABC123 and 12345 should match
        found = {it['tracking'] for it in items2}
        assert {'ABC123', '12345'}.issubset(found)


def test_search_matches_status_and_courier(tmp_path, monkeypatch):
    import db
    db.DB_PATH = tmp_path / 'tracked_search2.db'
    db.init_db()

    with app.test_client() as c:
        r1 = c.post('/api/tracked', json={'tracking': 'AAA'})
        r2 = c.post('/api/tracked', json={'tracking': 'BBB'})
        id1 = r1.get_json()['id']
        id2 = r2.get_json()['id']

        # mock unified.track to return different statuses and couriers
        def track_a(tracking):
            return {'courier': 'MockA', 'tracking_number': tracking, 'status': 'Delivered', 'history': [], 'latest_event': {}}

        def track_b(tracking):
            return {'courier': 'MockB', 'tracking_number': tracking, 'status': 'Error: not found', 'history': [], 'latest_event': {}}

        monkeypatch.setattr(unified, 'track', track_a)
        rc1 = c.post(f'/api/tracked/{id1}/check')
        assert rc1.status_code == 200

        monkeypatch.setattr(unified, 'track', track_b)
        rc2 = c.post(f'/api/tracked/{id2}/check')
        assert rc2.status_code == 200

        # search by status "delivered"
        s = c.get('/api/tracked?q=delivered')
        items = s.get_json().get('items', [])
        assert any(it['tracking'] == 'AAA' for it in items)

        # search by courier name
        s2 = c.get('/api/tracked?q=mockb')
        items2 = s2.get_json().get('items', [])
        assert any(it['tracking'] == 'BBB' for it in items2)
