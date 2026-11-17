"""Dynamic loader and table formatters for Exercise 6 optimization, drift audit & refactoring reports."""
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


def bench1_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["bench1_complexity"]["rows"]:
        rows.append([
            str(r["n_procs"]),
            f"{r['linear_us_per_step']:.3f} us",
            f"{r['linear_p95_us']:.3f} us",
            f"{r['heap_us_per_step']:.3f} us",
            f"{r['heap_p95_us']:.3f} us",
            f"{r['speedup']:.2f}x",
        ])
    return rows


def bench1_churn_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["bench1_complexity"]["churn_rows"]:
        rows.append([
            str(r["n_procs"]),
            str(r["cycles"]),
            f"{r['linear_churn_us']:.2f} us",
            f"{r['heap_churn_us']:.2f} us",
            f"{r['churn_speedup']:.2f}x",
            str(r["stale_pops"]),
        ])
    return rows


def bench2_rows(d: Dict) -> List[List[str]]:
    rows = []
    for s in d["bench2_ablation"]["stages"]:
        rows.append([
            s["stage"],
            f"{s['mean_lag']:.4f} +/- {s['ci95_lag']:.3f}",
            f"{s['p95_lag']:.4f}",
            f"{s['mean_gap']:.2f}",
            f"{s['mean_switches']:.2f}",
            f"{s['mean_sleeper_burst']:.2f} / {s['max_sleeper_burst']}",
        ])
    return rows


def bench2_workload_rows(d: Dict, start: int = 0, end: int = 20) -> List[List[str]]:
    rows = []
    for w in d["bench2_ablation"]["workloads_all"][start:end]:
        ws = ",".join(str(x) for x in w["weights"])
        rows.append([
            str(w["seed"]),
            f"S={w['sleep_len']}",
            f"[{ws}]",
            f"{w['V0']['lag']:.2f} / {w['V0']['burst']}t",
            f"{w['V1']['lag']:.2f} / {w['V1']['burst']}t",
            f"{w['V2']['lag']:.2f} ({w['V2']['sw']}sw)",
            f"{w['V3']['lag']:.2f} / {w['V3']['burst']}t",
        ])
    return rows


def bench3_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["bench3_sleeper"]["rows"]:
        p = r["policies"]
        rows.append([
            str(r["sleep_ticks"]),
            f"{p['gs_ratio:index']['post_wakeup_burst']}t / {p['gs_ratio:index']['max_starve_gap']}t",
            f"{p['gs_vtime:index']['post_wakeup_burst']}t / {p['gs_vtime:index']['max_starve_gap']}t",
            f"{p['gs_entitled:index']['post_wakeup_burst']}t / {p['gs_entitled:index']['max_starve_gap']}t",
            f"{p['gs_capped:index']['post_wakeup_burst']}t / {p['gs_capped:index']['max_starve_gap']}t",
        ])
    return rows


def bench3_cap_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["bench3_sleeper"]["cap_sensitivity"]:
        rows.append([
            str(r["wakeup_cap"]),
            f"{r['equal_burst_s40']}t",
            f"{r['equal_lag']:.2f}",
            f"{r['equal_gap']}t",
            f"{r['skew_burst_s24']}t",
            f"{r['skew_lag']:.3f}",
        ])
    return rows


def bench5_fp_rows(d: Dict, suite_key: str = "decimal_weights_suite") -> List[List[str]]:
    rows = []
    for r in d["bench5_fp_drift"][suite_key]["checkpoints"]:
        rows.append([
            f"{r['steps']:,}",
            f"{r['float_mismatch_cum']:,}",
            f"{r['fp_mismatch_cum']:,}",
            str(r["exact_used"]),
            str(r["fp_used"]),
            f"{r['max_float_vtime_err']:.2e}",
        ])
    return rows


def bench5_tie_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["bench5_fp_drift"]["tie_drift_cases"]:
        rows.append([
            str(r["cycles"]),
            r["float_accum"],
            f"{r['float_abs_error']:.2e}",
            f"{r['fp_value']:,}",
            "True" if r["fp_exact_zero_error"] else "False",
            "YES (breaks <)" if r["float_breaks_tie_lt_int"] else "No",
        ])
    return rows


def bench4_os_rows(d: Dict) -> List[List[str]]:
    leg = d["bench4_live_os"]["legacy"]
    opt = d["bench4_live_os"]["optimized"]
    rows = []
    for lbl, r in [("Legacy Arrival (dt=0.10s, used/w)", leg),
                   ("Refactored Arrival (dt=0.05s, V(t)+stay)", opt)]:
        sh = ", ".join(f"{s*100:.1f}%" for s in r["post_spawn_shares"])
        rows.append([
            lbl,
            f"{r['dt']:.2f} s",
            str(r["switches"]),
            sh,
            f"{r['max_post_spawn_deviation']*100:.2f}%",
        ])
    return rows


def bench4_sleeper_os_rows(d: Dict) -> List[List[str]]:
    uncap = d["bench4_live_os"]["sleeper_uncapped"]
    cap = d["bench4_live_os"]["sleeper_capped"]
    rows = []
    for lbl, r in [("Uncapped Linux Sleeper (dt=0.05s)", uncap),
                   ("gs_capped Linux Sleeper (cap=1*dt)", cap)]:
        sh = ", ".join(f"{s*100:.1f}%" for s in r["post_wake_shares"])
        rows.append([
            lbl,
            str(r["post_wake_steps"]),
            f"{r['max_sleeper_burst_steps']} steps",
            sh,
            f"{r['post_wake_dev']*100:.2f}%",
        ])
    return rows


def bench4_trace_rows(d: Dict, which: str = "optimized", start: int = 0, end: int = 16) -> List[List[str]]:
    rows = []
    for r in d["bench4_live_os"][which]["trace"][start:end]:
        sh = "/".join(f"{x*100:.0f}%" for x in r["active_shares"])
        vt = ", ".join(f"{x:.3f}" for x in r["vtimes"])
        rows.append([
            str(r["step"]),
            f"{r['elapsed_s']:.3f}s",
            "Yes" if r["spawned_p3"] else "No",
            r["chosen"],
            f"[{vt}]",
            sh,
        ])
    return rows


def bench4_sleeper_trace_rows(d: Dict, which: str = "sleeper_capped", start: int = 0, end: int = 18) -> List[List[str]]:
    rows = []
    for r in d["bench4_live_os"][which]["trace"][start:end]:
        sh = "/".join(f"{x*100:.0f}%" for x in r["post_wake_shares"])
        vt = f"{r['vtimes'][0]:.3f}, {r['vtimes'][1]:.3f}"
        rows.append([
            str(r["step"]),
            f"{r['elapsed_s']:.3f}s",
            r["phase"],
            r["chosen"],
            f"[{vt}]",
            sh,
        ])
    return rows


def code_snippet(rel_path: str, start_line: int, end_line: int) -> List[str]:
    p = os.path.join(REPO_ROOT, rel_path)
    with open(p, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{i:3d}: {lines[i-1]}" for i in range(max(1, start_line), min(len(lines), end_line) + 1)]


def seminar_slides_rows(lang: str = "en") -> List[List[str]]:
    import gs_decks
    spec = gs_decks.build_decks_spec(6)
    rows = []
    for idx, sl in enumerate(spec["slides"], start=1):
        fig = sl.get("figure", "(Cover / Summary)")
        title = sl["title_en"] if lang == "en" else sl["title_fa"]
        notes = sl["notes_en"] if lang == "en" else sl["notes_fa"]
        rows.append([str(idx), sl["tag"], title, fig, notes])
    return rows
