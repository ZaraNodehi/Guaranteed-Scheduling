"""Pytest invariants for Exercise 6 O(log n) heap, 120-seed ablation, float drift & live OS validation."""
import json
import os
import sys

import pymupdf
from pptx import Presentation

HERE = os.path.dirname(os.path.abspath(__file__))
EX6_DIR = os.path.dirname(HERE)
CODE_DIR = os.path.join(EX6_DIR, "code")
JSON_PATH = os.path.join(EX6_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)

from gs_optimized import OptimizedHeapScheduler, SCALE_FP, SCALE_LCM  # noqa: E402


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_optimized_heap_proportional_shares_and_sleeper_cap():
    hp = OptimizedHeapScheduler(wakeup_cap_ticks=1, use_stay=True, scale_fp=SCALE_FP)
    hp.add_task(0, "Steady", weight=1)
    hp.add_task(1, "Sleeper", weight=1)
    hp.sleep_task(1)
    for _ in range(40):
        assert hp.step() == 0
    hp.wake_task(1)
    post = [hp.step() for _ in range(10)]
    max_consec_sleeper = max(len(s) for s in "".join("1" if x == 1 else "0" for x in post).split("0"))
    assert max_consec_sleeper <= 2
    assert SCALE_LCM % 7 == 0 and SCALE_LCM % 11 == 0


def test_bench1_speedup_and_churn():
    d = _load()
    rows = d["bench1_complexity"]["rows"]
    r2k = next(r for r in rows if r["n_procs"] == 2000)
    assert r2k["speedup"] >= 40.0
    assert rows[-1]["n_procs"] == 4000
    assert rows[-1]["speedup"] >= 100.0
    assert d["bench1_complexity"]["churn_rows"][-1]["churn_speedup"] >= 40.0


def test_bench2_ablation_and_bench3_sleeper():
    d = _load()
    b2 = d["bench2_ablation"]
    assert b2["n_workloads"] == 120
    assert len(b2["workloads_all"]) == 120
    assert b2["stages"][-1]["max_sleeper_burst"] < b2["stages"][0]["max_sleeper_burst"]

    last_b3 = d["bench3_sleeper"]["rows"][-1]["policies"]
    assert last_b3["gs_ratio:index"]["post_wakeup_burst"] == 159
    assert last_b3["gs_vtime:index"]["post_wakeup_burst"] == 159
    assert last_b3["gs_capped:index"]["post_wakeup_burst"] == 1


def test_bench5_zero_fp_drift_decimal_and_lcm():
    d = _load()
    b5 = d["bench5_fp_drift"]
    assert b5["decimal_weights_suite"]["total_float_divergences_100k"] > 10_000
    assert b5["decimal_weights_suite"]["total_fp_divergences_100k"] == 0
    assert b5["lcm_prime_suite"]["total_fp_divergences_100k"] == 0


def test_bench4_live_os_arrival_and_sleeper():
    d = _load()
    b4 = d["bench4_live_os"]
    assert b4["optimized"]["max_post_spawn_deviation"] < b4["legacy"]["max_post_spawn_deviation"] * 0.5
    assert b4["sleeper_uncapped"]["max_sleeper_burst_steps"] >= 10
    assert b4["sleeper_capped"]["post_wake_dev"] < 0.10


def test_8_diagrams_decks_and_40p_reports():
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx",
               "docs/DECK_EN.pptx", "docs/DECK_FA.pptx",
               "docs/SPEAKER_EN.md", "docs/SPEAKER_FA.md"):
        p = os.path.join(EX6_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"

    en_pdf = pymupdf.open(os.path.join(EX6_DIR, "docs", "REPORT_EN.pdf"))
    fa_pdf = pymupdf.open(os.path.join(EX6_DIR, "docs", "REPORT_FA.pdf"))
    assert len(en_pdf) >= 40, f"REPORT_EN.pdf only {len(en_pdf)} pages"
    assert len(fa_pdf) >= 40, f"REPORT_FA.pdf only {len(fa_pdf)} pages"

    for dk in ("DECK_EN.pptx", "DECK_FA.pptx"):
        prs = Presentation(os.path.join(EX6_DIR, "docs", dk))
        assert len(prs.slides) == 10
        assert all(bool(s.notes_slide.notes_text_frame.text.strip()) for s in prs.slides)

    diags = [f for f in os.listdir(os.path.join(EX6_DIR, "diagrams")) if f.endswith(".png")]
    assert len(diags) == 8
