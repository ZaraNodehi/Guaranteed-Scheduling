"""Dynamic data loaders & table formatters for Exercise 6 (Capstone Integration)."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-6", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def pi_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["priority_inversion_audits"]:
        out.append([
            r["mode"],
            str(r["total_misses"]),
            str(r["high_misses"]),
            str(r["high_blocked_ticks"]),
            str(r["spin_stall_ticks"]),
            str(r["high_max_response_ticks"]),
        ])
    return out


def pipe_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["rt_rw_pipeline"]:
        out.append([
            f"{r['primitive']} ({r['policy']})",
            f"{r['rt_hit_rate_pct']:.2f}%",
            f"{r['rt_mean_lat_ms']:.3f}",
            f"{r['rt_p95_lat_ms']:.3f}",
            f"{r['rt_max_lat_ms']:.3f}",
            f"{r['total_throughput_ops_s']:,.1f}",
        ])
    return out


def gs_hybrid_rows(d: Dict) -> List[List[str]]:
    out = []
    for pol in ("rm", "edf", "gs_vtime:stay"):
        r = d["gs_rt_hybrid"][pol]
        out.append([
            pol,
            f"{r['utilization']:.4f}",
            str(r["misses"]),
            str(r["worst_response"]),
            str(r["context_switches"]),
            f"{r['jain_fairness']:.4f}",
        ])
    return out


def code_slice(rel_path: str, start_line: int, end_line: int) -> List[str]:
    p = os.path.join(REPO_ROOT, rel_path)
    with open(p, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{idx:03d}: {lines[idx - 1]}" for idx in range(start_line, min(end_line, len(lines)) + 1)]
