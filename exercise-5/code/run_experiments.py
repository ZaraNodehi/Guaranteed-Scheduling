"""Exercise 5 experiments: Randomized Monte Carlo sweeps, Pareto sensitivity, Zipf burst & OS trials.

Produces ``exercise-5/output/experiments.json`` covering:
- Sweep A [M]: 240 randomized dynamic workloads across N in {3, 5, 8} (mean, 95% CI, p95, p99 + 60 samples + ECDF)
- Sweep B [M]: Quantum sweep q in {1, 2, 3, 4, 6, 8, 12} (30 seeds each) mapping Lag vs Context-Switch Pareto
- Sweep C [M]: Process count N in {2, 4, 6, 8, 12, 16} & weight skew (1:1 vs 1:4) scaling
- Sweep D [D]: Live OS psutil CPU-bound subprocess benchmark across 5 poll intervals (0.01s..0.20s) + live trace
- Sweep E [M]: Heavy-tail Zipf weight skew [1,1,2,4,8,16] + mid-run burst arrival stress (60 seeds)
- Sweep F [M]: Paired 1000-resample Bootstrap 95% CI & pairwise win-rate audit over Sweep A
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
    seed_samples = []
    total_runs = 0
    for n_procs in (3, 5, 8):
        per_n = {p: {"lag": [], "gap": [], "sw": [], "ta": [], "jain": []} for p in policies}
        for seed_idx in range(80):
            ps = _gen_dynamic_procs(rng, n_procs)
            total_runs += 1
            row_res = {}
            for pol in policies:
                r = simulate_procs(ps, pol, quantum=1)
                row_res[pol] = r
                for d_tgt in (all_metrics[pol], per_n[pol]):
                    d_tgt["lag"].append(r.max_abs_lag)
                    d_tgt["gap"].append(r.max_starve_gap)
                    d_tgt["sw"].append(r.context_switches)
                    d_tgt["ta"].append(r.mean_turnaround)
                    d_tgt["jain"].append(r.jain_fairness)
                all_metrics[pol]["rmse"].append(r.rmse_lag)
            # Save every one of the 240 seeds for complete experimental census
            seed_samples.append({
                "seed_id": total_runs,
                "n_procs": n_procs,
                "total_work": sum(p.work for p in ps),
                "weights": [p.weight for p in ps],
                "stay_lag": round(row_res["gs_vtime:stay"].max_abs_lag, 4),
                "index_lag": round(row_res["gs_vtime:index"].max_abs_lag, 4),
                "ratio_lag": round(row_res["gs_ratio:index"].max_abs_lag, 4),
                "rr_lag": round(row_res["rr:index"].max_abs_lag, 4),
                "fifo_lag": round(row_res["fifo:index"].max_abs_lag, 4),
                "stay_sw": row_res["gs_vtime:stay"].context_switches,
                "index_sw": row_res["gs_vtime:index"].context_switches,
                "ratio_gap": row_res["gs_ratio:index"].max_starve_gap,
            })
        by_n[str(n_procs)] = {
            p: {m: _stats(vals) for m, vals in mmap.items()}
            for p, mmap in per_n.items()
        }

    overall = {
        p: {m: _stats(vals) for m, vals in mmap.items()}
        for p, mmap in all_metrics.items()
    }
    ecdf_lags = {
        p: [round(v, 4) for v in sorted(all_metrics[p]["lag"])]
        for p in ("gs_vtime:stay", "gs_vtime:index", "gs_entitled:index", "gs_ratio:index", "rr:index", "fifo:index")
    }
    ecdf_gaps = {
        p: [int(v) for v in sorted(all_metrics[p]["gap"])]
        for p in ("gs_vtime:stay", "gs_entitled:index", "gs_ratio:index", "rr:index", "fifo:index")
    }
    return {
        "n_workloads": total_runs,
        "overall": overall,
        "by_n": by_n,
        "seed_samples_60": seed_samples,
        "ecdf_lags": ecdf_lags,
        "ecdf_gaps": ecdf_gaps,
        "raw_for_bootstrap": all_metrics,
    }


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
        vt_sk_sw, rat_sk_sw = [], []
        for _ in range(20):
            ps_eq = [Proc(f"P{i+1}", 0 if i == 0 else rng.randint(0, 12), rng.randint(5, 12), 1)
                     for i in range(n)]
            ps_sk = [Proc(f"P{i+1}", 0 if i == 0 else rng.randint(0, 12), rng.randint(5, 12),
                          1 if i % 2 == 0 else 4) for i in range(n)]
            for ps, l_vt, l_rat, g_vt, g_rat, s_vt, s_rat in [
                (ps_eq, vt_eq_lag, rat_eq_lag, None, None, None, None),
                (ps_sk, vt_sk_lag, rat_sk_lag, vt_sk_gap, rat_sk_gap, vt_sk_sw, rat_sk_sw),
            ]:
                r_vt = simulate_procs(ps, "gs_vtime:stay", 1)
                r_rat = simulate_procs(ps, "gs_ratio:index", 1)
                l_vt.append(r_vt.max_abs_lag)
                l_rat.append(r_rat.max_abs_lag)
                if g_vt is not None:
                    g_vt.append(r_vt.max_starve_gap)
                    g_rat.append(r_rat.max_starve_gap)
                    s_vt.append(r_vt.context_switches)
                    s_rat.append(r_rat.context_switches)
        rows.append({
            "n_procs": n,
            "eq_vtime_lag": _stats(vt_eq_lag),
            "eq_ratio_lag": _stats(rat_eq_lag),
            "skew_vtime_lag": _stats(vt_sk_lag),
            "skew_ratio_lag": _stats(rat_sk_lag),
            "skew_vtime_gap": _stats(vt_sk_gap),
            "skew_ratio_gap": _stats(rat_sk_gap),
            "skew_vtime_sw": _stats(vt_sk_sw),
            "skew_ratio_sw": _stats(rat_sk_sw),
        })
    return {"scaling_rows": rows}


def run_sweep_d_os_intervals() -> Dict:
    """Live OS psutil CPU-bound subprocess control across 5 poll intervals [0.01s..0.20s]."""
    intervals = [0.01, 0.02, 0.05, 0.10, 0.20]
    weights = [1, 2, 4]
    duration = 1.2
    results = []
    dt005_trace = []
    burn_code = "import time\nend = time.monotonic() + 3.5\nx = 0\nwhile time.monotonic() < end:\n    x = (x + 1) & 0xFFFF\n"

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
                if dt == 0.05 and len(dt005_trace) < 24:
                    tot = sum(used)
                    W = sum(weights)
                    sh = [round(u / tot, 4) if tot > 0 else 0.0 for u in used]
                    tg = [w / W for w in weights]
                    err = round(max(abs(s - g) for s, g in zip(sh, tg)) * 100.0, 2) if tot > 0 else 0.0
                    dt005_trace.append({
                        "step": dispatches,
                        "elapsed_ms": round((time.monotonic() - t0) * 1000.0, 1),
                        "chosen": f"P{cur+1} (w={weights[cur]})",
                        "cum_cpu": [round(u, 4) for u in used],
                        "shares": sh,
                        "max_err_pct": err,
                    })
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
    return {"weights": weights, "interval_trials": results, "dt005_trace": dt005_trace}


def run_sweep_e_zipf_burst() -> Dict:
    """Sweep E [M]: 60 heavy-tail Zipf workloads [1,1,2,4,8,16] + t=15 burst shock."""
    rng = random.Random(202699)
    zipf_w = [1, 1, 2, 4, 8, 16]
    policies = ["gs_vtime:stay", "gs_vtime:index", "gs_vtime:max_weight",
                "gs_entitled:index", "gs_ratio:index", "stride:index", "rr:index"]
    agg = {p: {"lag": [], "gap": [], "sw": [], "ta": [], "jain": []} for p in policies}
    seed_rows = []
    for s in range(60):
        # 3 initial tasks at t=0..2 + 3 burst heavy/light arrivals clustered at t=15..17
        ws = list(zipf_w)
        rng.shuffle(ws)
        procs = []
        for i, w in enumerate(ws):
            arr = rng.randint(0, 2) if i < 3 else rng.randint(14, 17)
            work = rng.randint(6, 16)
            procs.append(Proc(f"P{i+1}", arrival=arr, work=work, weight=w))
        row = {}
        for p in policies:
            r = simulate_procs(procs, p, quantum=1)
            row[p] = r
            agg[p]["lag"].append(r.max_abs_lag)
            agg[p]["gap"].append(r.max_starve_gap)
            agg[p]["sw"].append(r.context_switches)
            agg[p]["ta"].append(r.mean_turnaround)
            agg[p]["jain"].append(r.jain_fairness)
        seed_rows.append({
            "seed": s + 1,
            "weights": ws,
            "stay_lag": round(row["gs_vtime:stay"].max_abs_lag, 4),
            "maxw_lag": round(row["gs_vtime:max_weight"].max_abs_lag, 4),
            "ratio_lag": round(row["gs_ratio:index"].max_abs_lag, 4),
            "rr_lag": round(row["rr:index"].max_abs_lag, 4),
            "stay_gap": row["gs_vtime:stay"].max_starve_gap,
            "ratio_gap": row["gs_ratio:index"].max_starve_gap,
        })
    summary = {p: {m: _stats(vals) for m, vals in mmap.items()} for p, mmap in agg.items()}
    return {"n_seeds": 60, "zipf_weights": zipf_w, "summary": summary, "samples_60": seed_rows}


def run_sweep_f_bootstrap(raw_metrics: Dict) -> Dict:
    """Sweep F [M]: 1000-resample paired bootstrap CI & win/tie/loss vs gs_vtime:stay across 240 runs."""
    rng = random.Random(77777)
    base_lag = raw_metrics["gs_vtime:stay"]["lag"]
    base_sw = raw_metrics["gs_vtime:stay"]["sw"]
    n = len(base_lag)
    competitors = ["gs_vtime:index", "gs_entitled:index", "stride:index",
                   "gs_ratio:index", "rr:index", "fifo:index"]
    comparisons = []
    for comp in competitors:
        comp_lag = raw_metrics[comp]["lag"]
        comp_sw = raw_metrics[comp]["sw"]
        diffs = [c - b for b, c in zip(base_lag, comp_lag)]
        wins = sum(1 for d in diffs if d > 1e-9)
        ties = sum(1 for d in diffs if abs(d) <= 1e-9)
        losses = sum(1 for d in diffs if d < -1e-9)
        sw_diffs = [c - b for b, c in zip(base_sw, comp_sw)]
        mean_d = sum(diffs) / n
        sd_d = math.sqrt(sum((d - mean_d) ** 2 for d in diffs) / max(1, n - 1))
        cohens_d = mean_d / max(sd_d, 1e-9)

        # 1000 paired bootstrap resamples
        boot_means = []
        for _ in range(1000):
            s_diff = 0.0
            for _j in range(n):
                idx = rng.randrange(n)
                s_diff += diffs[idx]
            boot_means.append(s_diff / n)
        boot_means.sort()
        comparisons.append({
            "competitor": comp,
            "stay_wins": wins,
            "ties": ties,
            "stay_losses": losses,
            "win_rate_pct": round(100.0 * wins / n, 2),
            "mean_lag_reduction": round(mean_d, 4),
            "boot_ci95_low": round(boot_means[25], 4),
            "boot_ci95_high": round(boot_means[975], 4),
            "cohens_d": round(cohens_d, 3),
            "mean_sw_saved_vs_comp": round(sum(sw_diffs) / n, 2),
        })
    return {"n_pairs": n, "n_bootstrap": 1000, "comparisons": comparisons}


def main() -> None:
    sw_a = run_sweep_a_monte_carlo()
    raw_boot = sw_a.pop("raw_for_bootstrap")
    sw_f = run_sweep_f_bootstrap(raw_boot)
    sw_b = run_sweep_b_quantum_pareto()
    sw_c = run_sweep_c_scaling()
    sw_d = run_sweep_d_os_intervals()
    sw_e = run_sweep_e_zipf_burst()

    payload = {
        "exercise": 5,
        "title": "Large-Scale Simulation Sweeps, Sensitivity, Zipf Burst & Pareto Analysis",
        "sweep_a_monte_carlo": sw_a,
        "sweep_b_quantum_pareto": sw_b,
        "sweep_c_scaling": sw_c,
        "sweep_d_os_intervals": sw_d,
        "sweep_e_zipf_burst": sw_e,
        "sweep_f_bootstrap": sw_f,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    ov = sw_a["overall"]
    print("Sweep A mean lag:", {k: ov[k]["lag"]["mean"] for k in ("gs_vtime:stay", "gs_vtime:index", "gs_ratio:index", "rr:index")})
    print("Sweep E zipf+burst mean lag:", {k: sw_e["summary"][k]["lag"]["mean"] for k in ("gs_vtime:stay", "gs_vtime:max_weight", "gs_ratio:index", "rr:index")})
    print("Sweep F wins vs ratio:", sw_f["comparisons"][3])
    print("Sweep D OS errors:", [(r["poll_dt_sec"], r["controller_switches"], r["max_share_deviation"]) for r in sw_d["interval_trials"]])


if __name__ == "__main__":
    main()
