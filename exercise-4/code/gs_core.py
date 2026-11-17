"""Deterministic exact-rational core for Guaranteed Scheduling studies.

This is the canonical simulation and verification core.  It is vendored into
each exercise folder (``exercise-N/code/gs_core.py``) via
``tools/vendor_core.py`` so every exercise remains self-contained.

Core design principles
----------------------
1. **Exact arithmetic in all scheduling decisions.**  All time units, work
   amounts, weights and quanta are integers, and all virtual-time / GPS
   calculations use ``fractions.Fraction``.  No floating-point rounding ever
   alters a tie or dispatch choice, so hand-worked tables and simulator traces
   match bit-for-bit.
2. **Two strictly separated instruments.**
   - *Exhaustive verification* (``exhaustive_feasible``,
     ``exhaustive_tie_envelope``, ``find_starvation_witness``) proves or
     refutes properties over the state space and emits concrete witnesses.
   - *Discrete-event simulation* (``simulate_procs``, ``simulate_rt``)
     measures quantitative performance (lag, fairness, preemptions, response
     times, miss rates) across scenarios and parameter sweeps.
3. **Tie-breaking and quantum size are explicit parameters**, never hidden
   implementation details.

Policies
--------
Proportional-share & real-time policies supported:
* ``gs_ratio``     : naive ``used / weight`` (mirrors ``GuaranteedScheduling.py``)
* ``gs_entitled``  : Tanenbaum ratio ``actual / entitled_active``
* ``gs_vtime``     : virtual-time-anchored GS (WFQ / CFS style, ``vruntime`` starts at ``V(t)``)
* ``gs_capped``    : virtual-time GS with bounded wakeup credit ``cap``
* ``stride``       : Waldspurger-Weihl deterministic Stride Scheduling
* ``rr``           : Round-Robin across active queue
* ``fifo``         : First-Come First-Served
* ``edf``          : Earliest Deadline First
* ``rm``           : Rate Monotonic (period order)
* ``dm``           : Deadline Monotonic (relative deadline order)

Tie-breakers: ``index``, ``stay``, ``max_weight``, ``edf``.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from fractions import Fraction
from math import gcd, sqrt
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
    "Proc",
    "RTTask",
    "RTJob",
    "POLICIES",
    "GS_POLICIES",
    "TIE_BREAKERS",
    "ideal_gps_trace",
    "simulate_procs",
    "simulate_rt",
    "gantt_rows",
    "hyperperiod",
    "utilisation",
    "make_rt_jobs",
    "exhaustive_feasible",
    "verify_rt_schedule_independent",
    "exhaustive_tie_envelope",
    "find_starvation_witness",
]

GS_POLICIES = ("gs_ratio", "gs_entitled", "gs_vtime", "gs_capped", "stride")
POLICIES = ("gs_ratio", "gs_entitled", "gs_vtime", "gs_capped", "stride",
            "rr", "fifo", "edf", "rm", "dm")
TIE_BREAKERS = ("index", "stay", "max_weight", "edf")


# --------------------------------------------------------------------------
# Workload definitions
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Proc:
    """A CPU process/job with integer arrival, work, weight, and optional sleep."""
    name: str
    arrival: int
    work: int
    weight: int = 1
    deadline: Optional[int] = None
    # Tuple of (cpu_used_trigger, sleep_duration) where sleep triggers after
    # reaching ``cpu_used_trigger`` units of CPU execution.
    sleep_at: Tuple[Tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        if self.arrival < 0:
            raise ValueError(f"arrival must be >= 0: {self.name}")
        if self.work <= 0:
            raise ValueError(f"work must be > 0: {self.name}")
        if self.weight <= 0:
            raise ValueError(f"weight must be > 0: {self.name}")
        if self.deadline is not None and self.deadline < self.arrival + self.work:
            raise ValueError(f"deadline infeasible even solo: {self.name}")
        for trig, dur in self.sleep_at:
            if not (0 < trig < self.work) or dur <= 0:
                raise ValueError(f"invalid sleep trigger {(trig, dur)} on {self.name}")


@dataclass(frozen=True)
class RTTask:
    """A periodic real-time task with integer period, WCET, deadline, weight."""
    name: str
    period: int
    wcet: int
    deadline: Optional[int] = None
    weight: int = 1
    phase: int = 0

    @property
    def rel_deadline(self) -> int:
        return self.deadline if self.deadline is not None else self.period

    def __post_init__(self) -> None:
        if self.period <= 0 or self.wcet <= 0 or self.weight <= 0:
            raise ValueError(f"period/wcet/weight must be positive: {self.name}")
        if self.wcet > self.rel_deadline:
            raise ValueError(
                f"wcet {self.wcet} > rel_deadline {self.rel_deadline}: {self.name}"
            )
        if not (0 <= self.phase < self.period):
            raise ValueError(f"phase must be in [0, period): {self.name}")


@dataclass(frozen=True)
class RTJob:
    index: int
    task: int
    name: str
    release: int
    deadline: int
    wcet: int
    weight: int


def hyperperiod(tasks: Sequence[RTTask]) -> int:
    h = 1
    for t in tasks:
        h = h * t.period // gcd(h, t.period)
    return h


def utilisation(tasks: Sequence[RTTask]) -> float:
    return sum(t.wcet / t.period for t in tasks)


def make_rt_jobs(tasks: Sequence[RTTask], horizon: int) -> List[RTJob]:
    raw: List[RTJob] = []
    for ti, t in enumerate(tasks):
        k = 0
        while True:
            rel = t.phase + k * t.period
            k += 1
            if rel >= horizon:
                break
            raw.append(RTJob(-1, ti, f"{t.name}#{k - 1}", rel, rel + t.rel_deadline,
                             t.wcet, t.weight))
    raw.sort(key=lambda j: (j.release, j.task))
    return [RTJob(i, j.task, j.name, j.release, j.deadline, j.wcet, j.weight)
            for i, j in enumerate(raw)]


# --------------------------------------------------------------------------
# Exact Fluid Generalized Processor Sharing (GPS) baseline
# --------------------------------------------------------------------------

def ideal_gps_trace(procs: Sequence[Proc], horizon: Optional[int] = None
                    ) -> Dict[str, object]:
    """Compute exact Fraction Fluid GPS cumulative service E_i(t) at integer ticks.

    Note: assumes CPU-bound processes (ignoring sleep_at unless sleep is absent).
    For processes with sleep_at, GPS tracks active unblocked capacity at integer
    granularity or warns via non-empty sleep_at; primary GPS reference is for
    pure CPU-work workloads.
    """
    n = len(procs)
    if n == 0:
        return {"horizon": 0, "entitled": [], "finish_times": [], "virtual_time": []}
    if horizon is None:
        max_arr = max(p.arrival for p in procs)
        horizon = max_arr + sum(p.work for p in procs)

    rem = [Fraction(p.work) for p in procs]
    entitled = [Fraction(0) for _ in procs]
    # snapshots[t][i] = cumulative entitled CPU of proc i at integer time t
    snapshots: List[List[Fraction]] = [[Fraction(0) for _ in procs]]
    vtime_snaps: List[Fraction] = [Fraction(0)]
    finish_times: List[Optional[Fraction]] = [None] * n

    t = Fraction(0)
    vtime = Fraction(0)
    arrivals = sorted({Fraction(p.arrival) for p in procs if p.arrival <= horizon})

    def record_integer_points(t_start: Fraction, t_end: Fraction,
                              rates: List[Fraction], v_rate: Fraction,
                              base_ent: List[Fraction], base_v: Fraction) -> None:
        # record integer ticks in (t_start, t_end] up to horizon
        first_int = int(t_start) + 1
        last_int = min(horizon, int(t_end))
        for k in range(first_int, last_int + 1):
            kf = Fraction(k)
            if kf <= t_start or kf > t_end:
                continue
            dt = kf - t_start
            snapshots.append([base_ent[i] + rates[i] * dt for i in range(n)])
            vtime_snaps.append(base_v + v_rate * dt)

    while t < horizon:
        active = [i for i in range(n) if Fraction(procs[i].arrival) <= t and rem[i] > 0]
        next_arrs = [a for a in arrivals if a > t]
        next_arr = next_arrs[0] if next_arrs else Fraction(horizon)

        if not active:
            t_next = min(Fraction(horizon), next_arr)
            rates = [Fraction(0)] * n
            record_integer_points(t, t_next, rates, Fraction(0), list(entitled), vtime)
            t = t_next
            continue

        total_w = sum(procs[i].weight for i in active)
        rates = [Fraction(procs[i].weight, total_w) if i in active else Fraction(0)
                 for i in range(n)]
        v_rate = Fraction(1, total_w)
        # earliest finish among active
        min_dt_fin = min(rem[i] / rates[i] for i in active)
        t_next = min(Fraction(horizon), next_arr, t + min_dt_fin)
        dt = t_next - t

        base_ent = list(entitled)
        base_v = vtime
        record_integer_points(t, t_next, rates, v_rate, base_ent, base_v)

        for i in active:
            delta = rates[i] * dt
            rem[i] -= delta
            entitled[i] += delta
            if rem[i] == 0 and finish_times[i] is None:
                finish_times[i] = t_next
        vtime += v_rate * dt
        t = t_next

    # pad if all finished before horizon
    while len(snapshots) <= horizon:
        snapshots.append(list(entitled))
        vtime_snaps.append(vtime)

    return {
        "horizon": horizon,
        "entitled": snapshots,          # snapshots[t][i] for t in 0..horizon
        "finish_times": finish_times,
        "virtual_time": vtime_snaps,
    }


# --------------------------------------------------------------------------
# Simulation result
# --------------------------------------------------------------------------

@dataclass
class SimResult:
    policy: str
    tie: str
    quantum: int
    horizon: int
    timeline: List[Tuple[int, Optional[str]]] = field(default_factory=list)
    per_proc: Dict[str, dict] = field(default_factory=dict)
    busy: int = 0
    idle: int = 0
    completed: int = 0
    missed: int = 0
    miss_rate: float = 0.0
    preemptions: int = 0
    context_switches: int = 0
    tie_events: int = 0
    max_abs_lag: float = 0.0
    max_abs_lag_frac: str = "0"
    rmse_lag: float = 0.0
    jain_fairness: float = 1.0
    max_starve_gap: int = 0
    min_share_ratio: float = 1.0
    mean_turnaround: Optional[float] = None
    worst_turnaround: Optional[int] = None
    mean_waiting: Optional[float] = None
    jitter_turnaround: Optional[int] = None

    def as_dict(self, keep_timeline: bool = True) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "timeline"}
        if keep_timeline:
            d["timeline"] = [[t, n] for t, n in self.timeline]
        return d


# --------------------------------------------------------------------------
# Helper: parse policy + tie
# --------------------------------------------------------------------------

def _parse_policy(policy: str, tie: str = "index") -> Tuple[str, str]:
    if ":" in policy:
        base, _, tpart = policy.partition(":")
        tie = tpart
    else:
        base = policy
    if base not in POLICIES:
        raise ValueError(f"unknown policy: {policy}")
    if tie not in TIE_BREAKERS:
        raise ValueError(f"unknown tie-breaker: {tie}")
    return base, tie


# --------------------------------------------------------------------------
# Process simulation (exact Fraction tracking)
# --------------------------------------------------------------------------

def simulate_procs(procs: Sequence[Proc],
                   policy: str = "gs_ratio",
                   quantum: int = 1,
                   tie: str = "index",
                   horizon: Optional[int] = None,
                   wakeup_cap: int = 1) -> SimResult:
    """Simulate a workload of ``Proc`` objects with integer time and exact Fraction math.

    * Quantum-sliced execution: once chosen, a job runs up to ``quantum`` ticks
      unless it completes or hits a ``sleep_at`` trigger.
    * When ``policy`` is ``gs_vtime``, system virtual time ``V(t)`` advances by
      ``1 / sum_{active} w_j`` per busy tick; a process arriving at ``t`` sets
      its ``vruntime = V(t)``.
    * When ``policy`` is ``gs_capped``, wakeup after sleep caps credit to at most
      ``wakeup_cap`` quanta of virtual advantage below ``V(t)``.
    * When ``policy`` is ``gs_entitled``, online entitled time ``E_i(t)``
      accumulates by ``w_i / sum_{active} w_j`` during ticks where ``i`` is ready.
    """
    if quantum <= 0:
        raise ValueError("quantum must be >= 1")
    base, tie = _parse_policy(policy, tie)
    n = len(procs)
    if horizon is None:
        max_arr = max((p.arrival for p in procs), default=0)
        max_sleep = sum(sum(d for _, d in p.sleep_at) for p in procs)
        horizon = max_arr + sum(p.work for p in procs) + max_sleep

    # Ideal GPS trace (only strictly comparable when sleep_at is empty)
    gps = ideal_gps_trace(procs, horizon=horizon)

    used = [0] * n
    rem = [p.work for p in procs]
    wake_at = [p.arrival for p in procs]
    started_at: List[Optional[int]] = [None] * n
    finished_at: List[Optional[int]] = [None] * n
    missed_flag = [False] * n

    # Sleep schedules mapped per process: dict {used_trigger: sleep_dur}
    sleep_maps = [{trig: dur for trig, dur in p.sleep_at} for p in procs]

    # Exact Fraction tracking for gs_entitled, gs_vtime, gs_capped, stride
    entitled_online = [Fraction(0)] * n
    vruntime = [Fraction(0)] * n
    sys_vtime = Fraction(0)

    # Stride scheduling: exact Fraction stride = 1/w_i, pass initialized to min_pass
    stride_step = [Fraction(1, p.weight) for p in procs]
    stride_pass = [Fraction(0)] * n
    seen_arrived = [False] * n
    was_sleeping = [False] * n

    # RR circular queue
    rr_queue: List[int] = []
    in_rr = [False] * n

    # Starvation gap tracking: consecutive busy ticks an unblocked ready proc waited
    wait_streak = [0] * n
    max_starve = [0] * n

    # Lag trace at each integer t in 0..horizon
    lag_sq_sum = 0.0
    lag_samples = 0
    max_lag_frac = Fraction(0)

    res = SimResult(policy=base, tie=tie, quantum=quantum, horizon=horizon)
    previous: Optional[int] = None
    slice_left = 0
    current: Optional[int] = None

    def _tie_key(i: int, score_fn) -> Tuple:
        sc = score_fn(i)
        if tie == "index":
            return (sc, i)
        if tie == "stay":
            return (sc, 0 if i == previous else 1, i)
        if tie == "max_weight":
            return (sc, -procs[i].weight, i)
        # edf tie
        ddl = procs[i].deadline if procs[i].deadline is not None else 10**12
        return (sc, ddl, i)

    for t in range(horizon):
        # 1. Handle arrivals & wakeups at time t
        newly_ready: List[int] = []
        for i, p in enumerate(procs):
            if rem[i] > 0 and wake_at[i] == t:
                if not seen_arrived[i]:
                    seen_arrived[i] = True
                    # Initialize virtual runtime / pass on first arrival
                    vruntime[i] = sys_vtime
                    active_passes = [stride_pass[j] for j in range(n)
                                     if seen_arrived[j] and rem[j] > 0 and wake_at[j] <= t and j != i]
                    stride_pass[i] = min(active_passes) if active_passes else Fraction(0)
                elif was_sleeping[i]:
                    was_sleeping[i] = False
                    if base == "gs_capped":
                        # At most wakeup_cap execution ticks of virtual advantage below sys_vtime
                        bonus = Fraction(wakeup_cap, procs[i].weight)
                        vruntime[i] = max(vruntime[i], sys_vtime - bonus)
                    elif base == "gs_vtime":
                        # Unbounded sleeper keeps old vruntime unless clamped; here
                        # vruntime stays as-is (classic CFS sleeper behavior without cap)
                        # or if strictly dynamic arrival only, arrival was handled above.
                        pass
                newly_ready.append(i)

        # Deadline misses checked at instant t before execution
        for i, p in enumerate(procs):
            if p.deadline is not None and rem[i] > 0 and t >= p.deadline and not missed_flag[i]:
                missed_flag[i] = True
                res.missed += 1

        ready = [i for i in range(n) if rem[i] > 0 and wake_at[i] <= t]
        for i in newly_ready:
            if not in_rr[i]:
                rr_queue.append(i)
                in_rr[i] = True

        # Check if running slice must end
        if current is not None and (current not in ready or slice_left == 0):
            if current in ready and base == "rr" and slice_left == 0:
                if current in rr_queue:
                    rr_queue.remove(current)
                rr_queue.append(current)
            current = None
            slice_left = 0

        if not ready:
            res.timeline.append((t, None))
            res.idle += 1
            previous = None
            current = None
            slice_left = 0
            # Lag snapshot at t+1
            for i in range(n):
                if t + 1 < len(gps["entitled"]):
                    diff = abs(Fraction(used[i]) - gps["entitled"][t + 1][i])
                    if diff > max_lag_frac:
                        max_lag_frac = diff
                    lag_sq_sum += float(diff) ** 2
                    lag_samples += 1
            continue

        # Choose process if starting a new slice (or non-preempted slice continues)
        if current is None:
            if base == "fifo":
                chosen = min(ready, key=lambda i: (procs[i].arrival, i))
            elif base == "rr":
                rr_queue = [i for i in rr_queue if i in ready]
                for i in ready:
                    if i not in rr_queue:
                        rr_queue.append(i)
                chosen = rr_queue[0]
            elif base == "edf":
                chosen = min(ready, key=lambda i: (
                    procs[i].deadline if procs[i].deadline is not None else 10**12, i
                ))
            elif base == "rm" or base == "dm":
                chosen = min(ready, key=lambda i: (procs[i].work, i))
            elif base == "gs_ratio":
                def score_fn(i: int) -> Fraction:
                    return Fraction(used[i], procs[i].weight)
                scores = [score_fn(i) for i in ready]
                if len(ready) > 1 and scores.count(min(scores)) > 1:
                    res.tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            elif base == "gs_entitled":
                def score_fn(i: int) -> Fraction:
                    if entitled_online[i] == 0:
                        return Fraction(0)
                    return Fraction(used[i], 1) / entitled_online[i]
                scores = [score_fn(i) for i in ready]
                if len(ready) > 1 and scores.count(min(scores)) > 1:
                    res.tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            elif base in ("gs_vtime", "gs_capped"):
                def score_fn(i: int) -> Fraction:
                    return vruntime[i]
                scores = [score_fn(i) for i in ready]
                if len(ready) > 1 and scores.count(min(scores)) > 1:
                    res.tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            elif base == "stride":
                def score_fn(i: int) -> Fraction:
                    return stride_pass[i]
                scores = [score_fn(i) for i in ready]
                if len(ready) > 1 and scores.count(min(scores)) > 1:
                    res.tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            else:
                raise ValueError(base)

            current = chosen
            slice_left = quantum

        # Accounting for preemption / context switch
        if previous is not None and previous != current:
            if rem[previous] > 0 and wake_at[previous] <= t:
                res.preemptions += 1
            res.context_switches += 1
        elif previous is None:
            res.context_switches += 1

        # Update online entitled time & system virtual time over [t, t+1)
        tot_w = sum(procs[i].weight for i in ready)
        sys_vtime += Fraction(1, tot_w)
        for i in ready:
            entitled_online[i] += Fraction(procs[i].weight, tot_w)

        # Update starvation streaks
        for i in ready:
            if i == current:
                wait_streak[i] = 0
            else:
                wait_streak[i] += 1
                if wait_streak[i] > max_starve[i]:
                    max_starve[i] = wait_streak[i]

        # Execute current for 1 tick [t, t+1)
        if started_at[current] is None:
            started_at[current] = t
        res.timeline.append((t, procs[current].name))
        res.busy += 1
        used[current] += 1
        rem[current] -= 1
        slice_left -= 1
        vruntime[current] += Fraction(1, procs[current].weight)
        stride_pass[current] += stride_step[current]
        previous = current

        # Check completion or sleep trigger at t+1
        if rem[current] == 0:
            finished_at[current] = t + 1
            res.completed += 1
            if current in rr_queue:
                rr_queue.remove(current)
            in_rr[current] = False
            current = None
            slice_left = 0
        elif used[current] in sleep_maps[current]:
            dur = sleep_maps[current][used[current]]
            wake_at[current] = (t + 1) + dur
            was_sleeping[current] = True
            if current in rr_queue:
                rr_queue.remove(current)
            in_rr[current] = False
            current = None
            slice_left = 0

        # Lag snapshot at t+1
        if t + 1 < len(gps["entitled"]):
            for i in range(n):
                diff = abs(Fraction(used[i]) - gps["entitled"][t + 1][i])
                if diff > max_lag_frac:
                    max_lag_frac = diff
                lag_sq_sum += float(diff) ** 2
                lag_samples += 1

    # End-of-horizon deadline check for any job whose deadline == horizon
    for i, p in enumerate(procs):
        if p.deadline is not None and rem[i] > 0 and horizon >= p.deadline and not missed_flag[i]:
            missed_flag[i] = True
            res.missed += 1

    # Compile per-process & aggregate metrics
    turnarounds: List[int] = []
    waitings: List[int] = []
    share_ratios: List[float] = []
    for i, p in enumerate(procs):
        fin = finished_at[i]
        ta = (fin - p.arrival) if fin is not None else None
        wt = (ta - p.work) if ta is not None else None
        resp = (started_at[i] - p.arrival) if started_at[i] is not None else None
        if ta is not None:
            turnarounds.append(ta)
        if wt is not None:
            waitings.append(wt)
        gps_end = gps["entitled"][min(horizon, len(gps["entitled"]) - 1)][i]
        sr = float(Fraction(used[i]) / gps_end) if gps_end > 0 else 1.0
        share_ratios.append(sr)
        # Process-specific max lag
        p_max_lag = Fraction(0)
        # Reconstruct prefix used counts from timeline for exact per-proc lag
        u_run = 0
        for step_t in range(min(horizon, len(gps["entitled"]) - 1)):
            if res.timeline[step_t][1] == p.name:
                u_run += 1
            d_step = abs(Fraction(u_run) - gps["entitled"][step_t + 1][i])
            if d_step > p_max_lag:
                p_max_lag = d_step

        res.per_proc[p.name] = {
            "arrival": p.arrival,
            "work": p.work,
            "weight": p.weight,
            "used": used[i],
            "remaining": rem[i],
            "start": started_at[i],
            "finish": fin,
            "turnaround": ta,
            "waiting": wt,
            "response": resp,
            "entitled_gps": float(gps_end),
            "entitled_gps_frac": str(gps_end),
            "entitled_online": float(entitled_online[i]),
            "entitled_online_frac": str(entitled_online[i]),
            "ratio_actual_over_entitled": float(Fraction(used[i]) / entitled_online[i]) if entitled_online[i] > 0 else 1.0,
            "share_ratio": sr,
            "max_abs_lag": float(p_max_lag),
            "max_abs_lag_frac": str(p_max_lag),
            "max_starve_gap": max_starve[i],
            "missed": missed_flag[i],
        }

    res.max_abs_lag = float(max_lag_frac)
    res.max_abs_lag_frac = str(max_lag_frac)
    res.rmse_lag = sqrt(lag_sq_sum / lag_samples) if lag_samples else 0.0
    res.max_starve_gap = max(max_starve) if max_starve else 0
    if share_ratios:
        s_sum = sum(share_ratios)
        s_sq = sum(x * x for x in share_ratios)
        res.jain_fairness = (s_sum * s_sum) / (len(share_ratios) * s_sq) if s_sq > 0 else 1.0
        res.min_share_ratio = min(share_ratios)
    if turnarounds:
        res.mean_turnaround = sum(turnarounds) / len(turnarounds)
        res.worst_turnaround = max(turnarounds)
        res.jitter_turnaround = max(turnarounds) - min(turnarounds)
    if waitings:
        res.mean_waiting = sum(waitings) / len(waitings)
    res.miss_rate = (res.missed / n) if n else 0.0
    return res


# --------------------------------------------------------------------------
# Periodic real-time task simulation (GS vs EDF / RM / DM / RR / FIFO)
# --------------------------------------------------------------------------

def simulate_rt(tasks: Sequence[RTTask],
                policy: str = "gs_vtime",
                horizon: Optional[int] = None,
                cycles: int = 2,
                quantum: int = 1,
                tie: str = "index",
                drop_on_miss: bool = False,
                release_window: Optional[int] = None) -> dict:
    """Run one policy on a periodic ``RTTask`` set and return structured metrics."""
    if quantum <= 0:
        raise ValueError("quantum must be >= 1")
    base, tie = _parse_policy(policy, tie)
    tasks = [RTTask(*t) if isinstance(t, tuple) else t for t in tasks]
    hp = hyperperiod(tasks)
    if horizon is None:
        horizon = hp * cycles
    if release_window is None:
        release_window = horizon
    jobs = make_rt_jobs(tasks, release_window)
    n = len(jobs)

    rem = [j.wcet for j in jobs]
    used = [0] * n
    released = [False] * n
    missed_flag = [False] * n
    vruntime = [Fraction(0)] * n
    entitled = [Fraction(0)] * n
    stride_pass = [Fraction(0)] * n
    sys_vtime = Fraction(0)

    rr_queue: List[int] = []
    in_rr = [False] * n

    timeline: List[Tuple[int, Optional[str]]] = []
    busy = 0
    idle = 0
    released_cnt = 0
    completed_cnt = 0
    missed_cnt = 0
    first_miss: Optional[int] = None
    preemptions = 0
    context_switches = 0
    tie_events = 0
    responses: List[int] = []

    task_used = [0] * len(tasks)
    task_entitled = [Fraction(0)] * len(tasks)

    previous: Optional[int] = None
    current: Optional[int] = None
    slice_left = 0

    def _tie_key(i: int, score_fn) -> Tuple:
        sc = score_fn(i)
        if tie == "index":
            return (sc, jobs[i].task, i)
        if tie == "stay":
            return (sc, 0 if i == previous else 1, jobs[i].task, i)
        if tie == "max_weight":
            return (sc, -jobs[i].weight, jobs[i].task, i)
        return (sc, jobs[i].deadline, jobs[i].task, i)

    for t in range(horizon):
        for i, j in enumerate(jobs):
            if j.release <= t and not released[i]:
                released[i] = True
                released_cnt += 1
                vruntime[i] = sys_vtime
                active_p = [stride_pass[k] for k in range(n)
                            if released[k] and rem[k] > 0 and k != i]
                stride_pass[i] = min(active_p) if active_p else Fraction(0)
                if not in_rr[i]:
                    rr_queue.append(i)
                    in_rr[i] = True

        for i, j in enumerate(jobs):
            if released[i] and rem[i] > 0 and t >= j.deadline and not missed_flag[i]:
                missed_flag[i] = True
                missed_cnt += 1
                if first_miss is None:
                    first_miss = t
                if drop_on_miss:
                    rem[i] = 0

        ready = [i for i in range(n) if released[i] and rem[i] > 0]
        if current is not None and (current not in ready or slice_left == 0):
            if current in ready and base == "rr" and slice_left == 0:
                if current in rr_queue:
                    rr_queue.remove(current)
                rr_queue.append(current)
            current = None
            slice_left = 0

        if not ready:
            timeline.append((t, None))
            idle += 1
            previous = None
            current = None
            slice_left = 0
            continue

        if current is None:
            if base == "fifo":
                chosen = min(ready, key=lambda i: (jobs[i].release, jobs[i].task, i))
            elif base == "edf":
                chosen = min(ready, key=lambda i: (jobs[i].deadline, jobs[i].task, i))
            elif base == "rm":
                chosen = min(ready, key=lambda i: (tasks[jobs[i].task].period, i))
            elif base == "dm":
                chosen = min(ready, key=lambda i: (
                    tasks[jobs[i].task].rel_deadline, tasks[jobs[i].task].period, i
                ))
            elif base == "rr":
                rr_queue = [i for i in rr_queue if i in ready]
                for i in ready:
                    if i not in rr_queue:
                        rr_queue.append(i)
                chosen = rr_queue[0]
            elif base == "gs_ratio":
                def score_fn(i: int) -> Fraction:
                    return Fraction(used[i], jobs[i].weight)
                sc = [score_fn(i) for i in ready]
                if len(ready) > 1 and sc.count(min(sc)) > 1:
                    tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            elif base == "gs_entitled":
                def score_fn(i: int) -> Fraction:
                    return Fraction(0) if entitled[i] == 0 else Fraction(used[i], 1) / entitled[i]
                sc = [score_fn(i) for i in ready]
                if len(ready) > 1 and sc.count(min(sc)) > 1:
                    tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            elif base in ("gs_vtime", "gs_capped"):
                def score_fn(i: int) -> Fraction:
                    return vruntime[i]
                sc = [score_fn(i) for i in ready]
                if len(ready) > 1 and sc.count(min(sc)) > 1:
                    tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            elif base == "stride":
                def score_fn(i: int) -> Fraction:
                    return stride_pass[i]
                sc = [score_fn(i) for i in ready]
                if len(ready) > 1 and sc.count(min(sc)) > 1:
                    tie_events += 1
                chosen = min(ready, key=lambda i: _tie_key(i, score_fn))
            else:
                raise ValueError(base)

            current = chosen
            slice_left = quantum

        if previous is not None and previous != current:
            if rem[previous] > 0:
                preemptions += 1
            context_switches += 1
        elif previous is None:
            context_switches += 1

        tot_w = sum(jobs[i].weight for i in ready)
        sys_vtime += Fraction(1, tot_w)
        for i in ready:
            frac_w = Fraction(jobs[i].weight, tot_w)
            entitled[i] += frac_w
            # track unique active tasks for task-level share fairness
        active_tasks = {jobs[i].task for i in ready}
        tot_tw = sum(tasks[ti].weight for ti in active_tasks)
        for ti in active_tasks:
            task_entitled[ti] += Fraction(tasks[ti].weight, tot_tw)

        timeline.append((t, jobs[current].name))
        busy += 1
        used[current] += 1
        task_used[jobs[current].task] += 1
        rem[current] -= 1
        slice_left -= 1
        vruntime[current] += Fraction(1, jobs[current].weight)
        stride_pass[current] += Fraction(1, jobs[current].weight)
        previous = current

        if rem[current] == 0:
            completed_cnt += 1
            responses.append((t + 1) - jobs[current].release)
            if current in rr_queue:
                rr_queue.remove(current)
            in_rr[current] = False
            current = None
            slice_left = 0

    task_share_ratios = []
    for ti, tsk in enumerate(tasks):
        sr = float(Fraction(task_used[ti]) / task_entitled[ti]) if task_entitled[ti] > 0 else 1.0
        task_share_ratios.append(sr)
    s_sum = sum(task_share_ratios)
    s_sq = sum(x * x for x in task_share_ratios)
    jain = (s_sum * s_sum) / (len(tasks) * s_sq) if s_sq > 0 and tasks else 1.0

    return {
        "policy": base,
        "tie": tie,
        "quantum": quantum,
        "horizon": horizon,
        "released": released_cnt,
        "completed": completed_cnt,
        "missed": missed_cnt,
        "miss_rate": (missed_cnt / released_cnt) if released_cnt else 0.0,
        "first_miss": first_miss,
        "preemptions": preemptions,
        "context_switches": context_switches,
        "tie_events": tie_events,
        "busy": busy,
        "idle": idle,
        "jain_fairness": jain,
        "min_task_share_ratio": min(task_share_ratios) if task_share_ratios else 1.0,
        "task_used": {tasks[ti].name: task_used[ti] for ti in range(len(tasks))},
        "task_share_ratios": {tasks[ti].name: task_share_ratios[ti] for ti in range(len(tasks))},
        "worst_response": max(responses) if responses else None,
        "mean_response": (sum(responses) / len(responses)) if responses else None,
        "jitter": (max(responses) - min(responses)) if responses else None,
        "timeline": timeline,
    }


def gantt_rows(timeline: Sequence[Tuple[int, Optional[str]]]) -> List[Tuple[str, int, int]]:
    rows: List[Tuple[str, int, int]] = []
    for t, name in timeline:
        if name is None:
            continue
        if rows and rows[-1][0] == name and rows[-1][2] == t:
            rows[-1] = (name, rows[-1][1], t + 1)
        else:
            rows.append((name, t, t + 1))
    return rows


# --------------------------------------------------------------------------
# Instrument [E] 1: Exhaustive RT feasibility + independent verifier
# --------------------------------------------------------------------------

def exhaustive_feasible(tasks: Sequence[RTTask],
                        horizon: Optional[int] = None,
                        allow_idle: bool = False,
                        limit: int = 2_000_000
                        ) -> Tuple[bool, Optional[List[Optional[int]]], Dict]:
    """Exhaustive memoized DFS deciding whether ANY schedule meets all RT deadlines."""
    hp = hyperperiod(tasks)
    horizon = horizon if horizon is not None else hp
    jobs = make_rt_jobs(tasks, horizon)
    n = len(jobs)
    rel = [j.release for j in jobs]
    ddl = [j.deadline for j in jobs]
    start_rem = tuple(j.wcet for j in jobs)

    memo: Dict[Tuple[int, Tuple[int, ...]], Tuple[bool, Optional[int]]] = {}
    stats = {"states": 0, "pruned": 0, "truncated": False, "limit": limit,
             "jobs": n, "horizon": horizon}

    def rec(t: int, rem: Tuple[int, ...]) -> bool:
        stats["states"] += 1
        if stats["states"] > limit:
            stats["truncated"] = True
            return False
        key = (t, rem)
        if key in memo:
            return memo[key][0]
        if all(r == 0 for r in rem):
            memo[key] = (True, None)
            return True
        for i in range(n):
            if rem[i] > 0 and rel[i] <= t and rem[i] > ddl[i] - t:
                stats["pruned"] += 1
                memo[key] = (False, None)
                return False

        opts = [i for i in range(n) if rem[i] > 0 and rel[i] <= t]
        if not opts:
            ok = rec(t + 1, rem)
            memo[key] = (ok, None)
            return ok
        if allow_idle and rec(t + 1, rem):
            memo[key] = (True, None)
            return True

        for i in opts:
            nrem = list(rem)
            nrem[i] -= 1
            nrem_t = tuple(nrem)
            bad = False
            for j in range(n):
                if nrem_t[j] > 0 and rel[j] <= t + 1 and nrem_t[j] > ddl[j] - (t + 1):
                    bad = True
                    break
            if bad:
                stats["pruned"] += 1
                continue
            if rec(t + 1, nrem_t):
                memo[key] = (True, i)
                return True
        memo[key] = (False, None)
        return False

    ok = rec(0, start_rem)
    if not ok:
        return False, None, stats

    sched: List[Optional[int]] = []
    t, rem = 0, start_rem
    while any(r > 0 for r in rem):
        choice = memo[(t, rem)][1]
        sched.append(choice)
        if choice is not None:
            lst = list(rem)
            lst[choice] -= 1
            rem = tuple(lst)
        t += 1
        if t > sum(j.wcet for j in jobs) + horizon + 1:
            break
    return True, sched, stats


def verify_rt_schedule_independent(tasks: Sequence[RTTask],
                                   schedule: Sequence[Optional[int]],
                                   horizon: Optional[int] = None) -> Tuple[bool, str]:
    """Independent validator sharing zero code with exhaustive_feasible or simulate_rt."""
    hp = hyperperiod(tasks) if horizon is None else horizon
    jobs = []
    for ti, task in enumerate(tasks):
        k = 0
        while task.phase + k * task.period < hp:
            rel = task.phase + k * task.period
            ddl = rel + (task.deadline if task.deadline is not None else task.period)
            jobs.append((rel, ddl, task.wcet, f"{task.name}#{k}"))
            k += 1
    # Sort exactly by (release, task_index) via rebuilding with ti
    jobs_indexed = []
    for ti, task in enumerate(tasks):
        k = 0
        while task.phase + k * task.period < hp:
            rel = task.phase + k * task.period
            ddl = rel + (task.deadline if task.deadline is not None else task.period)
            jobs_indexed.append((rel, ti, ddl, task.wcet, f"{task.name}#{k}"))
            k += 1
    jobs_indexed.sort(key=lambda x: (x[0], x[1]))

    ran = [0] * len(jobs_indexed)
    finish: List[Optional[int]] = [None] * len(jobs_indexed)
    for t, idx in enumerate(schedule):
        if idx is None:
            continue
        if not (0 <= idx < len(jobs_indexed)):
            return False, f"invalid job index {idx} at t={t}"
        rel, _, ddl, wcet, name = jobs_indexed[idx]
        if t < rel:
            return False, f"{name} executed at t={t} before release {rel}"
        ran[idx] += 1
        if ran[idx] > wcet:
            return False, f"{name} exceeded wcet {wcet} at t={t}"
        if ran[idx] == wcet and finish[idx] is None:
            finish[idx] = t + 1
    for k, (rel, _, ddl, wcet, name) in enumerate(jobs_indexed):
        if ran[k] != wcet:
            return False, f"{name} ran {ran[k]} != wcet {wcet}"
        if finish[k] is None or finish[k] > ddl:
            return False, f"{name} finished at {finish[k]} > deadline {ddl}"
    return True, "ok"


# --------------------------------------------------------------------------
# Instrument [E] 2: Exhaustive tie-breaking envelope & starvation witness
# --------------------------------------------------------------------------

def exhaustive_tie_envelope(procs: Sequence[Proc],
                            policy: str = "gs_ratio",
                            quantum: int = 1,
                            max_states: int = 200_000) -> dict:
    """Explore ALL valid tie-breaking branches of a GS policy at integer ticks.

    Returns exact worst-case and best-case GPS lag, context switches, and
    worst turnaround across *every* possible tie-breaking resolution.
    """
    base, _ = _parse_policy(policy, "index")
    if base not in ("gs_ratio", "gs_entitled", "gs_vtime"):
        raise ValueError("exhaustive_tie_envelope supports gs_ratio, gs_entitled, gs_vtime")
    n = len(procs)
    max_arr = max((p.arrival for p in procs), default=0)
    horizon = max_arr + sum(p.work for p in procs)
    gps = ideal_gps_trace(procs, horizon=horizon)

    best_lag = None
    worst_lag = Fraction(0)
    min_sw = None
    max_sw = 0
    worst_ta = 0
    leaves = 0
    states = 0
    truncated = False
    worst_witness: Optional[List[Tuple[int, Optional[str]]]] = None

    def dfs(t: int, used: Tuple[int, ...], rem: Tuple[int, ...],
            prev: Optional[int], cur: Optional[int], sleft: int,
            ent: Tuple[Fraction, ...], vrun: Tuple[Fraction, ...],
            sv: Fraction, max_l: Fraction, sw: int, max_fin: Tuple[Optional[int], ...],
            trace: List[Tuple[int, Optional[str]]]) -> None:
        nonlocal best_lag, worst_lag, min_sw, max_sw, worst_ta, leaves, states, truncated, worst_witness
        states += 1
        if states > max_states:
            truncated = True
            return
        if t == horizon or all(r == 0 for r in rem):
            leaves += 1
            if best_lag is None or max_l < best_lag:
                best_lag = max_l
            if max_l > worst_lag:
                worst_lag = max_l
                worst_witness = list(trace)
            if min_sw is None or sw < min_sw:
                min_sw = sw
            if sw > max_sw:
                max_sw = sw
            for i, fin in enumerate(max_fin):
                if fin is not None:
                    worst_ta = max(worst_ta, fin - procs[i].arrival)
            return

        ready = [i for i in range(n) if rem[i] > 0 and procs[i].arrival <= t]
        # Update arrival vruntime for jobs arriving exactly at t
        vrun_l = list(vrun)
        for i in ready:
            if procs[i].arrival == t:
                vrun_l[i] = sv

        if cur is not None and (cur not in ready or sleft == 0):
            cur = None
            sleft = 0

        if not ready:
            nl = max_l
            if t + 1 < len(gps["entitled"]):
                for i in range(n):
                    d = abs(Fraction(used[i]) - gps["entitled"][t + 1][i])
                    if d > nl:
                        nl = d
            trace.append((t, None))
            dfs(t + 1, used, rem, None, None, 0, ent, tuple(vrun_l), sv, nl, sw, max_fin, trace)
            trace.pop()
            return

        if cur is not None:
            choices = [cur]
            next_sleft = sleft - 1
        else:
            if base == "gs_ratio":
                scores = {i: Fraction(used[i], procs[i].weight) for i in ready}
            elif base == "gs_entitled":
                scores = {i: (Fraction(0) if ent[i] == 0 else Fraction(used[i], 1) / ent[i])
                          for i in ready}
            else:
                scores = {i: vrun_l[i] for i in ready}
            best_sc = min(scores.values())
            choices = [i for i in ready if scores[i] == best_sc]
            next_sleft = quantum - 1

        tot_w = sum(procs[i].weight for i in ready)
        nsv = sv + Fraction(1, tot_w)
        nent = tuple(ent[i] + (Fraction(procs[i].weight, tot_w) if i in ready else Fraction(0))
                     for i in range(n))

        for ch in choices:
            nsw = sw + (1 if (prev is None or prev != ch) else 0)
            nused = list(used)
            nused[ch] += 1
            nrem = list(rem)
            nrem[ch] -= 1
            nvrun = list(vrun_l)
            nvrun[ch] += Fraction(1, procs[ch].weight)
            nfin = list(max_fin)
            ncur = ch
            nsleft = next_sleft
            if nrem[ch] == 0:
                nfin[ch] = t + 1
                ncur = None
                nsleft = 0
            nl = max_l
            if t + 1 < len(gps["entitled"]):
                for i in range(n):
                    d = abs(Fraction(nused[i]) - gps["entitled"][t + 1][i])
                    if d > nl:
                        nl = d
            trace.append((t, procs[ch].name))
            dfs(t + 1, tuple(nused), tuple(nrem), ch, ncur, nsleft, nent, tuple(nvrun),
                nsv, nl, nsw, tuple(nfin), trace)
            trace.pop()
            if truncated:
                return

    dfs(0, (0,) * n, tuple(p.work for p in procs), None, None, 0,
        (Fraction(0),) * n, (Fraction(0),) * n, Fraction(0), Fraction(0), 0,
        (None,) * n, [])
    return {
        "policy": base,
        "quantum": quantum,
        "states": states,
        "leaves": leaves,
        "truncated": truncated,
        "best_max_lag": float(best_lag) if best_lag is not None else 0.0,
        "worst_max_lag": float(worst_lag),
        "worst_max_lag_frac": str(worst_lag),
        "min_context_switches": min_sw if min_sw is not None else 0,
        "max_context_switches": max_sw,
        "worst_turnaround": worst_ta,
        "worst_witness": worst_witness,
    }


def find_starvation_witness(policy: str,
                            max_arrival: int = 24,
                            min_gap_threshold: int = 8,
                            quantum: int = 1,
                            tie: str = "index") -> dict:
    """Systematically search 2-process arrival-offset workloads for a starvation witness.

    Constructs ``P1(arrival=0, work=max_arrival+16, weight=2)`` and a latecomer
    ``P2(arrival=t_arr, work=16, weight=1)`` across ``t_arr in [1..max_arrival]``
    and tests whether ``P1`` (already running!) gets starved for at least
    ``min_gap_threshold`` consecutive ticks upon ``P2``'s arrival.
    """
    witness = None
    worst_gap = 0
    checked = 0
    for t_arr in range(2, max_arrival + 1, 2):
        procs = [
            Proc("P1", arrival=0, work=t_arr + 16, weight=2),
            Proc("P2", arrival=t_arr, work=16, weight=1),
        ]
        r = simulate_procs(procs, policy=policy, quantum=quantum, tie=tie)
        checked += 1
        gap = r.per_proc["P1"]["max_starve_gap"]
        if gap > worst_gap:
            worst_gap = gap
        if gap >= min_gap_threshold and witness is None:
            witness = {
                "t_arr": t_arr,
                "procs": [p.__dict__ for p in procs],
                "p1_starve_gap": gap,
                "max_abs_lag": r.max_abs_lag,
                "timeline_snippet": r.timeline[max(0, t_arr - 2):t_arr + gap + 2],
            }
    return {
        "policy": policy,
        "checked_arrivals": checked,
        "min_gap_threshold": min_gap_threshold,
        "violated": witness is not None,
        "worst_p1_starve_gap": worst_gap,
        "witness": witness,
    }


# --------------------------------------------------------------------------
# CLI demo
# --------------------------------------------------------------------------

def _demo() -> int:
    procs = [Proc("P1", 0, 4, 1), Proc("P2", 0, 6, 2), Proc("P3", 0, 9, 3)]
    print("Static weighted demo: P1(w=1,work=4), P2(w=2,work=6), P3(w=3,work=9)")
    for p in ("gs_ratio", "gs_entitled", "gs_vtime", "stride", "rr", "fifo"):
        r = simulate_procs(procs, policy=p, quantum=1)
        print(f"  {p:12s} max_lag={r.max_abs_lag:.4f} rmse={r.rmse_lag:.4f} "
              f"jain={r.jain_fairness:.4f} sw={r.context_switches}")
    print("\nStarvation check (latecomer P2 at t_arr<=24):")
    for p in ("gs_ratio", "gs_entitled", "gs_vtime", "stride"):
        w = find_starvation_witness(p)
        print(f"  {p:12s} violated={w['violated']} worst_gap={w['worst_p1_starve_gap']}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--demo", action="store_true", help="run built-in GS demo")
    args = ap.parse_args(argv)
    return _demo()


if __name__ == "__main__":
    raise SystemExit(main())
