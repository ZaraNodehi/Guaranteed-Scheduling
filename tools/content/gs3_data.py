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


def w1_quantum_summary_rows(d: Dict) -> List[List[str]]:
    qr = d["workload1_static"]["quantum_runs"]
    rows = []
    for q in (1, 2, 3):
        for tie in ("index", "stay"):
            r = qr[f"q{q}_{tie}"]
            rows.append([
                f"q={q} : {tie}",
                f"{r['max_abs_lag']:.4f} ({r['max_abs_lag_frac']})",
                f"{r['rmse_lag']:.4f}",
                str(r["context_switches"]),
                str(r["preemptions"]),
                f"{r['mean_turnaround']:.2f}",
                f"{r['jain_fairness']:.4f}",
            ])
    return rows


def w1_q2_rows(d: Dict) -> List[List[str]]:
    tr = d["workload1_static"]["hand_trace_q2_stay"]
    sim_seq = d["workload1_static"]["quantum_runs"]["q2_stay"]["seq"]
    rows = []
    for r, s_nm in zip(tr, sim_seq):
        rb = r["ratios_before"]
        r_str = ", ".join(f"{k}:{rb[k]}" for k in ("P1", "P2", "P3") if k in rb)
        af = r["after"]
        lags = ", ".join(f"{k}:{af[k]['lag_frac']}" for k in ("P1", "P2", "P3"))
        rows.append([
            str(r["t"]),
            f"{r['event']} (rem_q={r['q_left_after']})",
            r_str,
            f"{r['chosen']} ({'OK' if r['chosen'] == s_nm else 'DIFF'})",
            lags,
        ])
    return rows


def w2_stride_rows(d: Dict, t_slice=None) -> List[List[str]]:
    tr = d["workload2_dynamic"]["stride_hand_trace"]
    sim_seq = d["workload2_dynamic"]["sim_runs"]["stride"]["seq"]
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


def w1_quantum_hand_rows(d: Dict, trace_key: str, sim_key: str) -> List[List[str]]:
    tr = d["workload1_static"][trace_key]
    sim_seq = d["workload1_static"]["quantum_runs"][sim_key]["seq"]
    rows = []
    for r, s_nm in zip(tr, sim_seq):
        rb = r["ratios_before"]
        r_str = ", ".join(f"{k}:{rb[k]}" for k in ("P1", "P2", "P3") if k in rb)
        af = r["after"]
        lags = ", ".join(f"{k}:{af[k]['lag_frac']}" for k in ("P1", "P2", "P3"))
        rows.append([
            str(r["t"]),
            f"{r['event']} (rem={r['q_left_after']})",
            r_str,
            f"{r['chosen']} ({'OK' if r['chosen'] == s_nm else 'DIFF'})",
            lags,
        ])
    return rows


def w3_first_drift_rows(d: Dict, start: int = 0, end: int = 30) -> List[List[str]]:
    tr = d["workload3_float_drift"]["primary_first_60"]
    rows = []
    for r in tr:
        if not (start <= r["t"] < end):
            continue
        ex_v = ", ".join(r["exact_vt"])
        fl_v = ", ".join(r["float_vt"])
        rows.append([
            str(r["t"]),
            ex_v,
            fl_v,
            f"P{r['exact']+1}",
            f"P{r['float']+1}",
            "FLIP!" if r["diverged"] else "match",
            f"{r['diff_ulp_max']:.2e}",
        ])
    return rows


def w3_precision_matrix_rows(d: Dict, start_case: int = 0, end_case: int = 5) -> List[List[str]]:
    pm = d["workload3_float_drift"]["precision_comparison"][start_case:end_case]
    rows = []
    fmt_names = [
        ("float32", "IEEE-754 float32"),
        ("float64", "IEEE-754 float64"),
        ("decimal28", "Decimal(28 digits)"),
        ("fixed_q10", "Fixed Q10 (1024/w)"),
        ("fixed_q20", "Fixed Q20 (2^20/w)"),
        ("lcm_stride", "Exact LCM//w"),
    ]
    for c in pm:
        w_lbl = f"{c['weights']} (LCM={c['lcm']})"
        for fk, fnm in fmt_names:
            fm = c["formats"][fk]
            ft = "NONE" if fm["first_divergence_t"] is None else f"t={fm['first_divergence_t']}"
            rows.append([
                w_lbl,
                fnm,
                f"{fm['diverged_ticks']}/{c['total_ticks']}",
                f"{fm['diverged_pct']:.2f}%",
                ft,
                str(fm["max_service_dev_ticks"]),
            ])
    return rows


def w4_hand_rows(d: Dict, start: int = 0, end: int = 24,
                 trace_key: str = "hand_trace_gs_vtime",
                 sim_key: str = "gs_vtime:index_q1") -> List[List[str]]:
    tr = d["workload4_asymmetric_audit"][trace_key]
    sim_seq = d["workload4_asymmetric_audit"]["sim_runs"][sim_key]["seq"]
    rows = []
    for r, s_nm in zip(tr, sim_seq):
        if not (start <= r["t"] < end):
            continue
        sb = r["scores_before"]
        sc_str = ", ".join(f"{k}:{sb[k]}" for k in ("P1", "P2", "P3") if k in sb)
        af = r["after"]
        lags = ", ".join(f"{k}:{af[k]['lag_frac']}" for k in ("P1", "P2", "P3"))
        rows.append([
            str(r["t"]),
            sc_str,
            f"{r['chosen']} ({'OK' if r['chosen'] == s_nm else 'DIFF'})",
            r["sys_vtime_after"],
            lags,
        ])
    return rows


def w3_drift_rows(d: Dict) -> List[List[str]]:
    rows = []
    for c in d["workload3_float_drift"]["cases"]:
        det = c["first_divergence_detail"]
        ft = "NONE" if c["first_divergence_t"] is None else f"t = {c['first_divergence_t']}"
        diff_s = "identical" if det is None else f"{det['exact_choice']} vs {det['float_choice']}"
        rows.append([
            str(c["weights"]),
            str(c["total_ticks"]),
            f"{c['diverged_ticks']} ({c['diverged_pct']:.2f}%)",
            ft,
            diff_s,
        ])
    return rows


def w4_quantum_summary_rows(d: Dict) -> List[List[str]]:
    sim = d["workload4_asymmetric_audit"]["sim_runs"]
    rows = []
    for q in (1, 2, 3):
        for pol in ("gs_ratio:index", "gs_entitled:index", "gs_vtime:index", "gs_vtime:stay", "stride:index", "rr:index"):
            r = sim[f"{pol}_q{q}"]
            rows.append([
                f"{pol} (q={q})",
                f"{r['max_abs_lag']:.4f} ({r['max_abs_lag_frac']})",
                f"{r['rmse_lag']:.4f}",
                str(r["max_starve_gap"]),
                str(r["context_switches"]),
                f"{r['mean_turnaround']:.2f}",
                f"{r['jain_fairness']:.4f}",
            ])
    return rows


def code_snippet(rel_path: str, start_line: int, end_line: int) -> List[str]:
    full = os.path.join(REPO_ROOT, rel_path)
    with open(full, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{i:3d} | {lines[i - 1]}" for i in range(start_line, min(end_line, len(lines)) + 1)]

