"""Automated test suite for Exercise 6 (Capstone Scheduling + Synchronization + Decks)."""
from __future__ import annotations

import json
import os
import sys

import fitz
from pptx import Presentation

EX6_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.join(EX6_DIR, "code")
OUT_JSON = os.path.join(EX6_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)

from integrated_kernel import simulate_priority_inversion, run_gs_rt_hybrid_audit  # noqa: E402


def test_priority_inversion_and_pip_rescue():
    no_pip = simulate_priority_inversion("no_pip", horizon=60)
    pip = simulate_priority_inversion("pip", horizon=60)
    spin = simulate_priority_inversion("spin_hazard", horizon=60, spin_limit=10)

    assert no_pip["high_misses"] >= 1
    assert no_pip["high_blocked_ticks"] > pip["high_blocked_ticks"]
    assert pip["high_misses"] == 0
    assert pip["high_max_response_ticks"] <= 8
    assert spin["high_misses"] >= 2 and spin["spin_stall_ticks"] > 20


def test_gs_rt_hybrid_and_experiments_json():
    hyb = run_gs_rt_hybrid_audit()
    assert hyb["rm"]["misses"] == 1
    assert hyb["edf"]["misses"] == 0
    assert hyb["gs_vtime:stay"]["misses"] == 0
    assert hyb["gs_vtime:stay"]["jain_fairness"] > hyb["edf"]["jain_fairness"]

    with open(OUT_JSON, encoding="utf-8") as f:
        d = json.load(f)
    pipe = {f"{r['primitive']}_{r['policy']}": r for r in d["rt_rw_pipeline"]}
    assert pipe["Monitor_fair"]["rt_hit_rate_pct"] >= 95.0
    assert pipe["CoarseMutex_serial"]["rt_hit_rate_pct"] < pipe["Monitor_fair"]["rt_hit_rate_pct"]


def test_capstone_deliverables_and_decks():
    diag_dir = os.path.join(EX6_DIR, "diagrams")
    assert len([f for f in os.listdir(diag_dir) if f.endswith(".png")]) == 6

    for stem in ("REPORT_EN", "REPORT_FA"):
        pdf = os.path.join(EX6_DIR, "docs", f"{stem}.pdf")
        docx = os.path.join(EX6_DIR, "docs", f"{stem}.docx")
        md = os.path.join(EX6_DIR, f"{stem}.md")
        assert os.path.exists(pdf) and os.path.exists(docx) and os.path.exists(md)
        with fitz.open(pdf) as doc:
            assert len(doc) >= 10

    for ppt_name in ("PRESENTATION_EN.pptx", "PRESENTATION_FA.pptx"):
        prs = Presentation(os.path.join(EX6_DIR, "docs", ppt_name))
        assert len(prs.slides) == 10
        assert all(bool(s.notes_slide.notes_text_frame.text.strip()) for s in prs.slides)

    for sp_name in ("SPEAKER_SCRIPT_EN.md", "SPEAKER_SCRIPT_FA.md"):
        assert os.path.exists(os.path.join(EX6_DIR, "docs", sp_name))
