from app import app


def test_status_keywords_endpoint():
    with app.test_client() as c:
        r = c.get('/api/status_keywords')
        assert r.status_code == 200
        data = r.get_json()
        assert 'delivered' in data and 'error' in data
        assert isinstance(data['delivered'], list)
        assert isinstance(data['error'], list)
