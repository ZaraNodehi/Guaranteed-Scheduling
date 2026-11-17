"""Dynamic loader and table formatters for Exercise 5 experimental reports."""
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


def sweep_a_rows(d: Dict) -> List[List[str]]:
    ov = d["sweep_a_monte_carlo"]["overall"]
    order = ["gs_vtime:stay", "gs_vtime:index", "stride:index", "gs_entitled:index",
             "gs_ratio:index", "rr:index", "fifo:index"]
    rows = []
    for p in order:
        m = ov[p]
        rows.append([
            p,
            f"{m['lag']['mean']:.3f} +/- {m['lag']['ci95']:.3f}",
            f"{m['lag']['p95']:.2f} / {m['lag']['p99']:.2f}",
            f"{m['rmse']['mean']:.3f}",
            f"{m['gap']['mean']:.2f}",
            f"{m['sw']['mean']:.1f}",
            f"{m['ta']['mean']:.2f}",
            f"{m['jain']['mean']:.4f}",
        ])
    return rows


def sweep_a_byn_rows(d: Dict) -> List[List[str]]:
    byn = d["sweep_a_monte_carlo"]["by_n"]
    rows = []
    for p in ("gs_vtime:stay", "gs_vtime:index", "gs_entitled:index", "gs_ratio:index", "rr:index", "fifo:index"):
        rows.append([
            p,
            f"{byn['3'][p]['lag']['mean']:.3f} +/- {byn['3'][p]['lag']['ci95']:.3f}",
            f"{byn['5'][p]['lag']['mean']:.3f} +/- {byn['5'][p]['lag']['ci95']:.3f}",
            f"{byn['8'][p]['lag']['mean']:.3f} +/- {byn['8'][p]['lag']['ci95']:.3f}",
            f"{byn['8'][p]['gap']['mean']:.2f}",
            f"{byn['8'][p]['sw']['mean']:.1f}",
        ])
    return rows


def sweep_a_seed_rows(d: Dict, start: int = 0, end: int = 20) -> List[List[str]]:
    rows = []
    for r in d["sweep_a_monte_carlo"]["seed_samples_60"][start:end]:
        rows.append([
            f"#{r['seed_id']} (N={r['n_procs']})",
            str(r["total_work"]),
            str(r["weights"]),
            f"{r['stay_lag']:.3f}",
            f"{r['index_lag']:.3f}",
            f"{r['ratio_lag']:.3f}",
            f"{r['rr_lag']:.3f}",
            f"{r['stay_sw']}/{r['ratio_gap']}",
        ])
    return rows


def sweep_b_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_b_quantum_pareto"]["rows"]:
        p = r["policies"]
        rows.append([
            str(r["quantum"]),
            f"{p['gs_vtime:stay']['lag']['mean']:.3f} / {p['gs_vtime:stay']['switches']['mean']:.1f}",
            f"{p['gs_vtime:index']['lag']['mean']:.3f} / {p['gs_vtime:index']['switches']['mean']:.1f}",
            f"{p['gs_ratio:index']['lag']['mean']:.3f} / {p['gs_ratio:index']['switches']['mean']:.1f}",
            f"{p['rr:index']['lag']['mean']:.3f} / {p['rr:index']['switches']['mean']:.1f}",
            f"{p['gs_vtime:stay']['turnaround']['mean']:.2f}",
        ])
    return rows


def sweep_b_rmse_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_b_quantum_pareto"]["rows"]:
        p = r["policies"]
        rows.append([
            str(r["quantum"]),
            f"{p['gs_vtime:stay']['rmse']['mean']:.3f} / {p['gs_vtime:stay']['lag']['p99']:.2f}",
            f"{p['gs_vtime:index']['rmse']['mean']:.3f} / {p['gs_vtime:index']['lag']['p99']:.2f}",
            f"{p['gs_ratio:index']['rmse']['mean']:.3f} / {p['gs_ratio:index']['lag']['p99']:.2f}",
            f"{p['rr:index']['rmse']['mean']:.3f} / {p['rr:index']['lag']['p99']:.2f}",
            f"{p['gs_ratio:index']['turnaround']['mean']:.2f}",
        ])
    return rows


def sweep_c_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_c_scaling"]["scaling_rows"]:
        rows.append([
            str(r["n_procs"]),
            f"{r['eq_vtime_lag']['mean']:.3f} +/- {r['eq_vtime_lag']['ci95']:.3f}",
            f"{r['eq_ratio_lag']['mean']:.3f} +/- {r['eq_ratio_lag']['ci95']:.3f}",
            f"{r['skew_vtime_lag']['mean']:.3f} +/- {r['skew_vtime_lag']['ci95']:.3f}",
            f"{r['skew_ratio_lag']['mean']:.3f} +/- {r['skew_ratio_lag']['ci95']:.3f}",
            f"{r['skew_vtime_gap']['mean']:.1f} vs {r['skew_ratio_gap']['mean']:.1f}",
        ])
    return rows


def sweep_c_extra_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_c_scaling"]["scaling_rows"]:
        rows.append([
            str(r["n_procs"]),
            f"{r['eq_vtime_lag']['p95']:.3f}",
            f"{r['eq_ratio_lag']['p95']:.3f}",
            f"{r['skew_vtime_lag']['p95']:.3f}",
            f"{r['skew_ratio_lag']['p95']:.3f}",
            f"{r['skew_vtime_sw']['mean']:.1f} vs {r['skew_ratio_sw']['mean']:.1f}",
        ])
    return rows


def sweep_d_os_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["sweep_d_os_intervals"]["interval_trials"]:
        sh = ", ".join(f"{s:.4f}" for s in r["actual_shares"])
        rows.append([
            f"{r['poll_dt_sec']:.2f} s",
            str(r["dispatches"]),
            str(r["controller_switches"]),
            f"{r['total_cpu_sec']:.3f} s",
            sh,
            f"{r['max_share_deviation']*100:.2f}%",
        ])
    return rows


def sweep_d_trace_rows(d: Dict, start: int = 0, end: int = 24) -> List[List[str]]:
    rows = []
    for r in d["sweep_d_os_intervals"]["dt005_trace"][start:end]:
        rows.append([
            str(r["step"]),
            f"{r['elapsed_ms']:.1f}",
            r["chosen"],
            ", ".join(f"{c:.3f}" for c in r["cum_cpu"]),
            ", ".join(f"{s:.3f}" for s in r["shares"]),
            f"{r['max_err_pct']:.2f}%",
        ])
    return rows


def sweep_e_summary_rows(d: Dict) -> List[List[str]]:
    sm = d["sweep_e_zipf_burst"]["summary"]
    order = ["gs_vtime:max_weight", "gs_vtime:stay", "gs_vtime:index",
             "gs_entitled:index", "stride:index", "gs_ratio:index", "rr:index"]
    rows = []
    for p in order:
        m = sm[p]
        rows.append([
            p,
            f"{m['lag']['mean']:.3f} +/- {m['lag']['ci95']:.3f}",
            f"{m['lag']['p95']:.2f} / {m['lag']['p99']:.2f}",
            f"{m['gap']['mean']:.2f}",
            f"{m['sw']['mean']:.1f}",
            f"{m['jain']['mean']:.4f}",
        ])
    return rows


def sweep_e_sample_rows(d: Dict, start: int = 0, end: int = 15) -> List[List[str]]:
    rows = []
    for r in d["sweep_e_zipf_burst"]["samples_60"][start:end]:
        rows.append([
            str(r["seed"]),
            str(r["weights"]),
            f"{r['maxw_lag']:.3f}",
            f"{r['stay_lag']:.3f}",
            f"{r['ratio_lag']:.3f}",
            f"{r['rr_lag']:.3f}",
            f"{r['stay_gap']} vs {r['ratio_gap']}",
        ])
    return rows


def seminar_slides_rows(lang: str = "en") -> List[List[str]]:
    import gs_decks
    spec = gs_decks.build_decks_spec(5)
    rows = []
    for idx, s in enumerate(spec["slides"], 1):
        title = s["title_fa"] if lang == "fa" else s["title_en"]
        notes = s["notes_fa"] if lang == "fa" else s["notes_en"]
        fig = s.get("figure") or ("(کاور/جمع‌بندی)" if lang == "fa" else "(Cover / Summary)")
        rows.append([str(idx), s["tag"], title, fig, notes])
    return rows


def sweep_f_bootstrap_rows(d: Dict) -> List[List[str]]:
    rows = []
    for c in d["sweep_f_bootstrap"]["comparisons"]:
        rows.append([
            c["competitor"],
            f"{c['stay_wins']}/{c['ties']}/{c['stay_losses']}",
            f"{c['win_rate_pct']:.2f}%",
            f"{c['mean_lag_reduction']:+.4f}",
            f"[{c['boot_ci95_low']:+.4f}, {c['boot_ci95_high']:+.4f}]",
            f"{c['cohens_d']:.3f}",
            f"{c['mean_sw_saved_vs_comp']:+.2f}",
        ])
    return rows


def code_snippet(rel_path: str, start_line: int, end_line: int) -> List[str]:
    full = os.path.join(REPO_ROOT, rel_path)
    with open(full, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{i:3d} | {lines[i - 1]}" for i in range(start_line, min(end_line, len(lines)) + 1)]
