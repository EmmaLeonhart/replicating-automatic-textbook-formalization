# replicating-automatic-textbook-formalization - Work Queue

**This file is a queue of concrete, executable steps, not a state snapshot.**
Finished work lives in `devlog.md` (dated entries) and `git log`;
longer-horizon items live in `todo.md`. **When an item is done, delete it
from this file AND append a dated entry to `devlog.md` in the same commit,
then push.** No checkmarks, no status indicators in place.

---

## Active — Replicate "Automatic Textbook Formalization" (arXiv:2604.03071)

**Scope decided with the user (2026-06-13):** the full experiment ($100K, ~30K
agents, one week, 8 machines) cannot be re-run. The replication is therefore
**artifact-verification + a Lean build**:

- The two authors' repos are the "recipe": `facebookresearch/repoprover`
  (orchestration) and `facebookresearch/algebraic-combinatorics` (the resulting
  Lean formalization). Both are public.
- Headline numbers to verify against the released Lean repo: **130K lines of
  Lean, 5,900 declarations, 340 target theorems/definitions**.
- The Appendix-A cost/caching formula ($100K total, $14K output) is a closed
  form with given inputs (N agents, T≈54.8 turns, C=83B input, 561M output) —
  **recompute it exactly.**
- User consented to **`lake build`** the formalization to confirm it compiles.

Work top to bottom; delete each item in the same commit that completes it (and
append to `devlog.md`).

5. **Check load-bearing references** (Grinberg textbook is public domain;
   urban2026 single-agent 130k-topology precedent; mathlib ~2.2M LOC). Record
   in `notes/claims.md`. Commit.

6. **`lake build` the formalization** (user-consented heavy step). Capture
   pass/fail + build stats into `results/build.json`. If it can't finish
   locally / in CI, document why. Commit.

8. **Write `FINDINGS.md`** — reported vs reproduced table, what the artifacts
   covered vs. what could not be re-run (the experiment itself), divergences.
   Commit.

9. **Set `paper.json` `status`** (`replicated` if the released artifacts match
   the headline numbers and build; otherwise `insufficient-hardware`/`failed`
   with reasons). Confirm `pages.yml` + `package.yml` run green; repo public.
   Keep `SKILL.md` truthful. Stop / hand back.

---

## Pointers

- Methodology / definition of done: `SKILL.md`.
- Long-horizon items: `todo.md`.
- Completed work + replication milestones (chronological): `devlog.md`.
- Narrative history: `git log`.
