import json
from tracking import parse_cupost_main
from unified import track_cu
from types import SimpleNamespace
from unittest.mock import patch


def test_parse_cupost_main_local_file():
    html = open('test.html', 'r', encoding='utf-8').read()
    parsed = parse_cupost_main(html)
    assert 'trackingNumber' in parsed
    assert 'trackingEvents' in parsed
    assert isinstance(parsed['trackingEvents'], list)


def test_track_cu_unified_mapping(monkeypatch):
    html = open('test.html', 'r', encoding='utf-8').read()
    mock_resp = SimpleNamespace(text=html, status_code=200, headers={})

    with patch('requests.post', return_value=mock_resp):
        res = track_cu('25129173683', debug=True)

    assert res['courier'] == 'CUpost'
    assert res['tracking_number'] == '25129173683'
    assert 'history' in res and isinstance(res['history'], list)
    assert '_debug' in res and 'parsed' in res['_debug']
