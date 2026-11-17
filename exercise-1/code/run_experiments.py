#!/usr/bin/env python3
"""Exercise 1 experiments: Introduction to Guaranteed Scheduling.

Produces ``exercise-1/output/experiments.json`` from deterministic integer-time
simulations, exact Fluid GPS baselines, exhaustive tie-envelope verification,
and repeated real-OS subprocess benchmarks implementing the exact ``psutil``
control loop of ``GuaranteedScheduling.py``.
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
from fractions import Fraction
from typing import List

import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
EX_ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from gs_core import (  # noqa: E402
    Proc,
    exhaustive_tie_envelope,
    find_starvation_witness,
    gantt_rows,
    ideal_gps_trace,
    simulate_procs,
)


def _cpu_burn_script(iters: int) -> str:
    return (
        "x = 1\n"
        f"for i in range({iters}):\n"
        "    x = (x * 1664525 + 1013904223) & 0xFFFFFFFF\n"
    )


def run_real_os_trial(weights: List[int], iters: int = 2_800_000,
                      quantum_sec: float = 0.03) -> dict:
    """Run one controlled trial using the exact logic of GuaranteedScheduling.py."""
    procs = []
    for i, w in enumerate(weights):
        procs.append({
            "name": f"P{i + 1}",
            "weight": w,
            "used": 0.0,
            "start": 0.0,
            "runtime": 0.0,
            "dispatches": 0,
            "zero_cpu_slices": 0,
            "process": None,
            "monitor": None,
            "finished": False,
        })

    try:
        for p in procs:
            p["start"] = time.perf_counter()
            p["process"] = subprocess.Popen(
                [sys.executable, "-c", _cpu_burn_script(iters)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            p["monitor"] = psutil.Process(p["process"].pid)
            p["monitor"].suspend()

        t_wall0 = time.perf_counter()
        while any(not p["finished"] for p in procs):
            avail = [p for p in procs if not p["finished"]]
            if not avail:
                break
            cur = min(avail, key=lambda p: p["used"] / p["weight"])
            proc = cur["process"]
            mon = cur["monitor"]
            cur["dispatches"] += 1
            try:
                before = mon.cpu_times()
                mon.resume()
                try:
                    proc.wait(timeout=quantum_sec)
                    cur["finished"] = True
                    cur["runtime"] = time.perf_counter() - cur["start"]
                    # Final cpu_times may be unavailable after exit; add quantum bound if 0
                    try:
                        after = mon.cpu_times()
                        delta = (after.user + after.system) - (before.user + before.system)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        delta = 0.0
                    cur["used"] += max(0.0, delta)
                except subprocess.TimeoutExpired:
                    mon.suspend()
                    after = mon.cpu_times()
                    delta = (after.user + after.system) - (before.user + before.system)
                    if delta <= 0.0:
                        cur["zero_cpu_slices"] += 1
                    cur["used"] += max(0.0, delta)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cur["finished"] = True
                cur["runtime"] = time.perf_counter() - cur["start"]
        total_wall = time.perf_counter() - t_wall0
    finally:
        for p in procs:
            pr = p["process"]
            if pr is not None and pr.poll() is None:
                try:
                    p["monitor"].resume()
                    pr.terminate()
                    pr.wait(timeout=2)
                except Exception:
                    pass

    # Compute realized runtime shares (with identical work, ideal priority ratio
    # gives faster turnaround to higher-weight processes: runtime_i ~ 1/w_i during overlap)
    total_cpu = sum(p["used"] for p in procs)
    zero_slices = sum(p["zero_cpu_slices"] for p in procs)
    total_dispatches = sum(p["dispatches"] for p in procs)
    runtimes = {p["name"]: round(p["runtime"], 4) for p in procs}
    cpus = {p["name"]: round(p["used"], 4) for p in procs}
    # Turnaround ratios relative to highest-weight process P3
    return {
        "total_wall_sec": round(total_wall, 4),
        "total_cpu_sec": round(total_cpu, 4),
        "total_dispatches": total_dispatches,
        "zero_cpu_slices": zero_slices,
        "runtimes_sec": runtimes,
        "cpu_used_sec": cpus,
        "dispatches_per_proc": {p["name"]: p["dispatches"] for p in procs},
        "finish_order": [p["name"] for p in sorted(procs, key=lambda x: x["runtime"])],
    }


def main() -> int:
    # ------------------------------------------------------------------
    # 1. Baseline static weighted workload (for exact step-by-step & Gantt)
    # ------------------------------------------------------------------
    baseline_procs = [
        Proc("P1", arrival=0, work=4, weight=1),
        Proc("P2", arrival=0, work=6, weight=2),
        Proc("P3", arrival=0, work=9, weight=3),
    ]
    gps_base = ideal_gps_trace(baseline_procs)
    baseline_runs = {}
    for pol, q in [("gs_ratio", 1), ("gs_ratio", 2), ("gs_vtime", 1),
                   ("stride", 1), ("rr", 2), ("fifo", 1)]:
        key = f"{pol}_q{q}"
        r = simulate_procs(baseline_procs, policy=pol, quantum=q, tie="index")
        d = r.as_dict(keep_timeline=True)
        d["gantt"] = [[n, s, e] for n, s, e in gantt_rows(r.timeline)]
        baseline_runs[key] = d

    # Tick-by-tick trajectory of cumulative A_i(t) vs E_i^GPS(t) for gs_ratio q=1
    r_base_q1 = simulate_procs(baseline_procs, policy="gs_ratio", quantum=1, tie="index")
    cum = {p.name: 0 for p in baseline_procs}
    trajectory = []
    for t in range(r_base_q1.horizon + 1):
        row = {"t": t}
        for idx, p in enumerate(baseline_procs):
            e_val = float(gps_base["entitled"][t][idx])
            row[f"{p.name}_actual"] = cum[p.name]
            row[f"{p.name}_gps"] = round(e_val, 4)
            row[f"{p.name}_lag"] = round(cum[p.name] - e_val, 4)
        trajectory.append(row)
        if t < r_base_q1.horizon:
            ran = r_base_q1.timeline[t][1]
            if ran is not None:
                cum[ran] += 1

    # ------------------------------------------------------------------
    # 2. Quantum size sweep (q in {1, 2, 4, 8, 16})
    # ------------------------------------------------------------------
    sweep_procs = [
        Proc("P1", arrival=0, work=16, weight=1),
        Proc("P2", arrival=0, work=24, weight=2),
        Proc("P3", arrival=0, work=32, weight=4),
        Proc("P4", arrival=0, work=24, weight=3),
    ]
    quantum_sweep = []
    for q in [1, 2, 4, 8, 16]:
        for pol in ["gs_ratio", "gs_vtime", "rr"]:
            r = simulate_procs(sweep_procs, policy=pol, quantum=q, tie="index")
            quantum_sweep.append({
                "policy": pol,
                "quantum": q,
                "max_abs_lag": round(r.max_abs_lag, 4),
                "max_abs_lag_frac": r.max_abs_lag_frac,
                "rmse_lag": round(r.rmse_lag, 4),
                "context_switches": r.context_switches,
                "preemptions": r.preemptions,
                "jain_fairness": round(r.jain_fairness, 6),
                "mean_turnaround": round(r.mean_turnaround or 0.0, 4),
                "worst_turnaround": r.worst_turnaround,
                "min_share_ratio": round(r.min_share_ratio, 4),
            })

    # ------------------------------------------------------------------
    # 3. Exhaustive tie-breaking verification [E]
    # ------------------------------------------------------------------
    env_weighted = exhaustive_tie_envelope(baseline_procs, policy="gs_ratio", quantum=1)
    equal_procs = [Proc("Q1", 0, 4, 2), Proc("Q2", 0, 4, 2), Proc("Q3", 0, 4, 2)]
    env_equal = exhaustive_tie_envelope(equal_procs, policy="gs_ratio", quantum=1)
    tie_sim_equal = {}
    for tie in ["index", "stay", "max_weight"]:
        r = simulate_procs(equal_procs, policy="gs_ratio", quantum=1, tie=tie)
        tie_sim_equal[tie] = {
            "max_abs_lag": round(r.max_abs_lag, 4),
            "context_switches": r.context_switches,
            "preemptions": r.preemptions,
            "jain_fairness": round(r.jain_fairness, 6),
        }

    # ------------------------------------------------------------------
    # 4. Dynamic arrival starvation check [E] (gs_ratio vs gs_vtime)
    # ------------------------------------------------------------------
    starve_ratio = find_starvation_witness("gs_ratio", max_arrival=20, min_gap_threshold=8)
    starve_vtime = find_starvation_witness("gs_vtime", max_arrival=20, min_gap_threshold=8)
    starve_entitled = find_starvation_witness("gs_entitled", max_arrival=20, min_gap_threshold=8)
    # Detailed comparison at t_arr = 12
    dyn_procs = [Proc("P1", arrival=0, work=28, weight=2),
                 Proc("P2", arrival=12, work=16, weight=1)]
    dyn_ratio = simulate_procs(dyn_procs, policy="gs_ratio", quantum=1)
    dyn_vtime = simulate_procs(dyn_procs, policy="gs_vtime", quantum=1)

    # ------------------------------------------------------------------
    # 5. Real OS subprocess experiment [M] vs Deterministic Sim [D]
    # ------------------------------------------------------------------
    os_weights = [1, 2, 4]
    trials = [run_real_os_trial(os_weights, iters=2_500_000, quantum_sec=0.03)
              for _ in range(5)]
    # Deterministic integer-time equivalent with equal work=6 quanta per process
    sim_eq_procs = [Proc("P1", 0, 6, 1), Proc("P2", 0, 6, 2), Proc("P3", 0, 6, 4)]
    sim_eq = simulate_procs(sim_eq_procs, policy="gs_ratio", quantum=1)

    med_rt = {
        f"P{i+1}": round(statistics.median(t["runtimes_sec"][f"P{i+1}"] for t in trials), 4)
        for i in range(3)
    }
    p1_med = med_rt["P1"] or 1.0
    sim_p1 = sim_eq.per_proc["P1"]["turnaround"] or 1

    os_summary = {
        "weights": os_weights,
        "quantum_sec": 0.03,
        "iters_per_proc": 2_500_000,
        "num_trials": len(trials),
        "trials": trials,
        "median_wall_sec": round(statistics.median(t["total_wall_sec"] for t in trials), 4),
        "median_dispatches": int(statistics.median(t["total_dispatches"] for t in trials)),
        "total_zero_cpu_slices": sum(t["zero_cpu_slices"] for t in trials),
        "per_proc_median_runtime_sec": med_rt,
        "per_proc_iqr_runtime_sec": {
            f"P{i+1}": round(
                (sorted(t["runtimes_sec"][f"P{i+1}"] for t in trials)[3]
                 - sorted(t["runtimes_sec"][f"P{i+1}"] for t in trials)[1]), 4
            )
            for i in range(3)
        },
        "os_normalized_runtime": {k: round(v / p1_med, 4) for k, v in med_rt.items()},
        "sim_equivalent_turnaround": {
            k: v["turnaround"] for k, v in sim_eq.per_proc.items()
        },
        "sim_normalized_turnaround": {
            k: round(v["turnaround"] / sim_p1, 4) for k, v in sim_eq.per_proc.items()
        },
        "sim_equivalent_max_lag": round(sim_eq.max_abs_lag, 4),
        "all_trials_ordered_p3_fastest": all(
            t["runtimes_sec"]["P3"] <= t["runtimes_sec"]["P2"] <= t["runtimes_sec"]["P1"]
            for t in trials
        ),
    }

    payload = {
        "exercise": 1,
        "title": "Introduction to Guaranteed Scheduling",
        "baseline": {
            "procs": [p.__dict__ for p in baseline_procs],
            "horizon": r_base_q1.horizon,
            "gps_finish_times": {
                baseline_procs[i].name: float(ft) if ft is not None else None
                for i, ft in enumerate(gps_base["finish_times"])
            },
            "runs": baseline_runs,
            "trajectory_gs_ratio_q1": trajectory,
        },
        "quantum_sweep": {
            "procs": [p.__dict__ for p in sweep_procs],
            "rows": quantum_sweep,
        },
        "exhaustive_tie_check": {
            "weighted_envelope": {k: v for k, v in env_weighted.items() if k != "worst_witness"},
            "equal_envelope": {k: v for k, v in env_equal.items() if k != "worst_witness"},
            "equal_sim_by_tie": tie_sim_equal,
        },
        "dynamic_arrival_check": {
            "starve_gs_ratio": starve_ratio,
            "starve_gs_vtime": starve_vtime,
            "starve_gs_entitled": starve_entitled,
            "dyn_t12_gs_ratio": dyn_ratio.as_dict(keep_timeline=True),
            "dyn_t12_gs_vtime": dyn_vtime.as_dict(keep_timeline=True),
        },
        "os_subprocess_benchmark": os_summary,
    }

    out_path = os.path.join(EX_ROOT, "output", "experiments.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
