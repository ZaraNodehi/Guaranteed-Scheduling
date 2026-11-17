"""Dynamic data loaders & table formatters for Exercise 5 reports (Readers-Writers)."""
from __future__ import annotations

import json
import os
from typing import Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
DATA_PATH = os.path.join(REPO_ROOT, "exercise-5", "output", "experiments.json")


def load() -> Dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def safety_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["safety_concurrency_audits"]:
        out.append([
            r["primitive"],
            r["policy"],
            str(r["max_concurrent_readers"]),
            str(r["max_concurrent_writers"]),
            str(r["safety_violations"]),
            str(r["final_counter"]),
            f"{r['elapsed_ms']:.2f}",
        ])
    return out


def starvation_rows(d: Dict, flood_mode: str) -> List[List[str]]:
    out = []
    for r in d["starvation_stress_audits"]:
        if r["flood_mode"] != flood_mode:
            continue
        out.append([
            r["primitive"],
            r["policy"],
            str(r["flood_ops"]),
            str(r["victim_ops"]),
            f"{r['victim_mean_wait_ms']:.2f}",
            f"{r['victim_max_wait_ms']:.2f}",
            f"{r['victim_p90_wait_ms']:.2f}",
        ])
    return out


def mix_rows(d: Dict, cs_ms: float) -> List[List[str]]:
    out = []
    for r in d["mix_sweep"]:
        if r["cs_sleep_ms"] != cs_ms:
            continue
        out.append([
            f"{r['read_pct']}% R / {r['write_pct']}% W",
            r["primitive"],
            f"{r['wall_ms']:.2f}",
            f"{r['cpu_ms']:.2f}",
            f"{r['throughput_ops_s']:,.1f}",
        ])
    return out


def cpu_burn_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["cpu_burn_audits"]:
        out.append([
            r["primitive"],
            f"{r['hold_ms']} ms",
            f"{r['wall_ms']:.2f}",
            f"{r['cpu_ms']:.2f}",
            f"{r['cpu_ratio']*100:.1f}%",
        ])
    return out


def bfs_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["bfs_rw_models"]:
        out.append([
            r["policy"].title(),
            str(r["reachable_states"]),
            str(r["transitions"]),
            str(r["dual_reader_states"]),
            str(r["safety_violations"]),
            str(r["writer_starvation_bypass_states"]),
        ])
    return out


def code_slice(rel_path: str, start_line: int, end_line: int) -> List[str]:
    p = os.path.join(REPO_ROOT, rel_path)
    with open(p, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{idx:03d}: {lines[idx - 1]}" for idx in range(start_line, min(end_line, len(lines)) + 1)]
