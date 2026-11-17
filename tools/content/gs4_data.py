"""Dynamic loader and table formatters for Exercise 4 formal proof reports."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-4", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def t1_audit_rows(d: Dict) -> List[List[str]]:
    t1 = d["theorem1_lag_bounds"]
    order = [
        ("eevdf", "EEVDF (eligible + vdeadline)"),
        ("wfq_finish", "WFQ / PGPS (finish (used+q)/w)"),
        ("gs_vtime:max_weight", "gs_vtime : max_weight"),
        ("gs_vtime:index", "gs_vtime : index"),
        ("gs_ratio:index", "gs_ratio : index"),
        ("gs_entitled:index", "gs_entitled : index"),
        ("stride:index", "stride : index"),
        ("rr:index", "Round Robin (unweighted)"),
        ("fifo:index", "FIFO (batch)"),
    ]
    rows = []
    for k, lbl in order:
        viols = t1["violations_above_q"][k]
        ratio = t1["max_lag_over_q"][k]
        mx = t1["max_lag_seen"][k]
        rows.append([
            lbl,
            f"{viols} / {t1['n_workloads']}",
            f"{ratio:.4f}x",
            f"{mx:.4f}",
        ])
    return rows


def t1_per_q_rows(d: Dict) -> List[List[str]]:
    pq = d["theorem1_lag_bounds"]["per_q_summary"]
    rows = []
    for pol in ("eevdf", "wfq_finish", "gs_vtime:max_weight", "gs_vtime:index", "rr:index", "fifo:index"):
        rows.append([
            pol,
            f"{pq['1'][pol]['mean_max_lag']:.3f} / {pq['1'][pol]['worst_max_lag']:.3f}",
            f"{pq['2'][pol]['mean_max_lag']:.3f} / {pq['2'][pol]['worst_max_lag']:.3f}",
            f"{pq['3'][pol]['mean_max_lag']:.3f} / {pq['3'][pol]['worst_max_lag']:.3f}",
        ])
    return rows


def t1_envelope_rows(d: Dict) -> List[List[str]]:
    rows = []
    for e in d["theorem1_lag_bounds"]["exhaustive_tie_envelopes"]:
        rows.append([
            f"{e['case']} {e['weights']}",
            f"{e['states']} / {e['leaves']}",
            f"[{e['best_max_lag']:.4f}, {e['worst_max_lag']:.4f}]",
            e["worst_max_lag_frac"],
            f"{e['sfq_theoretical_bound']:.4f}",
            f"[{e['min_switches']}, {e['max_switches']}]",
        ])
    return rows


def t2_scaling_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["theorem2_starvation_scaling"]["scaling_rows"]:
        rows.append([
            str(r["t_arrival"]),
            f"{r['gs_ratio_lag']:.1f} ({r['gs_ratio_lag_frac']})",
            str(r["gs_ratio_gap"]),
            f"{r['gs_entitled_lag']:.2f}",
            str(r["gs_entitled_gap"]),
            f"{r['gs_vtime_lag']:.2f}",
            str(r["gs_vtime_gap"]),
        ])
    return rows


def t3_rt_rows(d: Dict) -> List[List[str]]:
    rows = []
    for s in d["theorem3_exhaustive_rt"]["sets"]:
        ver = "PASS" if s["independent_verified"] else ("INFEAS" if not s["exhaustive_wc_feasible"] else "FAIL")
        rows.append([
            s["name"],
            f"{s['utilization']:.3f}",
            "FEAS" if s["exhaustive_wc_feasible"] else "INFEAS",
            f"{s['states_wc']} / {s['states_idle']}",
            ver,
            str(s["edf_missed"]),
            str(s["dm_missed"]),
            str(s["gs_vtime_missed"]),
        ])
    return rows


def t4_overload_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["theorem4_overload"]["sweep"]:
        p = r["policies"]
        rows.append([
            f"{r['utilization']:.2f}",
            f"{p['gs_vtime_eq']['jain']:.3f} / {p['gs_vtime_eq']['min_sr']:.3f}",
            f"{p['gs_ratio_eq']['jain']:.3f} / {p['gs_ratio_eq']['min_sr']:.3f}",
            f"{p['rr_eq']['jain']:.3f} / {p['rr_eq']['min_sr']:.3f}",
            f"{p['edf']['jain']:.3f} / {p['edf']['min_sr']:.3f}",
            f"{p['rm']['jain']:.3f} / {p['rm']['min_sr']:.3f}",
            f"{p['rm']['low_ticks']} vs {p['gs_vtime_eq']['low_ticks']}",
        ])
    return rows


def t1_per_weight_rows(d: Dict) -> List[List[str]]:
    rows = []
    for p in d["theorem1_lag_bounds"]["per_weight_summary"]:
        v = p["violations_of_12"]
        m = p["max_lag_over_q"]
        rows.append([
            str(p["weights"]),
            str(p["sum_w"]),
            f"{p['sfq_bound']:.4f}",
            f"{v['gs_vtime:index']}/12 ({m['gs_vtime:index']:.4f}q)",
            f"{v['wfq_finish']}/12 ({m['wfq_finish']:.4f}q)",
            f"{v['eevdf']}/12 ({m['eevdf']:.4f}q)",
            f"{v['rr:index']}/12 ({m['rr:index']:.2f}q)",
        ])
    return rows


def t1_q1_40_rows(d: Dict, start: int = 0, end: int = 20, q_key: str = "q1_40_cases") -> List[List[str]]:
    rows = []
    for r in d["theorem1_lag_bounds"][q_key][start:end]:
        rows.append([
            f"{r['weights']} x{r['scale']}",
            str(r["total_work"]),
            f"{r['gs_vtime_index']:.4f}",
            f"{r['gs_vtime_max_weight']:.4f}",
            f"{r['wfq_finish']:.4f}",
            f"{r['eevdf']:.4f}",
            f"{r['rr_index']:.4f}",
            f"{r['fifo_index']:.4f}",
        ])
    return rows


def t1_witness2_rows(d: Dict) -> List[List[str]]:
    w = d["theorem1_lag_bounds"]["witness_1234"]
    rows = []
    for a, b, c in zip(w["gs_vtime_index"], w["gs_vtime_max_weight"], w["wfq_finish"]):
        rows.append([
            str(a["t"]),
            f"{a['chosen']} ({a['max_abs_lag']:.4f})",
            ", ".join(a["lags_frac"]),
            f"{b['chosen']} ({b['max_abs_lag']:.4f})",
            f"{c['chosen']} ({c['max_abs_lag']:.4f})",
        ])
    return rows


def t3_specs_rows(d: Dict) -> List[List[str]]:
    rows = []
    for s in d["theorem3_exhaustive_rt"]["sets"]:
        rows.append([
            s["name"],
            str(s["horizon"]),
            s["tasks_spec"],
            f"{s['utilization']:.4f}",
            "FEASIBLE" if s["exhaustive_wc_feasible"] else "INFEASIBLE",
        ])
    return rows


def t3_f05_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["theorem3_exhaustive_rt"]["f05_trace_12t"]:
        rows.append([
            str(r["t"]),
            r["dfs_witness"],
            r["edf"],
            r["dm"],
            r["gs_vtime"],
            "EDF==DFS" if r["edf"] == r["dfs_witness"] else "Valid Alt",
        ])
    return rows


def t1_witness_rows(d: Dict, start: int = 0, end: int = 32) -> List[List[str]]:
    w = d["theorem1_lag_bounds"]["witness_1357"]
    idx_tr = w["gs_vtime_index"]
    mw_tr = w["gs_vtime_max_weight"]
    wfq_tr = w["wfq_finish"]
    rows = []
    for a, b, c in zip(idx_tr, mw_tr, wfq_tr):
        if not (start <= a["t"] < end):
            continue
        rows.append([
            str(a["t"]),
            f"{a['chosen']} ({a['max_abs_lag']:.4f})",
            ", ".join(a["lags_frac"]),
            f"{b['chosen']} ({b['max_abs_lag']:.4f})",
            f"{c['chosen']} ({c['max_abs_lag']:.4f})",
        ])
    return rows


def t3_dbf_rows(d: Dict) -> List[List[str]]:
    rows = []
    for s in d["theorem3_exhaustive_rt"]["sets"]:
        rows.append([
            s["name"],
            f"{s['utilization']:.3f}",
            f"L*={s['peak_dbf_L']}",
            f"{s['max_dbf_over_L']:.4f}",
            "PASS" if s["exhaustive_wc_feasible"] else "FAIL",
            "PASS" if s["exhaustive_idle_feasible"] else "FAIL",
            f"{s['states_wc']} vs {s['states_idle']}",
        ])
    return rows


def t4_weighted_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["theorem4_overload"]["sweep"]:
        wg = r["weighted_gs_vtime"]
        wr = r["weighted_rm"]
        ug = wg["task_used"]
        ur = wr["task_used"]
        rows.append([
            f"{r['utilization']:.2f}",
            f"{wg['jain']:.4f}",
            f"{wg['min_sr']:.4f}",
            f"{ug['High']}/{ug['Mid']}/{ug['Low']}",
            f"{wr['jain']:.4f}",
            f"{wr['min_sr']:.4f}",
            f"{ur['High']}/{ur['Mid']}/{ur['Low']}",
        ])
    return rows


def t4_equal_shares_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["theorem4_overload"]["sweep"]:
        p = r["policies"]
        rows.append([
            f"{r['utilization']:.2f}",
            f"{p['gs_vtime_eq']['low_ticks']}t ({p['gs_vtime_eq']['min_sr']:.2f})",
            f"{p['gs_ratio_eq']['low_ticks']}t ({p['gs_ratio_eq']['min_sr']:.2f})",
            f"{p['rr_eq']['low_ticks']}t ({p['rr_eq']['min_sr']:.2f})",
            f"{p['edf']['low_ticks']}t ({p['edf']['min_sr']:.2f})",
            f"{p['rm']['low_ticks']}t ({p['rm']['min_sr']:.2f})",
        ])
    return rows


def t2_witness_rows(d: Dict, start: int = 0, end: int = 24) -> List[List[str]]:
    rows = []
    for r in d["theorem2_starvation_scaling"]["witness_t8_24t"][start:end]:
        rows.append([
            str(r["t"]),
            f"{r['ratio_choice']} ({r['ratio_lag']:.2f})",
            r["ratio_lags"],
            f"{r['vtime_choice']} ({r['vtime_lag']:.2f})",
        ])
    return rows


def t3_f07_rows(d: Dict, start: int = 0, end: int = 24) -> List[List[str]]:
    rows = []
    for r in d["theorem3_exhaustive_rt"]["f07_trace_24t"][start:end]:
        rows.append([
            str(r["t"]),
            r["dfs_witness"],
            r["edf"],
            r["dm"],
            r["gs_vtime"],
            "EDF==DFS" if r["edf"] == r["dfs_witness"] else "Valid Alt",
        ])
    return rows


def code_snippet(rel_path: str, start_line: int, end_line: int) -> List[str]:
    full = os.path.join(REPO_ROOT, rel_path)
    with open(full, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{i:3d} | {lines[i - 1]}" for i in range(start_line, min(end_line, len(lines)) + 1)]

