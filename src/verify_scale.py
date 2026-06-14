"""Verify the headline *scale* numbers of the Automatic Textbook Formalization
paper (arXiv:2604.03071) against the released Lean code base.

Headline claims (abstract + SUMMARY.md of the released repo):
  - ~130,000 lines of Lean code
  - ~5,900 Lean declarations (theorem/lemma/def/abbrev/instance/structure/...)
  - 344 designated targets, of which 340 formalized (4 reclassified as exercises)

We count these *independently* from the released `algebraic-combinatorics`
repo, reusing the authors' own declaration regex (from
`scripts/gen_growth_charts.py`) so the methodology matches theirs exactly.

Run:  python src/verify_scale.py
Emits results/scale.json (reported vs reproduced).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FORMALIZATION = REPO_ROOT / "replication_target" / "algebraic-combinatorics"
LEAN_PKG = FORMALIZATION / "AlgebraicCombinatorics"
MANIFEST = FORMALIZATION / "manifest.json"
RESULTS = REPO_ROOT / "results"

# Authors' declaration regex, verbatim from
# algebraic-combinatorics/scripts/gen_growth_charts.py (_DECL_RE).
_DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)*"
    r"(?:(?:private|protected|noncomputable|unsafe|partial|nonrec)\s+)*"
    r"(?:theorem|lemma|def|abbrev|instance|structure|inductive|class)\b",
    re.MULTILINE,
)

# Paper / repo-reported headline figures.
REPORTED = {
    "lean_loc": 130_000,           # abstract: "130K lines of code"
    "declarations": 5_900,         # abstract: "5900 Lean declarations"
    "targets_total": 344,          # SUMMARY.md / manifest: designated targets
    "targets_formalized": 340,     # abstract: "all 340 target ... formalized"
    "targets_exercise": 4,         # reclassified as exercises, not attempted
}

# Tolerance for the "~" figures the paper rounds (130K, 5900). 5% is generous
# but the rounding alone is ~1-2%.
TOL = 0.05


def lean_files() -> list[Path]:
    """All .lean files in the formalization package, excluding the embedded
    LaTeX source tree (`/tex/`) and any build artifacts (`.lake`).

    Mirrors the authors' selection: they measure LOC and declarations over
    `AlgebraicCombinatorics/` .lean files, skipping `/tex/` paths.
    """
    files = []
    for p in LEAN_PKG.rglob("*.lean"):
        parts = set(p.parts)
        if ".lake" in parts or "tex" in parts:
            continue
        files.append(p)
    return sorted(files)


def count_loc_and_decls(files: list[Path]) -> tuple[int, int, int]:
    total_lines = 0
    total_decls = 0
    total_sorry = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        total_lines += text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        total_decls += len(_DECL_RE.findall(text))
        # `sorry` as a whole word (the unfinished-proof marker).
        total_sorry += len(re.findall(r"\bsorry\b", text))
    return total_lines, total_decls, total_sorry


def count_targets() -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    chapters = data["chapters"]
    targets = sum(len(c.get("target_theorems", [])) for c in chapters)
    return {"chapters": len(chapters), "targets_total": targets}


def within(reproduced: float, reported: float, tol: float = TOL) -> bool:
    if reported == 0:
        return reproduced == 0
    return abs(reproduced - reported) / reported <= tol


def main() -> dict:
    files = lean_files()
    loc, decls, sorries = count_loc_and_decls(files)
    targets = count_targets()

    reproduced = {
        "lean_files": len(files),
        "lean_loc": loc,
        "declarations": decls,
        "sorry_count": sorries,
        "targets_total": targets["targets_total"],
        "chapters": targets["chapters"],
    }

    checks = {
        "lean_loc": within(loc, REPORTED["lean_loc"]),
        "declarations": within(decls, REPORTED["declarations"]),
        "targets_total": reproduced["targets_total"] == REPORTED["targets_total"],
    }

    result = {
        "artifact": "facebookresearch/algebraic-combinatorics",
        "reported": REPORTED,
        "reproduced": reproduced,
        "checks": checks,
        "all_pass": all(checks.values()),
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "scale.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Lean files:    {reproduced['lean_files']}")
    print(f"Lean LOC:      {loc:,}  (reported ~{REPORTED['lean_loc']:,})  "
          f"{'PASS' if checks['lean_loc'] else 'FAIL'}")
    print(f"Declarations:  {decls:,}  (reported ~{REPORTED['declarations']:,})  "
          f"{'PASS' if checks['declarations'] else 'FAIL'}")
    print(f"Targets:       {reproduced['targets_total']} in {reproduced['chapters']} "
          f"chapters  (reported {REPORTED['targets_total']})  "
          f"{'PASS' if checks['targets_total'] else 'FAIL'}")
    print(f"sorry markers: {sorries}")
    print(f"ALL PASS: {result['all_pass']}")
    return result


if __name__ == "__main__":
    main()
