"""Exercise 3: Hand-Worked Paper Scheduling of EDF & RM with 3 Processes.

Produces exact tick-by-tick hand-trace data, Response-Time Analysis (RTA),
Baruah Demand Bound Function (dbf) audits, and zero-shared-code parity checks
against core/gs_core.py for two canonical 3-process periodic workloads:
  - Set A (Harmonic/Feasible, H=12, U=11/12=0.917): P1(3,1), P2(4,1), P3(6,2)
  - Set B (EDF-vs-RM Separator, H=24, U=23/24=0.958): P1(4,1), P2(6,2), P3(8,3)
  - Set C (Overload Reference, H=12, U=13/12=1.083): P1(3,1), P2(4,2), P3(6,2)
"""
from __future__ import annotations

import json
import math
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
EX3_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX3_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from gs_core import RTTask, simulate_rt  # noqa: E402


def indep_hand_trace_rt(tasks: List[Dict], alg: str, horizon: int, drop_on_miss: bool = False) -> Dict:
    """Zero-shared-code step-by-step paper-style simulator recording ready queue at every tick."""
    # Each job dict: name, job_id, rem, abs_deadline, period, release_t, missed_flag
    active: List[Dict] = []
    job_counts = {t["name"]: 0 for t in tasks}
    rows: List[Dict] = []
    misses: List[Dict] = []
    switches = 0
    preemptions = 0
    prev_chosen = None
    completions = {t["name"]: [] for t in tasks}

    for t in range(horizon):
        arrived_now = []
        for spec in tasks:
            nm = spec["name"]
            if t % spec["period"] == 0:
                jid = job_counts[nm]
                job_counts[nm] += 1
                label = f"{nm}#{jid}"
                active.append({
                    "name": nm,
                    "jid": jid,
                    "label": label,
                    "rem": spec["wcet"],
                    "deadline": t + spec["deadline"],
                    "period": spec["period"],
                    "release": t,
                    "missed": False,
                })
                arrived_now.append(label)

        # Check deadline misses strictly at t (matches gs_core.simulate_rt semantics)
        new_misses_t = []
        for jb in list(active):
            if t >= jb["deadline"] and jb["rem"] > 0 and not jb["missed"]:
                jb["missed"] = True
                mrec = {"tick": t, "job": jb["label"], "deadline": jb["deadline"]}
                misses.append(mrec)
                new_misses_t.append(jb["label"])
                if drop_on_miss:
                    active.remove(jb)

        if not active:
            if prev_chosen is not None:
                switches += 1
            prev_chosen = None
            rows.append({
                "t": t,
                "arrivals": ", ".join(arrived_now) if arrived_now else "-",
                "ready_queue": "EMPTY",
                "chosen": "IDLE",
                "reason": "No ready job",
                "rem_after": "-",
                "miss_at_t": ", ".join(new_misses_t) if new_misses_t else "-",
            })
            continue

        if alg == "EDF":
            active.sort(key=lambda j: (j["deadline"], j["name"], j["jid"]))
            top = active[0]
            reason = f"min abs_d={top['deadline']} ({top['label']})"
        else:  # RM: shortest period P_i
            active.sort(key=lambda j: (j["period"], j["name"], j["jid"]))
            top = active[0]
            reason = f"min P={top['period']} ({top['label']})"

        chosen_label = top["label"]
        ready_str = ", ".join(
            f"{j['label']}(r={j['rem']},d={j['deadline']})" for j in active
        )

        if prev_chosen is not None and prev_chosen != chosen_label:
            switches += 1
            if any(j["label"] == prev_chosen for j in active):
                preemptions += 1

        top["rem"] -= 1
        rem_left = top["rem"]
        if rem_left == 0:
            completions[top["name"]].append({
                "job": chosen_label,
                "release": top["release"],
                "finish": t + 1,
                "response_time": (t + 1) - top["release"],
                "tardy": (t + 1) > top["deadline"],
            })
            active.remove(top)
            prev_chosen = None if not active else chosen_label
        else:
            prev_chosen = chosen_label

        rows.append({
            "t": t,
            "arrivals": ", ".join(arrived_now) if arrived_now else "-",
            "ready_queue": ready_str,
            "chosen": chosen_label,
            "reason": reason,
            "rem_after": f"{chosen_label}:{rem_left}" if rem_left > 0 else f"{chosen_label}:DONE",
            "miss_at_t": ", ".join(new_misses_t) if new_misses_t else "-",
        })

    # Also check exact horizon boundary t == horizon (matches gs_core horizon loop or boundary audit)
    horizon_misses = []
    for jb in active:
        if horizon >= jb["deadline"] and jb["rem"] > 0 and not jb["missed"]:
            horizon_misses.append({"tick": horizon, "job": jb["label"], "deadline": jb["deadline"]})

    return {
        "alg": alg,
        "horizon": horizon,
        "missed_count": len(misses),
        "horizon_boundary_misses": horizon_misses,
        "misses": misses,
        "switches": switches,
        "preemptions": preemptions,
        "timeline": [r["chosen"] for r in rows],
        "trace_rows": rows,
        "completions": completions,
    }


def compute_rta(tasks: List[Dict]) -> List[Dict]:
    """Exact fixed-point Response-Time Analysis (RTA) for Rate-Monotonic priority order."""
    ordered = sorted(tasks, key=lambda x: (x["period"], x["name"]))
    out = []
    for idx, t_i in enumerate(ordered):
        c_i = t_i["wcet"]
        d_i = t_i["deadline"]
        r = c_i
        iters = [r]
        feasible = True
        while True:
            interference = 0
            for t_j in ordered[:idx]:
                interference += math.ceil(r / t_j["period"]) * t_j["wcet"]
            r_next = c_i + interference
            if r_next == r:
                break
            iters.append(r_next)
            if r_next > d_i:
                feasible = False
                r = r_next
                break
            r = r_next
        out.append({
            "name": t_i["name"],
            "period": t_i["period"],
            "wcet": c_i,
            "deadline": d_i,
            "priority": idx + 1,
            "iterations": iters,
            "worst_R_i": r,
            "rta_feasible": feasible and r <= d_i,
        })
    return out


def compute_dbf_curve(tasks: List[Dict], horizon: int) -> List[Dict]:
    """Baruah exact Processor Demand Bound Function dbf(L) vs supply L for t=1..horizon."""
    rows = []
    for L in range(1, horizon + 1):
        demand = 0
        terms = []
        for t in tasks:
            cnt = max(0, math.floor((L + t["period"] - t["deadline"]) / t["period"]))
            contrib = cnt * t["wcet"]
            demand += contrib
            terms.append(f"{t['name']}:{contrib}")
        rows.append({
            "L": L,
            "dbf": demand,
            "margin": L - demand,
            "feasible_at_L": demand <= L,
            "breakdown": ", ".join(terms),
        })
    return rows


def analyze_set(key: str, label: str, tasks_spec: List[Dict], horizon: int) -> Dict:
    n = len(tasks_spec)
    ll_bound = round(n * (2 ** (1 / n) - 1), 6)
    u_frac = sum(Fraction(t["wcet"], t["period"]) for t in tasks_spec)
    u_float = round(float(u_frac), 6)

    rt_objs = [RTTask(t["name"], t["period"], t["wcet"], t["deadline"]) for t in tasks_spec]
    gs_edf = simulate_rt(rt_objs, "edf:index", horizon)
    gs_rm = simulate_rt(rt_objs, "rm:index", horizon)
    gs_vtime = simulate_rt(rt_objs, "gs_vtime:stay", horizon)

    hand_edf = indep_hand_trace_rt(tasks_spec, "EDF", horizon)
    hand_rm = indep_hand_trace_rt(tasks_spec, "RM", horizon)

    gs_edf_tl = [x[1] if x[1] is not None else "IDLE" for x in gs_edf["timeline"]]
    gs_rm_tl = [x[1] if x[1] is not None else "IDLE" for x in gs_rm["timeline"]]

    assert hand_edf["timeline"] == gs_edf_tl, f"EDF mismatch on {key}!"
    assert hand_rm["timeline"] == gs_rm_tl, f"RM mismatch on {key}!"
    assert hand_edf["missed_count"] == gs_edf["missed"], f"EDF miss count mismatch on {key}!"
    assert hand_rm["missed_count"] == gs_rm["missed"], f"RM miss count mismatch on {key}!"

    rta = compute_rta(tasks_spec)
    dbf = compute_dbf_curve(tasks_spec, horizon)

    # Compute first-tick divergence between EDF and RM
    diffs = [
        {"t": t, "edf": e, "rm": r}
        for t, (e, r) in enumerate(zip(hand_edf["timeline"], hand_rm["timeline"]))
        if e != r
    ]

    return {
        "key": key,
        "label": label,
        "horizon": horizon,
        "tasks": tasks_spec,
        "utilization_frac": f"{u_frac.numerator}/{u_frac.denominator}",
        "utilization": u_float,
        "liu_layland_bound": ll_bound,
        "above_ll_bound": u_float > ll_bound,
        "hand_vs_gs_core_parity": True,
        "edf": hand_edf,
        "rm": hand_rm,
        "gs_vtime_ref": {
            "missed": gs_vtime["missed"],
            "timeline": [x[1] if x[1] is not None else "IDLE" for x in gs_vtime["timeline"]],
        },
        "edf_vs_rm_diff_ticks": diffs,
        "rta_rm": rta,
        "dbf_edf": dbf,
        "max_dbf_ratio": round(max(r["dbf"] / r["L"] for r in dbf), 4),
    }


def main() -> None:
    set_a = analyze_set(
        "set_a_harmonic_feasible",
        "Set A (Harmonic Feasible Paper Exercise, H=12, U=11/12=0.9167)",
        [
            {"name": "P1", "period": 3, "wcet": 1, "deadline": 3},
            {"name": "P2", "period": 4, "wcet": 1, "deadline": 4},
            {"name": "P3", "period": 6, "wcet": 2, "deadline": 6},
        ],
        horizon=12,
    )
    set_b = analyze_set(
        "set_b_edf_beats_rm",
        "Set B (Classic EDF vs RM Separator, H=24, U=23/24=0.9583)",
        [
            {"name": "P1", "period": 4, "wcet": 1, "deadline": 4},
            {"name": "P2", "period": 6, "wcet": 2, "deadline": 6},
            {"name": "P3", "period": 8, "wcet": 3, "deadline": 8},
        ],
        horizon=24,
    )
    set_c = analyze_set(
        "set_c_overload_domino",
        "Set C (Two-Hyperperiod Overload Domino, 2H=24, U=7/6=1.1667)",
        [
            {"name": "P1", "period": 3, "wcet": 1, "deadline": 3},
            {"name": "P2", "period": 4, "wcet": 2, "deadline": 4},
            {"name": "P3", "period": 6, "wcet": 2, "deadline": 6},
        ],
        horizon=24,
    )

    payload = {
        "exercise": "exercise-3",
        "topic": "Paper Hand-Worked Scheduling of EDF & RM with 3 Processes + Programmatic Audit",
        "set_a": set_a,
        "set_b": set_b,
        "set_c": set_c,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print("Wrote", out_path)
    for k in ("set_a", "set_b", "set_c"):
        s = payload[k]
        print(f"  {k}: U={s['utilization_frac']} ({s['utilization']:.4f}), EDF misses={s['edf']['missed_count']}, RM misses={s['rm']['missed_count']}, parity={s['hand_vs_gs_core_parity']}")


if __name__ == "__main__":
    main()
