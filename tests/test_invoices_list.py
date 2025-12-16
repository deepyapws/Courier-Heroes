import json
from types import SimpleNamespace
import unified
import tracking


def load_invoices():
    with open('tests/invoices.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def test_invoice_list_runs(monkeypatch):
    invoices = load_invoices()
    for it in invoices:
        inv = it['inv']
        expected = it.get('courier', '')

        # Prepare per-courier deterministic stubs so unified.track uses the right path
        if 'Lotte' in expected:
            # Ensure CJ and CVS do not claim this invoice
            monkeypatch.setattr(unified, 'track_cj', lambda invc, debug=False: None)
            monkeypatch.setattr(unified, 'track_cvs', lambda invc, debug=False: None)
            monkeypatch.setattr(unified.requests, 'post', lambda *a, **kw: SimpleNamespace(text='<html></html>'))
            monkeypatch.setattr(tracking, 'parse_tracking_html', lambda html: {
                'trackingNumber': inv,
                'carrier': {'name': '롯데글로벌로지스'},
                'trackingEvents': [{'timestamp': '2025-12-16 10:00', 'location': '', 'description': 'Delivered'}],
                'origin': 'Seoul',
                'destination': 'Busan',
                'deliveryStatus': 'Delivered'
            })

        elif 'CUpost' in expected:
            monkeypatch.setattr(unified.requests, 'post', lambda *a, **kw: SimpleNamespace(text='<html></html>'))
            monkeypatch.setattr(tracking, 'parse_cupost_main', lambda html: {
                'trackingNumber': inv,
                'trackingEvents': [{'timestamp': '2025-12-16 11:13:47', 'location': '', 'description': 'In transit', 'is_current': True}],
                'deliveryStatus': 'In transit',
                'origin': 'Seoul',
                'destination': 'Busan',
                'carrier': {'name': 'CUpost'},
            })

        elif 'CVSNet' in expected or 'GS25' in expected:
            monkeypatch.setattr(unified, 'track_cj', lambda invc, debug=False: None)
            monkeypatch.setattr(unified, 'track_cvs', lambda invc, debug=False: {
                'courier': 'CVSNet (GS25)', 'tracking_number': invc, 'status': 'In transit', 'history': []
            })

        # Run unified.track and assert basic expectations
        res = unified.track(inv, debug=True)
        assert isinstance(res, dict), f"Result for {inv} should be a dict"
        assert 'error' not in res, f"Tracking {inv} returned error: {res.get('error')}"
        # tracking_number may be normalized - accept same string or endswith
        tn = res.get('tracking_number') or res.get('tracking')
        assert tn is not None and (str(tn) == inv or str(tn).endswith(inv)), f"Wrong tracking_number for {inv}: {tn}"
