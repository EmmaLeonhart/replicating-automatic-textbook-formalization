"""Reproduce the Appendix-A token-caching cost model of arXiv:2604.03071.

The paper reports the formalization consumed:
  - C   = 83e9   input tokens  (with double-counting across multi-turn dialogs)
  - O   = 561e6  output tokens
  - T   ~ 54.8   average turns per agent dialog
and concludes:
  - Without input caching:  ~$430K total
  - With input caching:     ~$100K total
  - Output cost (both):     ~$14K

Appendix A derives the caching saving in closed form. Caching affects only the
*input* price. With per-token prices c_in (input), c_store (KV-cache store),
c_hit (KV-cache hit), and the paper's pricing ratios

    c_store = 2 * c_in      (1-hour cache write)
    c_hit   = 0.1 * c_in    (cache read)

the input prices are

    P_nocache = c_in * C                        = N m c_in (0.5 T^2 + 0.5 T)
    P_cache   = c_hit*C + (c_in+c_store)*N*L     = N m c_in (0.05 T^2 + 3.05 T)

using C = N m T(T+1)/2 and L = T m. The N and m factors cancel in the ratio, so
the caching multiplier is a function of T alone:

    R(T) = P_cache / P_nocache = (0.05 T^2 + 3.05 T) / (0.5 T^2 + 0.5 T)

These figures are consistent with Claude Opus 4.5 pricing ($5 / M input tokens,
$25 / M output tokens), which we use to reconstruct the absolute dollar amounts.

Run:  python src/cost_model.py   (emits results/cost.json)
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS = REPO_ROOT / "results"

# ── Given inputs from the paper ──────────────────────────────────────────────
INPUT_TOKENS = 83e9          # C
OUTPUT_TOKENS = 561e6        # O
AVG_TURNS = 54.8             # T

# Claude Opus 4.5 list pricing (USD per token). Input $5/M, output $25/M.
C_IN = 5.0 / 1e6
C_OUT = 25.0 / 1e6
# Paper's caching pricing ratios.
C_STORE = 2.0 * C_IN
C_HIT = 0.1 * C_IN

# ── Reported headline figures ────────────────────────────────────────────────
REPORTED = {
    "total_nocache_usd": 430_000,
    "total_cache_usd": 100_000,
    "output_usd": 14_000,
}


def caching_multiplier(T: float) -> float:
    """R(T) = P_cache / P_nocache for input tokens (Appendix A)."""
    return (0.05 * T**2 + 3.05 * T) / (0.5 * T**2 + 0.5 * T)


def cache_multiplier_from_ratios(T: float, c_in: float, c_store: float,
                                 c_hit: float) -> float:
    """Same multiplier rebuilt directly from the pricing ratios, used to
    cross-check that the paper's 0.05/3.05 coefficients are correct.

    P_nocache = c_in * C,                C = N m T(T+1)/2
    P_cache   = c_hit*C + (c_in+c_store)*N*L,   L = T m
              = N m [ c_hit*T(T+1)/2 + (c_in+c_store)*T ]
    Dividing by P_nocache = N m c_in T(T+1)/2:
    """
    # numerator coefficients (per N m): c_hit*T(T+1)/2 + (c_in+c_store)*T
    p_cache = c_hit * T * (T + 1) / 2 + (c_in + c_store) * T
    p_nocache = c_in * T * (T + 1) / 2
    return p_cache / p_nocache


def main() -> dict:
    # Output cost (caching does not touch output).
    output_usd = C_OUT * OUTPUT_TOKENS

    # Input cost without caching.
    input_nocache_usd = C_IN * INPUT_TOKENS

    # Caching multiplier — two independent derivations must agree.
    R_paper = caching_multiplier(AVG_TURNS)
    R_ratios = cache_multiplier_from_ratios(AVG_TURNS, C_IN, C_STORE, C_HIT)
    assert abs(R_paper - R_ratios) < 1e-12, (R_paper, R_ratios)

    input_cache_usd = R_paper * input_nocache_usd

    total_nocache = input_nocache_usd + output_usd
    total_cache = input_cache_usd + output_usd

    reproduced = {
        "caching_multiplier_R": round(R_paper, 5),
        "output_usd": round(output_usd),
        "input_nocache_usd": round(input_nocache_usd),
        "input_cache_usd": round(input_cache_usd),
        "total_nocache_usd": round(total_nocache),
        "total_cache_usd": round(total_cache),
    }

    def close(a, b, tol=0.05):
        return abs(a - b) / b <= tol

    checks = {
        "total_nocache": close(total_nocache, REPORTED["total_nocache_usd"]),
        "total_cache": close(total_cache, REPORTED["total_cache_usd"]),
        "output": close(output_usd, REPORTED["output_usd"]),
    }

    result = {
        "inputs": {
            "input_tokens": INPUT_TOKENS,
            "output_tokens": OUTPUT_TOKENS,
            "avg_turns_T": AVG_TURNS,
            "price_input_per_M": C_IN * 1e6,
            "price_output_per_M": C_OUT * 1e6,
            "c_store_over_c_in": C_STORE / C_IN,
            "c_hit_over_c_in": C_HIT / C_IN,
        },
        "reported": REPORTED,
        "reproduced": reproduced,
        "checks": checks,
        "all_pass": all(checks.values()),
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "cost.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Caching multiplier R(T={AVG_TURNS}) = {R_paper:.5f}")
    print(f"Output cost:        ${output_usd:,.0f}   (reported ~${REPORTED['output_usd']:,})  "
          f"{'PASS' if checks['output'] else 'FAIL'}")
    print(f"Total (no cache):   ${total_nocache:,.0f}   (reported ~${REPORTED['total_nocache_usd']:,})  "
          f"{'PASS' if checks['total_nocache'] else 'FAIL'}")
    print(f"Total (cache):      ${total_cache:,.0f}   (reported ~${REPORTED['total_cache_usd']:,})  "
          f"{'PASS' if checks['total_cache'] else 'FAIL'}")
    print(f"ALL PASS: {result['all_pass']}")
    return result


if __name__ == "__main__":
    main()
