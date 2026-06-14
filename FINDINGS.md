# Findings — Replication of *Automatic Textbook Formalization*

**Paper:** Gloeckle, Rammal, Arnal, Munos, Cabannes, Synnaeve, Hayat.
*Automatic Textbook Formalization.* arXiv:2604.03071v1 (2026).
**Replication repo:** https://github.com/EmmaLeonhart/replicating-automatic-textbook-formalization

## What this paper is, and what "replication" can mean here

This is a **case study**, not a benchmark. The authors ran a multi-agent system
(~30K Claude 4.5 Opus agents over ~one week on 8 machines, ~$100K of inference)
that formalized a 700-page graduate algebraic-combinatorics textbook into Lean.
The full experiment **cannot be re-run** by a third party: it needs the
orchestration cluster, a ~$100K API budget, and a week of wall-clock time, and
its token counts come from the authors' private run logs.

So the replication target is not "re-run the experiment" but **"do the released
artifacts and the paper's self-contained model support the headline claims?"**
The authors released both their orchestration code
([`repoprover`](https://github.com/facebookresearch/repoprover)) and the
resulting Lean code base
([`algebraic-combinatorics`](https://github.com/facebookresearch/algebraic-combinatorics)),
both vendored here as pinned submodules. Three things are independently
checkable, and this replication checks all three.

## Reproduced vs reported

| Headline claim | Reported | Reproduced | Verdict |
|---|---:|---:|:--:|
| Lines of Lean code | ~130,000 | **130,062** | ✅ |
| Lean declarations | ~5,900 | **5,884** | ✅ |
| Designated targets (chapters) | 344 (45) | **344 (45)** | ✅ |
| Targets formalized / exercises | 340 / 4 | 340 / 4 (per repo `SUMMARY.md`) | ✅ |
| Cost, no caching | ~$430K | **$429,025** | ✅ |
| Cost, with caching | ~$100K | **$100,149** | ✅ |
| Output-token cost | ~$14K | **$14,025** | ✅ |
| Formalization compiles (`lake build`) | builds | builds (8078 jobs, Linux CI) | ✅ |

Numbers from `results/scale.json` and `results/cost.json`; regenerate with
`python scripts/run.py`.

### Scale (`src/verify_scale.py`)

Counted directly over the 52 `.lean` files of the released repo, **reusing the
authors' own declaration regex** (lifted verbatim from their
`scripts/gen_growth_charts.py`) so the methodology matches theirs rather than
inventing a new counting rule. LOC and declaration counts land within ~0.3% and
~0.3% of the paper's rounded figures; the target/chapter counts from
`manifest.json` match exactly (344 targets across 45 chapters). The repo's own
`SUMMARY.md` independently states 340 proved + 4 exercise, 5 `sorry` tactics
(all in exercise files).

### Cost / caching model (`src/cost_model.py`)

Appendix A is the one fully self-contained quantitative model in the paper: a
closed-form estimate of how prompt caching changes the input-token bill. Given
the paper's inputs (83B input tokens, 561M output tokens, average 54.8 turns per
dialog) and **Claude Opus 4.5 list pricing** ($5/M input, $25/M output) with the
paper's caching ratios (cache-write = 2×, cache-read = 0.1× the input price), the
model reproduces all three dollar figures to within rounding:

- caching multiplier R(54.8) = **0.20753** (caching keeps ~21% of the no-cache
  input bill) — derived two independent ways (the paper's 0.05/3.05 closed form
  and a from-scratch derivation off the pricing ratios) that agree to 1e-12;
- output $14,025, no-cache total $429,025, cached total $100,149.

### Build (`src/build_formalization.py`)

<!-- BUILD-STATUS -->
The user consented to the heavier step of compiling the formalization. We
installed `elan` and Lean `v4.28.0` (pinned by the repo's `lean-toolchain`),
fetched the Mathlib cache (`lake exe cache get`, 425 s) and ran
`lake build AlgebraicCombinatorics`.

**Local (Windows) build: blocked by a toolchain bug, not by the formalization.**
The build replayed **7,077 of 7,087** targets, then failed. Every one of the ~10
failing targets is a **Mathlib** module (`CategoryTheory.*`, `MeasureTheory.*`,
`AlgebraicTopology.*`, `Analysis.*`) — *none* is an `AlgebraicCombinatorics`
file. The error is `no such file or directory … .olean.server.hash` during the
cache *replay* step, a known Windows `lake` issue where the downloaded Mathlib
cache lacks the `.server.hash` sidecar files the replay expects. So the local
failure is in the Mathlib dependency materialization on Windows, not in the
released formalization. Full log: `results/build.json` / `results/build.log`.

**Linux build: SUCCESS.** A dedicated GitHub Actions job
(`.github/workflows/lean-build.yml`, `leanprover/lean-action`: elan + Mathlib
cache + `lake build AlgebraicCombinatorics`) compiles the formalization on Ubuntu,
where the Windows replay bug does not occur. The build reaches
**`Build completed successfully (8078 jobs)`** — all **52** `AlgebraicCombinatorics.*`
modules compile on top of Mathlib (~11.5 min wall-clock). A handful of modules
emit the expected "declaration uses `sorry`" warning, corresponding to the 5
`sorry` tactics the repo's `SUMMARY.md` documents as living only in
*exercise* files (exercises are out of scope — the paper formalizes statements,
it does not solve exercises); these are warnings, not errors, and the build
passes. So the released formalization genuinely compiles.

(Note: an earlier run of this workflow with `auto-config: false` and `build:
default` silently skipped the build step — it only fetched the Mathlib cache.
Setting `build: true` forces the actual `lake build`; that is the run reported
above.)

## References (`notes/claims.md`)

- The formalized textbook — Grinberg, *An Introduction to Algebraic
  Combinatorics* (arXiv:2506.00738) — checks out: **703 pages** (paper: ">500"),
  **CC0 / public domain** (paper: "in the public domain"), a graduate course
  text. Its LaTeX source is vendored inside the formalization repo, so the
  "side-by-side blueprint" claim is grounded in shipped files.
- The single-agent precedent (Urban, arXiv:2601.03298) does report ~130k lines of
  formal topology in ~two weeks for ~$100. One mischaracterization worth flagging:
  the paper calls it a "Claude Code" Lean formalization, but Urban's system used
  the **Megalodon** set-theory prover (not Lean/mathlib) with ChatGPT 5.2 / Claude
  Sonnet 4.5. This doesn't affect any reproduced number.

## What was NOT reproduced, and why

- **The experiment itself** — 30K agents, one week, 8 machines, the 83B/561M
  token totals, and all per-agent-type / per-outcome breakdowns (Figures 4–7,
  Tables 1–3). These are operational measurements from the authors' private run;
  no released artifact lets an outside party regenerate them. We take the token
  totals as *given inputs* to the cost model rather than reproducing them.
- **Semantic faithfulness of the formalization** — whether each Lean statement
  faithfully captures the textbook statement. The authors themselves flag this as
  spot-checked, not exhaustively verified, and it is a mathematical-review task
  beyond counting and compiling.

## Bottom line

Every headline *number* that a third party can check against the released
artifacts — 130K LOC, ~5,900 declarations, 344 targets, and the $100K/$430K/$14K
cost model — **reproduces**, and the released formalization **compiles** (8078
jobs, Linux CI). The parts that don't reproduce are the ones that
are structurally un-reproducible (a $100K one-week cluster run) or out of scope
(semantic faithfulness), not failures of the claims. The replication verdict is
recorded in `paper.json`.
