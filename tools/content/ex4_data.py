"""Dynamic data loaders & table formatters for Exercise 4 reports (zero hardcoded numbers)."""
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


def fsm_rows(rows: List[Dict], lang: str = "en") -> List[List[str]]:
    out = []
    for r in rows:
        safe = "SAFE" if (r["mutex_violations"] == 0 and r["deadlock_states"] == 0 and "v1" not in r["model"] and "v4" not in r["model"]) else "UNSAFE"
        if lang == "fa":
            safe = "امن" if safe == "SAFE" else "ناامن"
        out.append([
            r["model"],
            str(r["reachable_states"]),
            str(r["transitions"]),
            str(r["max_bfs_depth"]),
            str(r["mutex_violations"]),
            str(r["deadlock_states"]),
            str(r["non_cs_spin_back_edges"]),
            safe,
        ])
    return out


def cs_sweep_rows(d: Dict, work_label_filter: str = "") -> List[List[str]]:
    out = []
    for r in d["cs_work_sweep_n2"]:
        if work_label_filter and r["workload"] != work_label_filter:
            continue
        out.append([
            r["workload"],
            r["primitive"],
            f"{r['wall_ms']:.2f}",
            f"{r['cpu_ms']:.2f}",
            f"{r['cpu_to_wall_ratio']:.3f}",
            f"{r['throughput_ops_s']:,.1f}",
            str(r["yield_spins"]),
        ])
    return out


def scaling_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["thread_scaling"]:
        out.append([
            str(r["n_threads"]),
            r["primitive"],
            str(r["total_ops"]),
            f"{r['wall_ms']:.2f}",
            f"{r['cpu_ms']:.2f}",
            f"{r['throughput_ops_s']:,.1f}",
            str(r["yield_spins"]),
        ])
    return out


def hold_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["lock_holder_sleep_audit"]:
        out.append([
            f"{r['hold_ms']} ms",
            r["primitive"],
            f"{r['wall_ms']:.2f}",
            f"{r['cpu_ms']:.2f}",
            f"{r['cpu_to_wall_ratio']*100:.1f}%",
            f"{r['throughput_ops_s']:,.1f}",
        ])
    return out


def bb_rows(d: Dict) -> List[List[str]]:
    out = []
    for r in d["bounded_buffer_bench"]:
        out.append([
            r["mode"],
            str(r["items"]),
            f"{r['wall_ms']:.2f}",
            f"{r['cpu_ms']:.2f}",
            str(r["cond_waits_or_spin_retries"]),
            f"{r['ops_per_s']:,.1f}",
        ])
    return out


def counterexample_rows(d: Dict, model_name: str, step_descs: List[str]) -> List[List[str]]:
    all_rows = d["dekker_evolution_fsm"] + d["all_primitives_fsm"]
    rec = next(r for r in all_rows if r["model"] == model_name)
    tr = rec["first_counterexample"]
    out = []
    for idx, st in enumerate(tr):
        desc = step_descs[idx] if idx < len(step_descs) else "Transition"
        out.append([str(idx), str(tuple(st)), desc])
    return out


def code_slice(rel_path: str, start_line: int, end_line: int) -> List[str]:
    p = os.path.join(REPO_ROOT, rel_path)
    with open(p, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{idx:03d}: {lines[idx - 1]}" for idx in range(start_line, min(end_line, len(lines)) + 1)]
