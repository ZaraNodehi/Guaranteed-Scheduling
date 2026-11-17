"""Pytest invariants for Exercise 5 Monte Carlo, Pareto, Zipf burst, bootstrap, OS trials & seminar deliverables."""
import json
import os

import pymupdf
from pptx import Presentation

HERE = os.path.dirname(os.path.abspath(__file__))
EX5_DIR = os.path.dirname(HERE)
JSON_PATH = os.path.join(EX5_DIR, "output", "experiments.json")


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_sweep_a_mc_and_ecdfs():
    d = _load()
    sw_a = d["sweep_a_monte_carlo"]
    assert sw_a["n_workloads"] == 240
    assert len(sw_a["seed_samples_60"]) == 240
    assert len(sw_a["ecdf_lags"]["gs_vtime:stay"]) == 240
    ov = sw_a["overall"]
    assert ov["gs_vtime:stay"]["lag"]["mean"] < ov["gs_ratio:index"]["lag"]["mean"] * 0.35
    assert ov["gs_vtime:stay"]["lag"]["p99"] < ov["rr:index"]["lag"]["p99"] * 0.25


def test_sweep_b_pareto_and_c_scaling():
    d = _load()
    rows = d["sweep_b_quantum_pareto"]["rows"]
    assert len(rows) == 7
    q1 = rows[0]["policies"]["gs_vtime:stay"]
    q2 = rows[1]["policies"]["gs_vtime:stay"]
    assert q2["switches"]["mean"] < q1["switches"]["mean"] * 0.65
    assert d["sweep_c_scaling"]["scaling_rows"][-1]["skew_vtime_lag"]["mean"] < 1.8


def test_sweep_e_zipf_and_f_bootstrap():
    d = _load()
    swe = d["sweep_e_zipf_burst"]
    assert swe["n_seeds"] == 60
    assert len(swe["samples_60"]) == 60
    assert swe["summary"]["gs_vtime:stay"]["lag"]["mean"] < swe["summary"]["gs_ratio:index"]["lag"]["mean"] * 0.55

    swf = d["sweep_f_bootstrap"]
    assert swf["n_pairs"] == 240
    assert swf["n_bootstrap"] == 1000
    vs_rat = next(c for c in swf["comparisons"] if c["competitor"] == "gs_ratio:index")
    assert vs_rat["win_rate_pct"] > 95.0
    assert vs_rat["cohens_d"] > 1.5


def test_sweep_d_live_os_5_intervals():
    d = _load()
    tr = d["sweep_d_os_intervals"]["interval_trials"]
    assert len(tr) == 5
    assert tr[0]["poll_dt_sec"] == 0.01
    assert tr[-1]["poll_dt_sec"] == 0.20
    assert tr[0]["max_share_deviation"] < 0.02
    assert tr[0]["controller_switches"] > tr[-1]["controller_switches"]
    assert 20 <= len(d["sweep_d_os_intervals"]["dt005_trace"]) <= 24


def test_8_diagrams_decks_and_40p_reports():
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx",
               "docs/DECK_EN.pptx", "docs/DECK_FA.pptx",
               "docs/SPEAKER_EN.md", "docs/SPEAKER_FA.md"):
        p = os.path.join(EX5_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"

    en_pdf = pymupdf.open(os.path.join(EX5_DIR, "docs", "REPORT_EN.pdf"))
    fa_pdf = pymupdf.open(os.path.join(EX5_DIR, "docs", "REPORT_FA.pdf"))
    assert len(en_pdf) >= 40, f"REPORT_EN.pdf only {len(en_pdf)} pages"
    assert len(fa_pdf) >= 40, f"REPORT_FA.pdf only {len(fa_pdf)} pages"

    for dk in ("DECK_EN.pptx", "DECK_FA.pptx"):
        prs = Presentation(os.path.join(EX5_DIR, "docs", dk))
        assert len(prs.slides) == 10
        assert all(bool(s.notes_slide.notes_text_frame.text.strip()) for s in prs.slides)

    diag_dir = os.path.join(EX5_DIR, "diagrams")
    diags = sorted(f for f in os.listdir(diag_dir) if f.endswith(".png"))
    assert len(diags) == 8
    for f in diags:
        assert os.path.getsize(os.path.join(diag_dir, f)) > 25_000
