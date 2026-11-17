"""Canonical tests for core/gs_core.py.

Every theoretical claim and every subtle bug/artifact in Guaranteed Scheduling
is pinned by a dedicated test here.
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "core"))

from gs_core import (  # noqa: E402
    POLICIES,
    GS_POLICIES,
    TIE_BREAKERS,
    Proc,
    RTTask,
    exhaustive_feasible,
    exhaustive_tie_envelope,
    find_starvation_witness,
    gantt_rows,
    hyperperiod,
    ideal_gps_trace,
    make_rt_jobs,
    simulate_procs,
    simulate_rt,
    utilisation,
    verify_rt_schedule_independent,
)

STATIC_DEMO = [Proc("P1", 0, 4, 1), Proc("P2", 0, 6, 2), Proc("P3", 0, 9, 3)]
RT_DEMO = [RTTask("T1", 6, 2, weight=2), RTTask("T2", 8, 2, weight=2),
           RTTask("T3", 12, 3, weight=3)]


# --------------------------------------------------------------------------
# Model & Exact Fluid GPS
# --------------------------------------------------------------------------

def test_proc_validation_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        Proc("bad_arr", -1, 4, 1)
    with pytest.raises(ValueError):
        Proc("bad_work", 0, 0, 1)
    with pytest.raises(ValueError):
        Proc("bad_weight", 0, 4, 0)
    with pytest.raises(ValueError):
        Proc("bad_ddl", 2, 5, 1, deadline=6)


def test_ideal_gps_conserves_cpu_and_is_monotonic():
    procs = [Proc("A", 0, 3, 1), Proc("B", 2, 4, 3), Proc("C", 10, 2, 2)]
    gps = ideal_gps_trace(procs, horizon=14)
    snaps = gps["entitled"]
    assert len(snaps) == 15
    for t in range(14):
        for i in range(len(procs)):
            assert snaps[t][i] <= snaps[t + 1][i]
            assert snaps[t + 1][i] <= procs[i].work
        assert sum(snaps[t + 1]) <= t + 1
    # Exact finish times: A and B finish by t=7 (3+4=7), C arrives at 10 and finishes at 12
    assert gps["finish_times"][0] <= 7
    assert gps["finish_times"][1] <= 7
    assert gps["finish_times"][2] == Fraction(12)


def test_gps_exact_ratios_on_static_weighted_set():
    # At t=6, all 3 procs (weights 1,2,3 -> sum 6) still active:
    # A(w=1) has 1, B(w=2) has 2, C(w=3) has 3.
    gps = ideal_gps_trace(STATIC_DEMO)
    assert gps["entitled"][6] == [Fraction(1), Fraction(2), Fraction(3)]
    # Total work = 19, all finish strictly at t=19 (sum=19)
    assert gps["entitled"][19] == [Fraction(4), Fraction(6), Fraction(9)]


# --------------------------------------------------------------------------
# Simulation invariants across all policies
# --------------------------------------------------------------------------

@pytest.mark.parametrize("policy", POLICIES)
def test_work_conservation_and_determinism(policy):
    r1 = simulate_procs(STATIC_DEMO, policy=policy, quantum=1)
    r2 = simulate_procs(STATIC_DEMO, policy=policy, quantum=1)
    assert r1.timeline == r2.timeline
    assert r1.busy + r1.idle == r1.horizon
    assert r1.completed == len(STATIC_DEMO)
    assert sum(d["used"] for d in r1.per_proc.values()) == sum(p.work for p in STATIC_DEMO)


def test_gantt_rows_partition_timeline_without_gaps():
    r = simulate_procs(STATIC_DEMO, policy="gs_ratio", quantum=2)
    rows = gantt_rows(r.timeline)
    reconstructed = []
    for name, s, e in rows:
        reconstructed.extend([name] * (e - s))
    assert reconstructed == [n for _, n in r.timeline if n is not None]


def test_static_simultaneous_gs_variants_match_exactly():
    """When all processes start at t=0 without sleeps, gs_ratio, gs_entitled,
    gs_vtime and stride produce the exact same max lag and equal final shares."""
    res = [simulate_procs(STATIC_DEMO, policy=p, quantum=1)
           for p in ("gs_ratio", "gs_entitled", "gs_vtime", "stride")]
    lags = {r.max_abs_lag_frac for r in res}
    assert len(lags) == 1
    assert res[0].max_abs_lag < res_rr_lag(STATIC_DEMO)


def res_rr_lag(procs):
    return simulate_procs(procs, policy="rr", quantum=2).max_abs_lag


# --------------------------------------------------------------------------
# The dynamic-arrival starvation bug in naive used/weight (GuaranteedScheduling.py)
# --------------------------------------------------------------------------

def test_naive_gs_ratio_starves_existing_process_on_late_arrival():
    """Pinning the real algorithmic flaw of naive ``used / weight``:
    a latecomer arrives with used=0 and monopolizes CPU against an active job."""
    w_ratio = find_starvation_witness("gs_ratio", max_arrival=20, min_gap_threshold=8)
    assert w_ratio["violated"] is True
    assert w_ratio["worst_p1_starve_gap"] >= 8
    assert w_ratio["witness"] is not None

    for safe_pol in ("gs_entitled", "gs_vtime", "stride"):
        w_safe = find_starvation_witness(safe_pol, max_arrival=20, min_gap_threshold=8)
        assert w_safe["violated"] is False, f"{safe_pol} unexpectedly starved P1"


def test_sleeper_exploit_bounded_by_gs_capped():
    """A process that sleeps for 20 ticks accumulates zero CPU time while sleeping;
    both naive gs_ratio and uncapped gs_vtime let it monopolize CPU upon wakeup,
    whereas gs_capped bounds its sleeper credit to wakeup_cap."""
    procs = [
        Proc("CPU_Hog", arrival=0, work=30, weight=1),
        Proc("Sleeper", arrival=0, work=15, weight=1, sleep_at=((1, 20),)),
    ]
    r_ratio = simulate_procs(procs, policy="gs_ratio", quantum=1)
    r_vtime = simulate_procs(procs, policy="gs_vtime", quantum=1)
    r_cap = simulate_procs(procs, policy="gs_capped", quantum=1, wakeup_cap=1)
    assert r_ratio.per_proc["CPU_Hog"]["max_starve_gap"] == 14
    assert r_vtime.per_proc["CPU_Hog"]["max_starve_gap"] == 14
    assert r_cap.per_proc["CPU_Hog"]["max_starve_gap"] <= 2


# --------------------------------------------------------------------------
# Quantum size & tie-breaking effects
# --------------------------------------------------------------------------

def test_larger_quantum_increases_lag_and_reduces_switches():
    procs = [Proc("P1", 0, 16, 1), Proc("P2", 0, 16, 2), Proc("P3", 0, 16, 4)]
    r1 = simulate_procs(procs, policy="gs_vtime", quantum=1)
    r4 = simulate_procs(procs, policy="gs_vtime", quantum=4)
    r8 = simulate_procs(procs, policy="gs_vtime", quantum=8)
    assert r1.max_abs_lag <= r4.max_abs_lag <= r8.max_abs_lag
    assert r1.context_switches >= r4.context_switches >= r8.context_switches


@pytest.mark.parametrize("tie", TIE_BREAKERS)
def test_tie_breakers_preserve_long_term_shares_but_change_switches(tie):
    procs = [Proc(f"P{i+1}", 0, 8, 2) for i in range(4)]
    r = simulate_procs(procs, policy="gs_vtime", quantum=1, tie=tie)
    assert r.jain_fairness == pytest.approx(1.0)
    assert r.completed == 4


def test_stay_tie_breaker_cuts_context_switches_on_equal_weights():
    procs = [Proc("A", 0, 6, 1), Proc("B", 0, 6, 1), Proc("C", 0, 6, 1)]
    r_idx = simulate_procs(procs, policy="gs_vtime", quantum=1, tie="index")
    r_stay = simulate_procs(procs, policy="gs_vtime", quantum=1, tie="stay")
    assert r_stay.context_switches <= r_idx.context_switches


def test_exhaustive_tie_envelope_bounds_simulated_policies():
    procs = [Proc("A", 0, 4, 1), Proc("B", 0, 4, 1), Proc("C", 0, 4, 2)]
    env = exhaustive_tie_envelope(procs, policy="gs_vtime", quantum=1)
    assert not env["truncated"]
    assert env["leaves"] >= 1
    for tie in ("index", "stay", "max_weight"):
        r = simulate_procs(procs, policy="gs_vtime", quantum=1, tie=tie)
        assert env["best_max_lag"] - 1e-9 <= r.max_abs_lag <= env["worst_max_lag"] + 1e-9
        assert env["min_context_switches"] <= r.context_switches <= env["max_context_switches"]


# --------------------------------------------------------------------------
# Real-time comparison & exhaustive feasibility checker + independent verifier
# --------------------------------------------------------------------------

def test_forced_idle_is_feasible_in_exhaustive_checker():
    """T1(8,2), T2(3,2) has a forced idle slot at t=14; must NOT return infeasible."""
    ts = [RTTask("T1", 8, 2), RTTask("T2", 3, 2)]
    ok_no, sched, _ = exhaustive_feasible(ts, allow_idle=False)
    ok_yes, _, _ = exhaustive_feasible(ts, allow_idle=True)
    assert ok_no and ok_yes
    valid, msg = verify_rt_schedule_independent(ts, sched)
    assert valid, msg


def test_independent_verifier_catches_invalid_schedule():
    ts = [RTTask("T1", 4, 2), RTTask("T2", 4, 2)]
    bad_sched = [0, 0, 0, 0]   # job 0 ran 4 != wcet 2, job 1 ran 0
    valid, _ = verify_rt_schedule_independent(ts, bad_sched)
    assert not valid


def test_edf_meets_all_feasible_constrained_sets_while_gs_equal_can_miss():
    """On a tight constrained-deadline task set feasible for EDF, equal-weight GS misses
    because it divides CPU equally rather than prioritizing urgent deadlines."""
    ts = [RTTask("T1", 5, 2, deadline=2, weight=1),
          RTTask("T2", 10, 4, deadline=10, weight=1)]
    ok, sched, st = exhaustive_feasible(ts)
    assert ok and not st["truncated"]
    valid, msg = verify_rt_schedule_independent(ts, sched)
    assert valid, msg
    assert simulate_rt(ts, "edf", cycles=1)["missed"] == 0
    assert simulate_rt(ts, "gs_vtime", cycles=1)["missed"] > 0


def test_overload_preserves_gs_fairness_while_rm_starves_low_priority():
    """Under overload U > 1, RM completely starves the lowest-priority task,
    while Guaranteed Scheduling delivers proportional CPU shares."""
    ts = [RTTask("High", 4, 3, weight=1),
          RTTask("Mid", 6, 3, weight=1),
          RTTask("Low", 12, 6, weight=1)]   # U = 0.75 + 0.50 + 0.50 = 1.75 > 1
    r_rm = simulate_rt(ts, "rm", cycles=2)
    r_gs = simulate_rt(ts, "gs_vtime", cycles=2)
    assert r_rm["task_used"]["Low"] == 0
    assert r_gs["task_used"]["Low"] > 0
    assert r_gs["jain_fairness"] > r_rm["jain_fairness"]
