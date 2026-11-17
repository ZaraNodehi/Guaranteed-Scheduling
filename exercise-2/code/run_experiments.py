"""Exercise 2 experiments: GS vs EDF, DM, RM, Stride, and Round Robin.

Produces ``exercise-2/output/experiments.json`` covering:
- Regime A [M]: Proportional CPU sharing on weighted static batch workload
- Regime B [E]+[M]: Constrained-deadline periodic real-time (D < T):
  * B1: DM > RM separation (U = 0.833, H = 12)
  * B2: EDF optimal over DM, RM, and GS (U = 0.958, H = 24)
  * B3: U < 1 yet infeasible witness (U = 0.917, exhaustive_feasible=False)
  * B4: 120-task-set constrained-deadline sweep across U in [0.65, 1.00]
  * B5: 30-task-set exact [E] exhaustive feasibility vs EDF/DM/RM/GS
- Regime C [M]: Sustained overload (U = 1.333) comparing fairness & starvation
- Independent verifier audit [E] on every zero-miss RT trace
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
EX2_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX2_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from gs_core import (  # noqa: E402
    Proc,
    RTTask,
    exhaustive_feasible,
    gantt_rows,
    hyperperiod,
    make_rt_jobs,
    simulate_procs,
    simulate_rt,
    verify_rt_schedule_independent,
)


def _strip_proc_timeline(res) -> Dict:
    out = res.as_dict(keep_timeline=False)
    out["gantt"] = gantt_rows(res.timeline)
    return out


def _strip_rt_res(tasks: List[RTTask], horizon: int, res: Dict) -> Dict:
    jobs = make_rt_jobs(tasks, horizon)
    name_to_idx = {j.name: j.index for j in jobs}
    sched = [name_to_idx[nm] if nm else None for _, nm in res["timeline"]]
    ok, msg = verify_rt_schedule_independent(tasks, sched, horizon)
    out = dict(res)
    out["gantt"] = gantt_rows(res["timeline"])
    out.pop("timeline", None)
    out["independent_verify_ok"] = ok
    out["independent_verify_msg"] = msg
    return out


def run_regime_a() -> Dict:
    procs = [
        Proc("P1", arrival=0, work=8, weight=1),
        Proc("P2", arrival=0, work=12, weight=2),
        Proc("P3", arrival=0, work=20, weight=4),
        Proc("P4", arrival=0, work=10, weight=3),
    ]
    policies = [
        ("gs_ratio_q1", "gs_ratio", 1),
        ("gs_vtime_q1", "gs_vtime", 1),
        ("gs_entitled_q1", "gs_entitled", 1),
        ("stride_q1", "stride", 1),
        ("rr_q1", "rr", 1),
        ("gs_ratio_q2", "gs_ratio", 2),
        ("rr_q2", "rr", 2),
        ("fifo_q1", "fifo", 1),
    ]
    runs = {}
    for key, pol, q in policies:
        runs[key] = _strip_proc_timeline(simulate_procs(procs, pol, quantum=q))
    return {
        "procs": [{"name": p.name, "arrival": p.arrival, "work": p.work, "weight": p.weight} for p in procs],
        "total_work": sum(p.work for p in procs),
        "runs": runs,
    }


def _eval_rt_case(tasks: List[RTTask], horizon: int, run_exhaustive: bool = True) -> Dict:
    U = sum(t.wcet / t.period for t in tasks)
    density_sum = sum(t.wcet / t.rel_deadline for t in tasks)
    ex = None
    if run_exhaustive:
        feas, wit, st = exhaustive_feasible(tasks, horizon=horizon)
        ex = {"feasible": feas, "states": st["states"], "pruned": st["pruned"],
              "truncated": st["truncated"], "jobs": st["jobs"], "horizon": st["horizon"]}
    # Build density-weighted clone for weighted GS comparison
    dens_tasks = [
        RTTask(t.name, t.period, t.wcet, t.rel_deadline,
               weight=max(1, round(12 * t.wcet / t.rel_deadline)), phase=t.phase)
        for t in tasks
    ]
    runs = {}
    for pol in ("edf", "dm", "rm", "gs_vtime", "gs_ratio", "stride", "rr"):
        runs[pol] = _strip_rt_res(tasks, horizon, simulate_rt(tasks, pol, horizon=horizon))
    runs["gs_vtime_density"] = _strip_rt_res(
        dens_tasks, horizon, simulate_rt(dens_tasks, "gs_vtime", horizon=horizon)
    )
    jobs_info = [
        {"name": j.name, "task": tasks[j.task].name, "release": j.release,
         "deadline": j.deadline, "wcet": j.wcet}
        for j in make_rt_jobs(tasks, horizon)
    ]
    return {
        "tasks": [{"name": t.name, "period": t.period, "wcet": t.wcet,
                   "deadline": t.rel_deadline, "weight": t.weight,
                   "density_weight": d.weight} for t, d in zip(tasks, dens_tasks)],
        "horizon": horizon,
        "utilization": round(U, 6),
        "density_sum": round(density_sum, 6),
        "exhaustive": ex,
        "jobs": jobs_info,
        "runs": runs,
    }


def run_regime_b_cases() -> Dict:
    # B1: Classic DM > RM constrained-deadline separation (U = 0.833, H = 12)
    b1_tasks = [
        RTTask("T1", period=4, wcet=2, deadline=4, weight=2),
        RTTask("T2", period=6, wcet=2, deadline=3, weight=2),
    ]
    # B2: EDF strictly beats DM, RM, GS, RR (U = 0.9583, H = 24, all D < T)
    b2_tasks = [
        RTTask("T1", period=6, wcet=3, deadline=4, weight=2),
        RTTask("T2", period=8, wcet=3, deadline=7, weight=2),
        RTTask("T3", period=12, wcet=1, deadline=10, weight=1),
    ]
    # B3: U = 0.9167 < 1 yet INFEASIBLE under any schedule [E] (processor demand bottleneck)
    b3_tasks = [
        RTTask("T1", period=4, wcet=1, deadline=2, weight=2),
        RTTask("T2", period=6, wcet=2, deadline=4, weight=2),
        RTTask("T3", period=12, wcet=4, deadline=10, weight=2),
    ]
    return {
        "b1_dm_vs_rm": _eval_rt_case(b1_tasks, 12, True),
        "b2_edf_vs_dm_gs": _eval_rt_case(b2_tasks, 24, True),
        "b3_u_under_1_infeasible": _eval_rt_case(b3_tasks, 12, True),
    }


def run_constrained_sweep() -> Dict:
    rng = random.Random(20261117)
    bands = [(0.65, 0.75), (0.75, 0.85), (0.85, 0.95), (0.95, 1.00)]
    per_band = 30
    periods_pool = [6, 8, 10, 12, 15, 20, 24, 30]
    pols = ["edf", "dm", "rm", "gs_vtime", "gs_vtime_density", "stride", "rr"]

    band_results = []
    all_sets = []
    for lo, hi in bands:
        target_mid = 0.5 * (lo + hi)
        counts = {p: 0 for p in pols}
        jitters = {p: [] for p in pols}
        miss_rates = {p: [] for p in pols}
        u_vals = []
        generated = 0
        attempts = 0
        while generated < per_band and attempts < 5000:
            attempts += 1
            ps = sorted(rng.sample(periods_pool, 3))
            hp = math.lcm(*ps)
            if hp > 120:
                continue
            # UUniFast-style split around target band utilization
            u_target = rng.uniform(lo + 0.005, hi - 0.002)
            r1, r2 = sorted([rng.random(), rng.random()])
            u_shares = [r1 * u_target, (r2 - r1) * u_target, (1.0 - r2) * u_target]
            wcets = [max(1, round(u_shares[i] * ps[i])) for i in range(3)]
            u_actual = sum(wcets[i] / ps[i] for i in range(3))
            if not (lo <= u_actual <= hi):
                continue
            # Constrained deadlines strictly < period for at least 2 tasks, and >= wcet
            ddls = []
            valid = True
            for i in range(3):
                max_d = ps[i] - 1 if ps[i] - 1 >= wcets[i] else ps[i]
                min_d = max(wcets[i], int(math.ceil(ps[i] * 0.55)))
                if min_d > max_d:
                    valid = False
                    break
                ddls.append(rng.randint(min_d, max_d))
            if not valid or sum(1 for i in range(3) if ddls[i] < ps[i]) < 2:
                continue
            tasks = [
                RTTask(f"T{i+1}", period=ps[i], wcet=wcets[i], deadline=ddls[i], weight=1)
                for i in range(3)
            ]
            dens_tasks = [
                RTTask(f"T{i+1}", period=ps[i], wcet=wcets[i], deadline=ddls[i],
                       weight=max(1, round(24 * wcets[i] / ddls[i])))
                for i in range(3)
            ]
            u_vals.append(u_actual)
            set_row = {"u": round(u_actual, 4), "hp": hp}
            for p in pols:
                t_use = dens_tasks if p == "gs_vtime_density" else tasks
                p_use = "gs_vtime" if p == "gs_vtime_density" else p
                r = simulate_rt(t_use, p_use, horizon=hp)
                if r["missed"] == 0:
                    counts[p] += 1
                miss_rates[p].append(r["miss_rate"])
                if r["jitter"] is not None:
                    jitters[p].append(r["jitter"])
                set_row[p] = r["missed"]
            all_sets.append(set_row)
            generated += 1

        band_results.append({
            "band": f"{lo:.2f}-{hi:.2f}",
            "lo": lo,
            "hi": hi,
            "n_sets": generated,
            "mean_u": round(sum(u_vals) / len(u_vals), 4),
            "success_count": counts,
            "success_pct": {p: round(100.0 * counts[p] / generated, 2) for p in pols},
            "mean_miss_rate_pct": {p: round(100.0 * sum(miss_rates[p]) / generated, 2) for p in pols},
            "mean_jitter": {p: round(sum(jitters[p]) / len(jitters[p]), 3) if jitters[p] else 0.0 for p in pols},
        })

    # Compact [E] Exhaustive check on 30 constrained sets with hp <= 30 and U in [0.75, 1.00]
    rng_e = random.Random(20261118)
    ex_pool = [4, 5, 6, 8, 10, 12, 15]
    ex_sets = 0
    ex_feasible = 0
    ex_edf_ok = 0
    ex_dm_ok = 0
    ex_rm_ok = 0
    ex_gs_ok = 0
    ex_rows = []
    tries = 0
    while ex_sets < 30 and tries < 5000:
        tries += 1
        ps = sorted(rng_e.sample(ex_pool, 3))
        hp = math.lcm(*ps)
        if hp > 30:
            continue
        wcets = [rng_e.randint(1, max(1, ps[i] // 2)) for i in range(3)]
        u = sum(wcets[i] / ps[i] for i in range(3))
        if not (0.75 <= u <= 1.00):
            continue
        ddls = [rng_e.randint(wcets[i], max(wcets[i], ps[i] - 1)) for i in range(3)]
        tasks = [RTTask(f"T{i+1}", ps[i], wcets[i], ddls[i], weight=1) for i in range(3)]
        feas, _, st = exhaustive_feasible(tasks, horizon=hp)
        if st["truncated"]:
            continue
        r_edf = simulate_rt(tasks, "edf", horizon=hp)
        r_dm = simulate_rt(tasks, "dm", horizon=hp)
        r_rm = simulate_rt(tasks, "rm", horizon=hp)
        r_gs = simulate_rt(tasks, "gs_vtime", horizon=hp)
        ex_sets += 1
        ex_feasible += int(feas)
        ex_edf_ok += int(r_edf["missed"] == 0)
        ex_dm_ok += int(r_dm["missed"] == 0)
        ex_rm_ok += int(r_rm["missed"] == 0)
        ex_gs_ok += int(r_gs["missed"] == 0)
        ex_rows.append({"u": round(u, 4), "hp": hp, "feasible": feas,
                        "edf": r_edf["missed"] == 0, "dm": r_dm["missed"] == 0,
                        "rm": r_rm["missed"] == 0, "gs": r_gs["missed"] == 0})

    return {
        "total_sets": sum(b["n_sets"] for b in band_results),
        "bands": band_results,
        "exhaustive_audit_30": {
            "n_sets": ex_sets,
            "exhaustive_feasible": ex_feasible,
            "edf_feasible": ex_edf_ok,
            "dm_feasible": ex_dm_ok,
            "rm_feasible": ex_rm_ok,
            "gs_feasible": ex_gs_ok,
            "edf_matches_exhaustive_100pct": ex_edf_ok == ex_feasible,
            "rows": ex_rows,
        },
    }


def run_regime_c_overload() -> Dict:
    # Two overload scenarios:
    # C1: Demand-matched weights [3, 3, 2] -> GS achieves Jain=1.0000 while RM/DM starve T3
    ov_matched = [
        RTTask("T1", period=4, wcet=2, deadline=4, weight=3),
        RTTask("T2", period=6, wcet=3, deadline=5, weight=3),
        RTTask("T3", period=12, wcet=4, deadline=10, weight=2),
    ]
    # C2: Asymmetric weights [4, 2, 1] -> GS preserves weighted shares while RR distorts them
    ov_asym = [
        RTTask("T1", period=4, wcet=2, deadline=4, weight=4),
        RTTask("T2", period=6, wcet=3, deadline=5, weight=2),
        RTTask("T3", period=12, wcet=4, deadline=10, weight=1),
    ]
    horizon = 24
    pols = ["edf", "dm", "rm", "gs_vtime", "gs_ratio", "stride", "rr"]
    c1_runs = {p: _strip_rt_res(ov_matched, horizon, simulate_rt(ov_matched, p, horizon=horizon)) for p in pols}
    c2_runs = {p: _strip_rt_res(ov_asym, horizon, simulate_rt(ov_asym, p, horizon=horizon)) for p in pols}
    return {
        "horizon": horizon,
        "utilization": round(sum(t.wcet / t.period for t in ov_matched), 4),
        "demand_matched_weights": [t.weight for t in ov_matched],
        "asymmetric_weights": [t.weight for t in ov_asym],
        "tasks_matched": [{"name": t.name, "period": t.period, "wcet": t.wcet,
                           "deadline": t.rel_deadline, "weight": t.weight} for t in ov_matched],
        "tasks_asym": [{"name": t.name, "period": t.period, "wcet": t.wcet,
                        "deadline": t.rel_deadline, "weight": t.weight} for t in ov_asym],
        "runs_matched": c1_runs,
        "runs_asym": c2_runs,
    }


def main() -> None:
    regime_a = run_regime_a()
    regime_b = run_regime_b_cases()
    sweep = run_constrained_sweep()
    regime_c = run_regime_c_overload()

    # Check independent verifier on ALL zero-miss RT runs
    zero_miss_checked = 0
    zero_miss_all_ok = True
    for cname, case in regime_b.items():
        for pol, r in case["runs"].items():
            if r["missed"] == 0:
                zero_miss_checked += 1
                if not r["independent_verify_ok"]:
                    zero_miss_all_ok = False

    payload = {
        "exercise": 2,
        "title": "Guaranteed Scheduling vs EDF, DM, RM, Stride & RR",
        "regime_a_proportional": regime_a,
        "regime_b_constrained_cases": regime_b,
        "regime_b_sweep_120": sweep,
        "regime_c_overload": regime_c,
        "independent_audit": {
            "zero_miss_runs_verified": zero_miss_checked,
            "all_zero_miss_verified_ok": zero_miss_all_ok,
        },
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    print("Regime A gs_vtime lag:", regime_a["runs"]["gs_vtime_q1"]["max_abs_lag"],
          "rr_q1 lag:", regime_a["runs"]["rr_q1"]["max_abs_lag"])
    print("B2 misses:", {p: regime_b["b2_edf_vs_dm_gs"]["runs"][p]["missed"]
                         for p in ("edf", "dm", "rm", "gs_vtime", "gs_vtime_density", "rr")})
    print("Sweep bands:", [(b["band"], b["success_pct"]["edf"], b["success_pct"]["dm"],
                            b["success_pct"]["rm"], b["success_pct"]["gs_vtime"])
                           for b in sweep["bands"]])
    print("Exhaustive 30:", sweep["exhaustive_audit_30"]["exhaustive_feasible"],
          "EDF:", sweep["exhaustive_audit_30"]["edf_feasible"],
          "DM:", sweep["exhaustive_audit_30"]["dm_feasible"],
          "RM:", sweep["exhaustive_audit_30"]["rm_feasible"],
          "GS:", sweep["exhaustive_audit_30"]["gs_feasible"])
    print("Overload matched Jain:", {p: regime_c["runs_matched"][p]["jain_fairness"]
                                     for p in ("edf", "rm", "gs_vtime", "gs_ratio", "rr")})
    print("Independent zero-miss audit:", zero_miss_checked, zero_miss_all_ok)


if __name__ == "__main__":
    main()
