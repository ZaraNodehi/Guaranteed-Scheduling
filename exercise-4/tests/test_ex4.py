"""Pytest invariants for Exercise 4 formal proofs, EEVDF, exhaustive checks, 8 diagrams & 40+p bilingual reports."""
import json
import os

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
EX4_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX4_DIR)
JSON_PATH = os.path.join(EX4_DIR, "output", "experiments.json")


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_core_parity():
    root_core = os.path.join(REPO_ROOT, "core", "gs_core.py")
    vend_core = os.path.join(EX4_DIR, "code", "gs_core.py")
    assert open(root_core, encoding="utf-8").read() == open(vend_core, encoding="utf-8").read()


def test_theorem1_sfq_vs_pgps_and_eevdf():
    d = _load()
    t1 = d["theorem1_lag_bounds"]
    assert t1["n_workloads"] == 120
    assert len(t1["q1_40_cases"]) == 40
    assert len(t1["q2_40_cases"]) == 40
    assert len(t1["q3_40_cases"]) == 40

    assert t1["violations_above_q"]["gs_vtime:index"] == 36
    assert t1["violations_above_q"]["gs_vtime:max_weight"] == 0
    assert t1["violations_above_q"]["wfq_finish"] == 0
    assert t1["violations_above_q"]["eevdf"] == 0
    assert t1["wfq_behind_violations_above_q"] == 0

    assert abs(t1["max_lag_over_q"]["gs_vtime:index"] - 1.3125) < 1e-4
    assert abs(t1["max_lag_over_q"]["wfq_finish"] - 0.9375) < 1e-4
    assert abs(t1["max_lag_over_q"]["eevdf"] - 0.75) < 1e-4
    assert t1["max_lag_over_q"]["eevdf"] < t1["max_lag_over_q"]["wfq_finish"]

    assert len(t1["witness_1357"]["gs_vtime_index"]) == 32
    assert len(t1["witness_1234"]["gs_vtime_index"]) == 20
    assert len(t1["exhaustive_tie_envelopes"]) == 5
    for env in t1["exhaustive_tie_envelopes"]:
        assert not env["truncated"]
        assert abs(env["worst_max_lag"] - env["sfq_theoretical_bound"]) <= 1e-4 or env["worst_max_lag"] < env["sfq_theoretical_bound"]


def test_theorem2_omega_starvation_vs_constant():
    d = _load()
    t2 = d["theorem2_starvation_scaling"]
    rows = t2["scaling_rows"]
    assert len(rows) == 7
    for r in rows:
        assert r["gs_ratio_lag"] == r["theoretical_ratio_lag"]
        assert r["gs_ratio_gap"] == r["t_arrival"]
        assert r["gs_entitled_lag"] == 0.5
        assert r["gs_entitled_gap"] == 2
        assert r["gs_vtime_lag"] == 0.5
        assert r["gs_vtime_gap"] == 1
        assert r["eevdf_lag"] == 0.5
        assert r["eevdf_gap"] == 1

    w8 = t2["witness_t8_24t"]
    assert len(w8) == 24
    # Ticks 8..15 are strictly locked out to P2 under gs_ratio
    assert all(w8[t]["ratio_choice"] == "P2" for t in range(8, 16))
    assert w8[15]["ratio_lag"] == 4.0


def test_theorem3_exhaustive_rt_and_baruah():
    d = _load()
    t3 = d["theorem3_exhaustive_rt"]
    assert t3["n_sets"] == 15
    assert t3["feasible_count"] == 10
    assert t3["infeasible_count"] == 5
    assert t3["independent_verified_count"] == 10
    assert t3["edf_100pct_matches_exhaustive"] is True
    assert len(t3["f05_trace_12t"]) == 12
    assert len(t3["f07_trace_24t"]) == 23

    for s in t3["sets"]:
        assert s["exhaustive_wc_feasible"] == s["exhaustive_idle_feasible"]
        if s["exhaustive_wc_feasible"]:
            assert s["max_dbf_over_L"] <= 1.0 + 1e-6
            assert s["edf_missed"] == 0
        else:
            assert s["max_dbf_over_L"] > 1.0 - 1e-6


def test_theorem4_overload_equal_and_weighted():
    d = _load()
    sweep = d["theorem4_overload"]["sweep"]
    assert len(sweep) == 6
    for row in sweep:
        assert row["weighted_gs_vtime"]["jain"] > 0.97
        assert row["weighted_gs_vtime"]["min_sr"] >= 0.75
        if row["utilization"] >= 1.24:
            assert row["policies"]["rm"]["min_sr"] == 0.0
            assert row["weighted_rm"]["min_sr"] == 0.0
    u20 = sweep[-1]["policies"]
    assert u20["gs_vtime_eq"]["jain"] > 0.90
    assert u20["gs_vtime_eq"]["min_sr"] > 0.50


def test_8_diagrams_and_40p_bilingual_reports():
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx"):
        p = os.path.join(EX4_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"

    en_pdf = pymupdf.open(os.path.join(EX4_DIR, "docs", "REPORT_EN.pdf"))
    fa_pdf = pymupdf.open(os.path.join(EX4_DIR, "docs", "REPORT_FA.pdf"))
    assert len(en_pdf) >= 40, f"REPORT_EN.pdf only {len(en_pdf)} pages"
    assert len(fa_pdf) >= 40, f"REPORT_FA.pdf only {len(fa_pdf)} pages"

    diag_dir = os.path.join(EX4_DIR, "diagrams")
    diags = sorted(f for f in os.listdir(diag_dir) if f.endswith(".png"))
    assert len(diags) == 8, f"Expected 8 diagrams, found {diags}"
    for f in diags:
        assert os.path.getsize(os.path.join(diag_dir, f)) > 25_000
