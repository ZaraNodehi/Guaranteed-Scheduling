"""Exercise 7 Capstone synthesis & cross-exercise empirical evaluation.

Generates ``exercise-7/output/experiments.json`` covering:
1. Cross-exercise metric consolidation pulled dynamically from exercise-{1..6}/output/experiments.json
2. Unified 6-Regime Stress Matrix across policies (gs_ratio, gs_entitled, gs_vtime,
   gs_capped, stride, edf, rm, rr, fifo)
3. Live Linux capstone fairness check on weighted processes [1, 2, 4] at dt=0.05s [D]
4. Repository completeness & parity audit across exercises 1..6 + core
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Dict, List

import psutil

HERE = os.path.dirname(os.path.abspath(__file__))
EX7_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX7_DIR)
OUT_DIR = os.path.join(EX7_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "exercise-6", "code"))
from gs_core import Proc, RTTask, simulate_procs, simulate_rt  # noqa: E402
from gs_optimized import LinearScanScheduler, OptimizedHeapScheduler  # noqa: E402


def _load_ex(n: int) -> Dict:
    p = os.path.join(REPO_ROOT, f"exercise-{n}", "output", "experiments.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build_cross_exercise_summary() -> Dict:
    e1 = _load_ex(1)
    e2 = _load_ex(2)
    e3 = _load_ex(3)
    e4 = _load_ex(4)
    e5 = _load_ex(5)
    e6 = _load_ex(6)

    e1_gs = e1["baseline"]["runs"]["gs_ratio_q1"]
    e2_asym = e2["regime_c_overload"]["runs_asym"]
    e2_rm = e2_asym["rm"]
    e2_gs = e2_asym["gs_vtime"]
    e3_drift = e3["workload3_float_drift"]["cases"][0]
    e4_t1 = e4["theorem1_lag_bounds"]
    e4_t2_last = e4["theorem2_starvation_scaling"]["scaling_rows"][-1]
    e4_t3 = e4["theorem3_exhaustive_rt"]
    ex5_a = e5["sweep_a_monte_carlo"]["overall"]
    ex6_b1 = e6["bench1_complexity"]["rows"][-1]
    ex6_b3 = e6["bench3_sleeper"]["rows"][-1]["policies"]
    ex6_b4 = e6["bench4_live_os"]

    return {
        "ex1_static_exact_lag": e1_gs["max_abs_lag"],
        "ex1_os_all_ordered": e1["os_subprocess_benchmark"]["all_trials_ordered_p3_fastest"],
        "ex1_os_median_wall_sec": e1["os_subprocess_benchmark"]["median_wall_sec"],
        "ex2_rt_sweep_total": e2["regime_b_sweep_120"]["total_sets"],
        "ex2_overload_rm_vs_gs": {
            "rm_min_share_ratio": e2_rm["min_task_share_ratio"],
            "gs_min_share_ratio": e2_gs["min_task_share_ratio"],
            "rm_missed": e2_rm["missed"],
            "gs_missed": e2_gs["missed"],
        },
        "ex3_float_drift_tick": e3_drift["first_divergence_t"],
        "ex4_static_bound_max_ratio": e4_t1["max_lag_over_q"],
        "ex4_violations_above_q": e4_t1["violations_above_q"],
        "ex4_dynamic_ratio_gap": e4_t2_last["gs_ratio_gap"],
        "ex4_dynamic_vtime_gap": e4_t2_last["gs_vtime_gap"],
        "ex4_rt_feasible_count": e4_t3["feasible_count"],
        "ex4_rt_edf_100pct": e4_t3["edf_100pct_matches_exhaustive"],
        "ex5_mc_240_seeds": {
            "gs_vtime_stay_lag": ex5_a["gs_vtime:stay"]["lag"]["mean"],
            "gs_ratio_index_lag": ex5_a["gs_ratio:index"]["lag"]["mean"],
            "rr_index_lag": ex5_a["rr:index"]["lag"]["mean"],
            "fifo_index_lag": ex5_a["fifo:index"]["lag"]["mean"],
        },
        "ex6_speedup_n2000": ex6_b1["speedup"],
        "ex6_sleeper_80_burst": {
            "gs_vtime": ex6_b3["gs_vtime:index"]["post_wakeup_burst"],
            "gs_capped": ex6_b3["gs_capped:index"]["post_wakeup_burst"],
        },
        "ex6_live_os_dev_ratio": round(
            ex6_b4["legacy"]["max_post_spawn_deviation"] / ex6_b4["optimized"]["max_post_spawn_deviation"], 2
        ),
    }


def run_six_regime_matrix() -> Dict:
    """Evaluate scheduler policies across 6 canonical operating regimes."""
    policies = [
        "gs_ratio:index",
        "gs_entitled:index",
        "gs_vtime:stay",
        "gs_capped:stay",
        "stride:index",
        "rr:index",
        "fifo:index",
    ]
    r1 = [Proc("A", 0, 15, 1), Proc("B", 0, 15, 2), Proc("C", 0, 15, 3), Proc("D", 0, 15, 4)]
    r2 = [Proc("P0", 0, 24, 1), Proc("P1", 0, 24, 2), Proc("Late1", 10, 12, 3), Proc("Late2", 14, 10, 2)]
    r3 = [Proc("Steady", 0, 50, 1), Proc("Sleeper", 0, 30, 1, sleep_at=((1, 40),))]

    def _run_set(procs):
        out = {}
        for pol in policies:
            res = simulate_procs(procs, pol, quantum=1)
            out[pol] = {
                "max_abs_lag": round(res.max_abs_lag, 4),
                "max_starve_gap": res.max_starve_gap,
                "context_switches": res.context_switches,
                "avg_turnaround": round(res.mean_turnaround, 3),
            }
        return out

    # Real-time regimes R4 (feasible U=0.90, tight deadline D1=1) and R5 (overload U=1.10)
    # RTTask(name, period, wcet, deadline, weight)
    rt_feas = [RTTask("T1", 3, 1, 1, weight=1), RTTask("T2", 5, 2, 5, weight=2), RTTask("T3", 6, 1, 6, weight=1)]
    rt_over = [RTTask("H1", 4, 2, 4, weight=2), RTTask("M2", 5, 2, 5, weight=2), RTTask("L3", 10, 2, 10, weight=2)]

    rt_pols = ["gs_vtime:stay", "gs_ratio:index", "edf:index", "rm:index", "rr:index", "fifo:index"]
    r4_out = {}
    r5_out = {}
    for pol in rt_pols:
        s4 = simulate_rt(rt_feas, pol, 40)
        r4_out[pol] = {
            "deadline_misses": s4["missed"],
            "min_share_ratio": round(s4["min_task_share_ratio"], 3),
        }
        s5 = simulate_rt(rt_over, pol, 40)
        r5_out[pol] = {
            "deadline_misses": s5["missed"],
            "min_share_ratio": round(s5["min_task_share_ratio"], 3),
        }

    # R6 Scale benchmark @ N = 2000 quick check
    ls, hp = LinearScanScheduler(), OptimizedHeapScheduler()
    for i in range(2000):
        ls.add_task(i, f"P{i}", (i % 5) + 1)
        hp.add_task(i, f"P{i}", (i % 5) + 1)
    t0 = time.perf_counter()
    for _ in range(500):
        ls.step()
    lin_us = (time.perf_counter() - t0) * 1e6 / 500
    t0 = time.perf_counter()
    for _ in range(500):
        hp.step()
    hp_us = (time.perf_counter() - t0) * 1e6 / 500

    return {
        "R1_Static_Weighted": _run_set(r1),
        "R2_Dynamic_Latecomers": _run_set(r2),
        "R3_Heavy_Sleeper_40": _run_set(r3),
        "R4_RT_Feasible_U090": r4_out,
        "R5_RT_Overload_U110": r5_out,
        "R6_Scale_N2000": {
            "linear_us": round(lin_us, 3),
            "heap_us": round(hp_us, 3),
            "speedup": round(lin_us / hp_us, 2),
        },
    }


def run_live_capstone_os_demo() -> Dict:
    """Live Linux verification of refactored V(t)+stay controller on weights [1, 2, 4] for 1.0s [D]."""
    burn = "import time\nend = time.monotonic() + 2.2\nx = 0\nwhile time.monotonic() < end:\n    x = (x + 1) & 0xFFFF\n"
    weights = [1, 2, 4]
    ideal = [w / sum(weights) for w in weights]
    dt = 0.05
    dur = 1.0

    procs, ps = [], []
    used = [0.0, 0.0, 0.0]
    last = [0.0, 0.0, 0.0]
    vtime = [0.0, 0.0, 0.0]
    prev = None
    switches = 0

    for _ in weights:
        sub = subprocess.Popen([sys.executable, "-c", burn])
        p = psutil.Process(sub.pid)
        try:
            p.suspend()
        except Exception:
            pass
        procs.append(sub)
        ps.append(p)

    t0 = time.monotonic()
    try:
        while time.monotonic() - t0 < dur:
            m = min(vtime)
            if prev is not None and abs(vtime[prev] - m) <= 1e-4:
                cur = prev
            else:
                cur = min(range(len(ps)), key=lambda i: (vtime[i], i))
            if prev is not None and cur != prev:
                switches += 1
            prev = cur
            try:
                ps[cur].resume()
            except Exception:
                pass
            time.sleep(dt)
            try:
                ps[cur].suspend()
                ct = ps[cur].cpu_times()
                c = float(ct.user + ct.system)
                delta = max(0.0, c - last[cur])
                last[cur] = c
                used[cur] += delta
                vtime[cur] += delta / weights[cur]
            except Exception:
                pass
    finally:
        for sub, p in zip(procs, ps):
            try:
                p.resume()
            except Exception:
                pass
            try:
                sub.kill()
                sub.wait(timeout=2)
            except Exception:
                pass

    tot = sum(used)
    shares = [round(u / tot, 4) if tot > 0 else 0.0 for u in used]
    max_err = round(max(abs(s - idl) for s, idl in zip(shares, ideal)), 4)
    return {
        "weights": weights,
        "ideal_shares": [round(x, 4) for x in ideal],
        "observed_shares": shares,
        "max_share_error": max_err,
        "switches": switches,
        "dt": dt,
    }


def audit_repository() -> List[Dict]:
    rows = []
    for k in range(1, 7):
        ex_dir = os.path.join(REPO_ROOT, f"exercise-{k}")
        diags = [f for f in os.listdir(os.path.join(ex_dir, "diagrams")) if f.endswith(".png")]
        rows.append({
            "exercise": f"exercise-{k}",
            "has_json": os.path.isfile(os.path.join(ex_dir, "output", "experiments.json")),
            "diagram_count": len(diags),
            "has_en_pdf": os.path.isfile(os.path.join(ex_dir, "docs", "REPORT_EN.pdf")),
            "has_fa_pdf": os.path.isfile(os.path.join(ex_dir, "docs", "REPORT_FA.pdf")),
            "has_en_docx": os.path.isfile(os.path.join(ex_dir, "docs", "REPORT_EN.docx")),
            "has_fa_docx": os.path.isfile(os.path.join(ex_dir, "docs", "REPORT_FA.docx")),
            "has_readme": os.path.isfile(os.path.join(ex_dir, "README.md")),
        })
    return rows


def main() -> None:
    payload = {
        "exercise": 7,
        "title": "Capstone Synthesis, Cross-Regime Decision Matrix, Repository Audit & Future Roadmap",
        "cross_exercise_summary": build_cross_exercise_summary(),
        "six_regime_matrix": run_six_regime_matrix(),
        "live_capstone_os_demo": run_live_capstone_os_demo(),
        "repo_audit_ex1_to_6": audit_repository(),
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    print("Summary:", json.dumps(payload["cross_exercise_summary"], indent=2))
    print("Live OS:", payload["live_capstone_os_demo"])
    print("R4 RT Feas:", payload["six_regime_matrix"]["R4_RT_Feasible_U090"])
    print("R5 RT Over:", payload["six_regime_matrix"]["R5_RT_Overload_U110"])


if __name__ == "__main__":
    main()
