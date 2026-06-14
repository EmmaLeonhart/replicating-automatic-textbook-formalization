"""Replication entry point (CI invokes this).

Runs the two re-runnable verifications for arXiv:2604.03071 and consolidates
their outputs into results/summary.json:

  1. Scale verification  — counts LOC / declarations / targets in the released
     `algebraic-combinatorics` Lean repo (needs the submodule checked out).
  2. Cost model          — recomputes the Appendix-A token-caching dollar
     figures (always runnable, no submodule needed).

The Lean `lake build` of the formalization is a separate, heavier step handled
by `src/build_formalization.py` and is not invoked here by default (it needs the
Lean toolchain and a long build). Pass --with-build to attempt it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
RESULTS = REPO_ROOT / "results"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-build", action="store_true",
                    help="also attempt the Lean lake build (slow, needs elan/lake)")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    summary = {"paper": "arXiv:2604.03071", "checks": {}}

    # 1. Cost model — always runnable.
    import cost_model
    cost = cost_model.main()
    summary["checks"]["cost_model"] = {
        "all_pass": cost["all_pass"],
        "reproduced": cost["reproduced"],
    }

    # 2. Scale verification — needs the submodule.
    import verify_scale
    have_submodule = verify_scale.MANIFEST.exists() and any(
        verify_scale.LEAN_PKG.rglob("*.lean"))
    if have_submodule:
        scale = verify_scale.main()
        summary["checks"]["scale"] = {
            "all_pass": scale["all_pass"],
            "reproduced": scale["reproduced"],
        }
    else:
        print("scale: SKIPPED (algebraic-combinatorics submodule not checked out)")
        summary["checks"]["scale"] = {"skipped": True}

    # 3. Optional Lean build.
    if args.with_build:
        import build_formalization
        build = build_formalization.main()
        summary["checks"]["build"] = build

    runnable = [c for c in summary["checks"].values()
                if not c.get("skipped")]
    summary["all_pass"] = all(c.get("all_pass", c.get("ok", False))
                              for c in runnable)

    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2),
                                          encoding="utf-8")
    print(f"\nSUMMARY all_pass={summary['all_pass']}  ->  results/summary.json")
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
