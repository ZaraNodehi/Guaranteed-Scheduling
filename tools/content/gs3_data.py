"""Dynamic loader and table formatters for Exercise 3 reports (zero hardcoded numbers)."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-3", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def w1_hand_rows(d: Dict, tie: str = "index") -> List[List[str]]:
    key_map = {"index": "hand_trace_index", "stay": "hand_trace_stay", "max_weight": "hand_trace_max_weight"}
    tr = d["workload1_static"][key_map[tie]]
    sim_seq = d["workload1_static"]["sim_runs"][f"gs_ratio:{tie}"]["seq"]
    rows = []
    for r, s_nm in zip(tr, sim_seq):
        rb = r["ratios_before"]
        r_str = ", ".join(f"{k}:{rb[k]}" for k in ("P1", "P2", "P3") if k in rb)
        tied = "/".join(r["tied_min"])
        af = r["after"]
        lags = ", ".join(f"{k}:{af[k]['lag_frac']}" for k in ("P1", "P2", "P3"))
        rows.append([
            str(r["t"]),
            r_str,
            tied,
            r["chosen"],
            "MATCH" if r["chosen"] == s_nm else "DIFF",
            lags,
        ])
    return rows


def w1_policy_rows(d: Dict) -> List[List[str]]:
    sim = d["workload1_static"]["sim_runs"]
    order = [
        "gs_ratio:index", "gs_vtime:index", "gs_entitled:index", "stride:index",
        "gs_ratio:stay", "gs_ratio:max_weight", "rr:index",
    ]
    rows = []
    for pol in order:
        r = sim[pol]
        rows.append([
            pol,
            f"{r['max_abs_lag']:.4f} ({r['max_abs_lag_frac']})",
            f"{r['rmse_lag']:.4f}",
            str(r["context_switches"]),
            str(r["preemptions"]),
            f"{r['mean_turnaround']:.2f}",
            f"{r['jain_fairness']:.4f}",
        ])
    return rows


def w2_dynamic_rows(d: Dict, pol: str, t_slice=None) -> List[List[str]]:
    tr = d["workload2_dynamic"]["hand_traces"][pol]
    sim_seq = d["workload2_dynamic"]["sim_runs"][pol]["seq"]
    rows = []
    for r, s_nm in zip(tr, sim_seq):
        if t_slice is not None and not (t_slice[0] <= r["t"] <= t_slice[1]):
            continue
        sb = r["scores_before"]
        sc_str = ", ".join(f"{k}:{sb[k]}" for k in ("P1", "P2", "P3") if k in sb)
        af = r["after"]
        p1_str = f"{af['P1']['actual']}/{af['P1']['gps_frac']} ({af['P1']['lag_frac']})"
        p2_str = f"{af['P2']['actual']}/{af['P2']['gps_frac']} ({af['P2']['lag_frac']})"
        p3_str = f"{af['P3']['actual']}/{af['P3']['gps_frac']} ({af['P3']['lag_frac']})"
        rows.append([
            str(r["t"]),
            sc_str,
            f"{r['chosen']} ({'OK' if r['chosen'] == s_nm else 'DIFF'})",
            p1_str,
            p2_str,
            p3_str,
        ])
    return rows


def w2_summary_rows(d: Dict) -> List[List[str]]:
    sim = d["workload2_dynamic"]["sim_runs"]
    rows = []
    for pol in ("gs_ratio", "gs_entitled", "gs_vtime", "stride", "rr"):
        r = sim[pol]
        rows.append([
            pol,
            f"{r['max_abs_lag']:.4f} ({r['max_abs_lag_frac']})",
            f"{r['rmse_lag']:.4f}",
            str(r["max_starve_gap"]),
            str(r["context_switches"]),
            f"{r['mean_turnaround']:.2f}",
            f"{r['jain_fairness']:.4f}",
        ])
    return rows


def w3_drift_rows(d: Dict) -> List[List[str]]:
    rows = []
    for c in d["workload3_float_drift"]["cases"]:
        det = c["first_divergence_detail"]
        rows.append([
            str(c["weights"]),
            str(c["total_ticks"]),
            f"{c['diverged_ticks']} ({c['diverged_pct']:.2f}%)",
            f"t = {c['first_divergence_t']}",
            f"{det['exact_choice']} vs {det['float_choice']}",
        ])
    return rows
