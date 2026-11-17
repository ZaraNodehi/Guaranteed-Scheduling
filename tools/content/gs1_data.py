"""Data loader for Exercise 1 reports (reads ONLY output/experiments.json)."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
JSON_PATH = os.path.join(REPO, "exercise-1", "output", "experiments.json")


def load() -> Dict[str, Any]:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt(v: Any, nd: int = 4) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def baseline_policy_rows(d: dict) -> List[List[str]]:
    order = [
        ("gs_ratio_q1", "gs_ratio (q=1)"),
        ("gs_vtime_q1", "gs_vtime (q=1)"),
        ("stride_q1", "stride (q=1)"),
        ("gs_ratio_q2", "gs_ratio (q=2)"),
        ("rr_q2", "rr (q=2)"),
        ("fifo_q1", "fifo (q=1)"),
    ]
    rows = []
    runs = d["baseline"]["runs"]
    for key, label in order:
        r = runs[key]
        rows.append([
            label,
            str(r["quantum"]),
            fmt(r["max_abs_lag"], 4) + f" ({r['max_abs_lag_frac']})",
            fmt(r["rmse_lag"], 4),
            str(r["context_switches"]),
            str(r["preemptions"]),
            fmt(r["mean_turnaround"], 2),
            fmt(r["jain_fairness"], 4),
        ])
    return rows


def baseline_proc_rows(d: dict, run_key: str = "gs_ratio_q1") -> List[List[str]]:
    r = d["baseline"]["runs"][run_key]
    rows = []
    for name in ["P1", "P2", "P3"]:
        p = r["per_proc"][name]
        rows.append([
            name,
            str(p["weight"]),
            str(p["work"]),
            str(p["start"]),
            str(p["finish"]),
            str(p["turnaround"]),
            str(p["waiting"]),
            fmt(p["entitled_gps"], 2) + f" ({p['entitled_gps_frac']})",
            fmt(p["max_abs_lag"], 4),
        ])
    return rows


def trajectory_rows(d: dict, start: int = 0, end: int = 10) -> List[List[str]]:
    traj = d["baseline"]["trajectory_gs_ratio_q1"]
    rows = []
    for row in traj[start:end]:
        rows.append([
            str(row["t"]),
            f"{row['P1_actual']} / {row['P1_gps']:.2f} ({row['P1_lag']:+.2f})",
            f"{row['P2_actual']} / {row['P2_gps']:.2f} ({row['P2_lag']:+.2f})",
            f"{row['P3_actual']} / {row['P3_gps']:.2f} ({row['P3_lag']:+.2f})",
        ])
    return rows


def quantum_rows(d: dict) -> List[List[str]]:
    rows = []
    for r in d["quantum_sweep"]["rows"]:
        rows.append([
            r["policy"],
            str(r["quantum"]),
            fmt(r["max_abs_lag"], 4),
            fmt(r["rmse_lag"], 4),
            str(r["context_switches"]),
            str(r["preemptions"]),
            fmt(r["mean_turnaround"], 2),
            str(r["worst_turnaround"]),
            fmt(r["jain_fairness"], 4),
        ])
    return rows


def tie_rows(d: dict) -> List[List[str]]:
    sims = d["exhaustive_tie_check"]["equal_sim_by_tie"]
    rows = []
    for tie in ["index", "stay", "max_weight"]:
        r = sims[tie]
        rows.append([
            tie,
            fmt(r["max_abs_lag"], 4),
            str(r["context_switches"]),
            str(r["preemptions"]),
            fmt(r["jain_fairness"], 4),
        ])
    return rows


def dynamic_rows(d: dict) -> List[List[str]]:
    dyn = d["dynamic_arrival_check"]
    rows = []
    for pol, res in [("gs_ratio (used/w)", dyn["dyn_t12_gs_ratio"]),
                     ("gs_vtime (V(t))", dyn["dyn_t12_gs_vtime"])]:
        p1 = res["per_proc"]["P1"]
        p2 = res["per_proc"]["P2"]
        rows.append([
            pol,
            str(p1["max_starve_gap"]),
            str(p1["finish"]),
            str(p2["finish"]),
            fmt(res["max_abs_lag"], 4),
            fmt(res["jain_fairness"], 4),
        ])
    return rows


def os_trial_rows(d: dict) -> List[List[str]]:
    rows = []
    for idx, tr in enumerate(d["os_subprocess_benchmark"]["trials"], start=1):
        rt = tr["runtimes_sec"]
        cpu = tr["cpu_used_sec"]
        rows.append([
            f"#{idx}",
            fmt(rt["P1"], 4),
            fmt(rt["P2"], 4),
            fmt(rt["P3"], 4),
            f"{cpu['P1']:.2f} / {cpu['P2']:.2f} / {cpu['P3']:.2f}",
            str(tr["total_dispatches"]),
            ",".join(tr["finish_order"]),
        ])
    return rows


def os_vs_sim_rows(d: dict) -> List[List[str]]:
    osb = d["os_subprocess_benchmark"]
    rows = []
    for p, w in zip(["P1", "P2", "P3"], osb["weights"]):
        rows.append([
            f"{p} (w={w})",
            fmt(osb["per_proc_median_runtime_sec"][p], 4),
            fmt(osb["per_proc_iqr_runtime_sec"][p], 4),
            fmt(osb["os_normalized_runtime"][p], 4),
            str(osb["sim_equivalent_turnaround"][p]),
            fmt(osb["sim_normalized_turnaround"][p], 4),
        ])
    return rows
