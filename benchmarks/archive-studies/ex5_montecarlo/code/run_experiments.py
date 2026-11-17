"""Exercise 5 experiments: Randomized Monte Carlo sweeps, Pareto sensitivity & OS polling interval trials.

Produces ``exercise-5/output/experiments.json`` covering:
- Sweep A [M]: 240 randomized dynamic workloads across N in {3, 5, 8} (mean, 95% CI, p95, p99)
- Sweep B [M]: Quantum sweep q in {1, 2, 3, 4, 6, 8, 12} (30 seeds each) mapping Lag vs Context-Switch Pareto
- Sweep C [M]: Process count N in {2, 4, 6, 8, 12, 16} & weight skew (1:1 vs skewed) scaling
- Sweep D [D]: Live OS psutil CPU-bound subprocess benchmark across poll intervals (0.02s, 0.05s, 0.10s)
"""
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
import time
from typing import Dict, List

import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
EX5_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX5_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from gs_core import Proc, simulate_procs  # noqa: E402


def _stats(vals: List[float]) -> Dict:
    xs = sorted(float(v) for v in vals)
    n = len(xs)
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / max(1, n - 1)
    sd = math.sqrt(var)
    ci95 = 1.96 * sd / math.sqrt(n)
    p50 = xs[n // 2]
    p95 = xs[min(n - 1, int(0.95 * n))]
    p99 = xs[min(n - 1, int(0.99 * n))]
    return {
        "n": n,
        "mean": round(mean, 4),
        "sd": round(sd, 4),
        "ci95": round(ci95, 4),
        "median": round(p50, 4),
        "p95": round(p95, 4),
        "p99": round(p99, 4),
        "max": round(xs[-1], 4),
    }


def _gen_dynamic_procs(rng: random.Random, n_procs: int) -> List[Proc]:
    procs = []
    # Ensure at least one t=0 anchor so CPU starts immediately
    for i in range(n_procs):
        arr = 0 if i == 0 else rng.randint(0, 14)
        work = rng.randint(5, 18)
        weight = rng.randint(1, 6)
        procs.append(Proc(f"P{i+1}", arrival=arr, work=work, weight=weight))
    return procs


def run_sweep_a_monte_carlo() -> Dict:
    """240 randomized dynamic workloads: 80 seeds each for N in {3, 5, 8}."""
    rng = random.Random(202605)
    policies = ["gs_vtime:index", "gs_vtime:stay", "gs_entitled:index",
                "gs_ratio:index", "stride:index", "rr:index", "fifo:index"]
    all_metrics = {p: {"lag": [], "rmse": [], "gap": [], "sw": [], "ta": [], "jain": []} for p in policies}
    by_n = {}
    total_runs = 0
    for n_procs in (3, 5, 8):
        per_n = {p: {"lag": [], "gap": [], "sw": [], "ta": [], "jain": []} for p in policies}
        for _ in range(80):
            ps = _gen_dynamic_procs(rng, n_procs)
            total_runs += 1
            for pol in policies:
                r = simulate_procs(ps, pol, quantum=1)
                for d_tgt in (all_metrics[pol], per_n[pol]):
                    d_tgt["lag"].append(r.max_abs_lag)
                    d_tgt["gap"].append(r.max_starve_gap)
                    d_tgt["sw"].append(r.context_switches)
                    d_tgt["ta"].append(r.mean_turnaround)
                    d_tgt["jain"].append(r.jain_fairness)
                all_metrics[pol]["rmse"].append(r.rmse_lag)
        by_n[str(n_procs)] = {
            p: {m: _stats(vals) for m, vals in mmap.items()}
            for p, mmap in per_n.items()
        }

    overall = {
        p: {m: _stats(vals) for m, vals in mmap.items()}
        for p, mmap in all_metrics.items()
    }
    return {"n_workloads": total_runs, "overall": overall, "by_n": by_n}


def run_sweep_b_quantum_pareto() -> Dict:
    """Quantum sweep q in [1, 2, 3, 4, 6, 8, 12] across 30 seeds (N=5 dynamic)."""
    rng = random.Random(9001)
    workloads = [_gen_dynamic_procs(rng, 5) for _ in range(30)]
    quanta = [1, 2, 3, 4, 6, 8, 12]
    policies = ["gs_vtime:index", "gs_vtime:stay", "gs_ratio:index", "rr:index"]
    rows = []
    for q in quanta:
        pol_stats = {}
        for pol in policies:
            lags, rmses, sws, tas = [], [], [], []
            for ps in workloads:
                r = simulate_procs(ps, pol, quantum=q)
                lags.append(r.max_abs_lag)
                rmses.append(r.rmse_lag)
                sws.append(r.context_switches)
                tas.append(r.mean_turnaround)
            pol_stats[pol] = {
                "lag": _stats(lags),
                "rmse": _stats(rmses),
                "switches": _stats(sws),
                "turnaround": _stats(tas),
            }
        rows.append({"quantum": q, "policies": pol_stats})
    return {"n_seeds": len(workloads), "quanta": quanta, "rows": rows}


def run_sweep_c_scaling() -> Dict:
    """Process count N in [2, 4, 6, 8, 12, 16] across equal vs skewed weights (20 seeds each)."""
    rng = random.Random(555)
    ns = [2, 4, 6, 8, 12, 16]
    rows = []
    for n in ns:
        vt_eq_lag, rat_eq_lag, vt_sk_lag, rat_sk_lag = [], [], [], []
        vt_sk_gap, rat_sk_gap = [], []
        for _ in range(20):
            ps_eq = [Proc(f"P{i+1}", 0 if i == 0 else rng.randint(0, 12), rng.randint(5, 12), 1)
                     for i in range(n)]
            ps_sk = [Proc(f"P{i+1}", 0 if i == 0 else rng.randint(0, 12), rng.randint(5, 12),
                          1 if i % 2 == 0 else 4) for i in range(n)]
            for ps, l_vt, l_rat, g_vt, g_rat in [
                (ps_eq, vt_eq_lag, rat_eq_lag, None, None),
                (ps_sk, vt_sk_lag, rat_sk_lag, vt_sk_gap, rat_sk_gap),
            ]:
                r_vt = simulate_procs(ps, "gs_vtime:index", 1)
                r_rat = simulate_procs(ps, "gs_ratio:index", 1)
                l_vt.append(r_vt.max_abs_lag)
                l_rat.append(r_rat.max_abs_lag)
                if g_vt is not None:
                    g_vt.append(r_vt.max_starve_gap)
                    g_rat.append(r_rat.max_starve_gap)
        rows.append({
            "n_procs": n,
            "eq_vtime_lag": _stats(vt_eq_lag),
            "eq_ratio_lag": _stats(rat_eq_lag),
            "skew_vtime_lag": _stats(vt_sk_lag),
            "skew_ratio_lag": _stats(rat_sk_lag),
            "skew_vtime_gap": _stats(vt_sk_gap),
            "skew_ratio_gap": _stats(rat_sk_gap),
        })
    return {"scaling_rows": rows}


def run_sweep_d_os_intervals() -> Dict:
    """Live OS psutil CPU-bound subprocess control across poll intervals [0.02s, 0.05s, 0.10s]."""
    intervals = [0.02, 0.05, 0.10]
    weights = [1, 2, 4]
    duration = 1.2
    results = []
    burn_code = "import time\nend = time.monotonic() + 3.0\nx = 0\nwhile time.monotonic() < end:\n    x = (x + 1) & 0xFFFF\n"

    for dt in intervals:
        procs = [subprocess.Popen([sys.executable, "-c", burn_code]) for _ in weights]
        ps = [psutil.Process(p.pid) for p in procs]
        for p in ps:
            try:
                p.suspend()
            except Exception:
                pass
        used = [0.0] * len(weights)
        last_cpu = [0.0] * len(weights)
        dispatches = 0
        switches = 0
        prev = None
        t0 = time.monotonic()
        try:
            while time.monotonic() - t0 < duration:
                # Choose minimum used/weight
                cur = min(range(len(weights)), key=lambda i: (used[i] / weights[i], i))
                if prev is not None and cur != prev:
                    switches += 1
                prev = cur
                dispatches += 1
                try:
                    ps[cur].resume()
                except Exception:
                    pass
                time.sleep(dt)
                try:
                    ps[cur].suspend()
                    ct = ps[cur].cpu_times()
                    c = float(ct.user + ct.system)
                    delta = max(0.0, c - last_cpu[cur])
                    last_cpu[cur] = c
                    used[cur] += delta
                except Exception:
                    pass
        finally:
            for p_sub, p_ps in zip(procs, ps):
                try:
                    p_ps.resume()
                except Exception:
                    pass
                try:
                    p_sub.kill()
                    p_sub.wait(timeout=2)
                except Exception:
                    pass

        tot_cpu = sum(used)
        W = sum(weights)
        shares = [round(u / tot_cpu, 4) if tot_cpu > 0 else 0.0 for u in used]
        targets = [round(w / W, 4) for w in weights]
        max_share_err = round(max(abs(s - tg) for s, tg in zip(shares, targets)), 4)
        results.append({
            "poll_dt_sec": dt,
            "duration_sec": duration,
            "dispatches": dispatches,
            "controller_switches": switches,
            "cpu_seconds": [round(u, 4) for u in used],
            "total_cpu_sec": round(tot_cpu, 4),
            "actual_shares": shares,
            "target_shares": targets,
            "max_share_deviation": max_share_err,
        })
    return {"weights": weights, "interval_trials": results}


def main() -> None:
    sw_a = run_sweep_a_monte_carlo()
    sw_b = run_sweep_b_quantum_pareto()
    sw_c = run_sweep_c_scaling()
    sw_d = run_sweep_d_os_intervals()

    payload = {
        "exercise": 5,
        "title": "Large-Scale Simulation Sweeps, Sensitivity & Pareto Analysis",
        "sweep_a_monte_carlo": sw_a,
        "sweep_b_quantum_pareto": sw_b,
        "sweep_c_scaling": sw_c,
        "sweep_d_os_intervals": sw_d,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    ov = sw_a["overall"]
    for pol in ("gs_vtime:index", "gs_vtime:stay", "gs_entitled:index", "gs_ratio:index", "rr:index", "fifo:index"):
        print(f"Sweep A {pol:18s}: lag={ov[pol]['lag']['mean']:.3f}+-{ov[pol]['lag']['ci95']:.3f} (p99={ov[pol]['lag']['p99']:.2f}), gap={ov[pol]['gap']['mean']:.2f}, sw={ov[pol]['sw']['mean']:.1f}, ta={ov[pol]['ta']['mean']:.2f}")
    print("Sweep D OS intervals:", [(r["poll_dt_sec"], r["controller_switches"], r["actual_shares"], r["max_share_deviation"])
                                    for r in sw_d["interval_trials"]])


if __name__ == "__main__":
    main()
