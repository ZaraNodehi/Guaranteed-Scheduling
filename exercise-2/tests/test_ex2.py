"""Verification tests for Exercise 2 deliverables and invariants."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX2_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX2_DIR)

sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import report_kit as rk  # noqa: E402


def test_vendored_core_matches_canonical():
    with open(os.path.join(REPO_ROOT, "core", "gs_core.py"), "rb") as f:
        canon = f.read()
    with open(os.path.join(EX2_DIR, "code", "gs_core.py"), "rb") as f:
        vend = f.read()
    assert canon == vend


def test_experiments_json_invariants():
    path = os.path.join(EX2_DIR, "output", "experiments.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        d = json.load(f)

    # Regime A: GS & Stride match and dominate RR
    ra = d["regime_a_proportional"]["runs"]
    assert ra["gs_ratio_q1"]["max_abs_lag"] == ra["gs_vtime_q1"]["max_abs_lag"] == ra["stride_q1"]["max_abs_lag"]
    assert ra["gs_vtime_q1"]["max_abs_lag"] < ra["rr_q1"]["max_abs_lag"]

    # Regime B cases [E]+[M]
    rb = d["regime_b_constrained_cases"]
    assert rb["b1_dm_vs_rm"]["exhaustive"]["feasible"] is True
    assert rb["b1_dm_vs_rm"]["runs"]["dm"]["missed"] == 0
    assert rb["b1_dm_vs_rm"]["runs"]["rm"]["missed"] > 0

    assert rb["b2_edf_vs_dm_gs"]["exhaustive"]["feasible"] is True
    assert rb["b2_edf_vs_dm_gs"]["runs"]["edf"]["missed"] == 0
    assert rb["b2_edf_vs_dm_gs"]["runs"]["dm"]["missed"] > 0
    assert rb["b2_edf_vs_dm_gs"]["runs"]["gs_vtime"]["missed"] > 0

    assert rb["b3_u_under_1_infeasible"]["utilization"] < 1.0
    assert rb["b3_u_under_1_infeasible"]["exhaustive"]["feasible"] is False

    # Sweep + 30-set Exhaustive EDF Optimality
    sw = d["regime_b_sweep_120"]
    assert sw["total_sets"] == 120
    ex30 = sw["exhaustive_audit_30"]
    assert ex30["n_sets"] == 30
    assert ex30["edf_matches_exhaustive_100pct"] is True
    assert ex30["edf_feasible"] == ex30["exhaustive_feasible"]
    assert ex30["dm_feasible"] < ex30["edf_feasible"]

    # Regime C Overload
    rc = d["regime_c_overload"]
    assert rc["utilization"] > 1.0
    assert rc["runs_matched"]["rm"]["min_task_share_ratio"] == 0.0
    assert rc["runs_matched"]["gs_vtime"]["jain_fairness"] > rc["runs_matched"]["rm"]["jain_fairness"]
    assert rc["runs_asym"]["gs_vtime"]["jain_fairness"] > rc["runs_asym"]["rr"]["jain_fairness"]

    # Independent verifier audit
    assert d["independent_audit"]["all_zero_miss_verified_ok"] is True


def test_diagrams_and_reports():
    for name in [
        "fig_ex2_taxonomy.png",
        "fig_ex2_regime_a_proportional.png",
        "fig_ex2_constrained_gantt.png",
        "fig_ex2_constrained_sweep.png",
        "fig_ex2_overload_domino.png",
        "fig_ex2_tradeoff_profile.png",
        "fig_ex2_utilization_bounds.png",
        "fig_ex2_multidim_radar.png",
    ]:
        p = os.path.join(EX2_DIR, "diagrams", name)
        assert os.path.exists(p) and os.path.getsize(p) > 5000

    for lang in ("EN", "FA"):
        pdf_p = os.path.join(EX2_DIR, "docs", f"REPORT_{lang}.pdf")
        docx_p = os.path.join(EX2_DIR, "docs", f"REPORT_{lang}.docx")
        md_p = os.path.join(EX2_DIR, f"REPORT_{lang}.md")
        assert os.path.exists(pdf_p) and os.path.exists(docx_p) and os.path.exists(md_p)
        pages = rk.pdf_page_count(pdf_p)
        assert 40 <= pages <= 48, f"{pdf_p} has {pages} pages"
