"""Dynamic loader and table formatters for Exercise 2 reports (zero hardcoded numbers)."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-2", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def regime_a_rows(d: Dict) -> List[List[str]]:
    runs = d["regime_a_proportional"]["runs"]
    order = [
        ("gs_ratio_q1", "gs_ratio", "1"),
        ("gs_vtime_q1", "gs_vtime", "1"),
        ("gs_entitled_q1", "gs_entitled", "1"),
        ("stride_q1", "stride", "1"),
        ("rr_q1", "rr", "1"),
        ("gs_ratio_q2", "gs_ratio", "2"),
        ("rr_q2", "rr", "2"),
        ("fifo_q1", "fifo", "1"),
    ]
    rows = []
    for key, pol, q in order:
        r = runs[key]
        rows.append([
            pol,
            q,
            f"{r['max_abs_lag']:.4f} ({r['max_abs_lag_frac']})",
            f"{r['rmse_lag']:.4f}",
            str(r["context_switches"]),
            str(r["preemptions"]),
            f"{r['mean_turnaround']:.2f}",
            f"{r['jain_fairness']:.4f}",
        ])
    return rows


def rt_case_rows(case: Dict) -> List[List[str]]:
    runs = case["runs"]
    order = [
        ("edf", "EDF"),
        ("dm", "DM"),
        ("rm", "RM"),
        ("gs_vtime", "gs_vtime (base w)"),
        ("gs_vtime_density", "gs_vtime (w~C/D)"),
        ("gs_ratio", "gs_ratio"),
        ("stride", "stride"),
        ("rr", "rr (q=1)"),
    ]
    rows = []
    for key, label in order:
        r = runs[key]
        wr = str(r["worst_response"]) if r["worst_response"] is not None else "-"
        jt = str(r["jitter"]) if r["jitter"] is not None else "-"
        ver = "PASS" if r["independent_verify_ok"] else "MISS"
        rows.append([
            label,
            f"{r['missed']}/{r['released']}",
            f"{100.0 * r['miss_rate']:.1f}%",
            wr,
            jt,
            str(r["context_switches"]),
            f"{r['jain_fairness']:.4f}",
            ver,
        ])
    return rows


def sweep_success_rows(d: Dict) -> List[List[str]]:
    rows = []
    for b in d["regime_b_sweep_120"]["bands"]:
        sp = b["success_pct"]
        rows.append([
            b["band"],
            f"{b['mean_u']:.3f}",
            f"{sp['edf']:.1f}%",
            f"{sp['dm']:.1f}%",
            f"{sp['rm']:.1f}%",
            f"{sp['gs_vtime_density']:.1f}%",
            f"{sp['gs_vtime']:.1f}%",
            f"{sp['stride']:.1f}%",
            f"{sp['rr']:.1f}%",
        ])
    return rows


def sweep_jitter_rows(d: Dict) -> List[List[str]]:
    rows = []
    for b in d["regime_b_sweep_120"]["bands"]:
        jt = b["mean_jitter"]
        mr = b["mean_miss_rate_pct"]
        rows.append([
            b["band"],
            f"{mr['edf']:.1f}% / {jt['edf']:.2f}",
            f"{mr['dm']:.1f}% / {jt['dm']:.2f}",
            f"{mr['rm']:.1f}% / {jt['rm']:.2f}",
            f"{mr['gs_vtime_density']:.1f}% / {jt['gs_vtime_density']:.2f}",
            f"{mr['gs_vtime']:.1f}% / {jt['gs_vtime']:.2f}",
            f"{mr['rr']:.1f}% / {jt['rr']:.2f}",
        ])
    return rows


def overload_rows(d: Dict, mode: str = "runs_asym") -> List[List[str]]:
    runs = d["regime_c_overload"][mode]
    order = ["gs_vtime", "stride", "edf", "rr", "gs_ratio", "dm", "rm"]
    rows = []
    for pol in order:
        r = runs[pol]
        tu = r["task_used"]
        rows.append([
            pol,
            f"{r['missed']}/{r['released']}",
            f"{r['jain_fairness']:.4f}",
            f"{r['min_task_share_ratio']:.4f}",
            f"{tu['T1']} / {tu['T2']} / {tu['T3']}",
            str(r["context_switches"]),
        ])
    return rows
