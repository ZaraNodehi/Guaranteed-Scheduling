"""Exercise 6 capstone tests: priority inheritance, GS, decks and philosophers."""
from __future__ import annotations
import json, os, sys
import fitz
from pptx import Presentation

EX6_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.join(EX6_DIR, "code")
OUT_JSON = os.path.join(EX6_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)
from integrated_kernel import simulate_priority_inversion, run_gs_rt_hybrid_audit  # noqa: E402
from dining_philosophers import (  # noqa: E402
    FairDiningTable, explore_fifo_model, naive_deadlock_witness, run_threaded_stress,
)


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


def test_dining_philosophers_deadlock_witness_and_fifo_model():
    naive = naive_deadlock_witness(5)
    assert naive["deadlocked"] and naive["all_forks_held"]
    assert naive["wait_for_cycle"] == [0, 1, 2, 3, 4, 0]
    result = explore_fifo_model(5)
    assert result["reachable_states"] > 100
    assert result["unsafe_states"] == 0
    assert result["deadlock_states"] == 0
    assert result["terminal_states"] > 0
    assert result["all_five_finish"]
    assert result["max_parallel_eaters"] == 2


def test_dining_philosophers_real_threads_finish_fairly():
    result = run_threaded_stress(count=5, rounds=4, meal_seconds=0.0002)
    assert result["passed"]
    assert result["completed_meals"] == 20
    assert result["completions_by_philosopher"] == [4] * 5
    assert result["safety_violations"] == 0
    assert result["admission_tickets_monotone"]
    assert result["threads_still_alive"] == []


def test_dining_philosophers_atomic_fork_reservation():
    table = FairDiningTable(5)
    ticket = table.acquire(0)
    snap = table.snapshot()
    assert snap["eating"] == [0]
    assert snap["fork_owner"][0] == 0 and snap["fork_owner"][1] == 0
    table.release(0)
    assert table.snapshot()["eating"] == []
    assert ticket == 0


def test_capstone_deliverables_and_decks():
    diag_dir = os.path.join(EX6_DIR, "diagrams")
    pngs = [f for f in os.listdir(diag_dir) if f.endswith(".png") and "rubric_flowchart" not in f]
    assert len(pngs) == 6
    dining_diagram = os.path.join(diag_dir, "fig_dining_philosophers_fifo.png")
    assert os.path.isfile(dining_diagram) and os.path.getsize(dining_diagram) > 10_000
    rubric_flow = os.path.join(diag_dir, "fig_exercise6_rubric_flowchart.png")
    assert os.path.isfile(rubric_flow) and os.path.getsize(rubric_flow) > 10_000
    for stem in ("REPORT_EN", "REPORT_FA"):
        pdf = os.path.join(EX6_DIR, "docs", f"{stem}.pdf")
        docx = os.path.join(EX6_DIR, "docs", f"{stem}.docx")
        md = os.path.join(EX6_DIR, f"{stem}.md")
        assert os.path.exists(pdf) and os.path.exists(docx) and os.path.exists(md)
        with fitz.open(pdf) as doc:
            assert len(doc) >= 10
    for ppt_name in ("PRESENTATION_EN.pptx", "PRESENTATION_FA.pptx"):
        prs = Presentation(os.path.join(EX6_DIR, "docs", ppt_name))
        assert len(prs.slides) == 11
        assert all(bool(s.notes_slide.notes_text_frame.text.strip()) for s in prs.slides)
    for sp_name in ("SPEAKER_SCRIPT_EN.md", "SPEAKER_SCRIPT_FA.md"):
        assert os.path.exists(os.path.join(EX6_DIR, "docs", sp_name))
    for lang in ("EN", "FA"):
        assert os.path.isfile(os.path.join(EX6_DIR, "docs", f"ARTICLE_{lang}.md"))
        article_pdf = os.path.join(EX6_DIR, "docs", f"ARTICLE_{lang}.pdf")
        article_docx = os.path.join(EX6_DIR, "docs", f"ARTICLE_{lang}.docx")
        assert os.path.isfile(article_pdf) and os.path.isfile(article_docx)
        with fitz.open(article_pdf) as article:
            assert len(article) >= 3
