"""Exercise 7: FIFO monitor solution for the Dining Philosophers problem.

The CPU scheduler and the shared-fork protocol solve different problems:
Guaranteed Scheduling distributes CPU service among runnable philosophers;
this monitor grants both forks atomically in FIFO order. A scheduler alone
cannot prevent circular wait or guarantee access to a fork.
"""
from __future__ import annotations

from collections import deque
from contextlib import contextmanager
import threading
import time
from typing import Dict, Iterator, List, Tuple


def fork_pair(philosopher: int, count: int) -> Tuple[int, int]:
    """Return the two fork IDs used by philosopher i (left=i, right=i+1)."""
    if count < 3:
        raise ValueError("Dining Philosophers requires at least 3 philosophers")
    if not 0 <= philosopher < count:
        raise ValueError(f"philosopher must be in [0, {count})")
    return philosopher, (philosopher + 1) % count


def ordered_fork_pair(philosopher: int, count: int) -> Tuple[int, int]:
    """The resource-hierarchy alternative: always acquire lower fork ID first."""
    return tuple(sorted(fork_pair(philosopher, count)))


class FairDiningTable:
    """A monitor that grants both forks together to the FIFO head only.

    A philosopher never holds one fork while waiting for the second one.
    The condition variable protects both fork ownership and the wait queue.
    FIFO admission prevents a later request from repeatedly bypassing the
    oldest hungry philosopher, assuming every granted meal eventually ends.
    """

    def __init__(self, count: int = 5):
        if count < 3:
            raise ValueError("Dining Philosophers requires at least 3 philosophers")
        self.count = count
        self._condition = threading.Condition()
        self._fork_owner: List[int | None] = [None] * count
        self._waiting = deque()
        self._next_ticket = 0
        self._eating = set()
        self._admission_order: List[int] = []
        self._admission_tickets: List[int] = []
        self._max_queue = 0

    def _is_available(self, philosopher: int) -> bool:
        left, right = fork_pair(philosopher, self.count)
        return self._fork_owner[left] is None and self._fork_owner[right] is None

    def _assert_safe(self) -> None:
        for philosopher in self._eating:
            left, right = fork_pair(philosopher, self.count)
            assert self._fork_owner[left] == philosopher
            assert self._fork_owner[right] == philosopher
            assert (philosopher + 1) % self.count not in self._eating
            assert (philosopher - 1) % self.count not in self._eating

    def acquire(self, philosopher: int) -> int:
        """Wait for a FIFO ticket and atomically reserve both forks."""
        if not 0 <= philosopher < self.count:
            raise ValueError(f"philosopher must be in [0, {self.count})")

        with self._condition:
            if philosopher in self._eating or any(
                waiting_id == philosopher for _, waiting_id in self._waiting
            ):
                raise RuntimeError(f"philosopher {philosopher} already has an active request")

            ticket = self._next_ticket
            self._next_ticket += 1
            self._waiting.append((ticket, philosopher))
            self._max_queue = max(self._max_queue, len(self._waiting))
            self._condition.notify_all()

            while (
                not self._waiting
                or self._waiting[0] != (ticket, philosopher)
                or not self._is_available(philosopher)
            ):
                self._condition.wait()

            self._waiting.popleft()
            left, right = fork_pair(philosopher, self.count)
            self._fork_owner[left] = philosopher
            self._fork_owner[right] = philosopher
            self._eating.add(philosopher)
            self._admission_order.append(philosopher)
            self._admission_tickets.append(ticket)
            self._assert_safe()
            self._condition.notify_all()
            return ticket

    def release(self, philosopher: int) -> None:
        """Release both forks and wake all waiters to re-check the FIFO guard."""
        with self._condition:
            if philosopher not in self._eating:
                raise RuntimeError(f"philosopher {philosopher} does not own both forks")
            left, right = fork_pair(philosopher, self.count)
            if self._fork_owner[left] != philosopher or self._fork_owner[right] != philosopher:
                raise RuntimeError("fork ownership invariant was violated")
            self._fork_owner[left] = None
            self._fork_owner[right] = None
            self._eating.remove(philosopher)
            self._assert_safe()
            self._condition.notify_all()

    @contextmanager
    def meal(self, philosopher: int) -> Iterator[int]:
        ticket = self.acquire(philosopher)
        try:
            yield ticket
        finally:
            self.release(philosopher)

    def snapshot(self) -> Dict:
        with self._condition:
            return {
                "waiting": [p for _, p in self._waiting],
                "waiting_tickets": [t for t, _ in self._waiting],
                "eating": sorted(self._eating),
                "fork_owner": list(self._fork_owner),
                "admission_order": list(self._admission_order),
                "admission_tickets": list(self._admission_tickets),
                "max_wait_queue": self._max_queue,
            }


def naive_deadlock_witness(count: int = 5) -> Dict:
    """Return the classic circular-wait state after every philosopher takes left."""
    if count < 3:
        raise ValueError("Dining Philosophers requires at least 3 philosophers")
    holders = {p: p for p in range(count)}
    waiting_for = {p: (p + 1) % count for p in range(count)}
    cycle = list(range(count)) + [0]
    return {
        "fork_holder": holders,
        "waiting_for_philosopher": waiting_for,
        "wait_for_cycle": cycle,
        "all_forks_held": len(set(holders.values())) == count,
        "deadlocked": True,
    }


def _adjacent_eaters(eating_mask: int, count: int) -> bool:
    for p in range(count):
        if eating_mask & (1 << p):
            if eating_mask & (1 << ((p + 1) % count)):
                return True
    return False


def explore_fifo_model(count: int = 5) -> Dict:
    """Exhaustively explore one meal per philosopher in the FIFO-monitor model.

    A state is (waiting_queue, eating_bitmask, finished_bitmask). Transitions
    are request, grant-to-FIFO-head, and finish-meal. The finite state space
    makes safety and deadlock checks reproducible without thread timing noise.
    """
    if count < 3 or count > 7:
        raise ValueError("model checker supports 3..7 philosophers")
    initial = (tuple(), 0, 0)
    pending = deque([initial])
    seen = {initial}
    transitions = 0
    unsafe_states = 0
    deadlock_states = 0
    terminal_states = 0
    max_parallel = 0
    max_queue = 0
    all_done = (1 << count) - 1

    while pending:
        queue, eating, done = pending.popleft()
        if _adjacent_eaters(eating, count):
            unsafe_states += 1
        max_parallel = max(max_parallel, eating.bit_count())
        max_queue = max(max_queue, len(queue))
        if not queue and eating == 0 and done == all_done:
            terminal_states += 1
            continue

        successors = set()
        claimed = set(queue)
        claimed.update(p for p in range(count) if eating & (1 << p))
        claimed.update(p for p in range(count) if done & (1 << p))

        # Request: philosophers may arrive in any order.
        for p in range(count):
            if p not in claimed:
                successors.add((queue + (p,), eating, done))

        # Grant: only the oldest waiter can acquire, and both forks are
        # reserved in this single transition (there is no hold-and-wait).
        if queue:
            p = queue[0]
            if not (eating & (1 << ((p - 1) % count))) and not (
                eating & (1 << ((p + 1) % count))
            ):
                successors.add((queue[1:], eating | (1 << p), done))

        # Finish: any philosopher currently eating releases both forks.
        for p in range(count):
            bit = 1 << p
            if eating & bit:
                successors.add((queue, eating & ~bit, done | bit))

        if not successors and not (not queue and eating == 0 and done == all_done):
            deadlock_states += 1

        for state in successors:
            transitions += 1
            if state not in seen:
                seen.add(state)
                pending.append(state)

    return {
        "philosophers": count,
        "reachable_states": len(seen),
        "transitions": transitions,
        "unsafe_states": unsafe_states,
        "deadlock_states": deadlock_states,
        "terminal_states": terminal_states,
        "max_parallel_eaters": max_parallel,
        "max_wait_queue": max_queue,
        "fifo_admission": True,
        "all_five_finish": terminal_states > 0,
    }


def run_threaded_stress(count: int = 5, rounds: int = 4, meal_seconds: float = 0.0005) -> Dict:
    """Run real threads against the monitor and independently audit overlap."""
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    table = FairDiningTable(count)
    start = threading.Barrier(count + 1)
    state_lock = threading.Lock()
    active = set()
    completions = [0] * count
    violations: List[str] = []
    errors: List[str] = []
    max_parallel = 0

    def worker(philosopher: int) -> None:
        nonlocal max_parallel
        try:
            start.wait(timeout=5)
            for _ in range(rounds):
                with table.meal(philosopher):
                    with state_lock:
                        if (philosopher - 1) % count in active:
                            violations.append(f"{philosopher} overlapped left neighbor")
                        if (philosopher + 1) % count in active:
                            violations.append(f"{philosopher} overlapped right neighbor")
                        active.add(philosopher)
                        max_parallel = max(max_parallel, len(active))
                    if meal_seconds:
                        time.sleep(meal_seconds)
                    with state_lock:
                        active.remove(philosopher)
                        completions[philosopher] += 1
                time.sleep(0)
        except Exception as exc:  # pragma: no cover - reported through the stress result
            errors.append(f"P{philosopher}: {type(exc).__name__}: {exc}")

    threads = [threading.Thread(target=worker, args=(p,), name=f"Philosopher-{p}") for p in range(count)]
    for thread in threads:
        thread.start()
    start.wait(timeout=5)
    for thread in threads:
        thread.join(timeout=10)

    alive = [thread.name for thread in threads if thread.is_alive()]
    snap = table.snapshot()
    return {
        "philosophers": count,
        "rounds_per_philosopher": rounds,
        "completed_meals": sum(completions),
        "completions_by_philosopher": completions,
        "safety_violations": len(violations),
        "violations": violations,
        "worker_errors": errors,
        "threads_still_alive": alive,
        "max_parallel_eaters": max_parallel,
        "final_waiting": snap["waiting"],
        "final_eating": snap["eating"],
        "final_fork_owner": snap["fork_owner"],
        "admission_tickets_monotone": snap["admission_tickets"] == sorted(snap["admission_tickets"]),
        "max_wait_queue": snap["max_wait_queue"],
        "passed": (
            sum(completions) == count * rounds
            and not violations
            and not errors
            and not alive
            and not snap["waiting"]
            and not snap["eating"]
            and all(owner is None for owner in snap["fork_owner"])
            and snap["admission_tickets"] == sorted(snap["admission_tickets"])
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps({
        "naive": naive_deadlock_witness(),
        "fifo_model": explore_fifo_model(),
        "threaded": run_threaded_stress(),
    }, ensure_ascii=False, indent=2))
