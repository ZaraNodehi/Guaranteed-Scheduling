"""Verification tests for Exercise 1 deliverables and reproducibility."""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX1_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX1_DIR)

sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import report_kit as rk  # noqa: E402


def test_vendored_core_matches_canonical():
    with open(os.path.join(REPO_ROOT, "core", "gs_core.py"), "rb") as f:
        canon = f.read()
    with open(os.path.join(EX1_DIR, "code", "gs_core.py"), "rb") as f:
        vend = f.read()
    assert canon == vend


def test_experiments_json_structure_and_invariants():
    path = os.path.join(EX1_DIR, "output", "experiments.json")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        d = json.load(f)

    # Baseline equivalence at simultaneous arrivals t = 0
    bp = d["baseline"]["runs"]
    assert bp["gs_ratio_q1"]["max_abs_lag"] == bp["gs_vtime_q1"]["max_abs_lag"] == bp["stride_q1"]["max_abs_lag"]
    assert bp["gs_ratio_q2"]["max_abs_lag"] < bp["rr_q2"]["max_abs_lag"]

    # Exhaustive tie-breaking invariants [E]
    etc = d["exhaustive_tie_check"]
    env_e = etc["equal_envelope"]
    assert env_e["truncated"] is False
    assert abs(env_e["best_max_lag"] - env_e["worst_max_lag"]) < 1e-12
    tc = etc["equal_sim_by_tie"]
    assert tc["stay"]["context_switches"] == env_e["min_context_switches"]
    assert tc["index"]["context_switches"] == env_e["max_context_switches"]

    # Dynamic arrival starvation discrepancy [E]+[D]
    da = d["dynamic_arrival_check"]
    assert da["starve_gs_ratio"]["violated"] is True
    assert da["starve_gs_vtime"]["violated"] is False
    assert da["starve_gs_entitled"]["violated"] is False
    assert da["dyn_t12_gs_ratio"]["per_proc"]["P1"]["max_starve_gap"] == 6
    assert da["dyn_t12_gs_vtime"]["per_proc"]["P1"]["max_starve_gap"] == 1

    # Real Linux OS subprocess benchmark [M]
    osb = d["os_subprocess_benchmark"]
    assert osb["num_trials"] == 5
    assert len(osb["trials"]) == 5
    assert osb["all_trials_ordered_p3_fastest"] is True
    assert osb["total_zero_cpu_slices"] == 0


def test_diagrams_present():
    expected = [
        "fig_ex1_architecture.png",
        "fig_ex1_flowchart.png",
        "fig_ex1_gantt_baseline.png",
        "fig_ex1_lag_trajectory.png",
        "fig_ex1_quantum_sweep.png",
        "fig_ex1_tie_envelope.png",
        "fig_ex1_latecomer_teaser.png",
        "fig_ex1_os_vs_sim.png",
    ]
    for name in expected:
        p = os.path.join(EX1_DIR, "diagrams", name)
        assert os.path.exists(p), f"Missing diagram: {p}"
        assert os.path.getsize(p) > 5000


def test_reports_page_count_and_no_overflow():
    for lang in ("EN", "FA"):
        pdf_p = os.path.join(EX1_DIR, "docs", f"REPORT_{lang}.pdf")
        docx_p = os.path.join(EX1_DIR, "docs", f"REPORT_{lang}.docx")
        md_p = os.path.join(EX1_DIR, f"REPORT_{lang}.md")
        assert os.path.exists(pdf_p)
        assert os.path.exists(docx_p)
        assert os.path.exists(md_p)
        pages = rk.pdf_page_count(pdf_p)
        assert 20 <= pages <= 40, f"{pdf_p} has {pages} pages"
