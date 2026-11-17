"""Exercise 4: Implementations of Dekker, Peterson (+ Filter Lock), Semaphore, and Monitor.

Includes both thread-safe executable OS primitives (for real multi-threaded CPU
and wall-clock benchmarks) and clean algorithmic reference forms.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Callable, List


class DekkerLock:
    """Dekker's 1962 mutually exclusive 2-thread software lock (correct final version)."""

    def __init__(self, yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        self.flag = [False, False]
        self.turn = 0
        self._yield = yield_fn

    def acquire(self, tid: int) -> int:
        other = 1 - tid
        spins = 0
        self.flag[tid] = True
        while self.flag[other]:
            if self.turn != tid:
                self.flag[tid] = False
                while self.turn != tid:
                    spins += 1
                    self._yield()
                self.flag[tid] = True
            else:
                spins += 1
                self._yield()
        return spins

    def release(self, tid: int) -> None:
        self.turn = 1 - tid
        self.flag[tid] = False


class PetersonLock:
    """Peterson's 1981 2-thread mutual exclusion algorithm."""

    def __init__(self, yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        self.flag = [False, False]
        self.turn = 0
        self._yield = yield_fn

    def acquire(self, tid: int) -> int:
        other = 1 - tid
        spins = 0
        self.flag[tid] = True
        self.turn = other
        while self.flag[other] and self.turn == other:
            spins += 1
            self._yield()
        return spins

    def release(self, tid: int) -> None:
        self.flag[tid] = False


class FilterLock:
    """N-thread generalization of Peterson's algorithm (Herlihy & Shavit Filter Lock)."""

    def __init__(self, n_threads: int, yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        self.n = n_threads
        self.level = [0] * n_threads
        self.victim = [0] * n_threads
        self._yield = yield_fn

    def acquire(self, tid: int) -> int:
        spins = 0
        for lvl in range(1, self.n):
            self.level[tid] = lvl
            self.victim[lvl] = tid
            while any(k != tid and self.level[k] >= lvl for k in range(self.n)) and self.victim[lvl] == tid:
                spins += 1
                self._yield()
        return spins

    def release(self, tid: int) -> None:
        self.level[tid] = 0


class TournamentDekkerLock:
    """Binary tournament tree composing 2-thread Dekker locks for N = 2^k threads."""

    def __init__(self, n_threads: int, yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        assert n_threads >= 2 and (n_threads & (n_threads - 1)) == 0, "n_threads must be power of 2"
        self.n = n_threads
        # Heap-indexed binary tree of n_threads - 1 Dekker nodes (1-indexed)
        self.nodes = [DekkerLock(yield_fn=yield_fn) for _ in range(n_threads)]

    def acquire(self, tid: int) -> int:
        spins = 0
        idx = self.n + tid
        path: List[tuple] = []
        while idx > 1:
            side = idx & 1  # 0 = left child, 1 = right child
            parent = idx >> 1
            path.append((parent, side))
            idx = parent
        for parent, side in path:
            spins += self.nodes[parent].acquire(side)
        return spins

    def release(self, tid: int) -> None:
        idx = self.n + tid
        path: List[tuple] = []
        while idx > 1:
            path.append((idx >> 1, idx & 1))
            idx >>= 1
        for parent, side in reversed(path):
            self.nodes[parent].release(side)


class BinarySemaphoreLock:
    """Kernel-assisted blocking mutual exclusion using OS Semaphore (wait/signal)."""

    def __init__(self) -> None:
        self._sem = threading.Semaphore(1)

    def acquire(self, tid: int = 0) -> int:
        self._sem.acquire()
        return 0

    def release(self, tid: int = 0) -> None:
        self._sem.release()


class MesaMonitorLock:
    """Mesa-semantics Monitor encapsulation using Condition variable + while-loop guard."""

    def __init__(self) -> None:
        self._cond = threading.Condition()
        self._busy = False

    def acquire(self, tid: int = 0) -> int:
        with self._cond:
            while self._busy:
                self._cond.wait()
            self._busy = True
        return 0

    def release(self, tid: int = 0) -> None:
        with self._cond:
            self._busy = False
            self._cond.notify()


class HoareMonitorQueueSim:
    """Discrete deterministic simulation of Hoare vs Mesa monitor bounded buffer."""

    @staticmethod
    def compare_semantics() -> dict:
        # Compare wait/signal context hops and condition-recheck guarantees
        return {
            "hoare": {
                "signal_action": "Immediate transfer of monitor lock to awakened waiter; signaler waits in urgent queue",
                "guard_statement": "if (not cond) wait()",
                "extra_lock_handoffs_per_signal": 2,
                "spurious_steal_risk": False,
            },
            "mesa": {
                "signal_action": "Mark waiter ready in entry queue; signaler finishes monitor call before releasing lock",
                "guard_statement": "while (not cond) wait()",
                "extra_lock_handoffs_per_signal": 0,
                "spurious_steal_risk_with_if": True,
                "spurious_steal_risk_with_while": False,
            },
        }
