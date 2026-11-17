"""Exercise 6 experiments: Algorithmic optimization, O(log n) heap scaling, ablation & live OS refactor.

Produces ``exercise-6/output/experiments.json`` covering:
- Bench 1 [M]: Dispatch microbenchmark N in {50, 100, 250, 500, 1000, 2000} (2000 dispatches x 5 repeats)
  comparing LinearScanScheduler O(N) vs OptimizedHeapScheduler O(log N)
- Bench 2 [E]+[M]: Incremental refactoring ablation V0 -> V1 (+V(t)) -> V2 (+stay) -> V3 (+gs_capped)
  across 30 dynamic + sleeper workloads
- Bench 3 [E]+[M]: Adversarial sleeper-exploit scaling S in {5, 10, 20, 40, 80} comparing gs_ratio,
  uncapped gs_vtime, and gs_capped (measuring post-wakeup consecutive lockout ticks!)
- Bench 4 [D]: Live OS dynamic-arrival comparison (legacy dt=0.10s unanchored vs refactored dt=0.05s V(t)+stay)
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
EX6_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX6_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from gs_core import Proc, simulate_procs  # noqa: E402
from gs_optimized import (  # noqa: E402
    LinearScanScheduler,
    OptimizedHeapScheduler,
    run_live_os_comparison,
)


def run_bench1_complexity() -> Dict:
    """Compare O(N) LinearScanScheduler vs O(log N) OptimizedHeapScheduler across N = 50..2000."""
    ns = [50, 100, 250, 500, 1000, 2000]
    n_steps = 2000
    repeats = 5
    rows = []
    for n in ns:
        lin_us_list = []
        heap_us_list = []
        rng = random.Random(1000 + n)
        weights = [rng.randint(1, 8) for _ in range(n)]

        for _ in range(repeats):
            ls = LinearScanScheduler()
            for i, w in enumerate(weights):
                ls.add_task(i, f"T{i}", w)
            t0 = time.perf_counter()
            for _ in range(n_steps):
                ls.step()
            dt_lin = (time.perf_counter() - t0) * 1e6 / n_steps
            lin_us_list.append(dt_lin)

            hp = OptimizedHeapScheduler(use_stay=True)
            for i, w in enumerate(weights):
                hp.add_task(i, f"T{i}", w)
            t0 = time.perf_counter()
            for _ in range(n_steps):
                hp.step()
            dt_hp = (time.perf_counter() - t0) * 1e6 / n_steps
            heap_us_list.append(dt_hp)

        lin_med = statistics.median(lin_us_list)
        hp_med = statistics.median(heap_us_list)
        rows.append({
            "n_procs": n,
            "n_steps": n_steps,
            "linear_us_per_step": round(lin_med, 3),
            "linear_p95_us": round(max(lin_us_list), 3),
            "heap_us_per_step": round(hp_med, 3),
            "heap_p95_us": round(max(heap_us_list), 3),
            "speedup": round(lin_med / hp_med, 2),
        })
    return {"rows": rows}


def _post_wakeup_lockout(timeline, sleeper_name: str, steady_name: str) -> int:
    """Measure max consecutive ticks of sleeper while steady still has work left."""
    steady_indices = [i for i, (_, nm) in enumerate(timeline) if nm == steady_name]
    if not steady_indices:
        return 0
    last_steady_idx = steady_indices[-1]
    best = 0
    cur = 0
    for idx, (t, nm) in enumerate(timeline):
        if idx > last_steady_idx:
            break
        if t < 2:
            continue
        if nm == sleeper_name:
            cur += 1
            best = max(best, cur)
        elif nm == steady_name:
            cur = 0
    return best


def run_bench2_ablation() -> Dict:
    """Incremental engineering ablation V0->V1->V2->V3 across 30 mixed dynamic + sleeper workloads."""
    rng = random.Random(6060)
    workloads = []
    for s in range(30):
        # 4 processes: P1 anchor at t=0, P2 sleeper, P3 & P4 dynamic latecomers
        sleep_len = rng.randint(6, 18)
        workloads.append([
            Proc("P1", 0, 26, rng.randint(1, 4)),
            Proc("P2", 0, 14, rng.randint(1, 3), sleep_at=((1, sleep_len),)),
            Proc("P3", rng.randint(4, 12), rng.randint(8, 16), rng.randint(1, 4)),
            Proc("P4", rng.randint(6, 16), rng.randint(8, 16), rng.randint(1, 4)),
        ])

    stages = [
        ("V0_legacy_gs_ratio", "gs_ratio:index"),
        ("V1_vtime_anchor", "gs_vtime:index"),
        ("V2_vtime_stay", "gs_vtime:stay"),
        ("V3_capped_stay", "gs_capped:stay"),
    ]
    rows = []
    for label, pol in stages:
        lags, gaps, sws, bursts = [], [], [], []
        for ps in workloads:
            r = simulate_procs(ps, pol, quantum=1)
            lags.append(r.max_abs_lag)
            gaps.append(r.max_starve_gap)
            sws.append(r.context_switches)
            bursts.append(_post_wakeup_lockout(r.timeline, "P2", "P1"))
        rows.append({
            "stage": label,
            "policy": pol,
            "mean_lag": round(statistics.mean(lags), 4),
            "p95_lag": round(sorted(lags)[int(0.95 * len(lags))], 4),
            "mean_gap": round(statistics.mean(gaps), 3),
            "mean_switches": round(statistics.mean(sws), 2),
            "mean_sleeper_burst": round(statistics.mean(bursts), 3),
            "max_sleeper_burst": max(bursts),
        })
    return {"n_workloads": len(workloads), "stages": rows}


def run_bench3_sleeper_mitigation() -> Dict:
    """Adversarial sleeper scaling across sleep durations S in [5, 10, 20, 40, 80]."""
    sleeps = [5, 10, 20, 40, 80]
    rows = []
    for S in sleeps:
        ps = [
            Proc("Steady", 0, S + 30, 1),
            Proc("Sleeper", 0, max(20, S), 1, sleep_at=((1, S),)),
        ]
        pol_out = {}
        for pol in ("gs_ratio:index", "gs_vtime:index", "gs_entitled:index", "gs_capped:index"):
            r = simulate_procs(ps, pol, 1)
            burst = _post_wakeup_lockout(r.timeline, "Sleeper", "Steady")
            pol_out[pol] = {
                "post_wakeup_burst": burst,
                "max_starve_gap": r.max_starve_gap,
                "max_abs_lag": round(r.max_abs_lag, 4),
            }
        rows.append({"sleep_ticks": S, "policies": pol_out})
    return {"rows": rows}


def run_bench4_live_os_refactor() -> Dict:
    """Compare legacy unanchored dt=0.10s vs refactored V(t)+stay dt=0.05s on live Linux."""
    legacy = run_live_os_comparison(mode="legacy")
    optimized = run_live_os_comparison(mode="optimized")
    return {"legacy": legacy, "optimized": optimized}


def main() -> None:
    b1 = run_bench1_complexity()
    b2 = run_bench2_ablation()
    b3 = run_bench3_sleeper_mitigation()
    b4 = run_bench4_live_os_refactor()

    payload = {
        "exercise": 6,
        "title": "Algorithmic Optimization, O(log n) Heap Refactoring & Sleeper Mitigation",
        "bench1_complexity": b1,
        "bench2_ablation": b2,
        "bench3_sleeper": b3,
        "bench4_live_os": b4,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    print("B1 N=2000 speedup:", b1["rows"][-1])
    print("B2 ablation:", [(s["stage"], s["mean_lag"], s["mean_switches"], s["max_sleeper_burst"])
                         for s in b2["stages"]])
    print("B3 S=80:", b3["rows"][-1]["policies"])
    print("B4 OS:", b4)


if __name__ == "__main__":
    main()
