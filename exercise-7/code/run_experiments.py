"""Exercise 7 Capstone synthesis, cross-exercise consolidation, EEVDF prototype & repository audit.

Generates ``exercise-7/output/experiments.json`` covering:
1. Cross-exercise metric consolidation pulled dynamically from exercise-{1..6}/output/experiments.json
2. Unified multi-regime stress matrix (R1 Static, R2 Dynamic, R3 Sleeper, R4 RT Feasible,
   R5 RT Overload, R6 Scale N=2000, R7 Combined Zipf+Latecomer+Sleeper Stress)
3. Full EEVDF prototype benchmark (eligibility + virtual deadline on variable request lengths L in {1,2,4})
4. Live Linux capstone fairness check on weighted processes [1, 2, 4] at dt=0.05s with full step trace [D]
5. End-to-end repository completeness & artifact audit across exercises 1..6 + core
"""
from __future__ import annotations

import json
import os
import random
import statistics
import subprocess
import sys
import time
from fractions import Fraction
from typing import Dict, List

import psutil
import pymupdf

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
    ex5_f = {c["competitor"]: c for c in e5["sweep_f_bootstrap"]["comparisons"]}
    ex5_d01 = e5["sweep_d_os_intervals"]["interval_trials"][0]
    ex6_b1_2k = next(r for r in e6["bench1_complexity"]["rows"] if r["n_procs"] == 2000)
    ex6_b1_4k = e6["bench1_complexity"]["rows"][-1]
    ex6_b2 = e6["bench2_ablation"]
    ex6_b3_80 = next(r for r in e6["bench3_sleeper"]["rows"] if r["sleep_ticks"] == 80)["policies"]
    ex6_b3_max = e6["bench3_sleeper"]["rows"][-1]["policies"]
    ex6_b5_dec = e6["bench5_fp_drift"]["decimal_weights_suite"]
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
            "boot_win_vs_ratio_pct": ex5_f["gs_ratio:index"]["win_rate_pct"],
            "os_dt001_err_pct": round(ex5_d01["max_share_deviation"] * 100.0, 2),
        },
        "ex6_speedup_n2000": ex6_b1_2k["speedup"],
        "ex6_speedup_n4000": ex6_b1_4k["speedup"],
        "ex6_ablation_n": ex6_b2["n_workloads"],
        "ex6_sleeper_80_burst": {
            "gs_vtime": ex6_b3_80["gs_vtime:index"]["post_wakeup_burst"],
            "gs_capped": ex6_b3_80["gs_capped:index"]["post_wakeup_burst"],
        },
        "ex6_sleeper_max_burst": {
            "sleep_ticks": e6["bench3_sleeper"]["rows"][-1]["sleep_ticks"],
            "gs_vtime": ex6_b3_max["gs_vtime:index"]["post_wakeup_burst"],
            "gs_capped": ex6_b3_max["gs_capped:index"]["post_wakeup_burst"],
        },
        "ex6_float64_div_100k": ex6_b5_dec["total_float_divergences_100k"],
        "ex6_fp_div_100k": ex6_b5_dec["total_fp_divergences_100k"],
        "ex6_legacy_os_err_pct": round(ex6_b4["legacy"]["max_post_spawn_deviation"] * 100.0, 2),
        "ex6_opt_os_err_pct": round(ex6_b4["optimized"]["max_post_spawn_deviation"] * 100.0, 2),
        "ex6_live_os_dev_ratio": round(
            ex6_b4["legacy"]["max_post_spawn_deviation"] / max(1e-6, ex6_b4["optimized"]["max_post_spawn_deviation"]), 2
        ),
        "ex6_sleeper_os_uncapped_burst": ex6_b4["sleeper_uncapped"]["max_sleeper_burst_steps"],
        "ex6_sleeper_os_capped_err_pct": round(ex6_b4["sleeper_capped"]["post_wake_dev"] * 100.0, 2),
    }


def run_six_regime_matrix() -> Dict:
    """Evaluate scheduler policies across 7 operating regimes (R1..R7)."""
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
    r7 = [
        Proc("Anchor", 0, 36, 2),
        Proc("ZipfBurst", 10, 18, 8),
        Proc("SleeperIO", 0, 18, 1, sleep_at=((2, 20),)),
        Proc("Med", 4, 20, 4),
    ]

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
        "R7_Combined_Stress": _run_set(r7),
    }


def simulate_eevdf_variable(tasks_spec: List[Dict], mode: str) -> Dict:
    """Simulate EEVDF vs fixed-quantum gs_capped vs RR on variable slice requests L_i."""
    n = len(tasks_spec)
    rem_total = [t["total"] for t in tasks_spec]
    req_len = [t["slice_len"] for t in tasks_spec]
    weights = [t["weight"] for t in tasks_spec]
    ve = [Fraction(0) for _ in range(n)]
    used = [0 for _ in range(n)]
    ideal = [Fraction(0) for _ in range(n)]
    sys_vt = Fraction(0)
    max_lag = Fraction(0)
    cur_idx = None
    cur_rem = 0
    switches = 0
    trace = []
    t = 0
    rr_ptr = 0
    horizon = sum(rem_total)

    while t < horizon:
        active = [i for i in range(n) if rem_total[i] > 0]
        w_sum = sum(weights[i] for i in active)
        if cur_idx is None or cur_rem == 0 or rem_total[cur_idx] == 0:
            if mode == "eevdf":
                elig = [i for i in active if ve[i] <= sys_vt]
                if not elig:
                    elig = active
                # Choose eligible request with earliest virtual deadline ve_i + L_i / w_i
                next_idx = min(
                    elig,
                    key=lambda i: (ve[i] + Fraction(min(req_len[i], rem_total[i]), weights[i]), i),
                )
                cur_rem = min(req_len[next_idx], rem_total[next_idx])
            elif mode == "gs_capped_var":
                next_idx = min(active, key=lambda i: (ve[i], i))
                cur_rem = min(req_len[next_idx], rem_total[next_idx])
            else:
                # RR slice=2
                while rem_total[rr_ptr] == 0:
                    rr_ptr = (rr_ptr + 1) % n
                next_idx = rr_ptr
                rr_ptr = (rr_ptr + 1) % n
                cur_rem = min(2, rem_total[next_idx])
            if cur_idx is not None and next_idx != cur_idx:
                switches += 1
            cur_idx = next_idx

        # Run 1 tick
        rem_total[cur_idx] -= 1
        used[cur_idx] += 1
        cur_rem -= 1
        ve[cur_idx] += Fraction(1, weights[cur_idx])
        sys_vt += Fraction(1, w_sum)
        for i in active:
            ideal[i] += Fraction(weights[i], w_sum)
        t += 1
        step_lag = max(abs(ideal[i] - used[i]) for i in range(n))
        if step_lag > max_lag:
            max_lag = step_lag
        trace.append({
            "t": t,
            "chosen": tasks_spec[cur_idx]["name"],
            "sys_vt": round(float(sys_vt), 3),
            "max_lag": round(float(step_lag), 3),
        })

    return {
        "max_abs_lag": round(float(max_lag), 4),
        "switches": switches,
        "trace": trace,
    }


def run_eevdf_prototype_benchmark() -> Dict:
    """Phase-2 EEVDF Prototype [E]+[M]: variable request lengths L_i in {1, 2, 4} comparing
    EEVDF (eligible ve_i <= V(t), min virtual deadline vd_i = ve_i + L_i/w_i) vs fixed-quantum
    gs_capped and unweighted RR across 40 randomized variable-slice workloads."""
    _simulate_slice_requests = simulate_eevdf_variable

    rng = random.Random(7070)
    runs_summary = {m: [] for m in ("eevdf", "gs_capped_var", "rr_var")}
    seed_rows = []
    for s in range(40):
        spec = [
            {"name": "T0", "weight": rng.randint(1, 5), "slice_len": rng.choice([1, 2, 4]), "total": rng.randint(8, 14)},
            {"name": "T1", "weight": rng.randint(1, 5), "slice_len": rng.choice([1, 2, 4]), "total": rng.randint(8, 14)},
            {"name": "T2", "weight": rng.randint(1, 5), "slice_len": rng.choice([1, 2, 4]), "total": rng.randint(8, 14)},
            {"name": "T3", "weight": rng.randint(1, 5), "slice_len": rng.choice([1, 2, 4]), "total": rng.randint(8, 14)},
        ]
        e = _simulate_slice_requests(spec, "eevdf")
        g = _simulate_slice_requests(spec, "gs_capped_var")
        r = _simulate_slice_requests(spec, "rr_var")
        runs_summary["eevdf"].append(e["max_abs_lag"])
        runs_summary["gs_capped_var"].append(g["max_abs_lag"])
        runs_summary["rr_var"].append(r["max_abs_lag"])
        seed_rows.append({
            "seed": s + 1,
            "weights": [x["weight"] for x in spec],
            "slices": [x["slice_len"] for x in spec],
            "eevdf_lag": e["max_abs_lag"],
            "gs_var_lag": g["max_abs_lag"],
            "rr_var_lag": r["max_abs_lag"],
            "eevdf_sw": e["switches"],
            "gs_var_sw": g["switches"],
        })

    # Canonical trace example exposing deadline urgency: EEVDF prevents B (L=4,w=1) from delaying short C (L=1,w=2)
    canon_spec = [
        {"name": "HeavyLong(L=4,w=4)", "weight": 4, "slice_len": 4, "total": 16},
        {"name": "SlowLong(L=4,w=1)", "weight": 1, "slice_len": 4, "total": 8},
        {"name": "UrgentShort(L=1,w=2)", "weight": 2, "slice_len": 1, "total": 10},
    ]
    c_eevdf = _simulate_slice_requests(canon_spec, "eevdf")
    c_gs = _simulate_slice_requests(canon_spec, "gs_capped_var")
    c_rr = _simulate_slice_requests(canon_spec, "rr_var")

    return {
        "n_workloads": 40,
        "summary": {
            m: {
                "mean_lag": round(statistics.mean(vals), 4),
                "p95_lag": round(sorted(vals)[int(0.95 * len(vals))], 4),
                "max_lag": round(max(vals), 4),
            }
            for m, vals in runs_summary.items()
        },
        "eevdf_beats_gs_var_count": sum(1 for row in seed_rows if row["eevdf_lag"] <= row["gs_var_lag"]),
        "seed_rows_40": seed_rows,
        "canonical_trace": {
            "eevdf": c_eevdf,
            "gs_capped_var": c_gs,
            "rr_var": c_rr,
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
    trace = []
    step_idx = 0

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
            step_idx += 1
            tot_now = sum(used)
            sh_now = [round(u / tot_now, 4) if tot_now > 0 else 0.0 for u in used]
            trace.append({
                "step": step_idx,
                "elapsed_s": round(time.monotonic() - t0, 3),
                "chosen": f"P{cur + 1} (w={weights[cur]})",
                "vtimes": [round(v, 4) for v in vtime],
                "shares": sh_now,
                "max_err": round(max(abs(s - idl) for s, idl in zip(sh_now, ideal)), 4),
            })
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
        "trace": trace,
    }


def audit_repository() -> List[Dict]:
    rows = []
    for k in range(1, 7):
        ex_dir = os.path.join(REPO_ROOT, f"exercise-{k}")
        diags = [f for f in os.listdir(os.path.join(ex_dir, "diagrams")) if f.endswith(".png")]
        en_pdf = os.path.join(ex_dir, "docs", "REPORT_EN.pdf")
        fa_pdf = os.path.join(ex_dir, "docs", "REPORT_FA.pdf")
        en_p = len(pymupdf.open(en_pdf)) if os.path.isfile(en_pdf) else 0
        fa_p = len(pymupdf.open(fa_pdf)) if os.path.isfile(fa_pdf) else 0
        rows.append({
            "exercise": f"exercise-{k}",
            "has_json": os.path.isfile(os.path.join(ex_dir, "output", "experiments.json")),
            "diagram_count": len(diags),
            "en_pages": en_p,
            "fa_pages": fa_p,
            "has_en_pdf": os.path.isfile(en_pdf),
            "has_fa_pdf": os.path.isfile(fa_pdf),
            "has_en_docx": os.path.isfile(os.path.join(ex_dir, "docs", "REPORT_EN.docx")),
            "has_fa_docx": os.path.isfile(os.path.join(ex_dir, "docs", "REPORT_FA.docx")),
            "has_decks": os.path.isfile(os.path.join(ex_dir, "docs", "DECK_EN.pptx")),
            "has_readme": os.path.isfile(os.path.join(ex_dir, "README.md")),
        })
    return rows


def main() -> None:
    payload = {
        "exercise": 7,
        "title": "Capstone Synthesis, Cross-Regime Decision Matrix, EEVDF Prototype & Repository Audit",
        "cross_exercise_summary": build_cross_exercise_summary(),
        "six_regime_matrix": run_six_regime_matrix(),
        "eevdf_prototype": run_eevdf_prototype_benchmark(),
        "live_capstone_os_demo": run_live_capstone_os_demo(),
        "repo_audit_ex1_to_6": audit_repository(),
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    print("EEVDF summary:", payload["eevdf_prototype"]["summary"],
          "wins/40:", payload["eevdf_prototype"]["eevdf_beats_gs_var_count"])
    print("Live OS:", {k: payload["live_capstone_os_demo"][k] for k in ("observed_shares", "max_share_error", "switches")})
    print("Repo audit pages:", [(r["exercise"], r["diagram_count"], r["en_pages"], r["fa_pages"]) for r in payload["repo_audit_ex1_to_6"]])


if __name__ == "__main__":
    main()
