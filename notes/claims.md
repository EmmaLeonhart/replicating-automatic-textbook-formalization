# Claims & References — load-bearing checks

What the paper's headline claims rest on, and whether the cited sources / released
artifacts actually support them. Verified during this replication (2026-06-13).

## Headline claims and how they are verified

| Claim (arXiv:2604.03071) | Source of truth | Status |
|---|---|---|
| 130K lines of Lean | released repo, counted | **Reproduced** — 130,062 LOC (`results/scale.json`) |
| 5,900 Lean declarations | released repo, counted | **Reproduced** — 5,884 (authors' own regex) |
| 340 targets formalized (of 344 designated; 4 → exercises) | `manifest.json` + `SUMMARY.md` | **Reproduced** — 344 targets / 45 chapters; SUMMARY: 340 proved, 4 exercise |
| ~$100K with caching / ~$430K without / ~$14K output | Appendix-A closed form | **Reproduced** — $100,149 / $429,025 / $14,025 (`results/cost.json`) |
| Formalization compiles | `lake build` | In progress (heavy build step) |
| One week, ~30K agents, 8 machines, 83B in / 561M out tokens | authors' run logs | **Not verifiable** — operational data from the run, not in any released artifact |

## Reference checks

### grinberg2025introduction — the formalized textbook (load-bearing)
- **arXiv:2506.00738**, "An Introduction to Algebraic Combinatorics", Darij Grinberg.
- Verified: **703 pages** (paper says "more than 500 pages" ✓), released under
  **CC0 1.0** i.e. effectively **public domain** (paper: "thanks to the author,
  is in the public domain" ✓), explicitly a **graduate course** textbook ✓,
  200+ exercises (consistent with the paper "focusing exclusively on
  formalization, not problem solving" and reclassifying 4 targets as exercises).
- The textbook LaTeX source is itself **vendored in the formalization repo**
  (`AlgebraicCombinatorics/tex/`, 47 `.tex` files), and `manifest.json` maps each
  target to its `source_path` in that tree — so the side-by-side claim is checkable.

### urban2026130klinesformaltopology — the single-agent precedent this paper scales up
- **arXiv:2601.03298**, "130k Lines of Formal Topology in Two Weeks: Simple and
  Cheap Autoformalization for Everyone?", Josef Urban.
- Verified: ~130k lines of formalized topology, ~two weeks, ~$100 in LLM costs —
  matches how 2604.03071 characterizes it (a cheap single-agent/CLI formalization
  of a topology textbook that this work scales up to multi-agent).
- **Nuance / minor mischaracterization:** 2604.03071 (§Method) describes Urban's
  work as a single CLI coding agent "using Claude Code" formalizing Munkres
  point-set topology. Urban's paper actually used a feedback loop with **ChatGPT
  (mostly 5.2) and Claude Sonnet 4.5** via their CLIs, and — importantly — the
  proof system was **Megalodon** (a higher-order set theory with a surreal-number
  library), **not Lean/mathlib**. The load-bearing point (a cheap ~130k-line
  single-agent textbook formalization exists, and this work scales it up to
  multi-agent on Lean) holds; the "Claude Code" / proof-system specifics are
  glossed. Not material to any reproduced number.

### The_mathlib_Community_2020 — mathlib scale context
- The paper cites mathlib at "roughly 2.2 million lines of code" as scale context
  for the size of the unformalized literature. This is background framing, not a
  reproduced number; consistent with publicly reported mathlib growth (order of
  millions of LOC by early 2026). Not load-bearing for any headline figure.

## What is explicitly out of scope (and why)

The experiment's *operational* figures — 30K agents, one week of wall-clock,
8 machines, 83B input / 561M output tokens, per-agent-type breakdowns — come from
the authors' private run logs. No released artifact lets an outside party
reproduce them; the cost model (Appendix A) is the only part of the cost analysis
that is self-contained, and it is reproduced exactly. See `notes/sources.md`.
