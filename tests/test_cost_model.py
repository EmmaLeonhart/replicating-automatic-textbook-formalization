"""Unit tests for the Appendix-A cost model reproduction."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cost_model as cm  # noqa: E402


def test_caching_multiplier_two_derivations_agree():
    """The closed-form 0.05/3.05 coefficients must match a derivation built
    straight from the pricing ratios, for a range of T."""
    for T in (10, 54.8, 100, 250):
        a = cm.caching_multiplier(T)
        b = cm.cache_multiplier_from_ratios(T, cm.C_IN, cm.C_STORE, cm.C_HIT)
        assert abs(a - b) < 1e-12


def test_caching_multiplier_at_paper_T():
    # Paper's avg T ~ 54.8 -> caching keeps ~20.75% of the no-cache input cost.
    assert abs(cm.caching_multiplier(54.8) - 0.20753) < 1e-4


def test_multiplier_below_one_for_long_dialogs():
    # Caching only helps once dialogs are long enough; at T=54.8 it must save.
    assert cm.caching_multiplier(54.8) < 1.0


def test_headline_dollar_figures_reproduce():
    r = cm.main()
    assert r["all_pass"] is True
    rep = r["reproduced"]
    # Within 5% of the paper's rounded headline figures.
    assert abs(rep["total_nocache_usd"] - 430_000) / 430_000 < 0.05
    assert abs(rep["total_cache_usd"] - 100_000) / 100_000 < 0.05
    assert abs(rep["output_usd"] - 14_000) / 14_000 < 0.05


def test_output_cost_from_opus_pricing():
    # 561e6 output tokens * $25/M = ~$14,025.
    assert abs(cm.C_OUT * cm.OUTPUT_TOKENS - 14_025) < 1.0
