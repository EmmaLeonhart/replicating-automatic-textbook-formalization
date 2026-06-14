# replicating-automatic-textbook-formalization — Devlog

**This file is where "done" lives.** `queue.md` is delete-only: when a queue
item is finished, the item is **deleted from `queue.md`** and a dated entry
is **appended here**, in the same commit as the work, then pushed. Never
tick a box in place — a checked box left in `queue.md` is the failure mode
this file exists to prevent.

Also record releases (tag + a one-line note), notable milestones, and
anything else worth a chronological trail. Newest entries at the bottom.

This is the **same convention as the cleanvibe repo's own `devlog.md`** —
every cleanvibe-scaffolded project gets one for the same reason.

See `CLAUDE.md` § "Workflow Rules" and `queue.md`'s preamble.

---

## 2026-06-13 — Project scaffolded

Scaffolded with `cleanvibe new` (cleanvibe v1.13.1). Future entries
land here as queue items get deleted.

## 2026-06-13 — Repo public, scope set, sources recorded, authors' repos vendored

- Pushed to a **public** GitHub repo:
  https://github.com/EmmaLeonhart/replicating-automatic-textbook-formalization
  (was a pre-existing private repo under the `EmmaLeonhart` account; flipped to
  public and wired up `origin`).
- **Scope decision (with the user):** the $100K / ~30K-agent / one-week case
  study cannot be re-run. Replication = verify the released artifacts against
  the headline numbers (130K Lean LOC, 5,900 declarations, 340/344 targets) +
  recompute the Appendix-A cost/caching model + `lake build` the formalization
  (user consented to the heavy build). Recorded in `notes/sources.md`.
- No inline reproduction recipe in the e-print `.tex`; the "recipe" is the two
  linked public repos, now added as pinned git submodules under
  `replication_target/`:
  - `repoprover` @ `386adba` — the multi-agent orchestration scaffold.
  - `algebraic-combinatorics` @ `b602231` — the resulting Lean code base.
- First independent corroboration already visible: the formalization repo's own
  `SUMMARY.md` reports 130,245 Lean LOC, 344 targets (340 proved + 4 exercises),
  ~5,900 declarations, 52 files — consistent with the paper's abstract.

## 2026-06-13 — Scale + cost reproduced, tests + CI green

Two of the three headline verifications now reproduce, with tests and CI.

- **Scale** (`src/verify_scale.py`, `results/scale.json`): independent count of
  the released Lean repo, reusing the authors' own declaration regex
  (`scripts/gen_growth_charts.py`). Reproduced **130,062 LOC** (reported ~130K),
  **5,884 declarations** (reported ~5,900), **344 targets across 45 chapters**
  (matches exactly). All three checks PASS. 52 Lean files; 16 `sorry`-word
  markers (repo's own SUMMARY notes 5 sorry *tactics*, all in exercise files).
- **Cost model** (`src/cost_model.py`, `results/cost.json`): recomputed the
  Appendix-A token-caching estimate from the paper's given inputs (C=83B input,
  561M output, T≈54.8) under Claude Opus 4.5 pricing ($5/M in, $25/M out). The
  caching multiplier R(54.8)=0.20753 is derived two independent ways (the
  paper's 0.05/3.05 closed form and a from-ratios derivation) and they agree.
  Reproduced **$14,025 output** (~$14K), **$429,025 no-cache** (~$430K),
  **$100,149 cached** (~$100K). All three checks PASS.
- `tests/` (10 tests, pytest) + `.github/workflows/ci.yml` (checks out
  submodules, runs tests + `scripts/run.py`, uploads `results/`). All green
  locally. `scripts/run.py` consolidates into `results/summary.json`
  (all_pass=True). `requirements.txt` pins pytest.
