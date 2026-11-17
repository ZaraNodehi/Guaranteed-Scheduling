"""Pytest invariants for Exercise 3 exact fractional verification."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX3_DIR = os.path.dirname(HERE)
CODE_DIR = os.path.join(EX3_DIR, "code")
JSON_PATH = os.path.join(EX3_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)

from gs_core import Proc, simulate_procs  # noqa: E402


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_w1_static_exact_hand_match():
    d = _load()
    w1 = d["workload1_static"]
    m = w1["hand_vs_program_matches"]
    assert m["index"] == m["total_ticks"] == 12
    assert m["stay"] == 12
    assert m["max_weight"] == 12
    assert w1["all_static_equiv"] is True


def test_w2_dynamic_exact_match_and_divergence():
    d = _load()
    w2 = d["workload2_dynamic"]
    assert w2["hand_vs_program_matches"] == {"gs_ratio": 18, "gs_entitled": 18, "gs_vtime": 18}
    assert w2["sim_runs"]["gs_ratio"]["max_abs_lag_frac"] == "29/10"
    assert w2["sim_runs"]["gs_vtime"]["max_abs_lag_frac"] == "7/10"
    assert w2["sim_runs"]["gs_ratio"]["max_starve_gap"] > w2["sim_runs"]["gs_vtime"]["max_starve_gap"]


def test_w3_ieee754_float_drift_present():
    d = _load()
    c0 = d["workload3_float_drift"]["cases"][0]
    assert c0["weights"] == [3, 6, 9]
    assert c0["diverged_ticks"] == 62
    assert c0["first_divergence_t"] == 18


def test_reports_and_diagrams_exist():
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx"):
        p = os.path.join(EX3_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"
    diags = [f for f in os.listdir(os.path.join(EX3_DIR, "diagrams")) if f.endswith(".png")]
    assert len(diags) == 6
