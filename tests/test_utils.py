import json
from utils import safe_print_json, save_debug_to_file


def test_save_debug_to_file(tmp_path):
    obj = {"msg": "hello — unicode test — en dash: \u2013"}
    p = tmp_path / "dbg" / "out.json"
    path = save_debug_to_file(obj, str(p))
    assert path == str(p)
    # file contains utf-8 JSON
    content = p.read_text(encoding="utf-8")
    data = json.loads(content)
    assert data["msg"].startswith("hello")
