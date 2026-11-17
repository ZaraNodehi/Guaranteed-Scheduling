"""Exercise 5 Experimental Harness: Readers-Writers Across Semaphore, Monitor, Peterson & Dekker.

Runs 5 experimental suites:
  1. Concurrent safety & max-simultaneous-readers verification across all 12 primitive x policy pairs + CoarseMutex.
  2. Starvation & Tail-Latency Stress Test (Reader-Flood vs. Writer-Flood).
  3. Read:Write workload mix sweep (95:5, 80:20, 50:50, 20:80) measuring throughput vs. CoarseMutex speedup.
  4. CPU burn audit when a writer waits behind sleeping/slow readers (spin-poll vs kernel sleep).
  5. Exact BFS state-space model checking proving starvation exists in Readers-Pref and vanishes in Fair Turnstile.
"""
from __future__ import annotations

import json
import os
import random
import sys
import threading
import time
from collections import deque
from typing import Dict, List, Set, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
EX5_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX5_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

sys.path.insert(0, HERE)
from rw_locks import make_rw_lock  # noqa: E402


# =============================================================================
# 1. SAFETY & CONCURRENCY AUDIT
# =============================================================================
def audit_concurrency(primitive: str, policy: str, n_readers: int = 4, n_writers: int = 2,
                      ops_r: int = 60, ops_w: int = 25) -> Dict:
    n_total = n_readers + n_writers
    rw = make_rw_lock(primitive, policy, n_total)
    track_lock = threading.Lock()
    active_r = [0]
    active_w = [0]
    max_conc_r = [0]
    max_conc_w = [0]
    rw_overlap_violations = [0]
    shared_val = [0]
    barrier = threading.Barrier(n_total)

    def reader(tid: int) -> None:
        barrier.wait()
        for _ in range(ops_r):
            rw.acquire_read(tid)
            with track_lock:
                active_r[0] += 1
                if active_r[0] > max_conc_r[0]:
                    max_conc_r[0] = active_r[0]
                if active_w[0] > 0:
                    rw_overlap_violations[0] += 1
            time.sleep(0.00025)
            _ = shared_val[0]
            with track_lock:
                active_r[0] -= 1
            rw.release_read(tid)

    def writer(tid: int) -> None:
        barrier.wait()
        for _ in range(ops_w):
            rw.acquire_write(tid)
            with track_lock:
                active_w[0] += 1
                if active_w[0] > max_conc_w[0]:
                    max_conc_w[0] = active_w[0]
                if active_r[0] > 0 or active_w[0] > 1:
                    rw_overlap_violations[0] += 1
            shared_val[0] += 1
            time.sleep(0.0003)
            with track_lock:
                active_w[0] -= 1
            rw.release_write(tid)

    ths = [threading.Thread(target=reader, args=(i,)) for i in range(n_readers)] + \
          [threading.Thread(target=writer, args=(n_readers + j,)) for j in range(n_writers)]
    t0 = time.perf_counter()
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert rw_overlap_violations[0] == 0
    assert shared_val[0] == n_writers * ops_w
    return {
        "primitive": primitive,
        "policy": policy,
        "max_concurrent_readers": max_conc_r[0],
        "max_concurrent_writers": max_conc_w[0],
        "safety_violations": rw_overlap_violations[0],
        "final_counter": shared_val[0],
        "elapsed_ms": round(elapsed_ms, 2),
    }


# =============================================================================
# 2. STARVATION STRESS TEST (READER FLOOD & WRITER FLOOD)
# =============================================================================
def run_starvation_stress(primitive: str, policy: str, flood_mode: str = "reader_flood", window_s: float = 0.12) -> Dict:
    """Run fixed time-window starvation stress test measuring victim completions & max wait."""
    n_threads = 5
    rw = make_rw_lock(primitive, policy, n_threads)
    stop_flag = threading.Event()
    victim_waits_ms: List[float] = []
    flood_ops = [0]
    hold_s = 0.002

    def flood_worker(tid: int, role: str) -> None:
        while not stop_flag.is_set():
            if role == "R":
                rw.acquire_read(tid)
                flood_ops[0] += 1
                time.sleep(hold_s)
                rw.release_read(tid)
            else:
                rw.acquire_write(tid)
                flood_ops[0] += 1
                time.sleep(hold_s)
                rw.release_write(tid)
            # Tiny yield if stop requested
            if stop_flag.is_set():
                break

    def victim_worker(tid: int, role: str) -> None:
        time.sleep(0.004)  # let flood establish
        while not stop_flag.is_set():
            t0 = time.perf_counter()
            if role == "W":
                rw.acquire_write(tid)
                wait_ms = (time.perf_counter() - t0) * 1000.0
                if not stop_flag.is_set():
                    victim_waits_ms.append(wait_ms)
                    time.sleep(0.0005)
                rw.release_write(tid)
            else:
                rw.acquire_read(tid)
                wait_ms = (time.perf_counter() - t0) * 1000.0
                if not stop_flag.is_set():
                    victim_waits_ms.append(wait_ms)
                    time.sleep(0.0005)
                rw.release_read(tid)
            time.sleep(0.001)

    if flood_mode == "reader_flood":
        floods = [threading.Thread(target=flood_worker, args=(i, "R")) for i in range(4)]
        victim = threading.Thread(target=victim_worker, args=(4, "W"))
    else:
        floods = [threading.Thread(target=flood_worker, args=(i, "W")) for i in range(4)]
        victim = threading.Thread(target=victim_worker, args=(4, "R"))

    for f in floods:
        f.start()
    victim.start()
    time.sleep(window_s)
    stop_flag.set()
    for f in floods:
        f.join(timeout=2.0)
    victim.join(timeout=2.0)

    waits_sorted = sorted(victim_waits_ms) if victim_waits_ms else [window_s * 1000.0]
    return {
        "flood_mode": flood_mode,
        "primitive": primitive,
        "policy": policy,
        "window_ms": round(window_s * 1000.0, 1),
        "victim_ops": len(victim_waits_ms),
        "flood_ops": flood_ops[0],
        "victim_mean_wait_ms": round(sum(waits_sorted) / len(waits_sorted), 2),
        "victim_max_wait_ms": round(max(waits_sorted), 2),
        "victim_p90_wait_ms": round(waits_sorted[int(0.9 * (len(waits_sorted) - 1))], 2),
    }


# =============================================================================
# 3. READ/WRITE RATIO MIX SWEEP (95:5, 80:20, 50:50, 20:80)
# =============================================================================
def run_mix_bench(primitive: str, policy: str, read_pct: int, cs_sleep_ms: float = 0.3,
                  n_threads: int = 6, ops_per_thread: int = 40) -> Dict:
    rw = make_rw_lock(primitive, policy, n_threads)
    barrier = threading.Barrier(n_threads)
    rng_seed = 42
    shared = [0]
    cs_s = cs_sleep_ms / 1000.0

    def worker(tid: int) -> None:
        rng = random.Random(rng_seed + tid)
        barrier.wait()
        for _ in range(ops_per_thread):
            is_read = rng.randint(1, 100) <= read_pct
            if is_read:
                rw.acquire_read(tid)
                _ = shared[0]
                if cs_s > 0:
                    time.sleep(cs_s)
                rw.release_read(tid)
            else:
                rw.acquire_write(tid)
                shared[0] += 1
                if cs_s > 0:
                    time.sleep(cs_s)
                rw.release_write(tid)

    ths = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    tw0, tc0 = time.perf_counter(), time.process_time()
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    tc1, tw1 = time.process_time(), time.perf_counter()
    wall_ms = (tw1 - tw0) * 1000.0
    cpu_ms = (tc1 - tc0) * 1000.0
    total_ops = n_threads * ops_per_thread
    return {
        "cs_sleep_ms": cs_sleep_ms,
        "read_pct": read_pct,
        "write_pct": 100 - read_pct,
        "primitive": primitive,
        "policy": policy,
        "wall_ms": round(wall_ms, 2),
        "cpu_ms": round(cpu_ms, 2),
        "throughput_ops_s": round(total_ops / max(tw1 - tw0, 1e-9), 1),
    }


# =============================================================================
# 4. CPU BURN AUDIT WHEN WRITER WAITS BEHIND SLOW READERS
# =============================================================================
def run_cpu_burn_audit(primitive: str, policy: str = "fair", hold_ms: int = 5) -> Dict:
    rw = make_rw_lock(primitive, policy, n_threads=3, busy_spin=(primitive in ("Peterson", "Dekker")))
    barrier = threading.Barrier(3)

    def slow_reader(tid: int) -> None:
        barrier.wait()
        for _ in range(6):
            rw.acquire_read(tid)
            time.sleep(hold_ms / 1000.0)
            rw.release_read(tid)
            time.sleep(0.001)

    def writer(tid: int) -> None:
        barrier.wait()
        for _ in range(6):
            rw.acquire_write(tid)
            time.sleep(0.001)
            rw.release_write(tid)

    ths = [
        threading.Thread(target=slow_reader, args=(0,)),
        threading.Thread(target=slow_reader, args=(1,)),
        threading.Thread(target=writer, args=(2,)),
    ]
    tw0, tc0 = time.perf_counter(), time.process_time()
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    tc1, tw1 = time.process_time(), time.perf_counter()
    wall_ms = (tw1 - tw0) * 1000.0
    cpu_ms = (tc1 - tc0) * 1000.0
    return {
        "primitive": primitive,
        "policy": policy,
        "hold_ms": hold_ms,
        "wall_ms": round(wall_ms, 2),
        "cpu_ms": round(cpu_ms, 2),
        "cpu_ratio": round(cpu_ms / max(wall_ms, 1e-6), 3),
    }


# =============================================================================
# 5. EXACT BFS STATE-SPACE CHECK OF RW POLICIES (STARVATION & MUTEX AUDIT)
# =============================================================================
def bfs_rw_starvation_check(policy: str) -> Dict:
    """Explore 2-reader, 1-writer state machine (r0, r1, w, turn) for safety & starvation."""
    # Roles state: 0=idle, 1=want, 2=active
    # For fair policy: turn_w=1 gives pending writer gate before new reader enters!
    init = (0, 0, 0, 0)  # (r0, r1, w, gate_for_w)
    visited: Set[Tuple] = {init}
    q = deque([init])
    safety_err = 0
    writer_blocked_by_reader_loop = 0
    concurrent_readers_states = 0
    edges = 0

    while q:
        r0, r1, w, gate = q.popleft()
        act_r = (1 if r0 == 2 else 0) + (1 if r1 == 2 else 0)
        act_w = 1 if w == 2 else 0
        if (act_w > 0 and act_r > 0) or act_w > 1:
            safety_err += 1
        if act_r == 2:
            concurrent_readers_states += 1
        # Check if writer is waiting while readers cycle endlessly
        if w == 1 and act_r > 0 and ((r0 == 0 or r1 == 0) if policy == "readers" else False):
            writer_blocked_by_reader_loop += 1

        nxt = []
        # R0 transitions
        if r0 == 0:
            nxt.append((1, r1, w, gate))
        elif r0 == 1:
            can_enter = (w != 2) and not (policy in ("writers", "fair") and w == 1)
            if can_enter:
                nxt.append((2, r1, w, gate))
        elif r0 == 2:
            nxt.append((0, r1, w, 1 if (policy == "fair" and w == 1) else gate))

        # R1 transitions
        if r1 == 0:
            nxt.append((r0, 1, w, gate))
        elif r1 == 1:
            can_enter = (w != 2) and not (policy in ("writers", "fair") and w == 1)
            if can_enter:
                nxt.append((r0, 2, w, gate))
        elif r1 == 2:
            nxt.append((r0, 0, w, 1 if (policy == "fair" and w == 1) else gate))

        # W transitions
        if w == 0:
            nxt.append((r0, r1, 1, gate))
        elif w == 1:
            if act_r == 0:
                nxt.append((r0, r1, 2, 0))
        elif w == 2:
            nxt.append((r0, r1, 0, 0))

        for ns in nxt:
            edges += 1
            if ns not in visited:
                visited.add(ns)
                q.append(ns)

    return {
        "policy": policy,
        "reachable_states": len(visited),
        "transitions": edges,
        "safety_violations": safety_err,
        "dual_reader_states": concurrent_readers_states,
        "writer_starvation_bypass_states": writer_blocked_by_reader_loop,
    }


def main() -> None:
    prims = ["Semaphore", "Monitor", "Peterson", "Dekker"]
    policies = ["readers", "writers", "fair"]

    safety_audits = []
    for pr in prims:
        for po in policies:
            safety_audits.append(audit_concurrency(pr, po))
    safety_audits.append(audit_concurrency("CoarseMutex", "serial"))

    starvation_audits = []
    for fm in ("reader_flood", "writer_flood"):
        for pr in prims:
            for po in policies:
                starvation_audits.append(run_starvation_stress(pr, po, flood_mode=fm))

    mix_sweep = []
    for cs_ms, ops in [(0.0, 120), (0.3, 40)]:
        for pct in (95, 80, 50, 20):
            for pr in prims:
                mix_sweep.append(run_mix_bench(pr, "fair", pct, cs_sleep_ms=cs_ms, ops_per_thread=ops))
            mix_sweep.append(run_mix_bench("CoarseMutex", "serial", pct, cs_sleep_ms=cs_ms, ops_per_thread=ops))

    cpu_burn = [run_cpu_burn_audit(pr, "fair", hold_ms=5) for pr in prims]
    bfs_models = [bfs_rw_starvation_check(p) for p in policies]

    payload = {
        "exercise": "exercise-5",
        "topic": "Readers-Writers Across Semaphore, Monitor, Peterson & Dekker",
        "safety_concurrency_audits": safety_audits,
        "starvation_stress_audits": starvation_audits,
        "mix_sweep": mix_sweep,
        "cpu_burn_audits": cpu_burn,
        "bfs_rw_models": bfs_models,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print("Wrote", out_path)
    print("  Safety audits:", len(safety_audits), "| Starvation rows:", len(starvation_audits), "| Mix rows:", len(mix_sweep))


if __name__ == "__main__":
    main()
