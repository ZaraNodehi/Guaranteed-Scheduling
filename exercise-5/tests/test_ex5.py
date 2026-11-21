"""Automated test suite for Exercise 5 (Readers-Writers across 4 primitives)."""
from __future__ import annotations

import importlib.util
import json
import os
import sys

import fitz

EX5_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.join(EX5_DIR, "code")
OUT_JSON = os.path.join(EX5_DIR, "output", "experiments.json")
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

_spec = importlib.util.spec_from_file_location("ex5_run_experiments", os.path.join(CODE_DIR, "run_experiments.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
audit_concurrency = _mod.audit_concurrency


def test_all_12_rw_locks_live_concurrency():
    for pr in ("Semaphore", "Monitor", "Peterson", "Dekker"):
        for po in ("readers", "writers", "fair"):
            res = audit_concurrency(pr, po, n_readers=4, n_writers=2, ops_r=15, ops_w=6)
            assert res["safety_violations"] == 0
            assert res["max_concurrent_readers"] >= 2


def test_experiments_json_starvation_speedup_and_bfs():
    assert os.path.exists(OUT_JSON)
    with open(OUT_JSON, encoding="utf-8") as f:
        d = json.load(f)

    # 1. Readers-Pref starves writer under reader flood across all 4 primitives
    r_flood = [r for r in d["starvation_stress_audits"] if r["flood_mode"] == "reader_flood"]
    for pr in ("Semaphore", "Monitor", "Peterson", "Dekker"):
        rp = next(r for r in r_flood if r["primitive"] == pr and r["policy"] == "readers")
        fp = next(r for r in r_flood if r["primitive"] == pr and r["policy"] == "fair")
        assert rp["victim_ops"] <= 1
        assert fp["victim_ops"] >= 10

    # 2. Fair Monitor/Peterson/Dekker defeat Writer-Flood barging (>= 5 victim reads)
    w_flood = [r for r in d["starvation_stress_audits"] if r["flood_mode"] == "writer_flood"]
    for pr in ("Monitor", "Peterson", "Dekker"):
        fp = next(r for r in w_flood if r["primitive"] == pr and r["policy"] == "fair")
        assert fp["victim_ops"] >= 5

    # 3. Read-heavy (95%) realistic scan (0.3 ms) achieves >= 2.5x speedup over CoarseMutex
    m95 = {r["primitive"]: r for r in d["mix_sweep"] if r["cs_sleep_ms"] == 0.3 and r["read_pct"] == 95}
    for pr in ("Semaphore", "Monitor", "Peterson", "Dekker"):
        assert m95[pr]["throughput_ops_s"] >= m95["CoarseMutex"]["throughput_ops_s"] * 2.5

    # 4. CPU burn ratio contrast
    cb = {r["primitive"]: r for r in d["cpu_burn_audits"]}
    assert cb["Peterson"]["cpu_ms"] > cb["Semaphore"]["cpu_ms"] * 10
    assert cb["Dekker"]["cpu_ms"] > cb["Monitor"]["cpu_ms"] * 10

    # 5. BFS states
    bfs = {r["policy"]: r for r in d["bfs_rw_models"]}
    assert bfs["readers"]["writer_starvation_bypass_states"] > 0
    assert bfs["fair"]["writer_starvation_bypass_states"] == 0
    assert all(v["safety_violations"] == 0 for v in bfs.values())


def test_deliverables_ex5():
    diag_dir = os.path.join(EX5_DIR, "diagrams")
    pngs = [f for f in os.listdir(diag_dir) if f.endswith(".png") and "rubric_flowchart" not in f]
    assert len(pngs) == 8
    rubric_flow = os.path.join(diag_dir, "fig_exercise5_rubric_flowchart.png")
    assert os.path.isfile(rubric_flow) and os.path.getsize(rubric_flow) > 10_000
    for stem in ("REPORT_EN", "REPORT_FA"):
        pdf = os.path.join(EX5_DIR, "docs", f"{stem}.pdf")
        docx = os.path.join(EX5_DIR, "docs", f"{stem}.docx")
        md = os.path.join(EX5_DIR, f"{stem}.md")
        assert os.path.exists(pdf) and os.path.exists(docx) and os.path.exists(md)
        with fitz.open(pdf) as doc:
            assert len(doc) >= 14
