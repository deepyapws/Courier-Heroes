from utils import normalize_history


def test_normalize_history_orders_oldest_first():
    # Input is newest-first; times are varied formats
    hist = [
        {'time': '2025-12-16 12:00', 'message': 'later'},
        {'time': '16 Dec 2025 10:00', 'message': 'earlier'},
        {'time': '2025.12.16 11:00', 'message': 'middle'},
    ]

    out = normalize_history(hist)
    times = [h['time'] for h in out]
    assert times[0].endswith('10:00')
    assert times[1].endswith('11:00')
    assert times[2].endswith('12:00')


def test_preserve_unparsable_at_end():
    hist = [
        {'time': 'Unknown', 'message': 'n/a'},
        {'time': '2025-12-16 09:00', 'message': 'earlier'},
        {'time': 'no time', 'message': 'n/a2'},
    ]
    out = normalize_history(hist)
    # parsed 09:00 should be first
    assert out[0]['time'].endswith('09:00')
    # unparsable items should be at the end preserving relative order
    assert out[-2]['message'] == 'n/a'
    assert out[-1]['message'] == 'n/a2'
