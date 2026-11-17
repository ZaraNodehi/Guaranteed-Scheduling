"""Pytest capstone verification across Exercise 7 synthesis & repository completeness."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX7_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX7_DIR)
JSON_PATH = os.path.join(EX7_DIR, "output", "experiments.json")


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_cross_exercise_synthesis_and_live_os():
    d = _load()
    s = d["cross_exercise_summary"]
    assert s["ex1_os_all_ordered"] is True
    assert s["ex3_float_drift_tick"] == 18
    assert s["ex4_rt_edf_100pct"] is True
    assert s["ex5_mc_240_seeds"]["gs_vtime_stay_lag"] < 1.0
    assert s["ex6_speedup_n2000"] >= 40.0
    assert s["ex6_sleeper_80_burst"]["gs_capped"] == 1
    # Capstone live OS check [1, 2, 4] stays closely proportional
    assert d["live_capstone_os_demo"]["max_share_error"] <= 0.08


def test_six_regime_matrix_and_demo_script():
    d = _load()
    m = d["six_regime_matrix"]
    # gs_capped:stay simultaneously beats gs_ratio on R2 dynamic and R3 sleeper!
    assert m["R2_Dynamic_Latecomers"]["gs_capped:stay"]["max_abs_lag"] < m["R2_Dynamic_Latecomers"]["gs_ratio:index"]["max_abs_lag"]
    assert m["R3_Heavy_Sleeper_40"]["gs_capped:stay"]["max_starve_gap"] <= 4
    assert m["R3_Heavy_Sleeper_40"]["gs_ratio:index"]["max_starve_gap"] >= 20
    # Demo script exits cleanly in < 5s
    proc = subprocess.run([sys.executable, os.path.join(EX7_DIR, "code", "demo_all.py")],
                          capture_output=True, text=True, timeout=15, check=True)
    assert "[Demo 5 - Heap Speedup" in proc.stdout


def test_all_exercises_1_to_7_complete():
    d = _load()
    for row in d["repo_audit_ex1_to_6"]:
        assert all([row["has_json"], row["diagram_count"] >= 6, row["has_en_pdf"],
                    row["has_fa_pdf"], row["has_en_docx"], row["has_fa_docx"], row["has_readme"]])
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx"):
        p = os.path.join(EX7_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"
    diags = [f for f in os.listdir(os.path.join(EX7_DIR, "diagrams")) if f.endswith(".png")]
    assert len(diags) == 6
