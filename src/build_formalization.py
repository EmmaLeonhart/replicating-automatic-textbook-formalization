"""Build the released Lean formalization to confirm it compiles.

This is the user-consented heavy verification step. It:
  1. fetches Mathlib's precompiled cache (`lake exe cache get`), then
  2. builds the project (`lake build AlgebraicCombinatorics`),
capturing return codes, wall-clock time and log tails into results/build.json.

Requires `elan`/`lake` on PATH (Lean toolchain v4.28.0, pinned by the repo's
`lean-toolchain`). On a machine without the toolchain this records a skip rather
than failing, so `scripts/run.py --with-build` stays usable everywhere.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FORMALIZATION = REPO_ROOT / "replication_target" / "algebraic-combinatorics"
RESULTS = REPO_ROOT / "results"


def _lake() -> str | None:
    lake = shutil.which("lake")
    if lake:
        return lake
    cand = Path(os.path.expanduser("~")) / ".elan" / "bin" / (
        "lake.exe" if os.name == "nt" else "lake")
    return str(cand) if cand.exists() else None


def _run(cmd: list[str], cwd: Path) -> dict:
    env = dict(os.environ)
    elan_bin = Path(os.path.expanduser("~")) / ".elan" / "bin"
    env["PATH"] = f"{elan_bin}{os.pathsep}{env.get('PATH', '')}"
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    dt = time.time() - t0
    out = (p.stdout or "") + (p.stderr or "")
    return {
        "cmd": " ".join(cmd),
        "returncode": p.returncode,
        "seconds": round(dt, 1),
        "log_tail": out[-4000:],
    }


def main() -> dict:
    RESULTS.mkdir(exist_ok=True)
    lake = _lake()
    if lake is None:
        result = {"ok": False, "skipped": True,
                  "reason": "lake/elan not found on PATH"}
        (RESULTS / "build.json").write_text(json.dumps(result, indent=2),
                                            encoding="utf-8")
        print("build: SKIPPED (no lake)")
        return result

    steps = []
    cache = _run([lake, "exe", "cache", "get"], FORMALIZATION)
    steps.append(cache)
    print(f"cache get: rc={cache['returncode']} ({cache['seconds']}s)")

    build = _run([lake, "build", "AlgebraicCombinatorics"], FORMALIZATION)
    steps.append(build)
    print(f"lake build: rc={build['returncode']} ({build['seconds']}s)")

    ok = build["returncode"] == 0
    result = {
        "ok": ok,
        "all_pass": ok,
        "toolchain": (FORMALIZATION / "lean-toolchain").read_text().strip(),
        "steps": steps,
    }
    (RESULTS / "build.json").write_text(json.dumps(result, indent=2),
                                        encoding="utf-8")
    print(f"BUILD ok={ok}")
    return result


if __name__ == "__main__":
    main()
