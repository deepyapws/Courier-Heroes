import json
from utils import extract_json


def test_extract_plain_object():
    txt = '{"a": 1, "b": "hello"}'
    out = extract_json(txt)
    assert isinstance(out, dict)
    assert out["a"] == 1


def test_extract_from_variable_assignment():
    txt = "var trackingInfo = {\n  'id': 123,\n  'message': 'ok'\n}; Some other JS();"
    out = extract_json(txt)
    assert isinstance(out, dict)
    assert out.get("id") == 123


def test_extract_array():
    txt = 'someprefix=[{"ts":1},{"ts":2}];'
    out = extract_json(txt)
    assert isinstance(out, list)
    assert len(out) == 2


def test_fix_trailing_commas_and_single_quotes():
    txt = "var data = {'x': 1, 'y': 2,};"
    out = extract_json(txt)
    assert isinstance(out, dict)
    assert out['x'] == 1


def test_handles_internal_braces_in_strings():
    txt = '{"a":"{not json}", "b": 2}'
    out = extract_json(txt)
    assert isinstance(out, dict)
    assert out['a'] == '{not json}'


def test_no_json_returns_none():
    txt = 'function foo() { return 1 + 2; } // no json here'
    out = extract_json(txt)
    assert out is None
