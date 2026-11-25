import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from stats import languages  # noqa: E402


def repo(**sizes: int) -> dict:
    return {"languages": {"edges": [{"size": s, "node": {"name": n}} for n, s in sizes.items()]}}


def test_sums_across_repos_and_sorts():
    out = languages([repo(Python=30, HTML=10), repo(Python=20, Go=40)])
    assert [n for n, _ in out] == ["Python", "Go", "HTML"]
    assert round(sum(p for _, p in out)) == 100


def test_tail_folds_into_other():
    out = languages([repo(A=50, B=20, C=10, D=10, E=5, F=3, G=2)], top=5)
    assert out[-1][0] == "Other" and round(out[-1][1]) == 5


def test_no_code_gives_empty_list():
    assert languages([repo()]) == []
