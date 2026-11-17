"""Exercise 3 experiments: Exact fractional hand verification & static vs dynamic divergence.

Produces ``exercise-3/output/experiments.json`` covering:
- Workload 1 [E]+[M]: 12-tick static weighted trace (P1(0,3,1), P2(0,5,2), P3(0,4,3))
  * Independent hand-algebra Fraction derivation vs gs_core (12/12 exact match)
  * Tie-breaker divergence (index vs stay vs max_weight) + exhaustive [E] envelope
- Workload 2 [E]+[M]+[D]: 18-tick dynamic arrival trace (P1(0,8,2), P2(4,6,2), P3(7,4,1))
  * Full tick-by-tick comparison of gs_ratio vs gs_entitled vs gs_vtime
  * Proves latecomer starvation in gs_ratio (lag 29/10) vs bounded gs_vtime (7/10)
- Workload 3 [D]: IEEE-754 float vs exact Fraction virtual-time drift (w=[3, 6, 9])
"""
from __future__ import annotations

import json
import math
import os
import struct
import sys
from fractions import Fraction
from functools import reduce
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
EX3_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX3_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from gs_core import (  # noqa: E402
    Proc,
    exhaustive_tie_envelope,
    gantt_rows,
    ideal_gps_trace,
    simulate_procs,
)


def _hand_trace_static(procs: List[Proc], tie: str = "index") -> List[Dict]:
    """Independent hand-derived exact Fraction trace for static simultaneous arrivals."""
    n = len(procs)
    horizon = sum(p.work for p in procs)
    gps = ideal_gps_trace(procs, horizon=horizon)
    used = [0] * n
    rem = [p.work for p in procs]
    prev = None
    rows = []
    for t in range(horizon):
        ready = [i for i in range(n) if rem[i] > 0]
        ratios = {procs[i].name: str(Fraction(used[i], procs[i].weight)) for i in ready}
        min_r = min(Fraction(used[i], procs[i].weight) for i in ready)
        tied = [procs[i].name for i in ready if Fraction(used[i], procs[i].weight) == min_r]

        if tie == "index":
            chosen = min(ready, key=lambda i: (Fraction(used[i], procs[i].weight), i))
        elif tie == "stay":
            chosen = min(ready, key=lambda i: (Fraction(used[i], procs[i].weight), 0 if i == prev else 1, i))
        elif tie == "max_weight":
            chosen = min(ready, key=lambda i: (Fraction(used[i], procs[i].weight), -procs[i].weight, i))
        else:
            raise ValueError(tie)

        used[chosen] += 1
        rem[chosen] -= 1
        lags_after = {}
        for i in range(n):
            lag_f = Fraction(used[i]) - gps["entitled"][t + 1][i]
            lags_after[procs[i].name] = {
                "actual": used[i],
                "entitled_frac": str(gps["entitled"][t + 1][i]),
                "entitled_dec": round(float(gps["entitled"][t + 1][i]), 4),
                "lag_frac": str(lag_f),
                "lag_dec": round(float(lag_f), 4),
            }
        rows.append({
            "t": t,
            "ready": [procs[i].name for i in ready],
            "ratios_before": ratios,
            "tied_min": tied,
            "chosen": procs[chosen].name,
            "min_ratio_frac": str(min_r),
            "after": lags_after,
        })
        prev = chosen
    return rows


def _hand_trace_dynamic(procs: List[Proc], policy: str) -> List[Dict]:
    """Independent Fraction trace for dynamic arrivals across [gs_ratio, gs_entitled, gs_vtime]."""
    n = len(procs)
    horizon = max(p.arrival for p in procs) + sum(p.work for p in procs)
    gps = ideal_gps_trace(procs, horizon=horizon)
    used = [0] * n
    rem = [p.work for p in procs]
    entitled_on = [Fraction(0)] * n
    vtime = [Fraction(0)] * n
    sys_vtime = Fraction(0)
    entered = [False] * n
    rows = []
    # Only record ticks while work remains (0..17) plus completion state
    total_work = sum(p.work for p in procs)
    for t in range(horizon):
        ready = [i for i in range(n) if procs[i].arrival <= t and rem[i] > 0]
        if not ready:
            break
        for i in ready:
            if not entered[i]:
                entered[i] = True
                if policy == "gs_vtime":
                    vtime[i] = sys_vtime
                elif policy == "stride":
                    active_other = [vtime[k] for k in range(n) if entered[k] and rem[k] > 0 and k != i]
                    vtime[i] = min(active_other) if active_other else Fraction(0)

        if policy == "gs_ratio":
            def score(i):
                return Fraction(used[i], procs[i].weight)
        elif policy == "gs_entitled":
            def score(i):
                return Fraction(0) if entitled_on[i] == 0 else Fraction(used[i]) / entitled_on[i]
        elif policy == "gs_vtime":
            def score(i):
                return vtime[i]
        elif policy == "stride":
            def score(i):
                return vtime[i]
        else:
            raise ValueError(policy)

        scores_before = {procs[i].name: str(score(i)) for i in ready}
        chosen = min(ready, key=lambda i: (score(i), i))

        tot_w = sum(procs[i].weight for i in ready)
        sys_vtime += Fraction(1, tot_w)
        for i in ready:
            entitled_on[i] += Fraction(procs[i].weight, tot_w)

        used[chosen] += 1
        rem[chosen] -= 1
        vtime[chosen] += Fraction(1, procs[chosen].weight)

        after = {}
        for i in range(n):
            lag_f = Fraction(used[i]) - gps["entitled"][t + 1][i]
            after[procs[i].name] = {
                "actual": used[i],
                "gps_frac": str(gps["entitled"][t + 1][i]),
                "lag_frac": str(lag_f),
                "lag_dec": round(float(lag_f), 4),
            }
        rows.append({
            "t": t,
            "ready": [procs[i].name for i in ready],
            "scores_before": scores_before,
            "chosen": procs[chosen].name,
            "sys_vtime_after": str(sys_vtime),
            "after": after,
        })
    assert len(rows) == total_work
    return rows


def _f32(x: float) -> float:
    return struct.unpack("f", struct.pack("f", float(x)))[0]


def _hand_trace_static_quantum(procs: List[Proc], quantum: int, tie: str = "index") -> List[Dict]:
    """Independent hand-derived Fraction trace with multi-tick quantum q >= 1."""
    n = len(procs)
    horizon = sum(p.work for p in procs)
    gps = ideal_gps_trace(procs, horizon=horizon)
    used = [0] * n
    rem = [p.work for p in procs]
    prev = None
    cur = None
    q_left = 0
    rows = []
    for t in range(horizon):
        ready = [i for i in range(n) if rem[i] > 0]
        if cur is None or rem[cur] == 0 or q_left == 0:
            if tie == "index":
                cur = min(ready, key=lambda i: (Fraction(used[i], procs[i].weight), i))
            elif tie == "stay":
                cur = min(ready, key=lambda i: (Fraction(used[i], procs[i].weight), 0 if i == prev else 1, i))
            else:
                raise ValueError(tie)
            q_left = quantum
            dispatch_event = "DISPATCH"
        else:
            dispatch_event = "CONT_Q"

        ratios = {procs[i].name: str(Fraction(used[i], procs[i].weight)) for i in ready}
        used[cur] += 1
        rem[cur] -= 1
        q_left -= 1
        prev = cur
        lags_after = {}
        for i in range(n):
            lag_f = Fraction(used[i]) - gps["entitled"][t + 1][i]
            lags_after[procs[i].name] = {
                "actual": used[i],
                "lag_frac": str(lag_f),
                "lag_dec": round(float(lag_f), 4),
            }
        rows.append({
            "t": t,
            "event": dispatch_event,
            "q_left_after": q_left,
            "ratios_before": ratios,
            "chosen": procs[cur].name,
            "after": lags_after,
        })
    return rows


def run_float_drift_study() -> Dict:
    """Compare exact Fraction virtual-time vs IEEE-754 float64, float32, fixed-point & LCM."""
    from decimal import Decimal, getcontext
    getcontext().prec = 28
    cases = [
        ("w_3_6_9", [3, 6, 9], [30, 60, 90]),
        ("w_3_7_10", [3, 7, 10], [30, 70, 100]),
        ("w_6_10_15", [6, 10, 15], [60, 100, 150]),
        ("w_5_7_11", [5, 7, 11], [50, 70, 110]),
        ("w_1_2_4", [1, 2, 4], [10, 20, 40]),
    ]
    results = []
    primary_trace = []
    precision_matrix = []
    for label, weights, works in cases:
        n = len(weights)
        tot = sum(works)
        rem_ex = list(works)
        rem_fl = list(works)
        vt_ex = [Fraction(0)] * n
        vt_fl = [0.0] * n
        diffs = 0
        first_diff_t = None
        first_diff_detail = None
        ex_seq = []
        for t in range(tot):
            act_ex = [i for i in range(n) if rem_ex[i] > 0]
            ce = min(act_ex, key=lambda i: (vt_ex[i], i))
            rem_ex[ce] -= 1
            vt_ex[ce] += Fraction(1, weights[ce])
            ex_seq.append(ce)

            act_fl = [i for i in range(n) if rem_fl[i] > 0]
            cf = min(act_fl, key=lambda i: (vt_fl[i], i))
            rem_fl[cf] -= 1
            vt_fl[cf] += 1.0 / weights[cf]

            if ce != cf:
                diffs += 1
                if first_diff_t is None:
                    first_diff_t = t
                    first_diff_detail = {
                        "t": t,
                        "exact_choice": f"P{ce+1}",
                        "float_choice": f"P{cf+1}",
                        "exact_vtime_frac": [str(v) for v in vt_ex],
                        "float_vtime_repr": [f"{v:.17g}" for v in vt_fl],
                    }
            if label == "w_3_6_9" and t < 60:
                primary_trace.append({
                    "t": t,
                    "exact": ce,
                    "float": cf,
                    "diverged": ce != cf,
                    "exact_vt": [str(v) for v in vt_ex],
                    "float_vt": [f"{v:.16g}" for v in vt_fl],
                    "diff_ulp_max": max(abs(float(vt_ex[k]) - vt_fl[k]) for k in range(n)),
                })
        results.append({
            "case": label,
            "weights": weights,
            "works": works,
            "total_ticks": tot,
            "diverged_ticks": diffs,
            "diverged_pct": round(100.0 * diffs / tot, 2),
            "first_divergence_t": first_diff_t,
            "first_divergence_detail": first_diff_detail,
        })

        # Compare 6 numerical formats against exact Fraction sequence
        lcm_val = reduce(math.lcm, weights)
        formats = {}
        for fmt in ("float32", "float64", "decimal28", "fixed_q10", "fixed_q20", "lcm_stride"):
            rem_m = list(works)
            if fmt.startswith("float"):
                vt_m = [0.0] * n
            elif fmt == "decimal28":
                vt_m = [Decimal(0)] * n
            else:
                vt_m = [0] * n
            d_cnt = 0
            first_m = None
            max_used_err = 0
            used_m = [0] * n
            used_ex = [0] * n
            for t in range(tot):
                act = [i for i in range(n) if rem_m[i] > 0]
                cm = min(act, key=lambda i: (vt_m[i], i))
                rem_m[cm] -= 1
                used_m[cm] += 1
                used_ex[ex_seq[t]] += 1
                if fmt == "float32":
                    vt_m[cm] = _f32(vt_m[cm] + _f32(1.0 / weights[cm]))
                elif fmt == "float64":
                    vt_m[cm] += 1.0 / weights[cm]
                elif fmt == "decimal28":
                    vt_m[cm] += Decimal(1) / Decimal(weights[cm])
                elif fmt == "fixed_q10":
                    vt_m[cm] += round(1024 / weights[cm])
                elif fmt == "fixed_q20":
                    vt_m[cm] += round((1 << 20) / weights[cm])
                else:  # lcm_stride
                    vt_m[cm] += lcm_val // weights[cm]
                if cm != ex_seq[t]:
                    d_cnt += 1
                    if first_m is None:
                        first_m = t
                max_used_err = max(max_used_err, max(abs(used_m[k] - used_ex[k]) for k in range(n)))
            formats[fmt] = {
                "diverged_ticks": d_cnt,
                "diverged_pct": round(100.0 * d_cnt / tot, 2),
                "first_divergence_t": first_m,
                "max_service_dev_ticks": max_used_err,
            }
        precision_matrix.append({
            "case": label,
            "weights": weights,
            "lcm": lcm_val,
            "total_ticks": tot,
            "formats": formats,
        })
    return {
        "cases": results,
        "primary_first_60": primary_trace,
        "precision_comparison": precision_matrix,
    }


def main() -> None:
    # Workload 1: Static simultaneous arrival
    w1_procs = [
        Proc("P1", arrival=0, work=3, weight=1),
        Proc("P2", arrival=0, work=5, weight=2),
        Proc("P3", arrival=0, work=4, weight=3),
    ]
    hand_w1_idx = _hand_trace_static(w1_procs, tie="index")
    hand_w1_stay = _hand_trace_static(w1_procs, tie="stay")
    hand_w1_mw = _hand_trace_static(w1_procs, tie="max_weight")

    sim_w1 = {}
    for pol in ("gs_ratio:index", "gs_vtime:index", "gs_entitled:index", "stride:index",
                "gs_ratio:stay", "gs_ratio:max_weight", "rr:index"):
        r = simulate_procs(w1_procs, pol, quantum=1)
        d = r.as_dict(keep_timeline=False)
        d["gantt"] = gantt_rows(r.timeline)
        d["seq"] = [nm for _, nm in r.timeline]
        sim_w1[pol] = d

    match_w1_idx = sum(1 for row, nm in zip(hand_w1_idx, sim_w1["gs_ratio:index"]["seq"]) if row["chosen"] == nm)
    match_w1_stay = sum(1 for row, nm in zip(hand_w1_stay, sim_w1["gs_ratio:stay"]["seq"]) if row["chosen"] == nm)
    match_w1_mw = sum(1 for row, nm in zip(hand_w1_mw, sim_w1["gs_ratio:max_weight"]["seq"]) if row["chosen"] == nm)
    env_w1 = exhaustive_tie_envelope(w1_procs, "gs_ratio", quantum=1)

    # Workload 1 quantum sensitivity (q=1, 2, 3) + hand trace verification for q=2
    w1_quantum_runs = {}
    for q in (1, 2, 3):
        for tie in ("index", "stay"):
            r = simulate_procs(w1_procs, f"gs_ratio:{tie}", quantum=q)
            d_q = r.as_dict(keep_timeline=False)
            d_q["gantt"] = gantt_rows(r.timeline)
            d_q["seq"] = [nm for _, nm in r.timeline]
            w1_quantum_runs[f"q{q}_{tie}"] = d_q
    hand_w1_q2_stay = _hand_trace_static_quantum(w1_procs, quantum=2, tie="stay")
    hand_w1_q2_idx = _hand_trace_static_quantum(w1_procs, quantum=2, tie="index")
    hand_w1_q3_stay = _hand_trace_static_quantum(w1_procs, quantum=3, tie="stay")
    match_w1_q2 = sum(1 for row, nm in zip(hand_w1_q2_stay, w1_quantum_runs["q2_stay"]["seq"]) if row["chosen"] == nm)
    match_w1_q2_idx = sum(1 for row, nm in zip(hand_w1_q2_idx, w1_quantum_runs["q2_index"]["seq"]) if row["chosen"] == nm)
    match_w1_q3_stay = sum(1 for row, nm in zip(hand_w1_q3_stay, w1_quantum_runs["q3_stay"]["seq"]) if row["chosen"] == nm)

    # Workload 2: Dynamic arrival
    w2_procs = [
        Proc("P1", arrival=0, work=8, weight=2),
        Proc("P2", arrival=4, work=6, weight=2),
        Proc("P3", arrival=7, work=4, weight=1),
    ]
    hand_w2 = {p: _hand_trace_dynamic(w2_procs, p) for p in ("gs_ratio", "gs_entitled", "gs_vtime")}
    hand_w2_stride = _hand_trace_dynamic(w2_procs, "stride")
    sim_w2 = {}
    matches_w2 = {}
    for pol in ("gs_ratio", "gs_entitled", "gs_vtime", "stride", "rr"):
        r = simulate_procs(w2_procs, f"{pol}:index", quantum=1)
        d = r.as_dict(keep_timeline=False)
        d["gantt"] = gantt_rows(r.timeline)
        d["seq"] = [nm for _, nm in r.timeline[:18]]
        sim_w2[pol] = d
        if pol in hand_w2:
            matches_w2[pol] = sum(1 for row, nm in zip(hand_w2[pol], d["seq"]) if row["chosen"] == nm)
    stride_match_w2 = sum(1 for row, nm in zip(hand_w2_stride, sim_w2["stride"]["seq"]) if row["chosen"] == nm)

    # Workload 3: IEEE-754 float drift
    drift = run_float_drift_study()

    # Workload 4: Asymmetric 24-tick dynamic verification + quantum trade-off [1:3:5]
    w4_procs = [
        Proc("P1", arrival=0, work=7, weight=1),
        Proc("P2", arrival=2, work=9, weight=3),
        Proc("P3", arrival=5, work=8, weight=5),
    ]
    hand_w4_vtime = _hand_trace_dynamic(w4_procs, "gs_vtime")
    hand_w4_ratio = _hand_trace_dynamic(w4_procs, "gs_ratio")
    hand_w4_entitled = _hand_trace_dynamic(w4_procs, "gs_entitled")
    hand_w4_stride = _hand_trace_dynamic(w4_procs, "stride")
    w4_sim = {}
    for q in (1, 2, 3):
        for pol in ("gs_ratio:index", "gs_entitled:index", "gs_vtime:index", "gs_vtime:stay", "stride:index", "rr:index"):
            r = simulate_procs(w4_procs, pol, quantum=q)
            dw4 = r.as_dict(keep_timeline=False)
            dw4["gantt"] = gantt_rows(r.timeline)
            dw4["seq"] = [nm for _, nm in r.timeline[:24]]
            w4_sim[f"{pol}_q{q}"] = dw4
    match_w4_vtime = sum(1 for row, nm in zip(hand_w4_vtime, w4_sim["gs_vtime:index_q1"]["seq"]) if row["chosen"] == nm)
    match_w4_ratio = sum(1 for row, nm in zip(hand_w4_ratio, w4_sim["gs_ratio:index_q1"]["seq"]) if row["chosen"] == nm)
    match_w4_entitled = sum(1 for row, nm in zip(hand_w4_entitled, w4_sim["gs_entitled:index_q1"]["seq"]) if row["chosen"] == nm)
    match_w4_stride = sum(1 for row, nm in zip(hand_w4_stride, w4_sim["stride:index_q1"]["seq"]) if row["chosen"] == nm)

    payload = {
        "exercise": 3,
        "title": "Hand-Worked Exact Fractional Verification vs Programmatic Output",
        "workload1_static": {
            "procs": [{"name": p.name, "arrival": p.arrival, "work": p.work, "weight": p.weight} for p in w1_procs],
            "horizon": 12,
            "hand_trace_index": hand_w1_idx,
            "hand_trace_stay": hand_w1_stay,
            "hand_trace_max_weight": hand_w1_mw,
            "hand_trace_q2_stay": hand_w1_q2_stay,
            "hand_trace_q2_index": hand_w1_q2_idx,
            "hand_trace_q3_stay": hand_w1_q3_stay,
            "q2_stay_match": match_w1_q2,
            "q2_index_match": match_w1_q2_idx,
            "q3_stay_match": match_w1_q3_stay,
            "quantum_runs": w1_quantum_runs,
            "sim_runs": sim_w1,
            "hand_vs_program_matches": {
                "index": match_w1_idx,
                "stay": match_w1_stay,
                "max_weight": match_w1_mw,
                "total_ticks": 12,
            },
            "all_static_equiv": (
                sim_w1["gs_ratio:index"]["seq"] == sim_w1["gs_vtime:index"]["seq"]
                == sim_w1["gs_entitled:index"]["seq"] == sim_w1["stride:index"]["seq"]
            ),
            "exhaustive_tie_envelope": env_w1,
        },
        "workload2_dynamic": {
            "procs": [{"name": p.name, "arrival": p.arrival, "work": p.work, "weight": p.weight} for p in w2_procs],
            "total_work": 18,
            "hand_traces": hand_w2,
            "stride_hand_trace": hand_w2_stride,
            "stride_hand_match": stride_match_w2,
            "sim_runs": sim_w2,
            "hand_vs_program_matches": matches_w2,
        },
        "workload3_float_drift": drift,
        "workload4_asymmetric_audit": {
            "procs": [{"name": p.name, "arrival": p.arrival, "work": p.work, "weight": p.weight} for p in w4_procs],
            "total_work": 24,
            "hand_trace_gs_vtime": hand_w4_vtime,
            "hand_trace_gs_ratio": hand_w4_ratio,
            "hand_trace_gs_entitled": hand_w4_entitled,
            "hand_trace_stride": hand_w4_stride,
            "hand_match_vtime": match_w4_vtime,
            "hand_match_ratio": match_w4_ratio,
            "hand_match_entitled": match_w4_entitled,
            "hand_match_stride": match_w4_stride,
            "sim_runs": w4_sim,
        },
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {out_path}")
    print("W1 matches:", payload["workload1_static"]["hand_vs_program_matches"],
          "all_static_equiv:", payload["workload1_static"]["all_static_equiv"])
    print("W2 matches:", matches_w2,
          "lags:", {p: sim_w2[p]["max_abs_lag_frac"] for p in ("gs_ratio", "gs_entitled", "gs_vtime")})
    print("W3 float drift:", [(c["case"], c["diverged_ticks"], c["total_ticks"], c["first_divergence_t"])
                              for c in drift["cases"]])


if __name__ == "__main__":
    main()
