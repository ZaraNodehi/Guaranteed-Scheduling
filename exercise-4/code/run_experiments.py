"""Exercise 4 Experimental Engine:
1. Exact BFS State-Space Model Checker for Dekker (v1..v5), Peterson (SC vs TSO),
   Binary Semaphore (correct vs buggy), and Monitor (Mesa 'if' vs 'while' & Hoare).
2. Real multi-threaded OS benchmarks (N=2 contention, CS work sweep, N=2/4/8 scaling,
   and lock-holder preemption / sleep CPU burn audit).
3. Multi-dimensional quantitative engineering matrix.
"""
from __future__ import annotations

import json
import os
import threading
import time
from collections import deque
from typing import Dict, List, Set, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
EX4_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(EX4_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

import sys
sys.path.insert(0, HERE)
from sync_primitives import (  # noqa: E402
    BinarySemaphoreLock,
    DekkerLock,
    FilterLock,
    HoareMonitorQueueSim,
    MesaMonitorLock,
    PetersonLock,
    TournamentDekkerLock,
)


# =============================================================================
# PART 1: EXACT BFS EXPLICIT-STATE MODEL CHECKER
# =============================================================================
def bfs_model_check(name: str, init_state: Tuple, step_fn, is_cs_fn, is_deadlock_allowed=None, max_states: int = 25000) -> Dict:
    visited: Set[Tuple] = {init_state}
    q = deque([init_state])
    parent: Dict[Tuple, Tuple | None] = {init_state: None}
    both_in_cs = 0
    deadlock_states = 0
    edges = 0
    max_depth = 0
    depth_map = {init_state: 0}
    livelock_cycles = 0
    first_error_trace: List[List[int]] = []

    def _trace_to(st: Tuple) -> List[List[int]]:
        path = []
        cur: Tuple | None = st
        while cur is not None:
            path.append(list(cur))
            cur = parent[cur]
        path.reverse()
        return path

    while q and len(visited) < max_states:
        s = q.popleft()
        d = depth_map[s]
        max_depth = max(max_depth, d)
        in0, in1 = is_cs_fn(s)
        if in0 and in1:
            both_in_cs += 1
            if not first_error_trace:
                first_error_trace = _trace_to(s)
        succs = step_fn(s)
        if not succs:
            if not (is_deadlock_allowed and is_deadlock_allowed(s)):
                deadlock_states += 1
                if not first_error_trace:
                    first_error_trace = _trace_to(s)
        for ns in succs:
            edges += 1
            if ns not in visited:
                visited.add(ns)
                parent[ns] = s
                depth_map[ns] = d + 1
                q.append(ns)
            elif depth_map.get(ns, 999999) <= d and (not in0 and not in1):
                livelock_cycles += 1

    return {
        "model": name,
        "reachable_states": len(visited),
        "transitions": edges,
        "max_bfs_depth": max_depth,
        "mutex_violations": both_in_cs,
        "deadlock_states": deadlock_states,
        "non_cs_spin_back_edges": livelock_cycles,
        "first_counterexample": first_error_trace,
    }


def check_dekker_variants() -> List[Dict]:
    # State tuple: (pc0, pc1, f0, f1, turn)
    # Variant 1: strict alternation (turn != i spin)
    # Variant 2: check other flag, then set own flag -> race!
    # Variant 3: set own flag, then spin while other flag -> deadlock!
    # Variant 4: set own flag, backoff temporarily on conflict without turn -> livelock!
    # Variant 5: complete Dekker (v5) -> SAFE!
    results = []

    # v1: Strict Alternation: 0=nc, 1=wait(turn==i), 2=cs, 3=set_turn(1-i)
    def step_v1(s):
        pc0, pc1, turn = s
        out = []
        if pc0 == 0: out.append((1, pc1, turn))
        elif pc0 == 1 and turn == 0: out.append((2, pc1, turn))
        elif pc0 == 2: out.append((3, pc1, turn))
        elif pc0 == 3: out.append((0, pc1, 1))
        if pc1 == 0: out.append((pc0, 1, turn))
        elif pc1 == 1 and turn == 1: out.append((pc0, 2, turn))
        elif pc1 == 2: out.append((pc0, 3, turn))
        elif pc1 == 3: out.append((pc0, 0, 0))
        return out
    r1 = bfs_model_check("Dekker v1 (Strict Alternation)", (0, 0, 0), step_v1, lambda s: (s[0] == 2, s[1] == 2))
    r1["defect"] = "Violates independence: if P0 stays in non-CS, P1 blocks forever after 1 round"
    results.append(r1)

    # v2: Check flag[j]==False first, then set flag[i]=True (TOCTOU race)
    # 0=nc, 1=test_other_flag, 2=set_own_flag, 3=cs, 4=clear_own_flag
    def step_v2(s):
        pc0, pc1, f0, f1 = s
        out = []
        if pc0 == 0: out.append((1, pc1, f0, f1))
        elif pc0 == 1: out.append((2 if not f1 else 1, pc1, f0, f1))
        elif pc0 == 2: out.append((3, pc1, 1, f1))
        elif pc0 == 3: out.append((4, pc1, f0, f1))
        elif pc0 == 4: out.append((0, pc1, 0, f1))
        if pc1 == 0: out.append((pc0, 1, f0, f1))
        elif pc1 == 1: out.append((pc0, 2 if not f0 else 1, f0, f1))
        elif pc1 == 2: out.append((pc0, 3, f0, 1))
        elif pc1 == 3: out.append((pc0, 4, f0, f1))
        elif pc1 == 4: out.append((pc0, 0, f0, 0))
        return out
    r2 = bfs_model_check("Dekker v2 (Check-Then-Set)", (0, 0, 0, 0), step_v2, lambda s: (s[0] == 3, s[1] == 3))
    r2["defect"] = "Mutual exclusion broken (both pass check before setting flag)"
    results.append(r2)

    # v3: Set own flag first, then spin on other flag (deadlock)
    # 0=nc, 1=set_flag, 2=wait_other_false, 3=cs, 4=clear_flag
    def step_v3(s):
        pc0, pc1, f0, f1 = s
        out = []
        if pc0 == 0: out.append((1, pc1, f0, f1))
        elif pc0 == 1: out.append((2, pc1, 1, f1))
        elif pc0 == 2 and not f1: out.append((3, pc1, f0, f1))
        elif pc0 == 3: out.append((4, pc1, f0, f1))
        elif pc0 == 4: out.append((0, pc1, 0, f1))
        if pc1 == 0: out.append((pc0, 1, f0, f1))
        elif pc1 == 1: out.append((pc0, 2, f0, 1))
        elif pc1 == 2 and not f0: out.append((pc0, 3, f0, f1))
        elif pc1 == 3: out.append((pc0, 4, f0, f1))
        elif pc1 == 4: out.append((pc0, 0, f0, 0))
        return out
    r3 = bfs_model_check("Dekker v3 (Set-Then-Wait)", (0, 0, 0, 0), step_v3, lambda s: (s[0] == 3, s[1] == 3))
    r3["defect"] = "Symmetric deadlock when both set flags before testing"
    results.append(r3)

    # v4: Symmetric backoff without turn (livelock possible)
    # 0=nc, 1=set_flag, 2=check_other(if true->3 else->5), 3=clear_flag, 4=retry(->1), 5=cs, 6=clear_exit
    def step_v4(s):
        pc0, pc1, f0, f1 = s
        out = []
        if pc0 == 0: out.append((1, pc1, f0, f1))
        elif pc0 == 1: out.append((2, pc1, 1, f1))
        elif pc0 == 2: out.append((3 if f1 else 5, pc1, f0, f1))
        elif pc0 == 3: out.append((4, pc1, 0, f1))
        elif pc0 == 4: out.append((1, pc1, f0, f1))
        elif pc0 == 5: out.append((6, pc1, f0, f1))
        elif pc0 == 6: out.append((0, pc1, 0, f1))
        if pc1 == 0: out.append((pc0, 1, f0, f1))
        elif pc1 == 1: out.append((pc0, 2, f0, 1))
        elif pc1 == 2: out.append((pc0, 3 if f0 else 5, f0, f1))
        elif pc1 == 3: out.append((pc0, 4, f0, 0))
        elif pc1 == 4: out.append((pc0, 1, f0, f1))
        elif pc1 == 5: out.append((pc0, 6, f0, f1))
        elif pc1 == 6: out.append((pc0, 0, f0, 0))
        return out
    r4 = bfs_model_check("Dekker v4 (Symmetric Backoff)", (0, 0, 0, 0), step_v4, lambda s: (s[0] == 5, s[1] == 5))
    r4["defect"] = "Symmetric livelock cycle (both repeatedly set & clear flags without turn)"
    results.append(r4)

    # v5: Complete Dekker's Algorithm (SAFE)
    # 0=nc, 1=set_flag, 2=test_other(if 1->3 else->7), 3=test_turn(if !=i ->4 else->2),
    # 4=clear_flag, 5=wait_turn_i(if turn==i->6), 6=set_flag(->2), 7=cs, 8=set_turn_other, 9=clear_flag(->0)
    def step_v5(s):
        pc0, pc1, f0, f1, turn = s
        out = []
        # P0
        if pc0 == 0: out.append((1, pc1, f0, f1, turn))
        elif pc0 == 1: out.append((2, pc1, 1, f1, turn))
        elif pc0 == 2: out.append((3 if f1 else 7, pc1, f0, f1, turn))
        elif pc0 == 3: out.append((4 if turn != 0 else 2, pc1, f0, f1, turn))
        elif pc0 == 4: out.append((5, pc1, 0, f1, turn))
        elif pc0 == 5 and turn == 0: out.append((6, pc1, f0, f1, turn))
        elif pc0 == 6: out.append((2, pc1, 1, f1, turn))
        elif pc0 == 7: out.append((8, pc1, f0, f1, turn))
        elif pc0 == 8: out.append((9, pc1, f0, f1, 1))
        elif pc0 == 9: out.append((0, pc1, 0, f1, turn))
        # P1
        if pc1 == 0: out.append((pc0, 1, f0, f1, turn))
        elif pc1 == 1: out.append((pc0, 2, f0, 1, turn))
        elif pc1 == 2: out.append((pc0, 3 if f0 else 7, f0, f1, turn))
        elif pc1 == 3: out.append((pc0, 4 if turn != 1 else 2, f0, f1, turn))
        elif pc1 == 4: out.append((pc0, 5, f0, 0, turn))
        elif pc1 == 5 and turn == 1: out.append((pc0, 6, f0, f1, turn))
        elif pc1 == 6: out.append((pc0, 2, f0, 1, turn))
        elif pc1 == 7: out.append((pc0, 8, f0, f1, turn))
        elif pc1 == 8: out.append((pc0, 9, f0, f1, 0))
        elif pc1 == 9: out.append((pc0, 0, f0, 0, turn))
        return out
    r5 = bfs_model_check("Dekker v5 (Correct Final)", (0, 0, 0, 0, 0), step_v5, lambda s: (s[0] == 7, s[1] == 7))
    r5["defect"] = "NONE — Verified safe under Sequential Consistency"
    results.append(r5)
    return results


def check_peterson_sem_mon() -> List[Dict]:
    out = []

    # 1) Peterson under Sequential Consistency (SC)
    # pc: 0=nc, 1=set_flag, 2=set_turn_other, 3=spin(while flag[other] and turn==other), 4=cs, 5=clear_flag
    def step_pet_sc(s):
        pc0, pc1, f0, f1, turn = s
        nxt = []
        if pc0 == 0: nxt.append((1, pc1, f0, f1, turn))
        elif pc0 == 1: nxt.append((2, pc1, 1, f1, turn))
        elif pc0 == 2: nxt.append((3, pc1, f0, f1, 1))
        elif pc0 == 3 and not (f1 and turn == 1): nxt.append((4, pc1, f0, f1, turn))
        elif pc0 == 4: nxt.append((5, pc1, f0, f1, turn))
        elif pc0 == 5: nxt.append((0, pc1, 0, f1, turn))

        if pc1 == 0: nxt.append((pc0, 1, f0, f1, turn))
        elif pc1 == 1: nxt.append((pc0, 2, f0, 1, turn))
        elif pc1 == 2: nxt.append((pc0, 3, f0, f1, 0))
        elif pc1 == 3 and not (f0 and turn == 0): nxt.append((pc0, 4, f0, f1, turn))
        elif pc1 == 4: nxt.append((pc0, 5, f0, f1, turn))
        elif pc1 == 5: nxt.append((pc0, 0, f0, 0, turn))
        return nxt
    rp_sc = bfs_model_check("Peterson (Sequential Consistency)", (0, 0, 0, 0, 0), step_pet_sc, lambda s: (s[0] == 4, s[1] == 4))
    rp_sc["defect"] = "NONE — Minimal 2-write SC mutual exclusion"
    out.append(rp_sc)

    # 2) Peterson under x86 TSO Store-Buffer Reordering (flag write buffered until after read of other's flag)
    # State: (pc0, pc1, mem_f0, mem_f1, buf_f0, buf_f1, turn)
    # pc: 0=nc, 1=buffer_f_true, 2=set_turn_other, 3=read_check, 4=cs, 5=clear_flag
    # Plus async store-buffer drain transitions whenever buf_f_i == 1 -> mem_f_i = 1
    def step_pet_tso(s):
        pc0, pc1, mf0, mf1, bf0, bf1, turn = s
        nxt = []
        # Store buffer flush transitions (CPU drains buffered store to coherent memory)
        if bf0: nxt.append((pc0, pc1, 1, mf1, 0, bf1, turn))
        if bf1: nxt.append((pc0, pc1, mf0, 1, bf0, 0, turn))
        # P0 instructions (sees own write or buffered write, reads mf1 for other)
        if pc0 == 0: nxt.append((1, pc1, mf0, mf1, bf0, bf1, turn))
        elif pc0 == 1: nxt.append((2, pc1, mf0, mf1, 1, bf1, turn))
        elif pc0 == 2: nxt.append((3, pc1, mf0, mf1, bf0, bf1, 1))
        elif pc0 == 3 and not (mf1 and turn == 1): nxt.append((4, pc1, mf0, mf1, bf0, bf1, turn))
        elif pc0 == 4: nxt.append((5, pc1, mf0, mf1, bf0, bf1, turn))
        elif pc0 == 5 and bf0 == 0: nxt.append((0, pc1, 0, mf1, 0, bf1, turn))
        # P1 instructions
        if pc1 == 0: nxt.append((pc0, 1, mf0, mf1, bf0, bf1, turn))
        elif pc1 == 1: nxt.append((pc0, 2, mf0, mf1, bf0, 1, turn))
        elif pc1 == 2: nxt.append((pc0, 3, mf0, mf1, bf0, bf1, 0))
        elif pc1 == 3 and not (mf0 and turn == 0): nxt.append((pc0, 4, mf0, mf1, bf0, bf1, turn))
        elif pc1 == 4: nxt.append((pc0, 5, mf0, mf1, bf0, bf1, turn))
        elif pc1 == 5 and bf1 == 0: nxt.append((pc0, 0, mf0, 0, bf0, 0, turn))
        return nxt
    rp_tso = bfs_model_check("Peterson (TSO Store Buffer, No Fence)", (0, 0, 0, 0, 0, 0, 0), step_pet_tso, lambda s: (s[0] == 4, s[1] == 4))
    rp_tso["defect"] = "TSO reordering lets buffered flag[i]=True lag behind read of flag[j], breaking CS!"
    out.append(rp_tso)

    # 3) Binary Semaphore (Correct P -> CS -> V)
    # State: (pc0, pc1, sem): 0=nc, 1=wait(P), 2=cs, 3=signal(V)
    def step_sem(s):
        pc0, pc1, sem = s
        nxt = []
        if pc0 == 0: nxt.append((1, pc1, sem))
        elif pc0 == 1 and sem > 0: nxt.append((2, pc1, sem - 1))
        elif pc0 == 2: nxt.append((3, pc1, sem))
        elif pc0 == 3: nxt.append((0, pc1, sem + 1))
        if pc1 == 0: nxt.append((pc0, 1, sem))
        elif pc1 == 1 and sem > 0: nxt.append((pc0, 2, sem - 1))
        elif pc1 == 2: nxt.append((pc0, 3, sem))
        elif pc1 == 3: nxt.append((pc0, 0, sem + 1))
        return nxt
    r_sem = bfs_model_check("Binary Semaphore (P/V Correct)", (0, 0, 1), step_sem, lambda s: (s[0] == 2, s[1] == 2))
    r_sem["defect"] = "NONE — Atomic P/V protects CS with zero busy-wait transitions"
    out.append(r_sem)

    # 4) Monitor Mesa-style with 'if' bug vs 'while' fix (2 consumers + 1 producer abstract model, buf in {0,1})
    # State: (c0, c1, p, buf, cond_wake0, cond_wake1): c_i: 0=idle,1=if_check,2=wait,3=woken_consume(buggy no recheck!),4=done;
    # If using 'if' in Mesa: waiter resumes directly at 3 even if other consumer stole item (buf==0 -> underflow violation!)
    def step_mesa_if(s):
        c0, c1, buf, prod_ready = s
        nxt = []
        # Producer fills buf if empty
        if buf == 0:
            nxt.append((c0, c1, 1, 0))
        # c0: 0=enter_check, 1=waiting, 2=woken_blindly(Mesa if), 3=consume
        if c0 == 0:
            nxt.append((3 if buf > 0 else 1, c1, buf, prod_ready))
        elif c0 == 1 and buf > 0:
            # Signal can wake c0, AND c1 might still run before c0!
            nxt.append((2, c1, buf, prod_ready))
        elif c0 == 2:
            nxt.append((3, c1, buf, prod_ready))
        elif c0 == 3:
            if buf > 0:
                nxt.append((0, c1, buf - 1, prod_ready))
            else:
                # Buffer underflow state (pc=99 sentinel)!
                nxt.append((99, c1, buf, prod_ready))
        # c1 symmetric
        if c1 == 0:
            nxt.append((c0, 3 if buf > 0 else 1, buf, prod_ready))
        elif c1 == 1 and buf > 0:
            nxt.append((c0, 2, buf, prod_ready))
        elif c1 == 2:
            nxt.append((c0, 3, buf, prod_ready))
        elif c1 == 3:
            if buf > 0:
                nxt.append((c0, 0, buf - 1, prod_ready))
            else:
                nxt.append((c0, 99, buf, prod_ready))
        return nxt
    r_mesa_if = bfs_model_check("Monitor (Mesa 'if' Bug)", (0, 0, 0, 0), step_mesa_if, lambda s: (s[0] == 99, True))
    r_mesa_if["defect"] = "Steal-lock / spurious wake lets consumer proceed on empty buffer (pc=99)"
    out.append(r_mesa_if)

    def step_mesa_while(s):
        c0, c1, buf, prod_ready = s
        nxt = []
        if buf == 0:
            nxt.append((c0, c1, 1, 0))
        if c0 == 0:
            nxt.append((3 if buf > 0 else 1, c1, buf, prod_ready))
        elif c0 == 1 and buf > 0:
            nxt.append((0, c1, buf, prod_ready))  # loops back to re-check while(buf==0)!
        elif c0 == 3 and buf > 0:
            nxt.append((0, c1, buf - 1, prod_ready))
        if c1 == 0:
            nxt.append((c0, 3 if buf > 0 else 1, buf, prod_ready))
        elif c1 == 1 and buf > 0:
            nxt.append((c0, 0, buf, prod_ready))
        elif c1 == 3 and buf > 0:
            nxt.append((c0, 0, buf - 1, prod_ready))
        return nxt
    r_mesa_wh = bfs_model_check("Monitor (Mesa 'while' Guard)", (0, 0, 0, 0), step_mesa_while, lambda s: (s[0] == 99, True))
    r_mesa_wh["defect"] = "NONE — Condition re-check prevents buffer underflow"
    out.append(r_mesa_wh)

    return out


# =============================================================================
# PART 2: LIVE MULTI-THREADED OS BENCHMARKS
# =============================================================================
def run_lock_bench(lock_factory, n_threads: int, iters_per_thread: int, work_loop: int, hold_sleep_s: float = 0.0) -> Dict:
    lock = lock_factory()
    shared_counter = [0]
    spins_total = [0]
    barrier = threading.Barrier(n_threads)

    def worker(tid: int) -> None:
        local_spins = 0
        barrier.wait()
        for _ in range(iters_per_thread):
            local_spins += lock.acquire(tid)
            # Critical Section
            v = shared_counter[0]
            acc = 0
            for k in range(work_loop):
                acc += k & 3
            if hold_sleep_s > 0:
                time.sleep(hold_sleep_s)
            shared_counter[0] = v + 1 + (acc & 0)
            lock.release(tid)
        spins_total[0] += local_spins

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    t_wall0 = time.perf_counter()
    t_cpu0 = time.process_time()
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    t_cpu1 = time.process_time()
    t_wall1 = time.perf_counter()

    expected = n_threads * iters_per_thread
    assert shared_counter[0] == expected, f"Lost update! got {shared_counter[0]} != {expected}"
    wall_ms = (t_wall1 - t_wall0) * 1000.0
    cpu_ms = (t_cpu1 - t_cpu0) * 1000.0
    ops_sec = expected / max(t_wall1 - t_wall0, 1e-9)
    return {
        "n_threads": n_threads,
        "total_ops": expected,
        "lost_updates": expected - shared_counter[0],
        "wall_ms": round(wall_ms, 2),
        "cpu_ms": round(cpu_ms, 2),
        "cpu_to_wall_ratio": round(cpu_ms / max(wall_ms, 1e-6), 3),
        "throughput_ops_s": round(ops_sec, 1),
        "yield_spins": spins_total[0],
    }


def main() -> None:
    dekker_fsm = check_dekker_variants()
    pet_sem_mon_fsm = check_peterson_sem_mon()

    # Benchmark Suite 1: 2-Thread Contention across CS Workloads
    cs_sweep = []
    # For real busy-wait CPU contrast vs yield(0): use true active spin check (pass lambda: None for short spin)
    # Actually time.sleep(0) yields GIL cleanly in Python while active counter loop burns real CPU!
    def spin_yield():
        pass  # pure busy-wait CPU burn (note: Python GIL switches every sys.getswitchinterval()=5ms unless short loop)

    for work_label, wloop, iters in [("Light (CS=0)", 0, 2500), ("Medium (CS=150)", 150, 2000), ("Heavy (CS=600)", 600, 400)]:
        for pname, fac in [
            ("Dekker (Busy-Wait)", lambda: DekkerLock(yield_fn=lambda: None)),
            ("Dekker (Yield)", lambda: DekkerLock(yield_fn=lambda: time.sleep(0))),
            ("Peterson (Busy-Wait)", lambda: PetersonLock(yield_fn=lambda: None)),
            ("Peterson (Yield)", lambda: PetersonLock(yield_fn=lambda: time.sleep(0))),
            ("Semaphore (Blocking)", BinarySemaphoreLock),
            ("Monitor (Mesa Cond)", MesaMonitorLock),
        ]:
            res = run_lock_bench(fac, n_threads=2, iters_per_thread=iters, work_loop=wloop)
            res["workload"] = work_label
            res["work_loop"] = wloop
            res["primitive"] = pname
            cs_sweep.append(res)

    # Benchmark Suite 2: Thread Scaling (N = 2, 4, 8)
    scaling = []
    for n_th, iters in [(2, 1200), (4, 800), (8, 400)]:
        for pname, fac in [
            ("Filter Lock (N-Peterson)", lambda n=n_th: FilterLock(n, yield_fn=lambda: time.sleep(0))),
            ("Tournament Dekker (Tree)", lambda n=n_th: TournamentDekkerLock(n, yield_fn=lambda: time.sleep(0))),
            ("Semaphore (Blocking)", BinarySemaphoreLock),
            ("Monitor (Mesa Cond)", MesaMonitorLock),
        ]:
            res = run_lock_bench(fac, n_threads=n_th, iters_per_thread=iters, work_loop=20)
            res["primitive"] = pname
            scaling.append(res)

    # Benchmark Suite 3: Lock-Holder I/O or Preemption Delay (CPU Burn Test)
    hold_audit = []
    for hold_ms in [2, 5, 10]:
        for pname, fac in [
            ("Dekker (Busy-Wait)", lambda: DekkerLock(yield_fn=lambda: None)),
            ("Peterson (Busy-Wait)", lambda: PetersonLock(yield_fn=lambda: None)),
            ("Semaphore (Blocking)", BinarySemaphoreLock),
            ("Monitor (Mesa Cond)", MesaMonitorLock),
        ]:
            res = run_lock_bench(fac, n_threads=2, iters_per_thread=10, work_loop=0, hold_sleep_s=hold_ms / 1000.0)
            res["hold_ms"] = hold_ms
            res["primitive"] = pname
            hold_audit.append(res)

    # Benchmark Suite 4: Bounded-Buffer Producer-Consumer (Condition Sync vs Spin Guard)
    def run_bb_bench(mode: str, n_items: int = 1200, cap: int = 8) -> Dict:
        buf: deque = deque()
        produced = [0]
        consumed = [0]
        retries = [0]

        if mode == "Semaphore (empty/full/mutex)":
            empty = threading.Semaphore(cap)
            full = threading.Semaphore(0)
            mtx = threading.Semaphore(1)

            def prod():
                for i in range(n_items):
                    empty.acquire()
                    mtx.acquire()
                    buf.append(i)
                    produced[0] += 1
                    mtx.release()
                    full.release()

            def cons():
                for _ in range(n_items):
                    full.acquire()
                    mtx.acquire()
                    buf.popleft()
                    consumed[0] += 1
                    mtx.release()
                    empty.release()

        elif mode == "Monitor (Mesa Condition)":
            cv = threading.Condition()

            def prod():
                for i in range(n_items):
                    with cv:
                        while len(buf) == cap:
                            retries[0] += 1
                            cv.wait()
                        buf.append(i)
                        produced[0] += 1
                        cv.notify_all()

            def cons():
                for _ in range(n_items):
                    with cv:
                        while len(buf) == 0:
                            retries[0] += 1
                            cv.wait()
                        buf.popleft()
                        consumed[0] += 1
                        cv.notify_all()

        else:  # Peterson lock + busy-wait polling for full/empty condition
            lk = PetersonLock(yield_fn=lambda: time.sleep(0))

            def prod():
                i = 0
                while i < n_items:
                    lk.acquire(0)
                    if len(buf) < cap:
                        buf.append(i)
                        produced[0] += 1
                        i += 1
                        lk.release(0)
                    else:
                        retries[0] += 1
                        lk.release(0)
                        time.sleep(0)

            def cons():
                i = 0
                while i < n_items:
                    lk.acquire(1)
                    if len(buf) > 0:
                        buf.popleft()
                        consumed[0] += 1
                        i += 1
                        lk.release(1)
                    else:
                        retries[0] += 1
                        lk.release(1)
                        time.sleep(0)

        t_p = threading.Thread(target=prod)
        t_c = threading.Thread(target=cons)
        tw0, tc0 = time.perf_counter(), time.process_time()
        t_p.start()
        t_c.start()
        t_p.join()
        t_c.join()
        tc1, tw1 = time.process_time(), time.perf_counter()
        assert produced[0] == n_items and consumed[0] == n_items and len(buf) == 0
        return {
            "mode": mode,
            "items": n_items,
            "capacity": cap,
            "wall_ms": round((tw1 - tw0) * 1000.0, 2),
            "cpu_ms": round((tc1 - tc0) * 1000.0, 2),
            "cond_waits_or_spin_retries": retries[0],
            "ops_per_s": round(n_items / max(tw1 - tw0, 1e-9), 1),
        }

    bb_bench = [
        run_bb_bench("Semaphore (empty/full/mutex)"),
        run_bb_bench("Monitor (Mesa Condition)"),
        run_bb_bench("Peterson (Lock + Spin Poll)"),
    ]

    # Hoare vs Mesa structural table
    monitor_semantics = HoareMonitorQueueSim.compare_semantics()

    payload = {
        "exercise": "exercise-4",
        "topic": "Comprehensive Comparison of Dekker, Peterson, Semaphore, and Monitor",
        "dekker_evolution_fsm": dekker_fsm,
        "all_primitives_fsm": pet_sem_mon_fsm,
        "cs_work_sweep_n2": cs_sweep,
        "thread_scaling": scaling,
        "lock_holder_sleep_audit": hold_audit,
        "bounded_buffer_bench": bb_bench,
        "monitor_semantics": monitor_semantics,
    }
    out_path = os.path.join(OUT_DIR, "experiments.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print("Wrote", out_path)
    print("  FSM audits:", len(dekker_fsm) + len(pet_sem_mon_fsm))
    print("  N=2 sweep rows:", len(cs_sweep), "| Scaling rows:", len(scaling), "| Hold audit rows:", len(hold_audit))


if __name__ == "__main__":
    main()
