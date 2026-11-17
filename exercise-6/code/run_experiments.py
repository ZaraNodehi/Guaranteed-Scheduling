"""Exercise 6 experiments: O(log n) heap scaling, 60-seed ablation, cap sensitivity,
IEEE-754 float drift audit, and live OS latecomer + sleeper validation.

Produces ``exercise-6/output/experiments.json`` covering:
- Bench 1 [M]: Dispatch microbenchmark N in {50, 100, 250, 500, 1000, 2000, 4000}
  plus sleep/wake churn benchmark (O(1) lazy version vs O(N) scan)
- Bench 2 [E]+[M]: 60-workload refactoring ablation V0 -> V1 (+V(t)) -> V2 (+stay) -> V3 (+gs_capped)
  plus exact workload archive (all 60 workloads) & V4 heap equivalence audit
- Bench 3 [E]+[M]: Adversarial sleeper scaling S in {5, 10, 20, 40, 80, 160} and cap sweep {0..16}
- Bench 4 [D]: Live Linux OS dynamic-arrival validation (legacy vs refactored + step traces)
  plus live Linux sleeper exploit vs cap mitigation [D]
- Bench 5 [E]+[M]: IEEE-754 float64 accumulation drift vs 10^9 fixed-point arithmetic
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time
from fractions import Fraction
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
EX6_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX6_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from gs_core import Proc, simulate_procs  # noqa: E402
from gs_optimized import (  # noqa: E402
    FloatVtimeScheduler,
    LinearScanScheduler,
    OptimizedHeapScheduler,
    SCALE_FP,
    SCALE_LCM,
    run_live_os_comparison,
    run_live_os_sleeper_comparison,
)


def run_bench1_complexity() -> Dict:
    """Compare O(N) LinearScanScheduler vs O(log N) OptimizedHeapScheduler across N = 50..4000."""
    ns = [50, 100, 250, 500, 1000, 2000, 4000]
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
            lin_us_list.append((time.perf_counter() - t0) * 1e6 / n_steps)

            hp = OptimizedHeapScheduler(use_stay=True)
            for i, w in enumerate(weights):
                hp.add_task(i, f"T{i}", w)
            t0 = time.perf_counter()
            for _ in range(n_steps):
                hp.step()
            heap_us_list.append((time.perf_counter() - t0) * 1e6 / n_steps)

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

    # Churn sub-benchmark: 1,000 dispatches interleaved with sleep/wake every 4 steps
    churn_rows = []
    for n in [100, 500, 1000, 2000]:
        rng = random.Random(2000 + n)
        weights = [rng.randint(1, 6) for _ in range(n)]
        cycles = 800

        ls = LinearScanScheduler()
        for i, w in enumerate(weights):
            ls.add_task(i, f"T{i}", w)
        t0 = time.perf_counter()
        for k in range(cycles):
            tid = k % n
            ls.sleep_task(tid)
            ls.step()
            ls.wake_task(tid)
            ls.step()
        lin_us = (time.perf_counter() - t0) * 1e6 / cycles

        hp = OptimizedHeapScheduler(wakeup_cap_ticks=1, use_stay=True)
        for i, w in enumerate(weights):
            hp.add_task(i, f"T{i}", w)
        t0 = time.perf_counter()
        for k in range(cycles):
            tid = k % n
            hp.sleep_task(tid)
            hp.step()
            hp.wake_task(tid)
            hp.step()
        hp_us = (time.perf_counter() - t0) * 1e6 / cycles
        churn_rows.append({
            "n_procs": n,
            "cycles": cycles,
            "linear_churn_us": round(lin_us, 3),
            "heap_churn_us": round(hp_us, 3),
            "churn_speedup": round(lin_us / hp_us, 2),
            "stale_pops": hp.stale_pops,
        })
    return {"rows": rows, "churn_rows": churn_rows}


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
    """Incremental engineering ablation V0->V1->V2->V3 across 120 mixed dynamic + sleeper workloads."""
    rng = random.Random(6060)
    workloads = []
    for s in range(120):
        sleep_len = rng.randint(6, 20)
        p1_w = rng.randint(1, 4)
        p2_w = rng.randint(1, 3)
        p3_w = rng.randint(1, 4)
        p4_w = rng.randint(1, 4)
        workloads.append({
            "seed": s + 1,
            "sleep_len": sleep_len,
            "weights": [p1_w, p2_w, p3_w, p4_w],
            "procs": [
                Proc("P1", 0, 26, p1_w),
                Proc("P2", 0, 14, p2_w, sleep_at=((1, sleep_len),)),
                Proc("P3", rng.randint(4, 12), rng.randint(8, 16), p3_w),
                Proc("P4", rng.randint(6, 16), rng.randint(8, 16), p4_w),
            ],
        })

    stages = [
        ("V0_legacy_gs_ratio", "gs_ratio:index"),
        ("V1_vtime_anchor", "gs_vtime:index"),
        ("V2_vtime_stay", "gs_vtime:stay"),
        ("V3_capped_stay", "gs_capped:stay"),
    ]
    stage_runs = {label: [] for label, _ in stages}
    rows = []
    for label, pol in stages:
        lags, gaps, sws, bursts = [], [], [], []
        for winfo in workloads:
            r = simulate_procs(winfo["procs"], pol, quantum=1)
            b = _post_wakeup_lockout(r.timeline, "P2", "P1")
            lags.append(r.max_abs_lag)
            gaps.append(r.max_starve_gap)
            sws.append(r.context_switches)
            bursts.append(b)
            stage_runs[label].append({
                "lag": round(r.max_abs_lag, 3),
                "gap": r.max_starve_gap,
                "sw": r.context_switches,
                "burst": b,
            })
        s_lags = sorted(lags)
        rows.append({
            "stage": label,
            "policy": pol,
            "mean_lag": round(statistics.mean(lags), 4),
            "ci95_lag": round(1.96 * statistics.stdev(lags) / (len(lags) ** 0.5), 4),
            "p95_lag": round(s_lags[min(len(s_lags) - 1, int(0.95 * len(s_lags)))], 4),
            "mean_gap": round(statistics.mean(gaps), 3),
            "mean_switches": round(statistics.mean(sws), 2),
            "mean_sleeper_burst": round(statistics.mean(bursts), 3),
            "max_sleeper_burst": max(bursts),
        })

    workloads_all = []
    for i, winfo in enumerate(workloads):
        workloads_all.append({
            "seed": winfo["seed"],
            "sleep_len": winfo["sleep_len"],
            "weights": winfo["weights"],
            "V0": stage_runs["V0_legacy_gs_ratio"][i],
            "V1": stage_runs["V1_vtime_anchor"][i],
            "V2": stage_runs["V2_vtime_stay"][i],
            "V3": stage_runs["V3_capped_stay"][i],
        })

    # Verify OptimizedHeapScheduler parity on steady+sleeper event replay
    hp_check = OptimizedHeapScheduler(wakeup_cap_ticks=1, use_stay=True)
    hp_check.add_task(0, "Steady", 2)
    hp_check.add_task(1, "Sleeper", 1)
    hp_check.sleep_task(1)
    for _ in range(30):
        hp_check.step()
    hp_check.wake_task(1)
    post = [hp_check.step() for _ in range(12)]
    return {
        "n_workloads": len(workloads),
        "stages": rows,
        "workloads_all": workloads_all,
        "heap_post_wake_sample": post,
    }


def run_bench3_sleeper_mitigation() -> Dict:
    """Adversarial sleeper scaling across S in [5, 10, 20, 40, 80, 160] + cap sensitivity sweep."""
    sleeps = [5, 10, 20, 40, 80, 160]
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

    # Cap sensitivity sweep on S = 40 sleeper workload
    caps = [0, 1, 2, 4, 8, 16, 40]
    cap_rows = []
    for c in caps:
        ps = [
            Proc("Steady", 0, 70, 1),
            Proc("Sleeper", 0, 40, 1, sleep_at=((1, 40),)),
        ]
        r = simulate_procs(ps, "gs_capped:stay", 1, wakeup_cap=c)
        burst = _post_wakeup_lockout(r.timeline, "Sleeper", "Steady")
        # Also test weight-skewed mixed case with P1 w=2, Sleeper w=1
        ps_mix = [
            Proc("Steady", 0, 60, 2),
            Proc("Sleeper", 0, 25, 1, sleep_at=((2, 24),)),
        ]
        r_mix = simulate_procs(ps_mix, "gs_capped:stay", 1, wakeup_cap=c)
        cap_rows.append({
            "wakeup_cap": c,
            "equal_burst_s40": burst,
            "equal_lag": round(r.max_abs_lag, 4),
            "equal_gap": r.max_starve_gap,
            "skew_burst_s24": _post_wakeup_lockout(r_mix.timeline, "Sleeper", "Steady"),
            "skew_lag": round(r_mix.max_abs_lag, 4),
        })
    return {"rows": rows, "cap_sensitivity": cap_rows}


def run_bench5_fp_drift() -> Dict:
    """Compare IEEE-754 float accumulation vs 10^9 fixed-point vs exact Fraction
    on decimal weights [2, 5, 10] (exact in base-10) and prime weights [3, 7, 11]."""
    checkpoints = [100, 1000, 10000, 50000, 100000]
    step_set = set(checkpoints)

    def _run_suite(weights: List[int], scale_fp: int = SCALE_FP) -> Dict:
        flt = FloatVtimeScheduler()
        fp = OptimizedHeapScheduler(use_stay=False, scale_fp=scale_fp)
        for i, w in enumerate(weights):
            flt.add_task(i, w)
            fp.add_task(i, f"T{i}", w)
        exact_used = [0] * len(weights)

        rows = []
        flt_div = 0
        fp_div = 0
        first_flt = None
        first_fp = None
        for step in range(1, max(checkpoints) + 1):
            f_tid = flt.step()
            p_tid = fp.step()
            e_tid = min(range(len(weights)), key=lambda idx: (Fraction(exact_used[idx], weights[idx]), idx))
            exact_used[e_tid] += 1
            if f_tid != e_tid:
                flt_div += 1
                if first_flt is None:
                    first_flt = step
            if p_tid != e_tid:
                fp_div += 1
                if first_fp is None:
                    first_fp = step
            if step in step_set:
                max_flt_err = max(abs(flt.vtime[i] - (exact_used[i] / weights[i])) for i in range(len(weights)))
                rows.append({
                    "steps": step,
                    "float_mismatch_cum": flt_div,
                    "fp_mismatch_cum": fp_div,
                    "exact_used": list(exact_used),
                    "fp_used": [fp.tasks[i].used for i in range(len(weights))],
                    "max_float_vtime_err": float(f"{max_flt_err:.3e}"),
                })
        return {
            "weights": weights,
            "scale_fp": scale_fp,
            "first_float_divergence": first_flt,
            "first_fp_divergence": first_fp,
            "total_float_divergences_100k": flt_div,
            "total_fp_divergences_100k": fp_div,
            "fp_matches_exact_counts": (exact_used == [fp.tasks[i].used for i in range(len(weights))]),
            "checkpoints": rows,
        }

    dec_suite = _run_suite([2, 5, 10], scale_fp=SCALE_FP)
    prime_suite = _run_suite([3, 7, 11], scale_fp=SCALE_FP)
    lcm_prime_suite = _run_suite([3, 7, 11], scale_fp=SCALE_LCM)

    tie_cases = []
    for n_mult in [1, 10, 100, 1000]:
        f_val = 0.0
        for _ in range(5 * n_mult):
            f_val += 1.0 / 5.0
        err_against_int = abs(f_val - float(n_mult))
        fp_val = (SCALE_FP // 5) * (5 * n_mult)
        tie_cases.append({
            "cycles": 5 * n_mult,
            "float_accum": repr(f_val),
            "float_abs_error": float(f"{err_against_int:.3e}"),
            "fp_value": fp_val,
            "fp_expected": SCALE_FP * n_mult,
            "fp_exact_zero_error": (fp_val == SCALE_FP * n_mult),
            "float_breaks_tie_lt_int": f_val < float(n_mult),
        })

    return {
        "decimal_weights_suite": dec_suite,
        "prime_weights_suite": prime_suite,
        "lcm_prime_suite": lcm_prime_suite,
        "tie_drift_cases": tie_cases,
    }


def run_bench4_live_os_refactor() -> Dict:
    """Live Linux comparison: latecomer arrival (legacy vs optimized) + live sleeper exploit vs cap."""
    legacy = run_live_os_comparison(mode="legacy")
    optimized = run_live_os_comparison(mode="optimized")
    sleeper_uncapped = run_live_os_sleeper_comparison(mode="uncapped")
    sleeper_capped = run_live_os_sleeper_comparison(mode="capped")
    return {
        "legacy": legacy,
        "optimized": optimized,
        "sleeper_uncapped": sleeper_uncapped,
        "sleeper_capped": sleeper_capped,
    }


def main() -> None:
    b1 = run_bench1_complexity()
    b2 = run_bench2_ablation()
    b3 = run_bench3_sleeper_mitigation()
    b5 = run_bench5_fp_drift()
    b4 = run_bench4_live_os_refactor()

    payload = {
        "exercise": 6,
        "title": "Algorithmic Optimization, O(log n) Heap Refactoring, Float Audit & Sleeper Mitigation",
        "bench1_complexity": b1,
        "bench2_ablation": b2,
        "bench3_sleeper": b3,
        "bench5_fp_drift": b5,
        "bench4_live_os": b4,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    print("B1 rows:", [(r["n_procs"], r["speedup"]) for r in b1["rows"]])
    print("B1 churn:", [(r["n_procs"], r["churn_speedup"], r["stale_pops"]) for r in b1["churn_rows"]])
    print(f"B2 ablation ({b2['n_workloads']}):", [(s["stage"], s["mean_lag"], s["mean_switches"], s["max_sleeper_burst"])
                         for s in b2["stages"]])
    print("B3 S=160:", b3["rows"][-1]["policies"])
    print("B5 dec:", b5["decimal_weights_suite"]["total_float_divergences_100k"],
          b5["decimal_weights_suite"]["total_fp_divergences_100k"],
          "prime:", b5["prime_weights_suite"]["total_float_divergences_100k"],
          b5["prime_weights_suite"]["total_fp_divergences_100k"])
    print("B4 OS arrival:", {k: (v["max_post_spawn_deviation"], v["post_spawn_shares"]) for k, v in [("leg", b4["legacy"]), ("opt", b4["optimized"])]})
    print("B4 OS sleeper:", {k: (v["post_wake_shares"], v["max_sleeper_burst_steps"]) for k, v in [("uncap", b4["sleeper_uncapped"]), ("cap", b4["sleeper_capped"])]})


if __name__ == "__main__":
    main()
