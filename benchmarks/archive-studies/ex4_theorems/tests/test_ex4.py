"""Pytest invariants for Exercise 4 formal proofs & exhaustive checks."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX4_DIR = os.path.dirname(HERE)
JSON_PATH = os.path.join(EX4_DIR, "output", "experiments.json")


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_theorem1_sfq_vs_wfq_bounds():
    d = _load()
    t1 = d["theorem1_lag_bounds"]
    assert t1["n_workloads"] == 120
    assert t1["violations_above_q"]["gs_vtime:index"] == 36
    assert t1["violations_above_q"]["gs_vtime:max_weight"] == 0
    assert t1["violations_above_q"]["wfq_finish"] == 0
    assert t1["wfq_behind_violations_above_q"] == 0
    for env in t1["exhaustive_tie_envelopes"]:
        assert not env["truncated"]
        assert abs(env["worst_max_lag"] - env["sfq_theoretical_bound"]) <= 1e-4 or env["worst_max_lag"] < env["sfq_theoretical_bound"]


def test_theorem2_omega_starvation_vs_constant():
    d = _load()
    rows = d["theorem2_starvation_scaling"]["scaling_rows"]
    assert len(rows) == 7
    for r in rows:
        assert r["gs_ratio_lag"] == r["theoretical_ratio_lag"]
        assert r["gs_ratio_gap"] == r["t_arrival"]
        assert r["gs_vtime_lag"] == 0.5
        assert r["gs_vtime_gap"] == 1


def test_theorem3_exhaustive_rt_and_theorem4_overload():
    d = _load()
    t3 = d["theorem3_exhaustive_rt"]
    assert t3["n_sets"] == 15
    assert t3["feasible_count"] == 10
    assert t3["independent_verified_count"] == 10
    assert t3["edf_100pct_matches_exhaustive"] is True

    u20 = d["theorem4_overload"]["sweep"][-1]["policies"]
    assert u20["rm"]["min_sr"] == 0.0
    assert u20["gs_vtime_eq"]["jain"] > 0.90
    assert u20["gs_vtime_eq"]["min_sr"] > 0.50


def test_reports_and_diagrams_exist():
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx"):
        p = os.path.join(EX4_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"
    diags = [f for f in os.listdir(os.path.join(EX4_DIR, "diagrams")) if f.endswith(".png")]
    assert len(diags) == 6
