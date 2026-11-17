"""Exercise 7 Live Capstone Demonstration Suite.

Runs fast (< 2s), deterministic live demonstrations covering every core lesson
from Exercises 1-6 (static weighted GPS, dynamic latecomer shock, sleeper
exploitation vs gs_capped, real-time EDF boundary vs GS overload resilience, and
O(log n) heap dispatch speedup).
"""
from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EX7_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX7_DIR)
EX6_CODE = os.path.join(REPO_ROOT, "exercise-6", "code")

sys.path.insert(0, HERE)
sys.path.insert(0, EX6_CODE)
from gs_core import Proc, RTTask, simulate_procs, simulate_rt  # noqa: E402
from gs_optimized import LinearScanScheduler, OptimizedHeapScheduler  # noqa: E402


def main() -> None:
    print("=== Guaranteed Scheduling Capstone Demo (Exercises 1-7) ===")

    # 1. Static proportional shares
    r1 = simulate_procs([Proc("A", 0, 12, 1), Proc("B", 0, 12, 2), Proc("C", 0, 12, 3)], "gs_vtime:index", 1)
    print(f"[Demo 1 - Static Weighted GPS] lag={r1.max_abs_lag:.4f}, sw={r1.context_switches}, avg_ta={r1.mean_turnaround:.2f}")

    # 2. Dynamic arrival shock
    dyn = [Proc("Anchor", 0, 30, 1), Proc("Latecomer", 12, 12, 1)]
    r2_leg = simulate_procs(dyn, "gs_ratio:index", 1)
    r2_vt = simulate_procs(dyn, "gs_vtime:stay", 1)
    print(f"[Demo 2 - Dynamic Arrival] gs_ratio gap={r2_leg.max_starve_gap} (lag={r2_leg.max_abs_lag:.2f}) vs gs_vtime:stay gap={r2_vt.max_starve_gap} (lag={r2_vt.max_abs_lag:.2f})")

    # 3. Sleeper wakeup burst
    slp = [Proc("Steady", 0, 50, 1), Proc("Sleeper", 0, 20, 1, sleep_at=((1, 20),))]
    r3_vt = simulate_procs(slp, "gs_vtime:index", 1)
    r3_cp = simulate_procs(slp, "gs_capped:stay", 1)
    print(f"[Demo 3 - Sleeper Exploit] uncapped gap={r3_vt.max_starve_gap} vs gs_capped:stay gap={r3_cp.max_starve_gap}")

    # 4. Real-time boundary vs overload: RTTask(name, period, wcet, deadline)
    rt_ok = [RTTask("T1", 3, 1, 1), RTTask("T2", 5, 2, 5), RTTask("T3", 6, 1, 6)]
    res_gs = simulate_rt(rt_ok, "gs_vtime:index", 30)
    res_edf = simulate_rt(rt_ok, "edf:index", 30)
    print(f"[Demo 4 - RT Boundary] gs_vtime misses={res_gs['missed']} vs EDF misses={res_edf['missed']}")

    # 5. O(log n) heap speedup @ N=1000
    n = 1000
    ls, hp = LinearScanScheduler(), OptimizedHeapScheduler()
    for i in range(n):
        ls.add_task(i, f"P{i}", (i % 5) + 1)
        hp.add_task(i, f"P{i}", (i % 5) + 1)
    t0 = time.perf_counter()
    for _ in range(1000):
        ls.step()
    t_lin = (time.perf_counter() - t0) * 1e6 / 1000
    t0 = time.perf_counter()
    for _ in range(1000):
        hp.step()
    t_hp = (time.perf_counter() - t0) * 1e6 / 1000
    print(f"[Demo 5 - Heap Speedup N={n}] Linear={t_lin:.2f} us/step vs Heap={t_hp:.3f} us/step ({t_lin/t_hp:.1f}x faster)")


if __name__ == "__main__":
    main()
