"""Automated test suite for Exercise 4 (Dekker, Peterson, Semaphore, Monitor)."""
from __future__ import annotations

import json
import os
import sys
import threading

import fitz

EX4_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.join(EX4_DIR, "code")
OUT_JSON = os.path.join(EX4_DIR, "output", "experiments.json")
sys.path.insert(0, CODE_DIR)

from sync_primitives import (  # noqa: E402
    BinarySemaphoreLock,
    DekkerLock,
    FilterLock,
    MesaMonitorLock,
    PetersonLock,
    TournamentDekkerLock,
)


def _verify_lock(factory, n_threads: int, iters: int) -> None:
    lock = factory()
    counter = [0]
    bar = threading.Barrier(n_threads)

    def worker(tid: int) -> None:
        bar.wait()
        for _ in range(iters):
            lock.acquire(tid)
            val = counter[0]
            counter[0] = val + 1
            lock.release(tid)

    ths = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    assert counter[0] == n_threads * iters


def test_all_primitives_zero_lost_updates():
    for fac in (DekkerLock, PetersonLock, BinarySemaphoreLock, MesaMonitorLock):
        _verify_lock(fac, 2, 250)
    _verify_lock(lambda: FilterLock(4), 4, 150)
    _verify_lock(lambda: TournamentDekkerLock(4), 4, 150)
    _verify_lock(BinarySemaphoreLock, 4, 150)
    _verify_lock(MesaMonitorLock, 4, 150)


def test_bfs_model_checker_invariants():
    assert os.path.exists(OUT_JSON)
    with open(OUT_JSON, encoding="utf-8") as f:
        d = json.load(f)

    dek = {r["model"]: r for r in d["dekker_evolution_fsm"]}
    assert dek["Dekker v2 (Check-Then-Set)"]["mutex_violations"] > 0
    assert dek["Dekker v3 (Set-Then-Wait)"]["deadlock_states"] > 0
    assert dek["Dekker v5 (Correct Final)"]["mutex_violations"] == 0
    assert dek["Dekker v5 (Correct Final)"]["deadlock_states"] == 0

    all_p = {r["model"]: r for r in d["all_primitives_fsm"]}
    assert all_p["Peterson (Sequential Consistency)"]["mutex_violations"] == 0
    assert all_p["Peterson (TSO Store Buffer, No Fence)"]["mutex_violations"] > 0
    assert all_p["Binary Semaphore (P/V Correct)"]["mutex_violations"] == 0
    assert all_p["Monitor (Mesa 'if' Bug)"]["mutex_violations"] > 0
    assert all_p["Monitor (Mesa 'while' Guard)"]["mutex_violations"] == 0


def test_cpu_burn_and_deliverables():
    with open(OUT_JSON, encoding="utf-8") as f:
        d = json.load(f)
    hold10 = {r["primitive"]: r for r in d["lock_holder_sleep_audit"] if r["hold_ms"] == 10}
    assert hold10["Peterson (Busy-Wait)"]["cpu_ms"] > hold10["Semaphore (Blocking)"]["cpu_ms"] * 10
    assert hold10["Dekker (Busy-Wait)"]["cpu_ms"] > hold10["Monitor (Mesa Cond)"]["cpu_ms"] * 10

    diag_dir = os.path.join(EX4_DIR, "diagrams")
    pngs = [f for f in os.listdir(diag_dir) if f.endswith(".png") and "rubric_flowchart" not in f]
    assert len(pngs) == 10
    rubric_flow = os.path.join(diag_dir, "fig_exercise4_rubric_flowchart.png")
    assert os.path.isfile(rubric_flow) and os.path.getsize(rubric_flow) > 10_000

    for stem in ("REPORT_EN", "REPORT_FA"):
        pdf = os.path.join(EX4_DIR, "docs", f"{stem}.pdf")
        docx = os.path.join(EX4_DIR, "docs", f"{stem}.docx")
        md = os.path.join(EX4_DIR, f"{stem}.md")
        assert os.path.exists(pdf) and os.path.exists(docx) and os.path.exists(md)
        with fitz.open(pdf) as doc:
            assert len(doc) >= 40, f"{stem}.pdf must be 40+ pages, got {len(doc)}"
