"""Data loader for Exercise 1 reports (reads ONLY output/experiments.json)."""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
JSON_PATH = os.path.join(REPO, "exercise-1", "output", "experiments.json")
sys.path.insert(0, os.path.join(REPO, "core"))
import gs_core as gsc  # noqa: E402


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


def envelope_rows(d: dict) -> List[List[str]]:
    etc = d["exhaustive_tie_check"]
    rows = []
    for key, label in [("weighted_envelope", "Weighted [1,2,4] (work 4,6,9)"),
                       ("equal_envelope", "Equal [1,1,1] (work 6,6,6)")]:
        ev = etc[key]
        rows.append([
            label,
            str(ev["states"]),
            str(ev["leaves"]),
            fmt(ev["best_max_lag"], 4),
            fmt(ev["worst_max_lag"], 4),
            f"{ev['min_context_switches']} .. {ev['max_context_switches']}",
            str(ev["worst_turnaround"]),
        ])
    return rows


def gantt_rows(d: dict, run_key: str) -> List[List[str]]:
    gantt = d["baseline"]["runs"][run_key]["gantt"]
    rows = []
    for idx, (proc, s, e) in enumerate(gantt, start=1):
        rows.append([str(idx), proc, f"[{s}, {e})", str(e - s)])
    return rows


def dyn_timeline_rows(d: dict, start: int = 0, end: int = 28) -> List[List[str]]:
    r_tl = d["dynamic_arrival_check"]["dyn_t12_gs_ratio"]["timeline"]
    v_tl = d["dynamic_arrival_check"]["dyn_t12_gs_vtime"]["timeline"]
    rows = []
    for t in range(start, min(end, len(r_tl), len(v_tl))):
        r_run = r_tl[t][1] if isinstance(r_tl[t], (tuple, list)) else r_tl[t]
        v_run = v_tl[t][1] if isinstance(v_tl[t], (tuple, list)) else v_tl[t]
        rows.append([
            str(t),
            str(r_run),
            str(v_run),
            "Newcomer catch-up burst" if t >= 12 and r_run == "P2" and v_run != r_run else (
                "Pre-arrival solo P1" if t < 12 else "Fair balanced slice"
            ),
        ])
    return rows


def gs_source_snippet(start_line: int, end_line: int) -> List[str]:
    src = os.path.join(REPO, "GuaranteedScheduling.py")
    with open(src, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    out = []
    for ln in range(max(1, start_line), min(len(lines), end_line) + 1):
        out.append(f"{ln:3d} | {lines[ln - 1]}")
    return out


def sleeper_comparison_rows() -> List[List[str]]:
    procs = [
        gsc.Proc("Steady", 0, 25, weight=1),
        gsc.Proc("Sleeper", 0, 12, weight=1, sleep_at=((1, 20),)),
    ]
    rows = []
    for pol, cap, lbl in [
        ("gs_ratio", 1, "gs_ratio (used/w)"),
        ("gs_vtime", 1, "gs_vtime (uncapped V(t))"),
        ("gs_capped", 1, "gs_capped (cap=1 tick)"),
    ]:
        res = gsc.simulate_procs(procs, policy=pol, quantum=1, tie="stay", wakeup_cap=cap)
        st = res.per_proc["Steady"]
        sl = res.per_proc["Sleeper"]
        rows.append([
            lbl,
            str(st["max_starve_gap"]),
            str(st["finish"]),
            str(sl["finish"]),
            fmt(res.max_abs_lag, 4),
            fmt(res.jain_fairness, 4),
        ])
    return rows


def float_drift_rows() -> List[List[str]]:
    rows = []
    fl_sum = 0.0
    fr_sum = Fraction(0, 1)
    step_fl = 1.0 / 3.0
    step_fr = Fraction(1, 3)
    for k in range(1, 13):
        fl_sum += step_fl
        fr_sum += step_fr
        diff = fl_sum - float(fr_sum)
        rows.append([
            str(k),
            f"{fl_sum:.17g}",
            str(fr_sum),
            f"{diff:+.3e}",
            "Exact" if diff == 0.0 else "ULP Drift!",
        ])
    return rows


def sleeper_timeline_rows(start: int = 19, end: int = 37) -> List[List[str]]:
    procs = [
        gsc.Proc("Steady", 0, 25, weight=1),
        gsc.Proc("Sleeper", 0, 12, weight=1, sleep_at=((1, 20),)),
    ]
    v_res = gsc.simulate_procs(procs, policy="gs_vtime", quantum=1, tie="stay")
    c_res = gsc.simulate_procs(procs, policy="gs_capped", quantum=1, tie="stay", wakeup_cap=1)
    v_tl = v_res.timeline
    c_tl = c_res.timeline
    rows = []
    for t in range(start, min(end, len(v_tl), len(c_tl))):
        vr = v_tl[t][1] if isinstance(v_tl[t], (tuple, list)) else v_tl[t]
        cr = c_tl[t][1] if isinstance(c_tl[t], (tuple, list)) else c_tl[t]
        note = "Sleeper blocked (I/O)" if t == 20 else (
            "Uncapped monopolizes CPU" if vr == "Sleeper" and cr != vr else "Capped balanced alternation"
        )
        rows.append([str(t), str(vr), str(cr), note])
    return rows


def non_dyadic_trace_rows() -> List[List[str]]:
    procs = [
        gsc.Proc("P1", 0, 4, weight=1),
        gsc.Proc("P2", 0, 6, weight=3),
        gsc.Proc("P3", 0, 9, weight=6),
    ]
    res = gsc.simulate_procs(procs, policy="gs_ratio", quantum=1, tie="index")
    gps = gsc.ideal_gps_trace(procs, horizon=19)["entitled"]
    counts = {"P1": 0, "P2": 0, "P3": 0}
    rows = []
    for t in range(0, 12):
        chosen = res.timeline[t][1] if isinstance(res.timeline[t], (tuple, list)) else res.timeline[t]
        counts[chosen] += 1
        rows.append([
            str(t),
            chosen,
            f"{counts['P1']}/1 = {counts['P1']:.2f}",
            f"{counts['P2']}/3 = {counts['P2']/3:.3f}",
            f"{counts['P3']}/6 = {counts['P3']/6:.3f}",
            f"{float(gps[t + 1][2]):.3f}",
        ])
    return rows


def opt_source_snippet(start_line: int, end_line: int) -> List[str]:
    src = os.path.join(REPO, "benchmarks", "archive-studies", "ex6_heap_opt", "code", "gs_optimized.py")
    if not os.path.exists(src):
        return ["# Optimized heap module archived"]
    with open(src, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{ln:3d} | {lines[ln - 1]}" for ln in range(max(1, start_line), min(len(lines), end_line) + 1)]


def core_source_snippet(start_line: int, end_line: int) -> List[str]:
    src = os.path.join(REPO, "core", "gs_core.py")
    with open(src, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{ln:3d} | {lines[ln - 1]}" for ln in range(max(1, start_line), min(len(lines), end_line) + 1)]


def opt_scaling_rows() -> List[List[str]]:
    p = os.path.join(REPO, "benchmarks", "archive-studies", "ex6_heap_opt", "output", "experiments.json")
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        od = json.load(f)
    rows = []
    for r in od["bench1_complexity"]["rows"]:
        rows.append([
            str(r["n_procs"]),
            f"{r['linear_us_per_step']:.3f} us",
            f"{r['linear_p95_us']:.3f} us",
            f"{r['heap_us_per_step']:.3f} us",
            f"{r['heap_p95_us']:.3f} us",
            f"{r['speedup']:.2f}x",
        ])
    return rows


def q2_vs_rr_timeline_rows(d: dict) -> List[List[str]]:
    gs2_tl = d["baseline"]["runs"]["gs_ratio_q2"]["timeline"]
    rr2_tl = d["baseline"]["runs"]["rr_q2"]["timeline"]
    step = 2 if len(gs2_tl) >= 38 else 1
    n_ticks = len(gs2_tl) // step
    rows = []
    for t in range(n_ticks):
        g = gs2_tl[t * step][1] if isinstance(gs2_tl[t * step], (tuple, list)) else gs2_tl[t * step]
        r = rr2_tl[t * step][1] if isinstance(rr2_tl[t * step], (tuple, list)) else rr2_tl[t * step]
        rows.append([
            str(t),
            str(g),
            str(r),
            "Identical slice" if g == r else "Weighted GS vs Equal RR",
        ])
    return rows




