"""Dynamic loader and table formatters for Exercise 7 Capstone reports."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-7", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def six_regime_rows(d: Dict) -> List[List[str]]:
    m = d["six_regime_matrix"]
    pols = [
        "gs_capped:stay",
        "gs_vtime:stay",
        "gs_entitled:index",
        "gs_ratio:index",
        "stride:index",
        "rr:index",
        "fifo:index",
    ]
    rows = []
    for p in pols:
        rows.append([
            p,
            f"{m['R1_Static_Weighted'][p]['max_abs_lag']:.2f}",
            f"{m['R2_Dynamic_Latecomers'][p]['max_abs_lag']:.2f} / gap {m['R2_Dynamic_Latecomers'][p]['max_starve_gap']}",
            f"gap {m['R3_Heavy_Sleeper_40'][p]['max_starve_gap']} / lag {m['R3_Heavy_Sleeper_40'][p]['max_abs_lag']:.1f}",
            f"{m['R1_Static_Weighted'][p]['context_switches']} sw",
        ])
    return rows


def rt_regime_rows(d: Dict) -> List[List[str]]:
    m = d["six_regime_matrix"]
    r4 = m["R4_RT_Feasible_U090"]
    r5 = m["R5_RT_Overload_U110"]
    rows = []
    for p in ("edf:index", "rm:index", "gs_ratio:index", "gs_vtime:stay", "rr:index", "fifo:index"):
        rows.append([
            p,
            str(r4[p]["deadline_misses"]),
            f"{r4[p]['min_share_ratio']:.3f}",
            str(r5[p]["deadline_misses"]),
            f"{r5[p]['min_share_ratio']:.3f}",
        ])
    return rows


def audit_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["repo_audit_ex1_to_6"]:
        rows.append([
            r["exercise"],
            "PASS" if r["has_json"] else "FAIL",
            f"{r['diagram_count']} PNGs",
            "PASS" if (r["has_en_pdf"] and r["has_en_docx"]) else "FAIL",
            "PASS" if (r["has_fa_pdf"] and r["has_fa_docx"]) else "FAIL",
            "PASS" if r["has_readme"] else "FAIL",
        ])
    return rows


def live_os_rows(d: Dict) -> List[List[str]]:
    o = d["live_capstone_os_demo"]
    rows = []
    for i, (w, idl, obs) in enumerate(zip(o["weights"], o["ideal_shares"], o["observed_shares"]), start=1):
        rows.append([
            f"Worker P{i} (w={w})",
            f"{idl*100:.2f}%",
            f"{obs*100:.2f}%",
            f"{abs(obs - idl)*100:.2f}%",
        ])
    return rows
