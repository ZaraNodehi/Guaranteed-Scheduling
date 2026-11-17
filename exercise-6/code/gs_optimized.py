"""Refactored O(log n) Guaranteed Scheduler with V(t) anchoring, stay tie-breaking,
anti-sleeper credit cap (gs_capped), and drift-free fixed-point arithmetic.

Contrasts directly with a faithful O(n) linear-scan baseline mirroring the
legacy ``GuaranteedScheduling.py`` architecture.
"""
from __future__ import annotations

import heapq
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import psutil

SCALE_FP = 1_000_000_000  # 10^9 nanosecond-grade fixed-point inverse weight unit


@dataclass
class TaskState:
    tid: int
    name: str
    weight: int
    used: int = 0
    vtime_fp: int = 0
    version: int = 0
    active: bool = True


class LinearScanScheduler:
    """Legacy O(n) linear-scan used/weight dispatcher (mirrors GuaranteedScheduling.py)."""

    def __init__(self) -> None:
        self.tasks: List[TaskState] = []

    def add_task(self, tid: int, name: str, weight: int) -> None:
        self.tasks.append(TaskState(tid=tid, name=name, weight=weight, used=0, vtime_fp=0))

    def step(self) -> Optional[int]:
        best_idx = -1
        best_score = float("inf")
        for idx, t in enumerate(self.tasks):
            if not t.active:
                continue
            sc = t.used / t.weight
            if sc < best_score:
                best_score = sc
                best_idx = idx
        if best_idx < 0:
            return None
        chosen = self.tasks[best_idx]
        chosen.used += 1
        return chosen.tid


class OptimizedHeapScheduler:
    """Refactored O(log n) min-heap GS scheduler with:
    - Fixed-point scaled integer virtual time (zero IEEE-754 drift)
    - Global virtual clock V(t) anchoring for newly arriving tasks
    - Anti-sleeper wakeup credit bound (cap_ticks * SCALE_FP // min_w)
    - Tie hysteresis (stay_bonus when equal to current running task)
    """

    def __init__(self, wakeup_cap_ticks: int = 1, use_stay: bool = True) -> None:
        self.tasks: Dict[int, TaskState] = {}
        self._heap: List[Tuple[int, int, int]] = []  # (vtime_fp, tid, version)
        self.sys_vtime_fp: int = 0
        self.active_weight_sum: int = 0
        self.last_tid: Optional[int] = None
        self.wakeup_cap_ticks = wakeup_cap_ticks
        self.use_stay = use_stay
        self.context_switches = 0

    def add_task(self, tid: int, name: str, weight: int) -> None:
        st = TaskState(tid=tid, name=name, weight=weight, used=0, vtime_fp=self.sys_vtime_fp, version=0)
        self.tasks[tid] = st
        self.active_weight_sum += weight
        heapq.heappush(self._heap, (st.vtime_fp, tid, st.version))

    def sleep_task(self, tid: int) -> None:
        st = self.tasks[tid]
        if st.active:
            st.active = False
            st.version += 1
            self.active_weight_sum -= st.weight

    def wake_task(self, tid: int) -> None:
        st = self.tasks[tid]
        if not st.active:
            st.active = True
            self.active_weight_sum += st.weight
            cap_floor = max(0, self.sys_vtime_fp - (self.wakeup_cap_ticks * SCALE_FP) // st.weight)
            if st.vtime_fp < cap_floor:
                st.vtime_fp = cap_floor
            st.version += 1
            heapq.heappush(self._heap, (st.vtime_fp, tid, st.version))

    def step(self) -> Optional[int]:
        if self.active_weight_sum <= 0:
            return None
        # Check stay optimization cleanly in O(1): if last_tid is still active and tied with heap min
        while self._heap:
            vt, tid, ver = self._heap[0]
            st = self.tasks.get(tid)
            if st is None or not st.active or st.version != ver:
                heapq.heappop(self._heap)
                continue
            break
        if not self._heap:
            return None

        min_vt = self._heap[0][0]
        if self.use_stay and self.last_tid is not None:
            lt = self.tasks.get(self.last_tid)
            if lt is not None and lt.active and lt.vtime_fp <= min_vt:
                chosen = lt
            else:
                _, tid, _ = heapq.heappop(self._heap)
                chosen = self.tasks[tid]
        else:
            _, tid, _ = heapq.heappop(self._heap)
            chosen = self.tasks[tid]

        if self.last_tid is not None and chosen.tid != self.last_tid:
            self.context_switches += 1
        self.last_tid = chosen.tid

        # Advance global V(t) and chosen task virtual time by exact integer fixed-point
        self.sys_vtime_fp += SCALE_FP // self.active_weight_sum
        chosen.used += 1
        chosen.vtime_fp += SCALE_FP // chosen.weight
        chosen.version += 1
        heapq.heappush(self._heap, (chosen.vtime_fp, chosen.tid, chosen.version))
        return chosen.tid


def run_live_os_comparison(mode: str = "optimized") -> Dict:
    """Compare legacy unanchored dt=0.10s vs refactored V(t)-anchored stay dt=0.05s
    when worker P3 arrives dynamically mid-run at t=0.6s (total 1.8s)."""
    burn = "import time\nend = time.monotonic() + 3.5\nx = 0\nwhile time.monotonic() < end:\n    x = (x + 1) & 0xFFFF\n"
    dt = 0.10 if mode == "legacy" else 0.05
    total_dur = 1.8
    spawn_at = 0.6

    procs: List[subprocess.Popen] = []
    ps: List[psutil.Process] = []
    weights = [2, 2]
    used = [0.0, 0.0]
    last_cpu = [0.0, 0.0]
    vtime = [0.0, 0.0]
    spawned_p3 = False
    p3_post_spawn_cpu = [0.0, 0.0, 0.0]
    pre_spawn_snapshot = None
    prev_idx = None
    switches = 0

    for _ in range(2):
        sub = subprocess.Popen([sys.executable, "-c", burn])
        p = psutil.Process(sub.pid)
        try:
            p.suspend()
        except Exception:
            pass
        procs.append(sub)
        ps.append(p)

    t0 = time.monotonic()
    try:
        while True:
            elapsed = time.monotonic() - t0
            if elapsed >= total_dur:
                break
            if (not spawned_p3) and elapsed >= spawn_at:
                spawned_p3 = True
                pre_spawn_snapshot = list(used)
                sub3 = subprocess.Popen([sys.executable, "-c", burn])
                p3 = psutil.Process(sub3.pid)
                try:
                    p3.suspend()
                except Exception:
                    pass
                procs.append(sub3)
                ps.append(p3)
                weights.append(2)
                used.append(0.0)
                last_cpu.append(0.0)
                if mode == "legacy":
                    vtime.append(0.0)
                else:
                    # Virtual-time anchor V(t) prevents latecomer CPU monopoly!
                    anchor = sum(vtime) / len(vtime)
                    vtime.append(anchor)

            if mode == "legacy":
                scores = [used[i] / weights[i] for i in range(len(ps))]
                cur = min(range(len(ps)), key=lambda i: (scores[i], i))
            else:
                scores = [vtime[i] for i in range(len(ps))]
                min_s = min(scores)
                if prev_idx is not None and abs(scores[prev_idx] - min_s) <= 1e-4:
                    cur = prev_idx
                else:
                    cur = min(range(len(ps)), key=lambda i: (scores[i], i))

            if prev_idx is not None and cur != prev_idx:
                switches += 1
            prev_idx = cur

            try:
                ps[cur].resume()
            except Exception:
                pass
            time.sleep(dt)
            try:
                ps[cur].suspend()
                ct = ps[cur].cpu_times()
                c = float(ct.user + ct.system)
                delta = max(0.0, c - last_cpu[cur])
                last_cpu[cur] = c
                used[cur] += delta
                vtime[cur] += delta / weights[cur]
                if spawned_p3:
                    p3_post_spawn_cpu[cur] += delta
            except Exception:
                pass
    finally:
        for sub, p in zip(procs, ps):
            try:
                p.resume()
            except Exception:
                pass
            try:
                sub.kill()
                sub.wait(timeout=2)
            except Exception:
                pass

    post_tot = sum(p3_post_spawn_cpu)
    post_shares = [round(x / post_tot, 4) if post_tot > 0 else 0.0 for x in p3_post_spawn_cpu]
    max_post_dev = round(max(abs(s - 1.0 / 3.0) for s in post_shares), 4)
    return {
        "mode": mode,
        "dt": dt,
        "switches": switches,
        "total_cpu": [round(x, 4) for x in used],
        "post_spawn_cpu": [round(x, 4) for x in p3_post_spawn_cpu],
        "post_spawn_shares": post_shares,
        "max_post_spawn_deviation": max_post_dev,
    }
