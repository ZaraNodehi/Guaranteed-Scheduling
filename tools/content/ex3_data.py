"""Dynamic data loaders & formatters for Exercise 3 reports (zero hardcoded numbers)."""
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


def task_rows(s: Dict) -> List[List[str]]:
    rows = []
    for i, t in enumerate(s["tasks"], 1):
        u = t["wcet"] / t["period"]
        rows.append([
            t["name"],
            str(t["period"]),
            str(t["wcet"]),
            str(t["deadline"]),
            f"{t['wcet']}/{t['period']} ({u:.4f})",
            f"Priority {i} (T={t['period']})",
        ])
    return rows


def trace_rows_slice(s: Dict, alg: str, start: int, end: int) -> List[List[str]]:
    out = []
    for r in s[alg]["trace_rows"][start:end]:
        out.append([
            str(r["t"]),
            r["arrivals"],
            r["ready_queue"],
            r["chosen"],
            r["rem_after"],
            r["miss_at_t"],
        ])
    return out


def side_by_side_slice(s: Dict, start: int, end: int) -> List[List[str]]:
    edf_rows = s["edf"]["trace_rows"][start:end]
    rm_rows = s["rm"]["trace_rows"][start:end]
    gs_tl = s["gs_vtime_ref"]["timeline"][start:end]
    out = []
    for e, r, g in zip(edf_rows, rm_rows, gs_tl):
        diff = "YES (Diverge)" if e["chosen"] != r["chosen"] else "-"
        if r["miss_at_t"] != "-" or e["miss_at_t"] != "-":
            diff = f"MISS: RM={r['miss_at_t']} / EDF={e['miss_at_t']}"
        out.append([
            str(e["t"]),
            e["arrivals"],
            e["chosen"],
            r["chosen"],
            g,
            diff,
        ])
    return out


def rta_rows(s: Dict) -> List[List[str]]:
    out = []
    for r in s["rta_rm"]:
        out.append([
            r["name"],
            str(r["priority"]),
            f"T={r['period']}, C={r['wcet']}, D={r['deadline']}",
            " -> ".join(str(x) for x in r["iterations"]),
            str(r["worst_R_i"]),
            "PASS" if r["rta_feasible"] else f"FAIL (R={r['worst_R_i']} > D={r['deadline']})",
        ])
    return out


def dbf_rows(s: Dict, start: int = 0, end: int = 12) -> List[List[str]]:
    out = []
    for r in s["dbf_edf"][start:end]:
        out.append([
            str(r["L"]),
            str(r["dbf"]),
            str(r["margin"]),
            "OK" if r["feasible_at_L"] else "OVERLOAD",
            r["breakdown"],
        ])
    return out


def completion_rows(s: Dict, alg: str) -> List[List[str]]:
    out = []
    for pname in ["P1", "P2", "P3"]:
        jobs = s[alg]["completions"][pname]
        rts = [j["response_time"] for j in jobs]
        tardies = sum(1 for j in jobs if j["tardy"])
        summary = ", ".join(f"{j['job']}[{j['release']}->{j['finish']}]" for j in jobs[:6])
        if len(jobs) > 6:
            summary += f" (+{len(jobs)-6} more)"
        out.append([
            pname,
            str(len(jobs)),
            f"{min(rts)} / {max(rts)}" if rts else "-",
            f"{sum(rts)/len(rts):.2f}" if rts else "-",
            str(tardies),
            summary,
        ])
    return out


def code_slice(rel_path: str, start_line: int, end_line: int) -> List[str]:
    p = os.path.join(REPO_ROOT, rel_path)
    with open(p, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{idx:03d}: {lines[idx - 1]}" for idx in range(start_line, min(end_line, len(lines)) + 1)]
