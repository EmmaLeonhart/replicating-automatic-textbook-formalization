"""Unit tests for the scale verification.

These require the `algebraic-combinatorics` submodule to be checked out. When it
is absent (e.g. a shallow clone without submodules) the tests skip rather than
fail, so the cost-model tests still run.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import verify_scale as vs  # noqa: E402

_HAVE_SUBMODULE = vs.MANIFEST.exists() and any(vs.LEAN_PKG.rglob("*.lean"))

requires_submodule = pytest.mark.skipif(
    not _HAVE_SUBMODULE,
    reason="algebraic-combinatorics submodule not checked out",
)


def test_decl_regex_matches_basic_forms():
    import re
    samples = [
        "theorem foo : True := trivial",
        "  lemma bar := rfl",
        "@[simp] def baz := 1",
        "noncomputable def qux := 2",
        "private theorem secret := rfl",
        "structure S where",
        "instance : Foo := ...",
    ]
    for s in samples:
        assert vs._DECL_RE.search(s), s
    # Non-declarations must not match.
    assert not vs._DECL_RE.search("-- def in a comment is fine to skip? no")  # leading '--' -> not a decl start
    assert not vs._DECL_RE.search("  apply theorem_name")


@requires_submodule
def test_targets_exactly_344():
    t = vs.count_targets()
    assert t["targets_total"] == 344
    assert t["chapters"] == 45


@requires_submodule
def test_loc_near_130k():
    files = vs.lean_files()
    loc, _decls, _sorry = vs.count_loc_and_decls(files)
    assert abs(loc - 130_000) / 130_000 < 0.05


@requires_submodule
def test_declarations_near_5900():
    files = vs.lean_files()
    _loc, decls, _sorry = vs.count_loc_and_decls(files)
    assert abs(decls - 5_900) / 5_900 < 0.05


@requires_submodule
def test_all_scale_checks_pass():
    r = vs.main()
    assert r["all_pass"] is True
