"""Exercise 4 experiments: Formal correctness proofs, SFQ vs PGPS bounds, exhaustive checks & overload.

Produces ``exercise-4/output/experiments.json`` covering:
- Theorem 1 [E]+[M]+[D]: 120 static workloads auditing naive lag <= q across:
  * Start-time GS (index tie): 36/120 exceed q (exact bound (n-1)*q*w_max/W = 21/16 on [1,3,5,7])
  * Start-time GS (max_weight tie): 0/120 violations (max lag/q = 15/16 = 0.9375)
  * PGPS/WFQ virtual finishing-time (used+q)/w: 0/120 behind > q (strict Parekh-Gallager bound!)
  * Plus 5 exhaustive DFS tie-breaker envelopes [E]
- Theorem 2 [E]+[D]: Constructive Omega(t_arr) starvation scaling of gs_ratio vs O(1) bounded gs_vtime & gs_entitled
- Theorem 3 [E]: Exhaustive DFS RT feasibility (allow_idle=False/True) + 100% independent verification across 15 sets
- Theorem 4 [M]: Overload fairness & graceful degradation sweep across U in [1.08 .. 2.00]
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
EX4_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX4_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from gs_core import (  # noqa: E402
    Proc,
    RTTask,
    exhaustive_feasible,
    exhaustive_tie_envelope,
    ideal_gps_trace,
    simulate_procs,
    simulate_rt,
    verify_rt_schedule_independent,
)


def _sim_wfq_finish(procs: List[Proc], quantum: int, trace_out: List[Dict] = None):
    """Exact PGPS/WFQ simulator ordered by virtual finishing time (used + q_step) / w."""
    n = len(procs)
    horizon = sum(p.work for p in procs)
    gps = ideal_gps_trace(procs, horizon=horizon)
    used = [0] * n
    rem = [p.work for p in procs]
    t = 0
    max_abs = 0.0
    max_behind = 0.0
    while t < horizon:
        act = [i for i in range(n) if rem[i] > 0]
        if not act:
            break
        c = min(act, key=lambda i: (Fraction(used[i] + min(quantum, rem[i]), procs[i].weight), i))
        step = min(quantum, rem[c])
        for _ in range(step):
            used[c] += 1
            rem[c] -= 1
            t += 1
            lags_t = []
            for i in range(n):
                lag_f = Fraction(used[i]) - gps["entitled"][t][i]
                lag = float(lag_f)
                lags_t.append((lag_f, lag))
                if abs(lag) > max_abs:
                    max_abs = abs(lag)
                if -lag > max_behind:
                    max_behind = -lag
            if trace_out is not None:
                worst_t = max(abs(x[1]) for x in lags_t)
                trace_out.append({
                    "t": t - 1,
                    "chosen": procs[c].name,
                    "lags_frac": [str(x[0]) for x in lags_t],
                    "max_abs_lag": round(worst_t, 4),
                })
    return max_abs, max_behind


def _sim_eevdf(procs: List[Proc], quantum: int) -> Dict:
    """Exact discrete EEVDF simulator: Eligible (v_i <= V(t)) with Earliest Virtual Deadline."""
    n = len(procs)
    t_end = max(p.arrival for p in procs) + sum(p.work for p in procs) + 5
    gps = ideal_gps_trace(procs, horizon=t_end)
    rem = [p.work for p in procs]
    used = [0] * n
    entered = [False] * n
    vt = [Fraction(0)] * n
    sys_vt = Fraction(0)
    t = 0
    max_abs = 0.0
    max_gap = [0] * n
    cur_gap = [0] * n

    while any(r > 0 for r in rem) and t < t_end:
        act = [i for i in range(n) if procs[i].arrival <= t and rem[i] > 0]
        if not act:
            t += 1
            continue
        for i in act:
            if not entered[i]:
                entered[i] = True
                vt[i] = sys_vt
        eligible = [i for i in act if vt[i] <= sys_vt]
        pool = eligible if eligible else act
        c = min(pool, key=lambda i: (vt[i] + Fraction(min(quantum, rem[i]), procs[i].weight), i))
        step = min(quantum, rem[c])
        for _ in range(step):
            tot_w = sum(procs[i].weight for i in range(n) if procs[i].arrival <= t and rem[i] > 0)
            sys_vt += Fraction(1, tot_w)
            for i in range(n):
                if procs[i].arrival <= t and rem[i] > 0:
                    if i == c:
                        cur_gap[i] = 0
                    else:
                        cur_gap[i] += 1
                        if cur_gap[i] > max_gap[i]:
                            max_gap[i] = cur_gap[i]
            used[c] += 1
            rem[c] -= 1
            vt[c] += Fraction(1, procs[c].weight)
            t += 1
            for i in range(n):
                lag = abs(float(Fraction(used[i]) - gps["entitled"][t][i]))
                if lag > max_abs:
                    max_abs = lag
    return {"max_abs_lag": max_abs, "max_starve_gap": max(max_gap)}


def _sim_trace_lags(procs: List[Proc], policy: str) -> List[Dict]:
    res = simulate_procs(procs, policy, quantum=1)
    gps = ideal_gps_trace(procs, horizon=len(res.timeline))
    used = [0] * len(procs)
    name_to_idx = {p.name: i for i, p in enumerate(procs)}
    out = []
    for t, nm in res.timeline:
        if nm is not None:
            used[name_to_idx[nm]] += 1
        lags_f = [Fraction(used[i]) - gps["entitled"][t + 1][i] for i in range(len(procs))]
        worst = max(abs(float(x)) for x in lags_f)
        out.append({
            "t": t,
            "chosen": nm or "IDLE",
            "lags_frac": [str(x) for x in lags_f],
            "max_abs_lag": round(worst, 4),
        })
    return out


def run_theorem1_lag_bounds() -> Dict:
    """120 static workloads across 10 weight sets x 4 scales x 3 quantums."""
    weight_sets = [
        [1, 1], [1, 3], [2, 5],
        [1, 1, 1], [1, 2, 3], [2, 3, 5], [3, 7, 11],
        [1, 1, 1, 1], [1, 2, 3, 4], [1, 3, 5, 7],
    ]
    policies = ["gs_ratio:index", "gs_vtime:index", "gs_vtime:max_weight",
                "gs_entitled:index", "stride:index", "rr:index", "fifo:index"]
    all_keys = policies + ["wfq_finish", "eevdf"]
    max_lag_seen = {p: 0.0 for p in all_keys}
    lag_over_q_seen = {p: 0.0 for p in all_keys}
    violations_of_q = {p: 0 for p in all_keys}
    wfq_behind_violations = 0
    wfq_max_behind_over_q = 0.0
    per_q_summary = {str(q): {p: [] for p in all_keys} for q in (1, 2, 3)}
    per_weight_rows = []
    q1_40_rows = []
    q2_40_rows = []
    q3_40_rows = []
    n_cases = 0

    for ws in weight_sets:
        ws_viols = {p: 0 for p in ("gs_vtime:index", "gs_vtime:max_weight", "wfq_finish", "eevdf", "rr:index")}
        ws_max_over_q = {p: 0.0 for p in ("gs_vtime:index", "gs_vtime:max_weight", "wfq_finish", "eevdf", "rr:index")}
        for scale in (2, 3, 4, 5):
            procs = [Proc(f"P{i+1}", 0, w * scale + (i % 2), w) for i, w in enumerate(ws)]
            for q in (1, 2, 3):
                n_cases += 1
                row_q = {}
                for pol in policies:
                    res = simulate_procs(procs, pol, quantum=q)
                    per_q_summary[str(q)][pol].append(res.max_abs_lag)
                    max_lag_seen[pol] = max(max_lag_seen[pol], res.max_abs_lag)
                    lag_over_q_seen[pol] = max(lag_over_q_seen[pol], res.max_abs_lag / q)
                    if res.max_abs_lag > q + 1e-9:
                        violations_of_q[pol] += 1
                        if pol in ws_viols:
                            ws_viols[pol] += 1
                    if pol in ws_max_over_q:
                        ws_max_over_q[pol] = max(ws_max_over_q[pol], res.max_abs_lag / q)
                    row_q[pol] = round(res.max_abs_lag, 4)

                w_abs, w_beh = _sim_wfq_finish(procs, q)
                per_q_summary[str(q)]["wfq_finish"].append(w_abs)
                max_lag_seen["wfq_finish"] = max(max_lag_seen["wfq_finish"], w_abs)
                lag_over_q_seen["wfq_finish"] = max(lag_over_q_seen["wfq_finish"], w_abs / q)
                wfq_max_behind_over_q = max(wfq_max_behind_over_q, w_beh / q)
                ws_max_over_q["wfq_finish"] = max(ws_max_over_q["wfq_finish"], w_abs / q)
                if w_abs > q + 1e-9:
                    violations_of_q["wfq_finish"] += 1
                    ws_viols["wfq_finish"] += 1
                if w_beh > q + 1e-9:
                    wfq_behind_violations += 1

                ee_r = _sim_eevdf(procs, q)
                e_abs = ee_r["max_abs_lag"]
                per_q_summary[str(q)]["eevdf"].append(e_abs)
                max_lag_seen["eevdf"] = max(max_lag_seen["eevdf"], e_abs)
                lag_over_q_seen["eevdf"] = max(lag_over_q_seen["eevdf"], e_abs / q)
                ws_max_over_q["eevdf"] = max(ws_max_over_q["eevdf"], e_abs / q)
                if e_abs > q + 1e-9:
                    violations_of_q["eevdf"] += 1
                    ws_viols["eevdf"] += 1

                entry = {
                    "weights": ws,
                    "scale": scale,
                    "total_work": sum(p.work for p in procs),
                    "gs_vtime_index": row_q["gs_vtime:index"],
                    "gs_vtime_max_weight": row_q["gs_vtime:max_weight"],
                    "wfq_finish": round(w_abs, 4),
                    "eevdf": round(e_abs, 4),
                    "rr_index": row_q["rr:index"],
                    "fifo_index": row_q["fifo:index"],
                }
                if q == 1:
                    q1_40_rows.append(entry)
                elif q == 2:
                    q2_40_rows.append(entry)
                else:
                    q3_40_rows.append(entry)
        per_weight_rows.append({
            "weights": ws,
            "sum_w": sum(ws),
            "sfq_bound": round(max(1.0, (len(ws) - 1) * max(ws) / sum(ws)), 4),
            "violations_of_12": ws_viols,
            "max_lag_over_q": {k: round(v, 4) for k, v in ws_max_over_q.items()},
        })

    # Tick-by-tick witness trace on [1, 3, 5, 7] (work = [2, 6, 10, 14], 32 ticks)
    wit_procs = [Proc("P1", 0, 2, 1), Proc("P2", 0, 6, 3), Proc("P3", 0, 10, 5), Proc("P4", 0, 14, 7)]
    wit_idx = _sim_trace_lags(wit_procs, "gs_vtime:index")
    wit_mw = _sim_trace_lags(wit_procs, "gs_vtime:max_weight")
    wit_wfq: List[Dict] = []
    _sim_wfq_finish(wit_procs, 1, trace_out=wit_wfq)

    # Second witness trace on [1, 2, 3, 4] (work = [2, 4, 6, 8], 20 ticks)
    wit2_procs = [Proc("P1", 0, 2, 1), Proc("P2", 0, 4, 2), Proc("P3", 0, 6, 3), Proc("P4", 0, 8, 4)]
    wit2_idx = _sim_trace_lags(wit2_procs, "gs_vtime:index")
    wit2_mw = _sim_trace_lags(wit2_procs, "gs_vtime:max_weight")
    wit2_wfq: List[Dict] = []
    _sim_wfq_finish(wit2_procs, 1, trace_out=wit2_wfq)

    # Exhaustive tie envelopes on 5 canonical static cases
    tie_cases = [
        ("eq_3", [Proc("P1", 0, 4, 1), Proc("P2", 0, 4, 1), Proc("P3", 0, 4, 1)]),
        ("w_1_2_3", [Proc("P1", 0, 3, 1), Proc("P2", 0, 5, 2), Proc("P3", 0, 4, 3)]),
        ("w_1_1_2", [Proc("P1", 0, 4, 1), Proc("P2", 0, 4, 1), Proc("P3", 0, 6, 2)]),
        ("w_1_2_3_4", [Proc("P1", 0, 2, 1), Proc("P2", 0, 4, 2), Proc("P3", 0, 6, 3), Proc("P4", 0, 8, 4)]),
        ("w_1_3_5_7", [Proc("P1", 0, 2, 1), Proc("P2", 0, 6, 3), Proc("P3", 0, 10, 5), Proc("P4", 0, 14, 7)]),
    ]
    envelopes = []
    for label, ps in tie_cases:
        env = exhaustive_tie_envelope(ps, policy="gs_vtime", quantum=1)
        wmax = max(p.weight for p in ps)
        W = sum(p.weight for p in ps)
        sfq_bound = max(1.0, (len(ps) - 1) * wmax / W)
        envelopes.append({
            "case": label,
            "weights": [p.weight for p in ps],
            "states": env["states"],
            "leaves": env["leaves"],
            "truncated": env["truncated"],
            "best_max_lag": round(env["best_max_lag"], 4),
            "worst_max_lag": round(env["worst_max_lag"], 4),
            "worst_max_lag_frac": env["worst_max_lag_frac"],
            "sfq_theoretical_bound": round(sfq_bound, 4),
            "min_switches": env["min_context_switches"],
            "max_switches": env["max_context_switches"],
        })

    q_agg = {}
    for q_str, pol_map in per_q_summary.items():
        q_agg[q_str] = {
            p: {
                "mean_max_lag": round(sum(vals) / len(vals), 4),
                "worst_max_lag": round(max(vals), 4),
            }
            for p, vals in pol_map.items()
        }

    return {
        "n_workloads": n_cases,
        "max_lag_seen": {p: round(v, 4) for p, v in max_lag_seen.items()},
        "max_lag_over_q": {p: round(v, 4) for p, v in lag_over_q_seen.items()},
        "violations_above_q": violations_of_q,
        "wfq_behind_violations_above_q": wfq_behind_violations,
        "wfq_max_behind_over_q": round(wfq_max_behind_over_q, 4),
        "per_q_summary": q_agg,
        "per_weight_summary": per_weight_rows,
        "q1_40_cases": q1_40_rows,
        "q2_40_cases": q2_40_rows,
        "q3_40_cases": q3_40_rows,
        "witness_1357": {
            "weights": [1, 3, 5, 7],
            "works": [2, 6, 10, 14],
            "gs_vtime_index": wit_idx,
            "gs_vtime_max_weight": wit_mw,
            "wfq_finish": wit_wfq,
        },
        "witness_1234": {
            "weights": [1, 2, 3, 4],
            "works": [2, 4, 6, 8],
            "gs_vtime_index": wit2_idx,
            "gs_vtime_max_weight": wit2_mw,
            "wfq_finish": wit2_wfq,
        },
        "exhaustive_tie_envelopes": envelopes,
    }


def run_theorem2_starvation_scaling() -> Dict:
    """Constructive Omega(t_arr) starvation witness for gs_ratio vs O(1) bound for gs_vtime."""
    delays = [2, 4, 8, 12, 16, 24, 32]
    rows = []
    for t1 in delays:
        ps = [Proc("P1", 0, 2 * t1 + 4, 2), Proc("P2", t1, t1 + 6, 2)]
        r_rat = simulate_procs(ps, "gs_ratio:index", 1)
        r_ent = simulate_procs(ps, "gs_entitled:index", 1)
        r_vt = simulate_procs(ps, "gs_vtime:index", 1)
        r_ee = _sim_eevdf(ps, 1)
        rows.append({
            "t_arrival": t1,
            "theoretical_ratio_lag": t1 / 2.0,
            "gs_ratio_lag": round(r_rat.max_abs_lag, 4),
            "gs_ratio_lag_frac": r_rat.max_abs_lag_frac,
            "gs_ratio_gap": r_rat.max_starve_gap,
            "gs_entitled_lag": round(r_ent.max_abs_lag, 4),
            "gs_entitled_gap": r_ent.max_starve_gap,
            "gs_vtime_lag": round(r_vt.max_abs_lag, 4),
            "gs_vtime_gap": r_vt.max_starve_gap,
            "eevdf_lag": round(r_ee["max_abs_lag"], 4),
            "eevdf_gap": r_ee["max_starve_gap"],
        })
    t2_wit_ps = [Proc("P1", 0, 20, 2), Proc("P2", 8, 14, 2)]
    t2_wit_rat = _sim_trace_lags(t2_wit_ps, "gs_ratio:index")
    t2_wit_vt = _sim_trace_lags(t2_wit_ps, "gs_vtime:index")
    t2_witness = [
        {
            "t": a["t"],
            "ratio_choice": a["chosen"],
            "ratio_lag": a["max_abs_lag"],
            "ratio_lags": ", ".join(a["lags_frac"]),
            "vtime_choice": b["chosen"],
            "vtime_lag": b["max_abs_lag"],
        }
        for a, b in zip(t2_wit_rat[:24], t2_wit_vt[:24])
    ]
    return {"scaling_rows": rows, "witness_t8_24t": t2_witness}


def run_theorem3_exhaustive_rt() -> Dict:
    """Exhaustive DFS feasibility + independent verification across 15 RT task sets."""
    rt_sets = [
        ("F01_tight_edf", [RTTask("T1", 5, 2, 2, 1), RTTask("T2", 10, 4, 10, 1)], 10),
        ("F02_harm_full", [RTTask("T1", 4, 2, 4, 2), RTTask("T2", 8, 4, 8, 2)], 8),
        ("F03_forced_slot", [RTTask("T1", 8, 2, 8, 1), RTTask("T2", 3, 2, 3, 1)], 24),
        ("F04_constr_pass", [RTTask("T1", 4, 1, 2, 1), RTTask("T2", 6, 2, 4, 1), RTTask("T3", 12, 4, 12, 1)], 12),
        ("F05_edf_only", [RTTask("T1", 4, 1, 4, 1), RTTask("T2", 6, 2, 3, 1), RTTask("T3", 12, 5, 12, 1)], 12),
        ("F06_dm_sep", [RTTask("T1", 6, 2, 2, 1), RTTask("T2", 4, 1, 4, 1), RTTask("T3", 12, 3, 12, 1)], 12),
        ("F07_u_958", [RTTask("T1", 6, 2, 6, 1), RTTask("T2", 8, 3, 5, 1), RTTask("T3", 12, 3, 12, 1)], 24),
        ("F08_u_100", [RTTask("T1", 4, 1, 4, 1), RTTask("T2", 6, 3, 6, 1), RTTask("T3", 12, 3, 12, 1)], 12),
        ("F09_asym_d", [RTTask("T1", 6, 2, 3, 2), RTTask("T2", 12, 5, 10, 2)], 12),
        ("F10_tri_tight", [RTTask("T1", 5, 2, 3, 1), RTTask("T2", 10, 3, 5, 1), RTTask("T3", 10, 2, 10, 1)], 10),
        ("I01_dbf_fail_917", [RTTask("T1", 4, 2, 2, 1), RTTask("T2", 6, 2, 3, 1), RTTask("T3", 12, 1, 12, 1)], 12),
        ("I02_dbf_fail_833", [RTTask("T1", 6, 3, 3, 1), RTTask("T2", 6, 2, 4, 1)], 12),
        ("I03_overload_108", [RTTask("T1", 4, 2, 4, 1), RTTask("T2", 6, 2, 6, 1), RTTask("T3", 12, 3, 12, 1)], 24),
        ("I04_tight_double", [RTTask("T1", 6, 3, 3, 1), RTTask("T2", 12, 5, 6, 1)], 12),
        ("I05_overload_117", [RTTask("T1", 6, 3, 6, 1), RTTask("T2", 8, 3, 8, 1), RTTask("T3", 12, 4, 12, 1)], 24),
    ]
    rows = []
    verified_ok = 0
    feasible_cnt = 0
    edf_matched_all_feasible = True
    f05_trace = []
    f07_trace = []
    for name, tasks, H in rt_sets:
        u = sum(t.wcet / t.period for t in tasks)
        # Compute peak demand ratio max_L (dbf(L) / L) across checkpoint deadlines up to H
        pts = sorted({k * t.period + t.deadline for t in tasks for k in range(H // t.period + 1)
                      if 0 < k * t.period + t.deadline <= H})
        max_dbf_ratio = 0.0
        peak_L = H
        for L in pts:
            dbf = sum(max(0, (L - t.deadline) // t.period + 1) * t.wcet for t in tasks)
            if dbf / L > max_dbf_ratio:
                max_dbf_ratio = dbf / L
                peak_L = L
        ok_wc, wit_wc, st_wc = exhaustive_feasible(tasks, horizon=H, allow_idle=False)
        ok_id, wit_id, st_id = exhaustive_feasible(tasks, horizon=H, allow_idle=True)
        edf_r = simulate_rt(tasks, "edf", horizon=H)
        dm_r = simulate_rt(tasks, "dm", horizon=H)
        gs_r = simulate_rt(tasks, "gs_vtime", horizon=H)
        indep_ok = None
        if ok_wc and wit_wc is not None:
            feasible_cnt += 1
            indep_ok, _ = verify_rt_schedule_independent(tasks, wit_wc, horizon=H)
            if indep_ok:
                verified_ok += 1
            if edf_r["missed"] != 0:
                edf_matched_all_feasible = False
        if name == "F05_edf_only" and wit_wc is not None:
            for tk in range(H):
                f05_trace.append({
                    "t": tk,
                    "dfs_witness": wit_wc[tk] or "IDLE",
                    "edf": edf_r["timeline"][tk][1] or "IDLE",
                    "dm": dm_r["timeline"][tk][1] or "IDLE",
                    "gs_vtime": gs_r["timeline"][tk][1] or "IDLE",
                })
        if name == "F07_u_958" and wit_wc is not None:
            lim = min(24, H, len(wit_wc), len(edf_r["timeline"]))
            for tk in range(lim):
                f07_trace.append({
                    "t": tk,
                    "dfs_witness": wit_wc[tk] or "IDLE",
                    "edf": edf_r["timeline"][tk][1] or "IDLE",
                    "dm": dm_r["timeline"][tk][1] or "IDLE",
                    "gs_vtime": gs_r["timeline"][tk][1] or "IDLE",
                })
        rows.append({
            "name": name,
            "horizon": H,
            "tasks_spec": "; ".join(f"{t.name}({t.wcet},{t.deadline},{t.period})" for t in tasks),
            "utilization": round(u, 4),
            "peak_dbf_L": peak_L,
            "max_dbf_over_L": round(max_dbf_ratio, 4),
            "exhaustive_wc_feasible": ok_wc,
            "exhaustive_idle_feasible": ok_id,
            "states_wc": st_wc["states"],
            "states_idle": st_id["states"],
            "truncated": st_wc["truncated"] or st_id["truncated"],
            "independent_verified": indep_ok,
            "edf_missed": edf_r["missed"],
            "dm_missed": dm_r["missed"],
            "gs_vtime_missed": gs_r["missed"],
        })
    return {
        "n_sets": len(rows),
        "feasible_count": feasible_cnt,
        "infeasible_count": len(rows) - feasible_cnt,
        "independent_verified_count": verified_ok,
        "edf_100pct_matches_exhaustive": edf_matched_all_feasible,
        "f05_trace_12t": f05_trace,
        "f07_trace_24t": f07_trace,
        "sets": rows,
    }


def run_theorem4_overload_sweep() -> Dict:
    """Sweep overload U in [1.08 .. 2.00] to verify GS fairness lower bound vs RM collapse."""
    configs = [
        ("U_1.08", [RTTask("High", 4, 2, 4, 3), RTTask("Mid", 6, 2, 6, 2), RTTask("Low", 12, 3, 12, 1)]),
        ("U_1.25", [RTTask("High", 4, 2, 4, 3), RTTask("Mid", 6, 3, 6, 2), RTTask("Low", 12, 3, 12, 1)]),
        ("U_1.42", [RTTask("High", 4, 2, 4, 3), RTTask("Mid", 6, 3, 6, 2), RTTask("Low", 12, 5, 12, 1)]),
        ("U_1.58", [RTTask("High", 4, 3, 4, 3), RTTask("Mid", 6, 3, 6, 2), RTTask("Low", 12, 4, 12, 1)]),
        ("U_1.75", [RTTask("High", 4, 3, 4, 3), RTTask("Mid", 6, 3, 6, 2), RTTask("Low", 12, 6, 12, 1)]),
        ("U_2.00", [RTTask("High", 4, 3, 4, 3), RTTask("Mid", 6, 4, 6, 2), RTTask("Low", 12, 7, 12, 1)]),
    ]
    rows = []
    for label, tasks in configs:
        u = sum(t.wcet / t.period for t in tasks)
        eq_tasks = [RTTask(t.name, t.period, t.wcet, t.deadline, 1) for t in tasks]
        pol_res = {}
        for pkey, tlist, pol in [
            ("gs_vtime_eq", eq_tasks, "gs_vtime"),
            ("gs_ratio_eq", eq_tasks, "gs_ratio"),
            ("rr_eq", eq_tasks, "rr"),
            ("edf", eq_tasks, "edf"),
            ("rm", eq_tasks, "rm"),
        ]:
            r = simulate_rt(tlist, pol, horizon=24)
            pol_res[pkey] = {
                "jain": round(r["jain_fairness"], 4),
                "min_sr": round(r["min_task_share_ratio"], 4),
                "missed": r["missed"],
                "low_ticks": r["task_used"]["Low"],
            }
        # Weighted overload (weights 3:2:1 preserved)
        r_wt = simulate_rt(tasks, "gs_vtime", horizon=24)
        r_rm_wt = simulate_rt(tasks, "rm", horizon=24)
        rows.append({
            "label": label,
            "utilization": round(u, 4),
            "policies": pol_res,
            "weighted_gs_vtime": {
                "jain": round(r_wt["jain_fairness"], 4),
                "min_sr": round(r_wt["min_task_share_ratio"], 4),
                "task_used": r_wt["task_used"],
            },
            "weighted_rm": {
                "jain": round(r_rm_wt["jain_fairness"], 4),
                "min_sr": round(r_rm_wt["min_task_share_ratio"], 4),
                "task_used": r_rm_wt["task_used"],
            },
        })
    return {"sweep": rows}


def main() -> None:
    t1 = run_theorem1_lag_bounds()
    t2 = run_theorem2_starvation_scaling()
    t3 = run_theorem3_exhaustive_rt()
    t4 = run_theorem4_overload_sweep()

    payload = {
        "exercise": 4,
        "title": "Formal Correctness Proofs, SFQ vs PGPS Lag Theorems, Exhaustive Verification & Overload",
        "theorem1_lag_bounds": t1,
        "theorem2_starvation_scaling": t2,
        "theorem3_exhaustive_rt": t3,
        "theorem4_overload": t4,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    print("T1 violations_above_q:", t1["violations_above_q"])
    print("T1 max_lag_over_q:", t1["max_lag_over_q"], "wfq_behind_viol:", t1["wfq_behind_violations_above_q"])
    print("T1 envelopes:", [(e["case"], e["states"], e["leaves"], e["worst_max_lag"], e["sfq_theoretical_bound"])
                            for e in t1["exhaustive_tie_envelopes"]])


if __name__ == "__main__":
    main()
