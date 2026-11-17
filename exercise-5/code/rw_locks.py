"""Exercise 5: Readers-Writers Locks Implemented Across Four Synchronization Paradigms.

Covers all three classical policies:
  1. Readers-Preference (First RW)
  2. Writers-Preference (Second RW)
  3. Fair / Turnstile FIFO (Third RW)
Implemented across:
  - Semaphore (SemRW_*)
  - Mesa Monitor / Condition Variables (MonRW_*)
  - Peterson FilterLock Spin + State Guards (PetRW_*)
  - Dekker Tournament Lock + State Guards (DekRW_*)
Plus a Coarse Mutex baseline (CoarseMutexRW) for concurrency speedup quantification.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable


# ---------------------------------------------------------------------------
# Internal reusable pure-software locks (self-contained for Exercise 5)
# ---------------------------------------------------------------------------
class _FilterLock:
    def __init__(self, n_threads: int, yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        self.n = n_threads
        self.level = [0] * n_threads
        self.victim = [0] * n_threads
        self._yield = yield_fn

    def acquire(self, tid: int) -> None:
        for lvl in range(1, self.n):
            self.level[tid] = lvl
            self.victim[lvl] = tid
            while any(k != tid and self.level[k] >= lvl for k in range(self.n)) and self.victim[lvl] == tid:
                self._yield()

    def release(self, tid: int) -> None:
        self.level[tid] = 0


class _Dekker2:
    def __init__(self, yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        self.flag = [False, False]
        self.turn = 0
        self._yield = yield_fn

    def acquire(self, tid: int) -> None:
        other = 1 - tid
        self.flag[tid] = True
        while self.flag[other]:
            if self.turn != tid:
                self.flag[tid] = False
                while self.turn != tid:
                    self._yield()
                self.flag[tid] = True
            else:
                self._yield()

    def release(self, tid: int) -> None:
        self.turn = 1 - tid
        self.flag[tid] = False


class _TournamentDekker:
    def __init__(self, n_threads: int, yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        # Round up to next power of 2 >= 2
        cap = 2
        while cap < n_threads:
            cap *= 2
        self.cap = cap
        self.nodes = [_Dekker2(yield_fn=yield_fn) for _ in range(cap)]

    def acquire(self, tid: int) -> None:
        idx = self.cap + tid
        path = []
        while idx > 1:
            path.append((idx >> 1, idx & 1))
            idx >>= 1
        for parent, side in path:
            self.nodes[parent].acquire(side)

    def release(self, tid: int) -> None:
        idx = self.cap + tid
        path = []
        while idx > 1:
            path.append((idx >> 1, idx & 1))
            idx >>= 1
        for parent, side in reversed(path):
            self.nodes[parent].release(side)


# ===========================================================================
# 1. SEMAPHORE IMPLEMENTATIONS
# ===========================================================================
class SemRWReadersPref:
    """First RW problem using Dijkstra Semaphores (classic Readers-Preference)."""

    def __init__(self) -> None:
        self.read_count = 0
        self.mutex = threading.Semaphore(1)
        self.rw_mutex = threading.Semaphore(1)

    def acquire_read(self, tid: int = 0) -> None:
        self.mutex.acquire()
        self.read_count += 1
        if self.read_count == 1:
            self.rw_mutex.acquire()
        self.mutex.release()

    def release_read(self, tid: int = 0) -> None:
        self.mutex.acquire()
        self.read_count -= 1
        if self.read_count == 0:
            self.rw_mutex.release()
        self.mutex.release()

    def acquire_write(self, tid: int = 0) -> None:
        self.rw_mutex.acquire()

    def release_write(self, tid: int = 0) -> None:
        self.rw_mutex.release()


class SemRWWritersPref:
    """Second RW problem using Semaphores (Courtois-Heymans-Parnas Writers-Preference)."""

    def __init__(self) -> None:
        self.read_count = 0
        self.write_count = 0
        self.rmutex = threading.Semaphore(1)
        self.wmutex = threading.Semaphore(1)
        self.read_try = threading.Semaphore(1)
        self.resource = threading.Semaphore(1)

    def acquire_read(self, tid: int = 0) -> None:
        self.read_try.acquire()
        self.rmutex.acquire()
        self.read_count += 1
        if self.read_count == 1:
            self.resource.acquire()
        self.rmutex.release()
        self.read_try.release()

    def release_read(self, tid: int = 0) -> None:
        self.rmutex.acquire()
        self.read_count -= 1
        if self.read_count == 0:
            self.resource.release()
        self.rmutex.release()

    def acquire_write(self, tid: int = 0) -> None:
        self.wmutex.acquire()
        self.write_count += 1
        if self.write_count == 1:
            self.read_try.acquire()
        self.wmutex.release()
        self.resource.acquire()

    def release_write(self, tid: int = 0) -> None:
        self.resource.release()
        self.wmutex.acquire()
        self.write_count -= 1
        if self.write_count == 0:
            self.read_try.release()
        self.wmutex.release()


class SemRWFairTurnstile:
    """Third RW problem using a FIFO turnstile semaphore (starvation-free)."""

    def __init__(self) -> None:
        self.read_count = 0
        self.turnstile = threading.Semaphore(1)
        self.mutex = threading.Semaphore(1)
        self.rw_mutex = threading.Semaphore(1)

    def acquire_read(self, tid: int = 0) -> None:
        self.turnstile.acquire()
        self.turnstile.release()
        self.mutex.acquire()
        self.read_count += 1
        if self.read_count == 1:
            self.rw_mutex.acquire()
        self.mutex.release()

    def release_read(self, tid: int = 0) -> None:
        self.mutex.acquire()
        self.read_count -= 1
        if self.read_count == 0:
            self.rw_mutex.release()
        self.mutex.release()

    def acquire_write(self, tid: int = 0) -> None:
        self.turnstile.acquire()
        self.rw_mutex.acquire()

    def release_write(self, tid: int = 0) -> None:
        self.rw_mutex.release()
        self.turnstile.release()


# ===========================================================================
# 2. MONITOR IMPLEMENTATIONS (Mesa Condition Variables)
# ===========================================================================
class MonRWReadersPref:
    def __init__(self) -> None:
        self.cond = threading.Condition()
        self.active_readers = 0
        self.active_writers = 0

    def acquire_read(self, tid: int = 0) -> None:
        with self.cond:
            while self.active_writers > 0:
                self.cond.wait()
            self.active_readers += 1

    def release_read(self, tid: int = 0) -> None:
        with self.cond:
            self.active_readers -= 1
            if self.active_readers == 0:
                self.cond.notify_all()

    def acquire_write(self, tid: int = 0) -> None:
        with self.cond:
            while self.active_writers > 0 or self.active_readers > 0:
                self.cond.wait()
            self.active_writers = 1

    def release_write(self, tid: int = 0) -> None:
        with self.cond:
            self.active_writers = 0
            self.cond.notify_all()


class MonRWWritersPref:
    def __init__(self) -> None:
        self.cond = threading.Condition()
        self.active_readers = 0
        self.active_writers = 0
        self.waiting_writers = 0

    def acquire_read(self, tid: int = 0) -> None:
        with self.cond:
            while self.active_writers > 0 or self.waiting_writers > 0:
                self.cond.wait()
            self.active_readers += 1

    def release_read(self, tid: int = 0) -> None:
        with self.cond:
            self.active_readers -= 1
            if self.active_readers == 0:
                self.cond.notify_all()

    def acquire_write(self, tid: int = 0) -> None:
        with self.cond:
            self.waiting_writers += 1
            try:
                while self.active_writers > 0 or self.active_readers > 0:
                    self.cond.wait()
                self.active_writers = 1
            finally:
                self.waiting_writers -= 1

    def release_write(self, tid: int = 0) -> None:
        with self.cond:
            self.active_writers = 0
            self.cond.notify_all()


class MonRWFairTurnstile:
    """Monitor RW with explicit ticket FIFO queue preventing both reader and writer starvation."""

    def __init__(self) -> None:
        self.cond = threading.Condition()
        self.active_readers = 0
        self.active_writers = 0
        self.next_ticket = 0
        self.serving_ticket = 0

    def acquire_read(self, tid: int = 0) -> None:
        with self.cond:
            my_ticket = self.next_ticket
            self.next_ticket += 1
            while my_ticket != self.serving_ticket or self.active_writers > 0:
                self.cond.wait()
            self.serving_ticket += 1
            self.active_readers += 1
            self.cond.notify_all()

    def release_read(self, tid: int = 0) -> None:
        with self.cond:
            self.active_readers -= 1
            if self.active_readers == 0:
                self.cond.notify_all()

    def acquire_write(self, tid: int = 0) -> None:
        with self.cond:
            my_ticket = self.next_ticket
            self.next_ticket += 1
            while my_ticket != self.serving_ticket or self.active_writers > 0 or self.active_readers > 0:
                self.cond.wait()
            self.serving_ticket += 1
            self.active_writers = 1

    def release_write(self, tid: int = 0) -> None:
        with self.cond:
            self.active_writers = 0
            self.cond.notify_all()


# ===========================================================================
# 3 & 4. PURE-SOFTWARE SPIN RW LOCKS (PETERSON FILTER & TOURNAMENT DEKKER)
# ===========================================================================
class _SpinStateRWBase:
    """Builds Readers-Pref, Writers-Pref, or Fair-FIFO RW protocol over any 2-op spin mutex."""

    def __init__(self, state_lock, policy: str = "readers", yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        assert policy in ("readers", "writers", "fair")
        self.lock = state_lock
        self.policy = policy
        self._yield = yield_fn
        self.active_readers = 0
        self.active_writers = 0
        self.waiting_writers = 0
        self.queue: deque = deque()

    def acquire_read(self, tid: int) -> None:
        if self.policy == "fair":
            token = ("R", tid)
            self.lock.acquire(tid)
            self.queue.append(token)
            self.lock.release(tid)
            while True:
                self.lock.acquire(tid)
                ok = (self.active_writers == 0 and self.queue[0] == token)
                if ok:
                    self.queue.popleft()
                    self.active_readers += 1
                    self.lock.release(tid)
                    return
                self.lock.release(tid)
                self._yield()
        else:
            while True:
                self.lock.acquire(tid)
                blocked = (self.active_writers > 0) or (self.policy == "writers" and self.waiting_writers > 0)
                if not blocked:
                    self.active_readers += 1
                    self.lock.release(tid)
                    return
                self.lock.release(tid)
                self._yield()

    def release_read(self, tid: int) -> None:
        self.lock.acquire(tid)
        self.active_readers -= 1
        self.lock.release(tid)

    def acquire_write(self, tid: int) -> None:
        if self.policy == "fair":
            token = ("W", tid)
            self.lock.acquire(tid)
            self.queue.append(token)
            self.lock.release(tid)
            while True:
                self.lock.acquire(tid)
                ok = (self.active_writers == 0 and self.active_readers == 0 and self.queue[0] == token)
                if ok:
                    self.queue.popleft()
                    self.active_writers = 1
                    self.lock.release(tid)
                    return
                self.lock.release(tid)
                self._yield()
        else:
            self.lock.acquire(tid)
            self.waiting_writers += 1
            self.lock.release(tid)
            while True:
                self.lock.acquire(tid)
                if self.active_writers == 0 and self.active_readers == 0:
                    self.waiting_writers -= 1
                    self.active_writers = 1
                    self.lock.release(tid)
                    return
                self.lock.release(tid)
                self._yield()

    def release_write(self, tid: int) -> None:
        self.lock.acquire(tid)
        self.active_writers = 0
        self.lock.release(tid)


class PetRW(_SpinStateRWBase):
    def __init__(self, n_threads: int, policy: str = "readers", yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        super().__init__(_FilterLock(n_threads, yield_fn=yield_fn), policy=policy, yield_fn=yield_fn)


class DekRW(_SpinStateRWBase):
    def __init__(self, n_threads: int, policy: str = "readers", yield_fn: Callable[[], None] = lambda: time.sleep(0)) -> None:
        super().__init__(_TournamentDekker(n_threads, yield_fn=yield_fn), policy=policy, yield_fn=yield_fn)


class CoarseMutexRW:
    """Baseline single lock serializing all readers and writers (zero reader concurrency)."""

    def __init__(self) -> None:
        self._m = threading.Lock()

    def acquire_read(self, tid: int = 0) -> None:
        self._m.acquire()

    def release_read(self, tid: int = 0) -> None:
        self._m.release()

    def acquire_write(self, tid: int = 0) -> None:
        self._m.acquire()

    def release_write(self, tid: int = 0) -> None:
        self._m.release()


def make_rw_lock(primitive: str, policy: str, n_threads: int, busy_spin: bool = False):
    yfn = (lambda: None) if busy_spin else (lambda: time.sleep(0))
    if primitive == "Semaphore":
        return {"readers": SemRWReadersPref, "writers": SemRWWritersPref, "fair": SemRWFairTurnstile}[policy]()
    if primitive == "Monitor":
        return {"readers": MonRWReadersPref, "writers": MonRWWritersPref, "fair": MonRWFairTurnstile}[policy]()
    if primitive == "Peterson":
        return PetRW(n_threads, policy=policy, yield_fn=yfn)
    if primitive == "Dekker":
        return DekRW(n_threads, policy=policy, yield_fn=yfn)
    if primitive == "CoarseMutex":
        return CoarseMutexRW()
    raise ValueError(primitive)
