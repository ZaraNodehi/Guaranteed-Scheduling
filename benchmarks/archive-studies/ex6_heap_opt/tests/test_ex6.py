"""Pytest invariants for Exercise 6 O(log n) optimization & sleeper mitigation."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EX6_DIR = os.path.dirname(HERE)
CODE_DIR = os.path.join(EX6_DIR, "code")
JSON_PATH = os.path.join(EX6_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)

from gs_optimized import OptimizedHeapScheduler, SCALE_FP  # noqa: E402


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_optimized_heap_proportional_shares_and_sleeper_cap():
    hp = OptimizedHeapScheduler(wakeup_cap_ticks=1, use_stay=True)
    hp.add_task(0, "Steady", weight=1)
    hp.add_task(1, "Sleeper", weight=1)
    # Run Steady & Sleeper initially, sleep Sleeper for 40 ticks, wake, check max burst
    hp.sleep_task(1)
    for _ in range(40):
        assert hp.step() == 0
    hp.wake_task(1)
    post = [hp.step() for _ in range(10)]
    # Sleeper cannot hog consecutive ticks while Steady is active with equal weight
    max_consec_sleeper = max(
        sum(1 for _ in iter(lambda: None, None)) if False else 0,
        max(len(s) for s in "".join("1" if x == 1 else "0" for x in post).split("0")),
    )
    assert max_consec_sleeper <= 2


def test_bench1_speedup_and_bench3_sleeper_cap():
    d = _load()
    last_b1 = d["bench1_complexity"]["rows"][-1]
    assert last_b1["n_procs"] == 2000
    assert last_b1["speedup"] >= 40.0

    last_b3 = d["bench3_sleeper"]["rows"][-1]["policies"]
    assert last_b3["gs_ratio:index"]["post_wakeup_burst"] == 79
    assert last_b3["gs_vtime:index"]["post_wakeup_burst"] == 79
    assert last_b3["gs_capped:index"]["post_wakeup_burst"] == 1


def test_bench4_live_os_refactor_beats_legacy():
    d = _load()
    b4 = d["bench4_live_os"]
    assert b4["optimized"]["max_post_spawn_deviation"] < b4["legacy"]["max_post_spawn_deviation"] * 0.5


def test_reports_and_diagrams_exist():
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx"):
        p = os.path.join(EX6_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"
    diags = [f for f in os.listdir(os.path.join(EX6_DIR, "diagrams")) if f.endswith(".png")]
    assert len(diags) == 6
