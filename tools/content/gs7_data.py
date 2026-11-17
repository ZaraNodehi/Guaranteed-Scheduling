"""Dynamic loader and table formatters for Exercise 7 Capstone synthesis reports."""
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
            f"{m['R7_Combined_Stress'][p]['max_abs_lag']:.2f} / gap {m['R7_Combined_Stress'][p]['max_starve_gap']}",
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


def eevdf_summary_rows(d: Dict) -> List[List[str]]:
    sm = d["eevdf_prototype"]["summary"]
    ct = d["eevdf_prototype"]["canonical_trace"]
    names = [
        ("eevdf", "EEVDF Prototype (ve<=V, min vd)"),
        ("gs_capped_var", "Fixed-Quantum gs_capped"),
        ("rr_var", "Unweighted Round-Robin (slice=2)"),
    ]
    rows = []
    for k, lbl in names:
        rows.append([
            lbl,
            f"{sm[k]['mean_lag']:.4f}",
            f"{sm[k]['p95_lag']:.4f}",
            f"{sm[k]['max_lag']:.4f}",
            f"{ct[k]['max_abs_lag']:.4f} ({ct[k]['switches']} sw)",
        ])
    return rows


def eevdf_seed_rows(d: Dict, start: int = 0, end: int = 20) -> List[List[str]]:
    rows = []
    for r in d["eevdf_prototype"]["seed_rows_40"][start:end]:
        ws = ",".join(str(x) for x in r["weights"])
        sl = ",".join(str(x) for x in r["slices"])
        rows.append([
            str(r["seed"]),
            f"[{ws}]",
            f"[{sl}]",
            f"{r['eevdf_lag']:.3f}",
            f"{r['gs_var_lag']:.3f}",
            f"{r['rr_var_lag']:.3f}",
            f"{r['eevdf_sw']} / {r['gs_var_sw']}",
        ])
    return rows


def audit_rows(d: Dict) -> List[List[str]]:
    rows = []
    for r in d["repo_audit_ex1_to_6"]:
        rows.append([
            r["exercise"],
            "PASS" if r["has_json"] else "FAIL",
            f"{r['diagram_count']} PNGs",
            f"{r['en_pages']}p (PDF+DOCX)" if (r["has_en_pdf"] and r["has_en_docx"]) else "FAIL",
            f"{r['fa_pages']}p (PDF+DOCX)" if (r["has_fa_pdf"] and r["has_fa_docx"]) else "FAIL",
            "10-slide PPTX" if r.get("has_decks") else ("README" if r["has_readme"] else "FAIL"),
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


def live_os_trace_rows(d: Dict, start: int = 0, end: int = 20) -> List[List[str]]:
    rows = []
    for r in d["live_capstone_os_demo"]["trace"][start:end]:
        sh = "/".join(f"{x*100:.1f}%" for x in r["shares"])
        vt = ", ".join(f"{x:.3f}" for x in r["vtimes"])
        rows.append([
            str(r["step"]),
            f"{r['elapsed_s']:.3f}s",
            r["chosen"],
            f"[{vt}]",
            sh,
            f"{r['max_err']*100:.2f}%",
        ])
    return rows


def code_snippet(rel_path: str, start_line: int, end_line: int) -> List[str]:
    p = os.path.join(REPO_ROOT, rel_path)
    with open(p, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [f"{i:3d}: {lines[i-1]}" for i in range(max(1, start_line), min(len(lines), end_line) + 1)]


def eevdf_canonical_trace_rows(d: Dict, start: int = 0, end: int = 17) -> List[List[str]]:
    ct = d["eevdf_prototype"]["canonical_trace"]
    ev_tr = ct["eevdf"]["trace"]
    gs_tr = ct["gs_capped_var"]["trace"]
    rr_tr = ct["rr_var"]["trace"]
    rows = []
    for i in range(start, min(end, len(ev_tr))):
        e, g, r = ev_tr[i], gs_tr[i], rr_tr[i]
        rows.append([
            str(e["t"]),
            e["chosen"].split("(")[0],
            f"{e['max_lag']:.3f}",
            g["chosen"].split("(")[0],
            f"{g['max_lag']:.3f}",
            f"{r['max_lag']:.3f}",
        ])
    return rows


def seminar_slides_rows(lang: str = "en") -> List[List[str]]:
    import gs_decks
    spec = gs_decks.build_decks_spec(7)
    rows = []
    for idx, sl in enumerate(spec["slides"], start=1):
        fig = sl.get("figure", "(Cover / Summary)")
        title = sl["title_en"] if lang == "en" else sl["title_fa"]
        notes = sl["notes_en"] if lang == "en" else sl["notes_fa"]
        rows.append([str(idx), sl["tag"], title, fig, notes])
    return rows
