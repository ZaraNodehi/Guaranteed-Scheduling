"""Pytest capstone verification across Exercise 7 synthesis, EEVDF prototype, 7 regimes & repo audit."""
import json
import os
import subprocess
import sys

import pymupdf

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
    assert s["ex6_speedup_n4000"] >= 120.0
    assert s["ex6_float64_div_100k"] > 0
    assert s["ex6_sleeper_max_burst"]["gs_capped"] == 1
    os_demo = d["live_capstone_os_demo"]
    assert os_demo["max_share_error"] <= 0.08
    assert len(os_demo["trace"]) >= 15


def test_seven_regime_matrix_and_demo_script():
    d = _load()
    m = d["six_regime_matrix"]
    assert "R7_Combined_Stress" in m
    assert m["R2_Dynamic_Latecomers"]["gs_capped:stay"]["max_abs_lag"] < m["R2_Dynamic_Latecomers"]["gs_ratio:index"]["max_abs_lag"]
    assert m["R3_Heavy_Sleeper_40"]["gs_capped:stay"]["max_starve_gap"] <= 4
    assert m["R3_Heavy_Sleeper_40"]["gs_ratio:index"]["max_starve_gap"] >= 20
    assert m["R7_Combined_Stress"]["gs_capped:stay"]["max_abs_lag"] < m["R7_Combined_Stress"]["gs_ratio:index"]["max_abs_lag"]
    proc = subprocess.run([sys.executable, os.path.join(EX7_DIR, "code", "demo_all.py")],
                          capture_output=True, text=True, timeout=15, check=True)
    assert "[Demo 5 - Heap Speedup" in proc.stdout
    assert "[Demo 6 - SCALE_LCM Prime Weights]" in proc.stdout
    assert "[Demo 7 - EEVDF Prototype]" in proc.stdout


def test_eevdf_prototype_and_stoica_bound():
    d = _load()
    ev = d["eevdf_prototype"]
    assert len(ev["seed_rows_40"]) == 40
    assert ev["eevdf_beats_gs_var_count"] >= 30
    assert ev["summary"]["eevdf"]["max_lag"] <= 4.0
    assert ev["summary"]["eevdf"]["mean_lag"] < ev["summary"]["gs_capped_var"]["mean_lag"]
    ct = ev["canonical_trace"]
    assert ct["eevdf"]["max_abs_lag"] < ct["gs_capped_var"]["max_abs_lag"]


def test_all_exercises_1_to_7_complete_and_40plus_pages():
    d = _load()
    for row in d["repo_audit_ex1_to_6"]:
        assert all([row["has_json"], row["diagram_count"] >= 8, row["has_en_pdf"],
                    row["has_fa_pdf"], row["has_en_docx"], row["has_fa_docx"], row["has_readme"],
                    row["en_pages"] >= 40, row["fa_pages"] >= 40])
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx",
               "docs/DECK_EN.pptx", "docs/DECK_FA.pptx",
               "docs/SPEAKER_EN.md", "docs/SPEAKER_FA.md"):
        p = os.path.join(EX7_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"
    diags = [f for f in os.listdir(os.path.join(EX7_DIR, "diagrams")) if f.endswith(".png")]
    assert len(diags) == 8
    for pdf in ("docs/REPORT_EN.pdf", "docs/REPORT_FA.pdf"):
        with pymupdf.open(os.path.join(EX7_DIR, pdf)) as doc:
            assert len(doc) >= 40, f"{pdf} has only {len(doc)} pages"


def test_core_parity_with_canonical():
    with open(os.path.join(REPO_ROOT, "core", "gs_core.py"), "rb") as f1, \
         open(os.path.join(EX7_DIR, "code", "gs_core.py"), "rb") as f2:
        assert f1.read() == f2.read()
