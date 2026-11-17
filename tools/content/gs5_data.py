"""Dynamic loader and table formatters for Exercise 5 experimental reports."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-5", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def sweep_a_rows(d: Dict) -> List[List[str]]:
    ov = d["sweep_a_monte_carlo"]["overall"]
    order = ["gs_vtime:stay", "gs_vtime:index", "stride:index", "gs_entitled:index",
             "gs_ratio:index", "rr:index", "fifo:index"]
    rows = []
    for p in order:
        m = ov[p]
        rows.append([
            p,
            f"{m['lag']['mean']:.3f} +/- {m['lag']['ci95']:.3f}",
            f"{m['lag']['p95']:.2f} / {m['lag']['p99']:.2f}",
            f"{m['rmse']['mean']:.3f}",
            f"{m['gap']['mean']:.2f}",
            f"{m['sw']['mean']:.1f}",
            f"{m['ta']['mean']:.2f}",
            f"{m['jain']['mean']:.4f}",
        ])
    return rows


def sweep_a_byn_rows(d: Dict) -> List[List[str]]:
    byn = d["sweep_a_monte_carlo"]["by_n"]
    rows = []
    for p in ("gs_vtime:stay", "gs_vtime:index", "gs_entitled:index", "gs_ratio:index", "rr:index", "fifo:index"):
        rows.append([
            p,
            f"{byn['3'][p]['lag']['mean']:.3f} +/- {byn['3'][p]['lag']['ci95']:.3f}",
            f"{byn['5'][p]['lag']['mean']:.3f} +/- {byn['5'][p]['lag']['ci95']:.3f}",
            f"{byn['8'][p]['lag']['mean']:.3f} +/- {byn['8'][p]['lag']['ci95']:.3f}",
            f"{byn['8'][p]['gap']['mean']:.2f}",
            f"{byn['8'][p]['sw']['mean']:.1f}",
        ])
    return rows


def sweep_b_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_b_quantum_pareto"]["rows"]:
        p = r["policies"]
        rows.append([
            str(r["quantum"]),
            f"{p['gs_vtime:stay']['lag']['mean']:.3f} / {p['gs_vtime:stay']['switches']['mean']:.1f}",
            f"{p['gs_vtime:index']['lag']['mean']:.3f} / {p['gs_vtime:index']['switches']['mean']:.1f}",
            f"{p['gs_ratio:index']['lag']['mean']:.3f} / {p['gs_ratio:index']['switches']['mean']:.1f}",
            f"{p['rr:index']['lag']['mean']:.3f} / {p['rr:index']['switches']['mean']:.1f}",
            f"{p['gs_vtime:stay']['turnaround']['mean']:.2f}",
        ])
    return rows


def sweep_c_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_c_scaling"]["scaling_rows"]:
        rows.append([
            str(r["n_procs"]),
            f"{r['eq_vtime_lag']['mean']:.3f} +/- {r['eq_vtime_lag']['ci95']:.3f}",
            f"{r['eq_ratio_lag']['mean']:.3f} +/- {r['eq_ratio_lag']['ci95']:.3f}",
            f"{r['skew_vtime_lag']['mean']:.3f} +/- {r['skew_vtime_lag']['ci95']:.3f}",
            f"{r['skew_ratio_lag']['mean']:.3f} +/- {r['skew_ratio_lag']['ci95']:.3f}",
            f"{r['skew_vtime_gap']['mean']:.1f} vs {r['skew_ratio_gap']['mean']:.1f}",
        ])
    return rows


def sweep_d_os_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_d_os_intervals"]["interval_trials"]:
        sh = ", ".join(f"{s:.4f}" for s in r["actual_shares"])
        rows.append([
            f"{r['poll_dt_sec']:.2f} s",
            str(r["dispatches"]),
            str(r["controller_switches"]),
            f"{r['total_cpu_sec']:.3f} s",
            sh,
            f"{r['max_share_deviation']*100:.2f}%",
        ])
    return rows
