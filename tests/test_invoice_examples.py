import json
from types import SimpleNamespace
import unified
import tracking


def test_unified_lotte_invoice(monkeypatch):
    lotte = "404931271275"

    # Make CJ and CVS return None so Lotte is tried and used
    monkeypatch.setattr(unified, 'track_cj', lambda invc, debug=False: None)
    monkeypatch.setattr(unified, 'track_cvs', lambda invc, debug=False: None)

    # Mock requests.post within unified.track_lotte to avoid network
    monkeypatch.setattr(unified.requests, 'post', lambda *a, **kw: SimpleNamespace(text='<html></html>'))

    # Mock the parser to return a parsed structure for our invoice
    def fake_parse(html):
        return {
            'trackingNumber': lotte,
            'carrier': {'name': '롯데글로벌로지스'},
            'trackingEvents': [
                {'timestamp': '2025-12-16 10:00', 'location': 'Seoul', 'description': 'Delivered'}
            ],
            'origin': 'Seoul',
            'destination': 'Busan',
            'deliveryStatus': 'Delivered'
        }

    monkeypatch.setattr(tracking, 'parse_tracking_html', fake_parse)

    res = unified.track(lotte, debug=True)
    assert isinstance(res, dict)
    assert 'error' not in res
    assert res['tracking_number'] == lotte
    assert 'Lotte' in res['courier'] or '롯데' in res['courier']
    assert isinstance(res['history'], list) and len(res['history']) == 1


def test_track_cu_invoice_using_fixture(monkeypatch):
    cu_post = "363225021454"
    # Stub network and parser so test is deterministic
    monkeypatch.setattr(unified.requests, 'post', lambda *a, **kw: SimpleNamespace(text='<html></html>', status_code=200, headers={}))
    monkeypatch.setattr(tracking, 'parse_cupost_main', lambda html: {
        'trackingNumber': cu_post,
        'trackingEvents': [{'timestamp': '2025-12-16 11:13:47', 'location': '', 'description': 'In transit', 'is_current': True}],
        'deliveryStatus': 'In transit',
        'origin': 'Seoul',
        'destination': 'Busan',
        'carrier': {'name': 'CUpost'},
    })

    # Call track_cu directly (this exercises the CUpost parser path)
    res = unified.track_cu(cu_post, debug=True)
    assert isinstance(res, dict)
    assert res.get('courier') == 'CUpost'
    assert 'tracking_number' in res
    assert isinstance(res.get('history', []), list)


def test_unified_gs_post_invoice(monkeypatch):
    gs_post_1 = "210535605545"

    # Simulate CJ failing and CVS handling this invoice
    monkeypatch.setattr(unified, 'track_cj', lambda invc, debug=False: None)

    def fake_cvs(invc, debug=False):
        return {
            'courier': 'CVSNet (GS25)',
            'tracking_number': invc,
            'status': 'In transit',
            'latest_event': {'message': 'In transit'},
            'history': []
        }

    monkeypatch.setattr(unified, 'track_cvs', fake_cvs)

    res = unified.track(gs_post_1, debug=True)
    assert isinstance(res, dict)
    assert res['tracking_number'] == gs_post_1
    assert 'CVS' in res['courier'] or 'GS25' in res['courier']
