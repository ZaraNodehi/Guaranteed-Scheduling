"""Pytest invariants for Exercise 3 exact fractional verification."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX3_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX3_DIR)
CODE_DIR = os.path.join(EX3_DIR, "code")
JSON_PATH = os.path.join(EX3_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import report_kit as rk  # noqa: E402


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_vendored_core_matches_canonical():
    with open(os.path.join(REPO_ROOT, "core", "gs_core.py"), "rb") as f:
        canon = f.read()
    with open(os.path.join(CODE_DIR, "gs_core.py"), "rb") as f:
        vend = f.read()
    assert canon == vend


def test_w1_static_exact_hand_match():
    d = _load()
    w1 = d["workload1_static"]
    m = w1["hand_vs_program_matches"]
    assert m["index"] == m["total_ticks"] == 12
    assert m["stay"] == 12
    assert m["max_weight"] == 12
    assert w1["q2_stay_match"] == 12
    assert w1["q2_index_match"] == 12
    assert w1["q3_stay_match"] == 12
    assert w1["all_static_equiv"] is True


def test_w2_dynamic_exact_match_and_divergence():
    d = _load()
    w2 = d["workload2_dynamic"]
    assert w2["hand_vs_program_matches"] == {"gs_ratio": 18, "gs_entitled": 18, "gs_vtime": 18}
    assert w2["stride_hand_match"] == 18
    assert w2["sim_runs"]["gs_ratio"]["max_abs_lag_frac"] == "29/10"
    assert w2["sim_runs"]["gs_vtime"]["max_abs_lag_frac"] == "7/10"
    assert w2["sim_runs"]["gs_ratio"]["max_starve_gap"] > w2["sim_runs"]["gs_vtime"]["max_starve_gap"]


def test_w3_ieee754_float_drift_and_lcm_zero():
    d = _load()
    c0 = d["workload3_float_drift"]["cases"][0]
    assert c0["weights"] == [3, 6, 9]
    assert c0["diverged_ticks"] == 62
    assert c0["first_divergence_t"] == 18
    pm = d["workload3_float_drift"]["precision_comparison"]
    assert len(pm) == 5
    for entry in pm:
        assert entry["formats"]["lcm_stride"]["diverged_ticks"] == 0
        assert entry["formats"]["lcm_stride"]["max_service_dev_ticks"] == 0


def test_w4_asymmetric_audit():
    d = _load()
    w4 = d["workload4_asymmetric_audit"]
    assert w4["hand_match_vtime"] == 24
    assert w4["hand_match_ratio"] == 24
    assert w4["hand_match_entitled"] == 24
    assert w4["hand_match_stride"] == 24
    assert w4["sim_runs"]["gs_ratio:index_q1"]["max_starve_gap"] == 14
    assert w4["sim_runs"]["gs_vtime:index_q1"]["max_abs_lag"] < 1.0


def test_reports_and_diagrams_exist():
    expected_figs = [
        "fig_ex3_verification_pipeline.png",
        "fig_ex3_static_hand_gantt.png",
        "fig_ex3_static_lag_fractions.png",
        "fig_ex3_dynamic_divergence.png",
        "fig_ex3_dynamic_lag_curves.png",
        "fig_ex3_float_drift.png",
        "fig_ex3_precision_formats.png",
        "fig_ex3_quantum_w4_audit.png",
    ]
    for nm in expected_figs:
        p = os.path.join(EX3_DIR, "diagrams", nm)
        assert os.path.isfile(p) and os.path.getsize(p) > 5000, f"Missing {p}"

    for lang in ("EN", "FA"):
        pdf_p = os.path.join(EX3_DIR, "docs", f"REPORT_{lang}.pdf")
        docx_p = os.path.join(EX3_DIR, "docs", f"REPORT_{lang}.docx")
        md_p = os.path.join(EX3_DIR, f"REPORT_{lang}.md")
        assert os.path.isfile(pdf_p) and os.path.isfile(docx_p) and os.path.isfile(md_p)
        pages = rk.pdf_page_count(pdf_p)
        assert 40 <= pages <= 48, f"{pdf_p} has {pages} pages"
