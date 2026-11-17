"""Integrated Real-Time Scheduling + Synchronization Kernel Simulator (Exercise 6).

Combines:
1. Discrete-tick Priority Inversion & Priority Inheritance Protocol (PIP) simulator
   modeling the classic Mars Pathfinder scenario (T_High, T_Medium, T_Low).
2. Spin-Lock vs Blocking-Lock Priority Preemption hazard simulator.
3. Live multi-threaded RT Telemetry + Readers-Writers shared table benchmark
   reusing Exercise 5's verified RW implementations.
"""
from __future__ import annotations

import os
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "exercise-5", "code"))

from core.gs_core import RTTask, simulate_rt  # noqa: E402
from rw_locks import make_rw_lock  # noqa: E402


@dataclass
class LockTaskSpec:
    name: str
    prio: int          # Higher integer = higher priority
    period: int
    wcet: int
    deadline: int
    lock_start: Optional[int] = None   # local execution tick when lock is requested
    lock_dur: int = 0                  # how many ticks lock is held
    release_offset: int = 0


def simulate_priority_inversion(mode: str = "no_pip", horizon: int = 60, spin_limit: int = 12) -> Dict:
    """Simulate T_Low, T_Medium, T_High sharing a single critical mutex M.

    Modes:
    - 'no_pip': Fixed-Priority Preemptive without Priority Inheritance (unbounded inversion).
    - 'pip': Fixed-Priority Preemptive WITH Priority Inheritance Protocol (Mars Pathfinder fix).
    - 'spin_hazard': Fixed-Priority Preemptive where lock is a spinlock (T_High spins forever/times out).
    """
    specs = [
        LockTaskSpec("T_Low",    prio=1, period=30, wcet=5, deadline=30, lock_start=0, lock_dur=4, release_offset=0),
        LockTaskSpec("T_High",   prio=3, period=18, wcet=3, deadline=8,  lock_start=1, lock_dur=2, release_offset=2),
        LockTaskSpec("T_Medium", prio=2, period=24, wcet=7, deadline=24, lock_start=None, lock_dur=0, release_offset=3),
    ]

    active_jobs: Dict[str, Dict] = {}
    lock_owner: Optional[str] = None
    timeline: List[Tuple[int, str]] = []
    misses: List[Dict] = []
    high_block_ticks = 0
    spin_stalls = 0
    high_latencies: List[int] = []

    for t in range(horizon):
        # 1. Release periodic jobs
        for sp in specs:
            if t >= sp.release_offset and (t - sp.release_offset) % sp.period == 0:
                job_id = (t - sp.release_offset) // sp.period
                active_jobs[sp.name] = {
                    "spec": sp,
                    "job_id": job_id,
                    "release": t,
                    "abs_deadline": t + sp.deadline,
                    "done": 0,
                    "holding_lock": False,
                    "lock_rem": 0,
                    "blocked": False,
                    "spinning": False,
                    "spin_ticks": 0,
                    "missed": False,
                }

        # 2. Check deadlines at start of tick
        for name, job in active_jobs.items():
            if not job["missed"] and t >= job["abs_deadline"] and job["done"] < job["spec"].wcet:
                job["missed"] = True
                misses.append({"task": name, "job_id": job["job_id"], "tick": t, "deadline": job["abs_deadline"]})

        # 3. Compute effective priorities (PIP boosts lock owner to max waiting priority)
        eff_prio: Dict[str, int] = {name: j["spec"].prio for name, j in active_jobs.items()}
        if mode == "pip" and lock_owner and lock_owner in active_jobs:
            waiter_prios = [
                j["spec"].prio for name, j in active_jobs.items()
                if j["blocked"] or (
                    j["spec"].lock_start is not None
                    and j["done"] == j["spec"].lock_start
                    and not j["holding_lock"]
                    and lock_owner != name
                )
            ]
            if waiter_prios:
                eff_prio[lock_owner] = max(eff_prio[lock_owner], max(waiter_prios))

        # 4. Select runnable highest-effective-priority job
        #    Note: in 'spin_hazard', a waiting job stays runnable (spinning!) instead of blocking.
        candidates = []
        for name, j in active_jobs.items():
            if j["done"] >= j["spec"].wcet:
                continue
            sp = j["spec"]
            # Check if job needs lock right now
            needs_lock = (
                sp.lock_start is not None
                and j["done"] == sp.lock_start
                and not j["holding_lock"]
                and sp.lock_dur > 0
            )
            if needs_lock and lock_owner is not None and lock_owner != name:
                if mode == "spin_hazard":
                    j["spinning"] = True
                    candidates.append(name)
                else:
                    j["blocked"] = True
                    if name == "T_High":
                        high_block_ticks += 1
                    # Recompute PIP boost immediately if mode == 'pip'
                    if mode == "pip" and lock_owner in eff_prio:
                        eff_prio[lock_owner] = max(eff_prio[lock_owner], sp.prio)
            else:
                j["blocked"] = False
                j["spinning"] = False
                candidates.append(name)

        if not candidates:
            timeline.append((t, "IDLE"))
            continue

        candidates.sort(key=lambda n: (-eff_prio[n], active_jobs[n]["release"], n))
        chosen = candidates[0]
        j = active_jobs[chosen]
        sp = j["spec"]

        # Handle lock request / spinning execution
        needs_lock = (
            sp.lock_start is not None
            and j["done"] == sp.lock_start
            and not j["holding_lock"]
            and sp.lock_dur > 0
        )
        if needs_lock:
            if lock_owner is None or lock_owner == chosen:
                lock_owner = chosen
                j["holding_lock"] = True
                j["lock_rem"] = sp.lock_dur
            elif mode == "spin_hazard":
                # Busy-spinning consumes the CPU tick without making progress!
                spin_stalls += 1
                j["spin_ticks"] += 1
                timeline.append((t, f"{chosen}_SPIN"))
                if chosen == "T_High":
                    high_block_ticks += 1
                if j["spin_ticks"] >= spin_limit and not j["missed"]:
                    j["missed"] = True
                    misses.append({"task": chosen, "job_id": j["job_id"], "tick": t + 1, "deadline": j["abs_deadline"], "reason": "spin_deadlock"})
                continue

        # Execute 1 useful CPU tick
        j["done"] += 1
        if j["holding_lock"]:
            j["lock_rem"] -= 1
            if j["lock_rem"] <= 0:
                j["holding_lock"] = False
                if lock_owner == chosen:
                    lock_owner = None
                # Unblock any waiting jobs so next tick sees them ready
                for oj in active_jobs.values():
                    oj["blocked"] = False

        timeline.append((t, chosen))
        if j["done"] >= sp.wcet:
            if chosen == "T_High":
                high_latencies.append((t + 1) - j["release"])
            del active_jobs[chosen]

    return {
        "mode": mode,
        "horizon": horizon,
        "total_misses": len(misses),
        "high_misses": sum(1 for m in misses if m["task"] == "T_High"),
        "misses": misses,
        "high_blocked_ticks": high_block_ticks,
        "spin_stall_ticks": spin_stalls,
        "high_max_response_ticks": max(high_latencies) if high_latencies else horizon,
        "timeline_sample": [f"{t}:{p}" for t, p in timeline[:24]],
        "timeline": timeline,
    }


def run_rt_rw_pipeline(primitive: str, policy: str, duration_s: float = 0.25) -> Dict:
    """Live multi-threaded RT telemetry + RW shared routing table benchmark.

    - 3 periodic telemetry reader threads (0.25 ms read scan, 0.2 ms sleep)
    - 1 route writer thread (0.5 ms exclusive update, 1.5 ms sleep)
    - 1 high-priority RT control thread reading state with strict 4.0 ms deadline
    """
    rw = make_rw_lock(primitive, policy, n_threads=5)
    stop = threading.Event()
    table = {"version": 0, "route_crc": 100}
    rt_latencies_ms: List[float] = []
    rt_deadline_ms = 1.6
    reader_ops = [0]
    writer_ops = [0]

    def reader_worker(tid: int) -> None:
        while not stop.is_set():
            rw.acquire_read(tid)
            _ = table["version"] + table["route_crc"]
            time.sleep(0.00035)
            rw.release_read(tid)
            reader_ops[0] += 1
            time.sleep(0.0002)

    def writer_worker(tid: int) -> None:
        while not stop.is_set():
            rw.acquire_write(tid)
            table["version"] += 1
            table["route_crc"] ^= 0x5A
            time.sleep(0.0008)
            rw.release_write(tid)
            writer_ops[0] += 1
            time.sleep(0.0012)

    def rt_control_worker(tid: int) -> None:
        while not stop.is_set():
            t0 = time.perf_counter()
            rw.acquire_read(tid)
            _ = table["version"]
            rw.release_read(tid)
            lat = (time.perf_counter() - t0) * 1000.0
            rt_latencies_ms.append(lat)
            time.sleep(0.0012)

    ths = (
        [threading.Thread(target=reader_worker, args=(i,)) for i in range(3)]
        + [threading.Thread(target=writer_worker, args=(3,))]
        + [threading.Thread(target=rt_control_worker, args=(4,))]
    )
    tc0, tw0 = time.process_time(), time.perf_counter()
    for th in ths:
        th.start()
    time.sleep(duration_s)
    stop.set()
    for th in ths:
        th.join(timeout=2.0)
    tw1, tc1 = time.perf_counter(), time.process_time()

    wall_s = max(tw1 - tw0, 1e-9)
    lats = sorted(rt_latencies_ms) if rt_latencies_ms else [0.0]
    hits = sum(1 for x in lats if x <= rt_deadline_ms)
    total_ops = reader_ops[0] + writer_ops[0] + len(lats)
    return {
        "primitive": primitive,
        "policy": policy,
        "duration_ms": round(wall_s * 1000.0, 2),
        "cpu_ms": round((tc1 - tc0) * 1000.0, 2),
        "reader_ops": reader_ops[0],
        "writer_ops": writer_ops[0],
        "rt_samples": len(lats),
        "rt_deadline_hits": hits,
        "rt_hit_rate_pct": round(100.0 * hits / max(len(lats), 1), 2),
        "rt_mean_lat_ms": round(sum(lats) / len(lats), 3),
        "rt_p95_lat_ms": round(lats[int(0.95 * (len(lats) - 1))], 3),
        "rt_max_lat_ms": round(max(lats), 3),
        "total_throughput_ops_s": round(total_ops / wall_s, 1),
    }


def run_gs_rt_hybrid_audit() -> Dict:
    """Compare pure RM vs EDF vs GS under mixed periodic RT workload from Exercise 3."""
    tasks = [
        RTTask("T_Ctrl", period=4, wcet=1, deadline=4, weight=4),
        RTTask("T_Nav",  period=6, wcet=2, deadline=6, weight=3),
        RTTask("T_Log",  period=8, wcet=3, deadline=8, weight=2),
    ]
    res = {}
    for pol in ("rm", "edf", "gs_vtime:stay"):
        sim = simulate_rt(tasks, horizon=24, policy=pol, drop_on_miss=False)
        res[pol] = {
            "misses": sim["missed"],
            "context_switches": sim["context_switches"],
            "preemptions": sim["preemptions"],
            "jain_fairness": round(sim["jain_fairness"], 4),
            "worst_response": sim["worst_response"],
            "utilization": round(sum(t.wcet / t.period for t in tasks), 4),
        }
    return res
