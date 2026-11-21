"""Exercise 7 validation suite."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pytest
import fitz
from pptx import Presentation
EX7=Path(__file__).resolve().parents[1]
OUT=EX7/"output"/"experiments.json"
sys.path.insert(0,str(EX7/"code"))
from dining_philosophers import (  # noqa: E402
    FairDiningTable, explore_fifo_model, fork_pair, naive_deadlock_witness,
    ordered_fork_pair, run_threaded_stress,
)


def test_deadlock_witness_contains_complete_cycle():
    witness=naive_deadlock_witness(5)
    assert witness["deadlocked"] is True
    assert witness["all_forks_held"] is True
    assert witness["wait_for_cycle"] == [0,1,2,3,4,0]
    assert all(witness["waiting_for_philosopher"][p] == (p+1)%5 for p in range(5))


def test_fifo_finite_state_model_checks_safety_and_progress():
    result=explore_fifo_model(5)
    assert result["reachable_states"] > 100
    assert result["transitions"] >= result["reachable_states"]-1
    assert result["unsafe_states"] == 0
    assert result["deadlock_states"] == 0
    assert result["terminal_states"] > 0
    assert result["all_five_finish"] is True
    assert result["max_parallel_eaters"] == 2


def test_monitor_atomically_owns_both_forks():
    table=FairDiningTable(5)
    ticket=table.acquire(2)
    snap=table.snapshot()
    left,right=fork_pair(2,5)
    assert snap["eating"] == [2]
    assert snap["fork_owner"][left] == 2
    assert snap["fork_owner"][right] == 2
    assert len([x for x in snap["fork_owner"] if x==2]) == 2
    table.release(2)
    assert table.snapshot()["eating"] == []
    assert table.snapshot()["fork_owner"] == [None]*5
    assert ticket == 0


def test_rejects_double_acquire_and_invalid_philosopher():
    table=FairDiningTable(5)
    table.acquire(0)
    with pytest.raises(RuntimeError):
        table.acquire(0)
    table.release(0)
    with pytest.raises(ValueError):
        table.acquire(5)
    with pytest.raises(ValueError):
        fork_pair(0,2)
    with pytest.raises(ValueError):
        ordered_fork_pair(6,5)


def test_resource_hierarchy_returns_global_order():
    for p in range(5):
        a,b=ordered_fork_pair(p,5)
        assert a < b
        assert set((a,b)) == set(fork_pair(p,5))


def test_real_threads_complete_without_adjacent_overlap():
    result=run_threaded_stress(count=5,rounds=4,meal_seconds=0.0002)
    assert result["passed"] is True
    assert result["completed_meals"] == 20
    assert result["completions_by_philosopher"] == [4]*5
    assert result["safety_violations"] == 0
    assert result["worker_errors"] == []
    assert result["threads_still_alive"] == []
    assert result["final_waiting"] == []
    assert result["final_eating"] == []
    assert result["final_fork_owner"] == [None]*5
    assert result["admission_tickets_monotone"] is True


def test_experiment_json_matches_live_and_model_checks():
    assert OUT.is_file()
    d=json.loads(OUT.read_text(encoding="utf-8"))
    assert d["exercise"] == "Exercise 7"
    assert d["naive_deadlock_witness"]["deadlocked"]
    assert d["fifo_model"]["unsafe_states"] == 0
    assert d["fifo_model"]["deadlock_states"] == 0
    assert d["thread_stress"]["completed_meals"] == 20
    assert d["thread_stress"]["passed"] is True
    assert d["gs_cpu_study"]["equal_weight"]["jain_fairness"] > .99
    equal=d["gs_cpu_study"]["equal_weight"]["per_proc"]
    assert [equal[f"P{i}"]["used"] for i in range(5)] == [20]*5
    weighted=d["gs_cpu_study"]["weighted"]["per_proc"]
    assert [weighted[f"P{i}"]["used"] for i in range(5)] == [10,10,20,20,40]


def test_exercise7_reports_figures_flowchart_and_deck():
    for stem in ("REPORT_EN","REPORT_FA"):
        pdf=EX7/"docs"/f"{stem}.pdf"
        assert pdf.is_file()
        assert (EX7/"docs"/f"{stem}.docx").is_file()
        assert (EX7/f"{stem}.md").is_file()
        with fitz.open(pdf) as doc:
            assert len(doc) > 40
    worksheet=EX7/"WORKSHEET_DINING_PHILOSOPHERS.pdf"
    assert worksheet.is_file()
    with fitz.open(worksheet) as doc:
        assert len(doc) == 2
    for name in [
        "fig_ex7_table_topology.png","fig_ex7_wait_for_cycle.png",
        "fig_ex7_gs_service_shares.png","fig_ex7_fifo_queue_timeline.png",
        "fig_ex7_state_space_audit.png","fig_ex7_deadlock_comparison.png",
        "fig_ex7_fifo_monitor.png","fig_ex7_invariants.png","fig_ex7_verification.png",
        "fig_ex7_fairness_metrics.png","fig_ex7_summary.png",
        "fig_exercise7_rubric_flowchart.png"
    ]:
        p=EX7/"diagrams"/name
        assert p.is_file() and p.stat().st_size > 10_000
    for lang in ("EN","FA"):
        assert (EX7/"docs"/f"ARTICLE_{lang}.md").is_file()
        article_pdf=EX7/"docs"/f"ARTICLE_{lang}.pdf"
        assert article_pdf.is_file()
        assert (EX7/"docs"/f"ARTICLE_{lang}.docx").is_file()
        with fitz.open(article_pdf) as doc:
            assert len(doc) >= 3
    for name in ("PRESENTATION_EN.pptx","PRESENTATION_FA.pptx"):
        prs=Presentation(EX7/"docs"/name)
        assert len(prs.slides)==7
        assert all(bool(s.notes_slide.notes_text_frame.text.strip()) for s in prs.slides)
    for name in ("SPEAKER_SCRIPT_EN.md","SPEAKER_SCRIPT_FA.md"):
        assert (EX7/"docs"/name).is_file()
    video=EX7/"media"/"dining_philosophers_demo.mp4"
    assert video.is_file() and video.stat().st_size > 20_000
    for name in ("PRESENTATION_EN.pptx","PRESENTATION_FA.pptx",
                 "SPEAKER_SCRIPT_EN.md","SPEAKER_SCRIPT_FA.md"):
        assert (EX7/"docs"/name).is_file()
