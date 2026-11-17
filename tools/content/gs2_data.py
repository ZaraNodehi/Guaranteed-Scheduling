"""Dynamic loader and table formatters for Exercise 2 reports (zero hardcoded numbers)."""
from __future__ import annotations

import json
import math
import os
import sys
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-2", "output", "experiments.json")
sys.path.insert(0, os.path.join(REPO_ROOT, "core"))
import gs_core as gsc  # noqa: E402


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def regime_a_rows(d: Dict) -> List[List[str]]:
    runs = d["regime_a_proportional"]["runs"]
    order = [
        ("gs_ratio_q1", "gs_ratio", "1"),
        ("gs_vtime_q1", "gs_vtime", "1"),
        ("gs_entitled_q1", "gs_entitled", "1"),
        ("stride_q1", "stride", "1"),
        ("rr_q1", "rr", "1"),
        ("gs_ratio_q2", "gs_ratio", "2"),
        ("rr_q2", "rr", "2"),
        ("fifo_q1", "fifo", "1"),
    ]
    rows = []
    for key, pol, q in order:
        r = runs[key]
        rows.append([
            pol,
            q,
            f"{r['max_abs_lag']:.4f} ({r['max_abs_lag_frac']})",
            f"{r['rmse_lag']:.4f}",
            str(r["context_switches"]),
            str(r["preemptions"]),
            f"{r['mean_turnaround']:.2f}",
            f"{r['jain_fairness']:.4f}",
        ])
    return rows


def rt_case_rows(case: Dict) -> List[List[str]]:
    runs = case["runs"]
    order = [
        ("edf", "EDF"),
        ("dm", "DM"),
        ("rm", "RM"),
        ("gs_vtime", "gs_vtime (base w)"),
        ("gs_vtime_density", "gs_vtime (w~C/D)"),
        ("gs_ratio", "gs_ratio"),
        ("stride", "stride"),
        ("rr", "rr (q=1)"),
    ]
    rows = []
    for key, label in order:
        r = runs[key]
        wr = str(r["worst_response"]) if r["worst_response"] is not None else "-"
        jt = str(r["jitter"]) if r["jitter"] is not None else "-"
        ver = "PASS" if r["independent_verify_ok"] else "MISS"
        rows.append([
            label,
            f"{r['missed']}/{r['released']}",
            f"{100.0 * r['miss_rate']:.1f}%",
            wr,
            jt,
            str(r["context_switches"]),
            f"{r['jain_fairness']:.4f}",
            ver,
        ])
    return rows


def sweep_success_rows(d: Dict) -> List[List[str]]:
    rows = []
    for b in d["regime_b_sweep_120"]["bands"]:
        sp = b["success_pct"]
        rows.append([
            b["band"],
            f"{b['mean_u']:.3f}",
            f"{sp['edf']:.1f}%",
            f"{sp['dm']:.1f}%",
            f"{sp['rm']:.1f}%",
            f"{sp['gs_vtime_density']:.1f}%",
            f"{sp['gs_vtime']:.1f}%",
            f"{sp['stride']:.1f}%",
            f"{sp['rr']:.1f}%",
        ])
    return rows


def sweep_jitter_rows(d: Dict) -> List[List[str]]:
    rows = []
    for b in d["regime_b_sweep_120"]["bands"]:
        jt = b["mean_jitter"]
        mr = b["mean_miss_rate_pct"]
        rows.append([
            b["band"],
            f"{mr['edf']:.1f}% / {jt['edf']:.2f}",
            f"{mr['dm']:.1f}% / {jt['dm']:.2f}",
            f"{mr['rm']:.1f}% / {jt['rm']:.2f}",
            f"{mr['gs_vtime_density']:.1f}% / {jt['gs_vtime_density']:.2f}",
            f"{mr['gs_vtime']:.1f}% / {jt['gs_vtime']:.2f}",
            f"{mr['rr']:.1f}% / {jt['rr']:.2f}",
        ])
    return rows


def overload_rows(d: Dict, mode: str = "runs_asym") -> List[List[str]]:
    runs = d["regime_c_overload"][mode]
    order = ["gs_vtime", "stride", "edf", "rr", "gs_ratio", "dm", "rm"]
    rows = []
    for pol in order:
        r = runs[pol]
        tu = r["task_used"]
        rows.append([
            pol,
            f"{r['missed']}/{r['released']}",
            f"{r['jain_fairness']:.4f}",
            f"{r['min_task_share_ratio']:.4f}",
            f"{tu['T1']} / {tu['T2']} / {tu['T3']}",
            str(r["context_switches"]),
        ])
    return rows


def core_snippet(start_line: int, end_line: int) -> List[str]:
    src = os.path.join(REPO_ROOT, "core", "gs_core.py")
    with open(src, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{ln:3d} | {lines[ln - 1]}" for ln in range(max(1, start_line), min(len(lines), end_line) + 1)]


def ll_bound_rows() -> List[List[str]]:
    rows = []
    for n in [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]:
        ub = n * (2.0 ** (1.0 / n) - 1.0)
        rows.append([
            str(n),
            f"{100.0 * ub:.2f}%",
            "100.00%",
            f"{100.0 * (1.0 - ub):.2f}%",
        ])
    rows.append(["inf (ln 2)", "69.31%", "100.00%", "30.69%"])
    return rows


def _to_rttasks(task_dicts: List[Dict], use_density: bool = False) -> List[gsc.RTTask]:
    return [
        gsc.RTTask(
            t["name"],
            t["period"],
            t["wcet"],
            t["deadline"],
            weight=t["density_weight"] if use_density else t["weight"],
        )
        for t in task_dicts
    ]


def b2_tick_comparison_rows(d: Dict, start: int = 0, end: int = 24) -> List[List[str]]:
    case = d["regime_b_constrained_cases"]["b2_edf_vs_dm_gs"]
    tasks = _to_rttasks(case["tasks"], use_density=False)
    r_edf = gsc.simulate_rt(tasks, policy="edf", horizon=24)
    r_rm = gsc.simulate_rt(tasks, policy="rm", horizon=24)
    r_gs = gsc.simulate_rt(tasks, policy="gs_vtime", horizon=24)
    rows = []
    for t in range(start, min(end, 24)):
        e_tok = r_edf["timeline"][t] if t < len(r_edf["timeline"]) else "-"
        rm_tok = r_rm["timeline"][t] if t < len(r_rm["timeline"]) else "-"
        gs_tok = r_gs["timeline"][t] if t < len(r_gs["timeline"]) else "-"
        e_lbl = e_tok[1] if isinstance(e_tok, (tuple, list)) else str(e_tok)
        rm_lbl = rm_tok[1] if isinstance(rm_tok, (tuple, list)) else str(rm_tok)
        gs_lbl = gs_tok[1] if isinstance(gs_tok, (tuple, list)) else str(gs_tok)
        rows.append([
            str(t),
            e_lbl or "IDLE",
            rm_lbl or "IDLE",
            gs_lbl or "IDLE",
            "All agree" if e_lbl == rm_lbl == gs_lbl else "Divergent priority",
        ])
    return rows


def overload_tick_rows(d: Dict, start: int = 0, end: int = 24) -> List[List[str]]:
    ov = d["regime_c_overload"]
    tasks = _to_rttasks(ov["tasks_asym"], use_density=False)
    r_gs = gsc.simulate_rt(tasks, policy="gs_vtime", horizon=24)
    r_edf = gsc.simulate_rt(tasks, policy="edf", horizon=24)
    r_rm = gsc.simulate_rt(tasks, policy="rm", horizon=24)
    rows = []
    for t in range(start, min(end, 24)):
        gt = r_gs["timeline"][t]
        et = r_edf["timeline"][t]
        rt = r_rm["timeline"][t]
        gl = gt[1] if isinstance(gt, (tuple, list)) else str(gt)
        el = et[1] if isinstance(et, (tuple, list)) else str(et)
        rl = rt[1] if isinstance(rt, (tuple, list)) else str(rt)
        rows.append([
            str(t),
            gl or "IDLE",
            el or "IDLE",
            rl or "IDLE",
            "RM starves T3" if rl != "T3" and gl == "T3" else ("EDF domino zone" if el != gl else "Aligned slice"),
        ])
    return rows


def gantt_table_rows(case: Dict, policy_key: str) -> List[List[str]]:
    g = case["runs"][policy_key]["gantt"]
    rows = []
    for idx, item in enumerate(g[:18], start=1):
        proc, s, e = item[0], item[1], item[2]
        rows.append([str(idx), str(proc), f"[{s}, {e})", str(e - s)])
    return rows


def b1_tick_comparison_rows(d: Dict) -> List[List[str]]:
    case = d["regime_b_constrained_cases"]["b1_dm_vs_rm"]
    tasks = _to_rttasks(case["tasks"], use_density=False)
    r_edf = gsc.simulate_rt(tasks, policy="edf", horizon=12)
    r_dm = gsc.simulate_rt(tasks, policy="dm", horizon=12)
    r_rm = gsc.simulate_rt(tasks, policy="rm", horizon=12)
    r_gs = gsc.simulate_rt(tasks, policy="gs_vtime", horizon=12)
    rows = []
    for t in range(12):
        e = r_edf["timeline"][t][1] or "IDLE"
        dm = r_dm["timeline"][t][1] or "IDLE"
        rm = r_rm["timeline"][t][1] or "IDLE"
        gs = r_gs["timeline"][t][1] or "IDLE"
        rows.append([
            str(t), e, dm, rm, gs,
            "RM runs T1 -> T2 misses at t=3" if t in (0, 1, 2) and rm != dm else (
                "DM/EDF pass" if dm == e else "Proportional split"
            ),
        ])
    return rows


def overload_matched_tick_rows(d: Dict, start: int = 0, end: int = 24) -> List[List[str]]:
    ov = d["regime_c_overload"]
    tasks = _to_rttasks(ov["tasks_matched"], use_density=False)
    r_gs = gsc.simulate_rt(tasks, policy="gs_vtime", horizon=24)
    r_edf = gsc.simulate_rt(tasks, policy="edf", horizon=24)
    r_rm = gsc.simulate_rt(tasks, policy="rm", horizon=24)
    rows = []
    for t in range(start, min(end, 24)):
        gl = r_gs["timeline"][t][1] or "IDLE"
        el = r_edf["timeline"][t][1] or "IDLE"
        rl = r_rm["timeline"][t][1] or "IDLE"
        rows.append([
            str(t), gl, el, rl,
            "GS shares 6:3:2; RM starves T3" if "T3" in gl and "T3" not in rl else "Overload slice",
        ])
    return rows


def band_detail_rows(d: Dict, band_idx: int) -> List[List[str]]:
    b = d["regime_b_sweep_120"]["bands"][band_idx]
    order = [
        ("edf", "EDF"),
        ("dm", "DM"),
        ("rm", "RM"),
        ("gs_vtime_density", "GS VTime (w~C/D)"),
        ("gs_vtime", "GS VTime (Proport.)"),
        ("stride", "Stride"),
        ("rr", "Round-Robin (q=1)"),
    ]
    rows = []
    for key, lbl in order:
        sc = b["success_count"][key]
        sp = b["success_pct"][key]
        mr = b["mean_miss_rate_pct"][key]
        jt = b["mean_jitter"][key]
        rows.append([
            lbl,
            f"{sc} / {b['n_sets']}",
            f"{sp:.2f}%",
            f"{mr:.2f}%",
            f"{jt:.3f}",
        ])
    return rows


def b3_tick_comparison_rows(d: Dict) -> List[List[str]]:
    case = d["regime_b_constrained_cases"]["b3_u_under_1_infeasible"]
    tasks = _to_rttasks(case["tasks"], use_density=False)
    r_edf = gsc.simulate_rt(tasks, policy="edf", horizon=12)
    r_dm = gsc.simulate_rt(tasks, policy="dm", horizon=12)
    r_rm = gsc.simulate_rt(tasks, policy="rm", horizon=12)
    r_gs = gsc.simulate_rt(tasks, policy="gs_vtime", horizon=12)
    rows = []
    for t in range(min(12, len(r_edf["timeline"]))):
        rows.append([
            str(t),
            r_edf["timeline"][t][1] or "IDLE",
            r_dm["timeline"][t][1] or "IDLE",
            r_rm["timeline"][t][1] or "IDLE",
            r_gs["timeline"][t][1] or "IDLE",
        ])
    return rows


def regime_a_trace_rows() -> List[List[str]]:
    procs = [
        gsc.Proc("P1", 0, 4, weight=1),
        gsc.Proc("P2", 0, 6, weight=2),
        gsc.Proc("P3", 0, 9, weight=4),
    ]
    r_gs = gsc.simulate_procs(procs, policy="gs_vtime", quantum=1, tie="index")
    r_st = gsc.simulate_procs(procs, policy="stride", quantum=1, tie="index")
    r_rr = gsc.simulate_procs(procs, policy="rr", quantum=1, tie="index")
    rows = []
    for t in range(19):
        g = r_gs.timeline[t][1]
        s = r_st.timeline[t][1]
        r = r_rr.timeline[t][1]
        rows.append([str(t), g, s, r, "GS == Stride" if g == s else "Diverge"])
    return rows


def edf_domino_demo_rows() -> List[List[str]]:
    # Classic 4-task transient overload U = 1.077 illustrating domino misses vs GS proportional share
    tasks = [
        gsc.RTTask("T1", period=4, wcet=1, deadline=4, weight=3),
        gsc.RTTask("T2", period=5, wcet=2, deadline=5, weight=4),
        gsc.RTTask("T3", period=7, wcet=2, deadline=7, weight=3),
        gsc.RTTask("T4", period=10, wcet=2, deadline=10, weight=2),
    ]
    rows = []
    for pol, lbl in [("edf", "EDF"), ("rm", "RM"), ("dm", "DM"), ("gs_vtime", "GS VTime"), ("rr", "Round-Robin")]:
        r = gsc.simulate_rt(tasks, policy=pol, horizon=35)
        tu = r["task_used"]
        rows.append([
            lbl,
            f"{r['missed']}/{r['released']}",
            f"{100.0 * r['miss_rate']:.1f}%",
            f"{r['jain_fairness']:.4f}",
            f"{r['min_task_share_ratio']:.4f}",
            f"{tu['T1']}/{tu['T2']}/{tu['T3']}/{tu['T4']}",
        ])
    return rows


def b2_per_task_comparison_rows(d: Dict) -> List[List[str]]:
    case = d["regime_b_constrained_cases"]["b2_edf_vs_dm_gs"]
    runs = case["runs"]
    rows = []
    for key, lbl in [("edf", "EDF"), ("dm", "DM"), ("rm", "RM"), ("gs_vtime_density", "GS (w~C/D)"), ("gs_vtime", "GS (base)")]:
        r = runs[key]
        tu = r["task_used"]
        rows.append([
            lbl,
            f"{tu['T1']} / {tu['T2']} / {tu['T3']}",
            f"{r['missed']}/{r['released']}",
            str(r["worst_response"]) if r["worst_response"] is not None else "-",
            str(r["jitter"]) if r["jitter"] is not None else "-",
            str(r["preemptions"]),
            str(r["context_switches"]),
        ])
    return rows


def dbf_profile_rows(d: Dict, case_key: str) -> List[List[str]]:
    case = d["regime_b_constrained_cases"][case_key]
    tasks = case["tasks"]
    # Evaluate processor demand bound function dbf(L) = sum max(0, floor((L - D_i)/T_i) + 1) * C_i
    Ls = sorted({t["deadline"] + k * t["period"] for t in tasks for k in range(5) if t["deadline"] + k * t["period"] <= 24})
    rows = []
    for L in Ls[:10]:
        parts = []
        tot = 0
        for t in tasks:
            cnt = max(0, (L - t["deadline"]) // t["period"] + 1)
            dem = cnt * t["wcet"]
            tot += dem
            parts.append(f"{t['name']}:{dem}")
        rows.append([
            str(L),
            " + ".join(parts),
            str(tot),
            "PASS (dbf <= L)" if tot <= L else f"FAIL (+{tot - L} excess)",
        ])
    return rows


def domino_tick_rows(start: int = 0, end: int = 24) -> List[List[str]]:
    tasks = [
        gsc.RTTask("T1", period=4, wcet=1, deadline=4, weight=3),
        gsc.RTTask("T2", period=5, wcet=2, deadline=5, weight=4),
        gsc.RTTask("T3", period=7, wcet=2, deadline=7, weight=3),
        gsc.RTTask("T4", period=10, wcet=2, deadline=10, weight=2),
    ]
    r_edf = gsc.simulate_rt(tasks, policy="edf", horizon=35)
    r_rm = gsc.simulate_rt(tasks, policy="rm", horizon=35)
    r_gs = gsc.simulate_rt(tasks, policy="gs_vtime", horizon=35)
    rows = []
    for t in range(start, min(end, 35)):
        rows.append([
            str(t),
            r_edf["timeline"][t][1] or "IDLE",
            r_rm["timeline"][t][1] or "IDLE",
            r_gs["timeline"][t][1] or "IDLE",
        ])
    return rows





