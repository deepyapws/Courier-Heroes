import os


def test_logos_exist():
    base = os.path.join(os.path.dirname(__file__), os.pardir, 'static', 'img')
    files = ['cj.svg', 'cvs.svg', 'lotte.svg', 'hanjin.svg', 'koreapost.svg', 'cupost.svg', 'unknown.svg']
    for f in files:
        path = os.path.abspath(os.path.join(base, f))
        assert os.path.exists(path), f"Missing expected logo: {path}"
