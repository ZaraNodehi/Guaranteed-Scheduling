"""Dynamic loader and table formatters for Exercise 6 optimization & refactoring reports."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-6", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def bench1_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["bench1_complexity"]["rows"]:
        rows.append([
            str(r["n_procs"]),
            f"{r['linear_us_per_step']:.3f} us",
            f"{r['linear_p95_us']:.3f} us",
            f"{r['heap_us_per_step']:.3f} us",
            f"{r['heap_p95_us']:.3f} us",
            f"{r['speedup']:.2f}x",
        ])
    return rows


def bench2_rows(d: Dict) -> List[List[str]]:
    rows = []
    for s in d["bench2_ablation"]["stages"]:
        rows.append([
            s["stage"],
            f"{s['mean_lag']:.4f}",
            f"{s['p95_lag']:.4f}",
            f"{s['mean_gap']:.2f}",
            f"{s['mean_switches']:.2f}",
            f"{s['mean_sleeper_burst']:.2f} / {s['max_sleeper_burst']}",
        ])
    return rows


def bench3_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["bench3_sleeper"]["rows"]:
        p = r["policies"]
        rows.append([
            str(r["sleep_ticks"]),
            f"{p['gs_ratio:index']['post_wakeup_burst']}t / {p['gs_ratio:index']['max_starve_gap']}t",
            f"{p['gs_vtime:index']['post_wakeup_burst']}t / {p['gs_vtime:index']['max_starve_gap']}t",
            f"{p['gs_entitled:index']['post_wakeup_burst']}t / {p['gs_entitled:index']['max_starve_gap']}t",
            f"{p['gs_capped:index']['post_wakeup_burst']}t / {p['gs_capped:index']['max_starve_gap']}t",
        ])
    return rows


def bench4_os_rows(d: Dict) -> List[List[str]]:
    leg = d["bench4_live_os"]["legacy"]
    opt = d["bench4_live_os"]["optimized"]
    rows = []
    for lbl, r in [("Legacy (dt=0.10s, unanchored used/w)", leg),
                   ("Refactored (dt=0.05s, V(t) + stay)", opt)]:
        sh = ", ".join(f"{s*100:.1f}%" for s in r["post_spawn_shares"])
        rows.append([
            lbl,
            f"{r['dt']:.2f} s",
            str(r["switches"]),
            sh,
            f"{r['max_post_spawn_deviation']*100:.2f}%",
        ])
    return rows
