# Sources & Reproduction Recipe

## Recipe finding

The arXiv e-print source (`replication_target/source/paper.tex`) contains **no
inline reproduction recipe** — no `SKILL.md`/`AGENTS.md`, no `run.sh`/`Makefile`
reproduce target, no Dockerfile, no replication zip. A grep for
`reproduc|replicat|skill|run.sh|makefile|dockerfile|.zip` over the source hits
only the rhetorical phrase "the *replication crisis* of mathematics" in the
introduction.

Instead, the paper links two open-source artifacts in its metadata block
(`paper.tex` lines 33–34):

| Artifact | Repo | Role |
|----------|------|------|
| Code | https://github.com/facebookresearch/repoprover | The multi-agent orchestration scaffold ("RepoProver") |
| Formalization | https://github.com/facebookresearch/algebraic-combinatorics | The resulting Lean code base (the experiment's output) |

Both are public. They are added to this repo as git submodules under
`replication_target/` and pinned to the commit that was current when this
replication ran.

## Why the experiment cannot be re-run

The headline result is a **case study**, not a benchmark: a single ~one-week run
of ~30K Claude 4.5 Opus agents across 8 machines, costing ~$100K in inference
(83B input tokens, 561M output tokens). Re-executing it is out of scope for a
replication — it requires the orchestration infrastructure, a Claude API budget
on the order of $100K, and a week of wall-clock time on a multi-machine cluster.

## Scope decided with the user (2026-06-13)

Because the experiment itself is not re-runnable, the replication verifies the
**released artifacts** against the paper's headline claims, plus rebuilds the one
self-contained quantitative model in the paper:

1. **Scale of the released formalization** — the paper claims **130K lines of
   Lean**, **5,900 declarations**, and **340 target theorems/definitions** all
   formalized. These are static properties of the `algebraic-combinatorics`
   repo and are directly countable.
2. **Appendix-A cost/caching model** — a closed-form estimate with all inputs
   given in the paper (N agents, avg T ≈ 54.8 turns, C = 83B input tokens,
   561M output tokens, pricing ratios c_store = 2 c_in, c_hit = c_in/10). The
   ~$100K total and ~$14K output figures are recomputed exactly.
3. **`lake build`** of the formalization to confirm it compiles (user
   consented to this heavier step). Requires installing `elan`/`lake`; the Lean
   toolchain is not currently present on this machine.

What this replication does **not** attempt: re-running the multi-agent
orchestration, reproducing the token counts (those come from the authors' run
logs), or re-deriving the per-agent-type breakdowns in the figures.
