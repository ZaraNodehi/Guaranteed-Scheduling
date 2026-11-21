"""Verification suite for Exercise 3 (3-process EDF vs RM paper scheduling)."""
from __future__ import annotations

import json
import os
import sys

import fitz

EX3_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.join(EX3_DIR, "code")
OUT_JSON = os.path.join(EX3_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)

from gs_core import RTTask, simulate_rt  # noqa: E402
from run_experiments import indep_hand_trace_rt  # noqa: E402


def test_experiments_json_parity_and_invariants():
    assert os.path.exists(OUT_JSON)
    with open(OUT_JSON, encoding="utf-8") as f:
        d = json.load(f)

    sa, sb, sc = d["set_a"], d["set_b"], d["set_c"]
    assert sa["edf"]["missed_count"] == 0 and sa["rm"]["missed_count"] == 0
    assert len(sa["edf_vs_rm_diff_ticks"]) == 2
    assert [x["t"] for x in sa["edf_vs_rm_diff_ticks"]] == [4, 5]

    assert sb["edf"]["missed_count"] == 0
    assert sb["rm"]["missed_count"] == 1
    assert sb["rm"]["misses"][0] == {"tick": 8, "job": "P3#0", "deadline": 8}
    assert sb["rta_rm"][-1]["rta_feasible"] is False
    assert sb["rta_rm"][-1]["worst_R_i"] == 9

    assert sc["edf"]["missed_count"] == 5
    assert sc["rm"]["missed_count"] == 3
    assert all(r["feasible_at_L"] for r in sb["dbf_edf"])


def test_zero_shared_code_parity_live():
    tasks = [
        {"name": "P1", "period": 4, "wcet": 1, "deadline": 4},
        {"name": "P2", "period": 6, "wcet": 2, "deadline": 6},
        {"name": "P3", "period": 8, "wcet": 3, "deadline": 8},
    ]
    rt = [RTTask(t["name"], t["period"], t["wcet"], t["deadline"]) for t in tasks]
    for alg_name, gs_alg in [("EDF", "edf:index"), ("RM", "rm:index")]:
        h = indep_hand_trace_rt(tasks, alg_name, 24)
        g = simulate_rt(rt, gs_alg, 24)
        g_tl = [x[1] or "IDLE" for x in g["timeline"]]
        assert h["timeline"] == g_tl
        assert h["missed_count"] == g["missed"]


def test_bilingual_worked_answer_key_matches_reference_traces():
    for lang in ("EN", "FA"):
        key = os.path.join(EX3_DIR, f"WORKED_SOLUTION_{lang}.md")
        assert os.path.isfile(key)
        content = open(key, encoding="utf-8").read()
        assert "P3#0" in content
        assert "Set B" in content or "مجموعه B" in content
        assert "t=8" in content
    with open(OUT_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["set_a"]["edf"]["trace_rows"]) == 12
    assert len(data["set_b"]["rm"]["trace_rows"]) == 24
    assert data["set_b"]["rm"]["misses"][0]["tick"] == 8


def test_deliverables_worksheet_diagrams_and_reports():
    diag_dir = os.path.join(EX3_DIR, "diagrams")
    pngs = [f for f in os.listdir(diag_dir) if f.endswith(".png") and "rubric_flowchart" not in f]
    assert len(pngs) == 8
    rubric_flow = os.path.join(diag_dir, "fig_exercise3_rubric_flowchart.png")
    assert os.path.isfile(rubric_flow) and os.path.getsize(rubric_flow) > 10_000
    for p in pngs:
        assert os.path.getsize(os.path.join(diag_dir, p)) > 40_000

    ws_pdf = os.path.join(EX3_DIR, "WORKSHEET_PAPER_TEMPLATE.pdf")
    assert os.path.exists(ws_pdf)
    with fitz.open(ws_pdf) as doc:
        assert len(doc) == 2

    scan_dir = os.path.join(EX3_DIR, "handwritten_scan")
    assert os.path.exists(os.path.join(scan_dir, "README.md"))
    assert os.path.exists(os.path.join(scan_dir, "PAPER_WORKSHEET_P1.png"))
    assert os.path.exists(os.path.join(scan_dir, "PAPER_WORKSHEET_P2.png"))

    # Two complete hand-copy reference guides for the same required Sets A and B.
    guide_dir = os.path.join(EX3_DIR, "paper_copy_guides")
    for copy_no in (1, 2):
        guide_pdf = os.path.join(guide_dir, f"HAND_COPY_GUIDE_STUDENT_{copy_no}.pdf")
        assert os.path.isfile(guide_pdf)
        with fitz.open(guide_pdf) as guide:
            assert len(guide) == 3
            guide_text = "\\n".join(page.get_text() for page in guide)
            assert "SET A" in guide_text and "SET B" in guide_text
            assert "P3#0" in guide_text and "dbf(8)" in guide_text
        preview_dir = os.path.join(guide_dir, f"student_{copy_no}_png")
        for page_no in (1, 2, 3):
            preview = os.path.join(preview_dir, f"page_{page_no}.png")
            assert os.path.isfile(preview) and os.path.getsize(preview) > 20_000


    for stem in ("REPORT_EN", "REPORT_FA"):
        pdf = os.path.join(EX3_DIR, "docs", f"{stem}.pdf")
        docx = os.path.join(EX3_DIR, "docs", f"{stem}.docx")
        md = os.path.join(EX3_DIR, f"{stem}.md")
        assert os.path.exists(pdf) and os.path.exists(docx) and os.path.exists(md)
        with fitz.open(pdf) as doc:
            assert len(doc) >= 15
