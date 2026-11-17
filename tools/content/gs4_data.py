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
    for pol in ("wfq_finish", "gs_vtime:max_weight", "gs_vtime:index", "rr:index", "fifo:index"):
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
