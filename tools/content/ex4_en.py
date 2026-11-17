"""Exercise 4 English Comprehensive Comparative Monograph (40+ dense pages):
Dekker, Peterson, Semaphore, and Monitor — State-Space Verification, Hardware Memory
Ordering, OS Threading Benchmarks, Energy/CPU Burn, and Systems Architecture.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, HERE)

import report_kit as rk  # noqa: E402
import ex4_data as ed  # noqa: E402


def build() -> rk.Report:
    d = ed.load()
    dfsm = {r["model"]: r for r in d["dekker_evolution_fsm"]}
    pfsm = {r["model"]: r for r in d["all_primitives_fsm"]}
    mesa_if = pfsm["Monitor (Mesa 'if' Bug)"]
    mesa_wh = pfsm["Monitor (Mesa 'while' Guard)"]
    hold10 = {r["primitive"]: r for r in d["lock_holder_sleep_audit"] if r["hold_ms"] == 10}
    sc8 = {r["primitive"]: r for r in d["thread_scaling"] if r["n_threads"] == 8}
    bb = {r["mode"]: r for r in d["bounded_buffer_bench"]}
    fig_dir = os.path.join(REPO_ROOT, "exercise-4", "diagrams")

    rep = rk.Report(
        title="Exercise 4: Comprehensive Comparative Study of Dekker, Peterson, Semaphore, and Monitor",
        subtitle="Formal BFS Model Checking, Hardware Memory Barriers (SC vs. x86 TSO), OS Threading Contention, CPU Busy-Wait Burn, Multi-Thread Scalability & Kernel Synchronization Architecture (40+ Pages)",
        lang="en",
        rtl=False,
        cover_meta=[
            ("Repository", "ZaraNodehi/Guaranteed-Scheduling"),
            ("Deliverable", "Exercise 4 — All-Angles Comparison: Dekker vs. Peterson vs. Semaphore vs. Monitor"),
            ("Primitives Evaluated", "Dekker (v1-v5, Tournament Tree), Peterson (2T, Filter Lock, TSO), Semaphore, Monitor (Hoare & Mesa)"),
            ("Verification Standard", "Exhaustive BFS State-Space Model Checker + Live OS POSIX/Threading Benchmarks"),
        ],
    )

    rep.page(rk.cover(rep.cover_meta))
    rep.page(rk.toc())

    blocks = [
        # =====================================================================
        # CHAPTER 1
        # =====================================================================
        rk.ptitle("1. Executive Synthesis: Four Milestones in Operating System Synchronization"),
        rk.para(
            "Concurrent threads sharing mutable memory require deterministic coordination to prevent lost updates, "
            "torn reads, deadlocks, and unbounded starvation. Over five decades of operating systems research, four "
            "foundational abstractions shaped how engineers solve the Critical Section (CS) and Condition "
            "Synchronization problems: (1) Dekker's Algorithm (1962), the first mathematically proven pure-software "
            "two-process mutual exclusion protocol; (2) Peterson's Algorithm (1981), which distilled Dekker's nested "
            "branching into three symmetric lines of code; (3) Dijkstra's Semaphore (1965), which elevated "
            "synchronization from spinning user variables to kernel-assisted wait/signal queues; and (4) Brinch "
            "Hansen & Hoare's Monitor (1974), which encapsulated shared state, mutual exclusion, and condition "
            "variables inside a structured programming abstraction."
        ),
        rk.para(
            "Students frequently learn these four primitives as isolated textbook recipes without measuring how "
            "dramatically they diverge across hardware memory models, multi-core scaling, lock-holder preemption, "
            "CPU energy efficiency, and software bug surfaces. Exercise 4 closes that gap with a two-tier "
            "verification pipeline: an exact Breadth-First Search (BFS) explicit-state model checker across all 10 "
            "correct and defective variants, paired with live OS multi-threaded benchmarks capturing real wall-clock "
            "latency, process CPU burn (time.process_time), throughput scaling up to N = 8 threads, and bounded-buffer "
            "condition synchronization."
        ),
        rk.kv([
            ("Dekker v5 vs. Peterson (SC)", f"Peterson shrinks reachable BFS states 3.2x ({dfsm['Dekker v5 (Correct Final)']['reachable_states']} -> {pfsm['Peterson (Sequential Consistency)']['reachable_states']} states) with 0 mutex/deadlock errors"),
            ("Modern CPU Memory Reordering", f"Without memory barriers (x86 TSO store buffer), Peterson fails in {pfsm['Peterson (TSO Store Buffer, No Fence)']['mutex_violations']} reachable states out of {pfsm['Peterson (TSO Store Buffer, No Fence)']['reachable_states']}"),
            ("Mesa Monitor Guard Rule", f"Using 'if' instead of 'while' in Mesa monitors leaks {mesa_if['mutex_violations']} buffer-underflow states; 'while' restores 0 errors"),
            ("CPU Burn on 10ms Hold Delay", f"Peterson/Dekker burn {hold10['Peterson (Busy-Wait)']['cpu_ms']:.1f} / {hold10['Dekker (Busy-Wait)']['cpu_ms']:.1f} ms CPU ({hold10['Peterson (Busy-Wait)']['cpu_to_wall_ratio']*100:.1f}% core) vs. {hold10['Semaphore (Blocking)']['cpu_ms']:.1f} ms for Semaphore (~195x less CPU!)"),
            ("N=8 Contention Scaling", f"Monitor ({sc8['Monitor (Mesa Cond)']['throughput_ops_s']:,.0f} ops/s) and Tournament Dekker ({sc8['Tournament Dekker (Tree)']['throughput_ops_s']:,.0f} ops/s) outscale O(N) Filter Lock ({sc8['Filter Lock (N-Peterson)']['throughput_ops_s']:,.0f} ops/s)"),
        ]),
        rk.table(
            ["Synchronization Mechanism", "Year", "Layer / Backing", "Wait Behavior", "Multi-Thread Scaling", "Primary Failure Mode"],
            [
                ["Dekker's Algorithm (v5)", "1962", "Pure Shared Memory", "Busy-Wait Spin", "2T native; O(log N) tree", "Store-buffer reordering; spin burn"],
                ["Peterson's Algorithm", "1981", "Pure Shared Memory", "Busy-Wait Spin", "2T native; O(N) Filter Lock", "Store-buffer reordering; O(N) levels"],
                ["Semaphore (P/V)", "1965", "OS Kernel / Futex", "Sleep Queue (Blocking)", "O(1) per op, arbitrary N", "Misordered P/V deadlock; priority inv."],
                ["Monitor (Hoare / Mesa)", "1974", "Language + Condvar", "Sleep Queue (Blocking)", "O(1) per op, arbitrary N", "Using 'if' instead of 'while' in Mesa"],
            ],
            widths=[3.2, 1.2, 2.8, 2.8, 3.2, 4.0],
            caption="High-level architectural taxonomy of the four synchronization primitives compared in Exercise 4.",
        ),

        # =====================================================================
        # CHAPTER 2
        # =====================================================================
        rk.ptitle("2. Formal Problem Statement: Dijkstra's Criteria & Memory Consistency"),
        rk.para(
            "A critical section protocol is valid if and only if it simultaneously satisfies three non-negotiable "
            "correctness properties defined by Edsger W. Dijkstra (1965) across every possible interleaving schedule "
            "generated by an adversarial OS scheduler:"
        ),
        rk.bullets([
            "1. Mutual Exclusion (Safety): At any discrete point in global execution, at most one thread resides inside its critical section: !(in_CS_0 AND in_CS_1) across all reachable states.",
            "2. Progress (Deadlock Freedom / Liveness): If no thread is executing in its critical section and one or more threads wish to enter, only threads not in their remainder sections participate in deciding who enters next, and this selection cannot be postponed indefinitely.",
            "3. Bounded Waiting (Starvation Freedom): After thread T_i issues a request to enter its critical section, there exists a finite upper bound B on the number of times competing threads can enter CS before T_i is granted entry (for Dekker v5 and Peterson, B = 1 turn!).",
        ]),
        rk.h1("2.1 Why Hardware Memory Consistency Changes Everything"),
        rk.para(
            "Classical proofs of Dekker and Peterson implicitly assume Sequential Consistency (SC)—meaning every read "
            "and write takes effect immediately in a single global memory order matching program order. Real modern "
            "CPUs violate SC for performance: x86-64 implements Total Store Ordering (TSO), buffering writes into a "
            "per-core FIFO Store Buffer before draining them to coherent L1 cache, while ARMv8 and RISC-V implement "
            "Weak/Relaxed Ordering that may reorder independent loads and stores across cores. Consequently, store-load "
            "reordering ('write flag[i]=True' buffered locally while 'read flag[j]' executes early against RAM) "
            "breaks pure-software locks unless an explicit hardware memory fence (MFENCE, DMB ISH, or C11 seq_cst) "
            "flushes the store buffer before the remote flag load."
        ),
        rk.formula(
            "Safety Invariant:  G !(pc_0 == CS  &&  pc_1 == CS)     [Must hold on ALL reachable states]\n"
            "Liveness Property: G (request_i  ==>  F in_CS_i)         [Bounded bypass B <= 1 for 2 threads]\n"
            "Store-Load Hazard: Store(flag[i]=1) -> StoreBuf  ||  Load(flag[j]) -> L1 Cache  [Breaks w/o MFENCE]"
        ),

        # =====================================================================
        # CHAPTER 3
        # =====================================================================
        rk.ptitle("3. Dekker's Algorithm (1962): Full 5-Stage Evolution & State-Space Proof"),
        rk.para(
            "The easiest way to understand why Dekker's final algorithm requires both flag[0..1] and a shared turn "
            "variable is to trace the four failed historical attempts before arriving at Version 5. Our BFS model "
            "checker encodes each variant as a finite-state transition system and explores every single reachable "
            "interleaving exhaustively."
        ),
        rk.image("ex4_fig6_dekker_evolution_fsm.png", width_cm=16.8,
                 caption="Evolution of Dekker's algorithm from failed variants v1-v4 to complete v5 and Peterson's 1981 unification."),
        rk.table(
            ["Variant", "States", "Edges", "BFS Depth", "Mutex Err", "Deadlocks", "Spin Cycles", "Verdict"],
            ed.fsm_rows(d["dekker_evolution_fsm"]),
            widths=[4.2, 1.3, 1.3, 1.5, 1.5, 1.5, 1.7, 2.2],
            caption="Exhaustive BFS model-checker results across all five historical Dekker variants.",
        ),
        rk.h1("3.1 Dissecting Each Historical Failure Mode"),
        rk.bullets([
            f"Dekker v1 (Strict Alternation, {dfsm['Dekker v1 (Strict Alternation)']['reachable_states']} states): Preserves mutual exclusion (0 CS violations) and zero deadlock in tight loops, but binds progress rigidly to the other thread. If P0 remains outside its CS indefinitely with turn == 0, P1 stalls permanently after one turn.",
            f"Dekker v2 (Check-Then-Set, {dfsm['Dekker v2 (Check-Then-Set)']['reachable_states']} states): P0 checks !flag[1], gets preempted before setting flag[0]=True; P1 checks !flag[0], sets flag[1]=True, and both enter CS! Our BFS catches {dfsm['Dekker v2 (Check-Then-Set)']['mutex_violations']} exact dual-CS violation state.",
            f"Dekker v3 (Set-Then-Wait, {dfsm['Dekker v3 (Set-Then-Wait)']['reachable_states']} states): Setting flag[i]=True first eliminates the race, yet if both set their flags simultaneously before testing, both spin forever waiting for the other to clear—producing {dfsm['Dekker v3 (Set-Then-Wait)']['deadlock_states']} terminal deadlock state.",
            f"Dekker v4 (Symmetric Backoff, {dfsm['Dekker v4 (Symmetric Backoff)']['reachable_states']} states): Temporarily dropping flag[i]=False resolves deadlocks, but symmetric timing creates {dfsm['Dekker v4 (Symmetric Backoff)']['non_cs_spin_back_edges']} non-CS spin back-edges where both threads yield and re-enter in lockstep forever (livelock).",
            f"Dekker v5 (Complete Correct Form, {dfsm['Dekker v5 (Correct Final)']['reachable_states']} states): Combines intent flags with a polite tie-breaking turn variable: on contention, only the thread without turn backs down (flag[i]=False; while turn != i: spin; flag[i]=True), while the thread holding turn retains its raised flag. On CS exit, turn is ceded to 1 - i, capping bypass at B = 1.",
        ]),
        rk.h1("3.2 Dekker v5 Proof Sketch (Mutual Exclusion & Bounded Waiting)"),
        rk.para(
            "Mutual exclusion holds because a thread enters CS only after observing flag[other] == False while its "
            "own flag[i] == True remains continuously raised. Since the backoff branch only drops flag[i] inside "
            "the turn != i guard, the flag[i] == True invariant holds from the final check of flag[other] through CS "
            "completion. Bounded waiting holds because once P1 exits CS, it unconditionally writes turn = 0 and clears "
            "flag[1] = False; if P0 is waiting in the backoff loop, turn == 0 releases it immediately and gives P0 "
            "priority if P1 attempts to re-enter."
        ),

        # =====================================================================
        # CHAPTER 4
        # =====================================================================
        rk.ptitle("4. Peterson's Algorithm (1981) & N-Thread Filter / Tournament Locks"),
        rk.para(
            "Nineteen years after Dekker, Gary Peterson demonstrated that explicit backoff branches are completely "
            "unnecessary. By setting flag[i] = True AND immediately ceding priority via turn = other ('After you!'), "
            "the last thread to execute turn = other traps itself in the spin loop while letting the earlier contender "
            "proceed straight into CS. Under Sequential Consistency, our BFS verifies Peterson across just "
            f"{pfsm['Peterson (Sequential Consistency)']['reachable_states']} reachable states (compared to "
            f"{dfsm['Dekker v5 (Correct Final)']['reachable_states']} for Dekker v5 — a 3.2x smaller state space!) "
            "with zero mutex errors and zero deadlocks."
        ),
        rk.h1("4.1 Exact Safety & Progress Proof of Peterson's Lock"),
        rk.para(
            "Suppose both Thread 0 and Thread 1 reside inside CS simultaneously. Thread 0 observed (flag[1] == False "
            "OR turn == 0) after writing flag[0] = True and turn = 1; Thread 1 observed (flag[0] == False OR "
            "turn == 1) after writing flag[1] = True and turn = 0. Because neither thread clears flag[i] until exiting "
            "CS, both must have passed their while-guard due to turn. However, turn is a single scalar variable holding "
            "either 0 or 1—never both simultaneously! The thread whose write to turn executed second overwrote turn "
            "with the opponent's ID and could not have exited its loop until the opponent exited CS—a direct contradiction."
        ),
        rk.h1("4.2 Scaling Beyond 2 Threads: Filter Lock vs. Tournament Dekker Tree"),
        rk.para(
            "Neither native Dekker nor native Peterson directly supports N > 2 threads. Two classical generalizations "
            "solve N-thread pure-software exclusion with dramatically different asymptotic behavior:"
        ),
        rk.bullets([
            "Filter Lock (Generalization of Peterson, O(N) contention levels): Threads climb N - 1 waiting rooms level[i] = 1..N-1; at each level L, at most N - L threads may pass because victim[L] traps the last arriver. Each thread pays O(N) atomic scans per acquire—causing cache-line bouncing and steep throughput degradation at N = 8.",
            "Tournament Dekker / Peterson Binary Tree (O(log N) contention depth): Organizes N = 2^k threads as leaves of a complete binary tree of 2-thread locks. Each acquire traverses only log2(N) nodes (3 hops for N = 8!), isolating spin traffic to disjoint pairs and scaling closely alongside kernel locks.",
        ]),
        rk.code(ed.code_slice("exercise-4/code/sync_primitives.py", 50, 84),
                caption="Executable PetersonLock and N-thread FilterLock implementations (sync_primitives.py, lines 50-84)."),
        rk.code(ed.code_slice("exercise-4/code/sync_primitives.py", 87, 118),
                caption="Binary TournamentDekkerLock composing 2-thread locks for O(log N) scaling (lines 87-118)."),

        # =====================================================================
        # CHAPTER 5
        # =====================================================================
        rk.ptitle("5. Hardware Memory Barriers & Store-Buffer Failures on Modern CPUs"),
        rk.para(
            "A critical real-world lesson omitted in introductory courses is why raw Dekker and Peterson fail "
            "catastrophically when compiled without memory barriers on modern superscalar processors (x86-64, ARM64, "
            "Apple Silicon, RISC-V). Even when variables are declared volatile in C/C++ (which only suppresses "
            "compiler register caching), CPU store buffers delay propagating flag[i] = True to shared L1/L3 memory "
            "while allowing the subsequent read of flag[j] to bypass ahead and hit coherent cache immediately."
        ),
        rk.image("ex4_fig7_memory_fence_tso.png", width_cm=16.8,
                 caption="Hardware TSO store-buffer race breaking Peterson & Dekker without MFENCE/DMB barriers."),
        rk.para(
            f"To verify this rigorously rather than merely asserting it, our BFS model checker explicitly modeled an "
            f"x86 Total Store Ordering (TSO) store buffer holding uncommitted flag[i] writes prior to memory drain. "
            f"Reachable states expanded nearly 5x from {pfsm['Peterson (Sequential Consistency)']['reachable_states']} "
            f"to {pfsm['Peterson (TSO Store Buffer, No Fence)']['reachable_states']}, exposing exactly "
            f"{pfsm['Peterson (TSO Store Buffer, No Fence)']['mutex_violations']} reachable states where BOTH Core 0 "
            "and Core 1 enter the critical section simultaneously! Inserting a full memory fence (x86 MFENCE / LOCK "
            "XCHG, ARM64 DMB ISH, or C++11 memory_order_seq_cst) drains the store buffer before loading flag[j], "
            "restoring Sequential Consistency at the cost of ~15-40 CPU cycles per barrier."
        ),
        rk.note(
            "Note on Python Execution: CPython serializes bytecode execution via the Global Interpreter Lock (GIL), "
            "which acts as an accidental sequential-consistency fence between Python bytecode boundaries. In C, C++, "
            "Rust, or bare-metal kernel code running across multiple physical cores, omitting atomic seq_cst fences "
            "causes silent data corruption under high contention."
        ),

        # =====================================================================
        # CHAPTER 6
        # =====================================================================
        rk.ptitle("6. Dijkstra's Semaphore (1965): Blocking Queues & Misuse Hazards"),
        rk.para(
            "Whereas Dekker and Peterson trap waiting threads in CPU-burning spin loops inside user space, Dijkstra's "
            "Semaphore S = (count, wait_queue) delegates waiting to the OS scheduler or kernel futex subsystem. "
            "Two indivisible primitives govern S: P(S) (wait/acquire) decrements count and, if negative or zero "
            "prior to decrement, suspends the calling thread in a kernel sleep queue (yielding 100% of its CPU time "
            "to other runnable work); V(S) (signal/release) increments count and wakes one sleeping waiter."
        ),
        rk.table(
            ["Property", "Binary Semaphore (Mutex Usage)", "Counting Semaphore (Resource Pool)", "Kernel Implementation (Linux / POSIX)"],
            [
                ["Initial Value", "S = 1 (one token)", "S = K (K buffer slots / permits)", "sem_init(&s, 0, K) or futex(2) word"],
                ["State Space (2T)", f"{pfsm['Binary Semaphore (P/V Correct)']['reachable_states']} states (0 spin edges!)", "O(K * N) compact queue states", "Atomic CAS fast path + sleep queue slow path"],
                ["Wait Overhead", "0 syscalls if uncontended (futex)", "Sleeps in TASK_INTERRUPTIBLE", "~1-5 us context hop when sleeping"],
                ["Classic Failure", "Swapped V()/P() breaks CS; missing V() deadlocks", "Negative count leak / signal mismatch", "No ownership check (any thread may V())"],
            ],
            widths=[2.8, 4.4, 4.6, 5.4],
            caption="Structural summary of Binary vs. Counting Semaphores and Linux/POSIX implementation details.",
        ),
        rk.h1("6.1 Why Semaphores Remain Notoriously Error-Prone in Large Systems"),
        rk.para(
            "Despite eliminating busy-wait CPU waste, raw semaphores scatter synchronization logic across arbitrary "
            "control paths without enforcing lexical scoping or ownership. Any thread can call V(S) even if it never "
            "called P(S); forgetting a single V(S) on an early error return causes permanent deadlock; and reversing "
            "P(empty); P(mutex) into P(mutex); P(empty) inside Producer-Consumer creates an immediate circular deadlock. "
            "These software-engineering hazards motivated Brinch Hansen and Hoare to invent Monitors."
        ),

        # =====================================================================
        # CHAPTER 7
        # =====================================================================
        rk.ptitle("7. Monitors (Hoare 1974 vs. Mesa): Encapsulation & Spurious Wakeups"),
        rk.para(
            "A Monitor binds shared data structures, initialization, and synchronized procedures behind a single "
            "mutual-exclusion boundary (implicit lock acquisition on entry, implicit release on exit), supplemented "
            "by one or more Condition Variables supporting wait(), notify()/signal(), and notify_all()/broadcast(). "
            "Crucially, two subtly different signaling semantics govern real-world monitors:"
        ),
        rk.image("ex4_fig8_hoare_vs_mesa_monitor.png", width_cm=16.8,
                 caption="Comparison of Hoare (1974) signal-and-wait semantics vs. Mesa (POSIX/Java/Python) signal-and-continue semantics."),
        rk.bullets([
            "Hoare Semantics (Signal-and-Wait): When Thread A calls c.signal() while Thread B waits on c, Thread A immediately transfers monitor ownership to B and enters a privileged Urgent Queue. Because B runs immediately before any external entrant, B's condition remains guaranteed true—so 'if (!cond) wait()' suffices, at the cost of +2 extra context switches per signal.",
            f"Mesa Semantics (Signal-and-Continue — POSIX pthreads, Java, C++, Python): notify() merely moves a waiting thread from the Condition Queue to the Monitor Entry Queue while the signaler finishes its procedure. Between notification and re-acquisition, an outside barging thread may enter the monitor and invalidate the condition! As proved by our BFS model checker, using 'if (!cond)' triggers {mesa_if['mutex_violations']} fatal buffer-underflow states out of {mesa_if['reachable_states']}, whereas 'while (!cond) wait()' shrinks reachable states to {mesa_wh['reachable_states']} with ZERO errors.",
        ]),
        rk.table(
            ["Semantic Aspect", "Hoare Monitor (1974)", "Mesa Monitor (POSIX / Java / Python)"],
            [
                ["Signal Action", d["monitor_semantics"]["hoare"]["signal_action"], d["monitor_semantics"]["mesa"]["signal_action"]],
                ["Required Guard", d["monitor_semantics"]["hoare"]["guard_statement"], d["monitor_semantics"]["mesa"]["guard_statement"]],
                ["Extra Lock Handoffs / Signal", str(d["monitor_semantics"]["hoare"]["extra_lock_handoffs_per_signal"]), str(d["monitor_semantics"]["mesa"]["extra_lock_handoffs_per_signal"])],
                ["Spurious / Steal-Lock Hazard", "Immune (immediate handoff)", "Fatal with 'if'; Immune with 'while' loop"],
            ],
            widths=[3.8, 6.7, 6.7],
            caption="Structural comparison between Hoare and Mesa monitor signaling rules.",
        ),

        # =====================================================================
        # CHAPTER 8
        # =====================================================================
        rk.ptitle("8. Unified Exhaustive BFS State-Space Model Checking Synthesis"),
        rk.para(
            "Combining all 10 explicit-state models into one comparative frame illuminates a clean mathematical "
            "hierarchy. Pure shared-memory protocols achieve correctness under SC only after significant state "
            "complexity (Dekker v5 = 134 states, Peterson = 42 states), collapse instantly under weak memory ordering "
            "(TSO Peterson = 200 states, 8 mutex errors), and require explicit fences. Conversely, atomic OS "
            "abstractions compress reachable state spaces dramatically (Semaphore = 12 states, Mesa Monitor with "
            "while = 17 states) with zero spin back-edges."
        ),
        rk.image("ex4_fig1_state_space_audit.png", width_cm=16.8,
                 caption="Exhaustive BFS state count and safety/deadlock error counts across all 10 checked models."),
        rk.table(
            ["Checked Model", "States", "Edges", "Max Depth", "Mutex Err", "Deadlocks", "Spin Edges", "Status"],
            ed.fsm_rows(d["all_primitives_fsm"]),
            widths=[4.6, 1.3, 1.3, 1.4, 1.4, 1.4, 1.6, 2.2],
            caption="BFS explicit-state model checker audit across Peterson (SC vs. TSO), Semaphore, and Monitor models.",
        ),

        # =====================================================================
        # CHAPTER 9
        # =====================================================================
        rk.ptitle("9. Live OS Benchmark A: Critical Section Workload Sweep (N = 2)"),
        rk.para(
            "We benchmarked all four mechanisms under live OS threads (threading.Thread + threading.Barrier "
            "synchronization) across three critical section lengths: Light (CS = 0 arithmetic loops, 5,000 ops), "
            "Medium (CS = 150 loops, 4,000 ops), and Heavy (CS = 600 loops, 800 ops), evaluating both unyielding "
            "spin (Busy-Wait) and cooperative yield (time.sleep(0)) variants for Dekker and Peterson."
        ),
        rk.image("ex4_fig3_throughput_vs_cs_work.png", width_cm=16.8,
                 caption="2-thread throughput (k ops/sec) across Light, Medium, and Heavy critical-section workloads."),
        rk.table(
            ["Workload", "Primitive Variant", "Wall (ms)", "CPU (ms)", "CPU/Wall", "Throughput (ops/s)", "Yield Spins"],
            ed.cs_sweep_rows(d, "Light (CS=0)"),
            widths=[2.4, 3.6, 1.8, 1.8, 1.8, 3.2, 2.6],
            caption="N = 2 Light Critical Section (CS = 0) live OS benchmark measurements (5,000 total operations).",
        ),
        rk.table(
            ["Workload", "Primitive Variant", "Wall (ms)", "CPU (ms)", "CPU/Wall", "Throughput (ops/s)", "Yield Spins"],
            ed.cs_sweep_rows(d, "Medium (CS=150)"),
            widths=[2.4, 3.6, 1.8, 1.8, 1.8, 3.2, 2.6],
            caption="N = 2 Medium Critical Section (CS = 150) live OS benchmark measurements (4,000 total operations).",
        ),
        rk.table(
            ["Workload", "Primitive Variant", "Wall (ms)", "CPU (ms)", "CPU/Wall", "Throughput (ops/s)", "Yield Spins"],
            ed.cs_sweep_rows(d, "Heavy (CS=600)"),
            widths=[2.4, 3.6, 1.8, 1.8, 1.8, 3.2, 2.6],
            caption="N = 2 Heavy Critical Section (CS = 600) live OS benchmark measurements (800 total operations).",
        ),
        rk.para(
            "Empirical Crossover Insight: In Light (CS = 0), pure shared-memory reads/writes (Peterson and Dekker) "
            "achieve ~3.1M-3.8M ops/sec—over 3x faster than OS Semaphore (~956k ops/sec) because two memory stores "
            "avoid C-level semaphore object calls. However, once actual CS work rises (Heavy CS = 600), critical "
            "section computation dominates lock entry overhead and all primitives converge around 80k-86k ops/sec "
            "(and under unyielding busy-wait with GIL quantum preemption on heavy work, spin saturation can collapse "
            "throughput dramatically unless cooperative yielding or OS blocking is used)."
        ),

        # =====================================================================
        # CHAPTER 10
        # =====================================================================
        rk.ptitle("10. Live OS Benchmark B: Multi-Thread Scaling (N = 2, 4, 8 Threads)"),
        rk.para(
            "Real systems rarely stop at two threads. Evaluating N = 2, 4, and 8 concurrent threads exposes the sharp "
            "asymptotic difference between flat O(N) Filter Lock polling, O(log N) Tournament Dekker trees, and "
            "O(1) kernel-backed Semaphores and Monitors."
        ),
        rk.image("ex4_fig4_multithread_scaling.png", width_cm=16.8,
                 caption="Throughput scaling and wall-clock latency growth across N = 2, 4, and 8 threads."),
        rk.table(
            ["N", "Synchronization Primitive", "Total Ops", "Wall (ms)", "CPU (ms)", "Throughput (ops/s)", "Yield Spins"],
            ed.scaling_rows(d),
            widths=[1.0, 4.4, 2.0, 2.0, 2.0, 3.2, 2.6],
            caption="Complete multi-thread scalability benchmark results for N = 2, 4, and 8 OS threads.",
        ),
        rk.para(
            f"At N = 8 threads, Filter Lock (N-Peterson) throughput collapses by more than 4x down to "
            f"{sc8['Filter Lock (N-Peterson)']['throughput_ops_s']:,.1f} ops/sec because every entrant scans up to "
            "N = 8 level variables across 7 barrier stages. By contrast, Tournament Dekker traverses only log2(8) = 3 "
            f"binary locks and sustains {sc8['Tournament Dekker (Tree)']['throughput_ops_s']:,.1f} ops/sec, while "
            f"Monitor reaches {sc8['Monitor (Mesa Cond)']['throughput_ops_s']:,.1f} ops/sec cleanly."
        ),

        # =====================================================================
        # CHAPTER 11
        # =====================================================================
        rk.ptitle("11. Live OS Benchmark C: Lock-Holder Delay & CPU Burn Audit"),
        rk.para(
            "Now consider what occurs whenever a thread holding a lock is preempted by the OS scheduler, suffers a "
            "page fault, or performs short blocking I/O (simulated via 2 ms, 5 ms, and 10 ms CS hold intervals). "
            "Measuring both elapsed wall time (time.perf_counter) and actual OS process CPU cycles consumed "
            "(time.process_time) isolates the single largest practical flaw of busy-waiting software locks."
        ),
        rk.image("ex4_fig2_busywait_vs_blocking_cpu.png", width_cm=16.8,
                 caption="Wall time vs. burned CPU time under lock-holder delay (left) and CPU utilization ratio across 2-10 ms holds (right)."),
        rk.table(
            ["Hold Delay", "Primitive", "Wall (ms)", "CPU Burned (ms)", "CPU/Wall %", "Throughput (ops/s)"],
            ed.hold_rows(d),
            widths=[2.0, 4.4, 2.4, 2.8, 2.4, 3.2],
            caption="CPU burn audit across 2 ms, 5 ms, and 10 ms lock-holder sleep/preemption intervals.",
        ),
        rk.para(
            f"At a 10 ms hold interval across 20 total operations (~200 ms aggregate hold work): Semaphore completes "
            f"in {hold10['Semaphore (Blocking)']['wall_ms']:.1f} ms wall time while burning just "
            f"{hold10['Semaphore (Blocking)']['cpu_ms']:.1f} ms of CPU ({hold10['Semaphore (Blocking)']['cpu_to_wall_ratio']*100:.1f}% core); "
            f"Monitor behaves nearly identically ({hold10['Monitor (Mesa Cond)']['wall_ms']:.1f} ms wall, "
            f"{hold10['Monitor (Mesa Cond)']['cpu_ms']:.1f} ms CPU). Meanwhile, Peterson (Busy-Wait) wastes "
            f"{hold10['Peterson (Busy-Wait)']['cpu_ms']:.1f} ms of active CPU ({hold10['Peterson (Busy-Wait)']['cpu_to_wall_ratio']*100:.1f}% "
            f"of total runtime!) and drags wall latency out to {hold10['Peterson (Busy-Wait)']['wall_ms']:.1f} ms due "
            f"to contention over CPU quanta—consuming nearly 200x more CPU cycles than blocking primitives!"
        ),

        # =====================================================================
        # CHAPTER 12
        # =====================================================================
        rk.ptitle("12. Condition Synchronization: Bounded-Buffer Producer-Consumer"),
        rk.para(
            "Mutual exclusion alone cannot solve Producer-Consumer synchronization cleanly: a producer must sleep when "
            "the ring buffer is full (len == cap), and a consumer must sleep when the buffer is empty (len == 0). "
            "Comparing all three paradigms on 1,200 items with buffer capacity 8 highlights their expressive divide:"
        ),
        rk.image("ex4_fig5_bounded_buffer_sync.png", width_cm=16.8,
                 caption="Bounded-buffer producer-consumer throughput and condition-wait / polling-retry counts."),
        rk.table(
            ["Implementation Mode", "Items", "Wall (ms)", "CPU (ms)", "Waits / Poll Retries", "Throughput (items/s)"],
            ed.bb_rows(d),
            widths=[4.6, 1.6, 2.0, 2.0, 3.4, 3.6],
            caption="Bounded-buffer Producer-Consumer performance across Semaphore, Mesa Monitor, and Peterson Poll.",
        ),
        rk.bullets([
            f"Counting Semaphores (empty=8, full=0, mutex=1): Require {bb['Semaphore (empty/full/mutex)']['cond_waits_or_spin_retries']} explicit condition retries because the kernel counters track exact slot availability before entry. Throughput reaches {bb['Semaphore (empty/full/mutex)']['ops_per_s']:,.1f} items/s, though swapping acquire order (mutex before empty) instantly deadlocks.",
            f"Mesa Monitor (Condition Variable + while): Consolidates both guards cleanly around one encapsulated buffer, executing {bb['Monitor (Mesa Condition)']['cond_waits_or_spin_retries']} condition waits cleanly and achieving highest throughput ({bb['Monitor (Mesa Condition)']['ops_per_s']:,.1f} items/s).",
            f"Peterson Lock + Spin Polling: Because Peterson only offers mutual exclusion (no condition sleep queue!), a thread seeing a full/empty buffer must release the lock, sleep/yield, and retry ({bb['Peterson (Lock + Spin Poll)']['cond_waits_or_spin_retries']} wasted spin-poll acquisitions).",
        ]),

        # =====================================================================
        # CHAPTER 13
        # =====================================================================
        rk.ptitle("13. Priority Inversion, Real-Time Guarantees & OS Kernel Bridges"),
        rk.para(
            "Bridging back to Exercises 1-3 (scheduling), synchronization primitives interact directly with OS CPU "
            "schedulers. Under strict static-priority scheduling (such as Rate Monotonic), two pathologies emerge:"
        ),
        rk.bullets([
            "Priority Inversion on Blocking Locks (Mars Pathfinder Failure): When Low-priority thread L holds Semaphore/Monitor S, Medium-priority M preempts L indefinitely, stalling High-priority H waiting on S. Solution: Priority Inheritance Protocol (PIP) or Priority Ceiling Protocol (PCP), built natively into POSIX pthread_mutexattr_setprotocol(PTHREAD_PRIO_INHERIT).",
            "Spinlock Deadlock on Uniprocessors: On a 1-core preemptive RTOS, if High-priority H spins forever in Dekker or Peterson waiting for Low-priority L to exit CS, H starves L of CPU cycles—creating an unbreakable live deadlock! Real-time kernels strictly prohibit unyielding user spinlocks unless preemption is disabled or lock holders execute strictly on distinct cores.",
            "Modern Linux Futex Hybridization: Linux pthread_mutex and glibc sem_t optimize the uncontended path in user space via atomic compare-and-swap (zero syscalls, like Peterson) and enter the kernel futex(FUTEX_WAIT) sleep queue only upon genuine contention—capturing both worlds.",
        ]),

        # =====================================================================
        # CHAPTER 14
        # =====================================================================
        rk.ptitle("14. Comprehensive 15-Dimension Engineering Comparison & Decision Matrix"),
        rk.image("ex4_fig9_architecture_comparison.png", width_cm=16.8,
                 caption="Four-column architectural comparison of Dekker, Peterson, Semaphore, and Monitor."),
        rk.image("ex4_fig10_decision_profile.png", width_cm=16.8,
                 caption="Seven-axis engineering capability profile comparing all four synchronization mechanisms."),
        rk.table(
            ["Criterion", "Dekker (1962)", "Peterson (1981)", "Semaphore (1965)", "Monitor (1974)"],
            [
                ["Hardware Requirement", "Atomic load/store + MFENCE", "Atomic load/store + MFENCE", "Atomic RMW + Kernel/Futex", "Mutex + Condition Variable"],
                ["CPU Busy-Wait?", "Yes (spins ~98% on hold)", "Yes (spins ~98% on hold)", "No (~1% CPU, sleeps)", "No (~1% CPU, sleeps)"],
                ["N-Thread Native?", "No (needs O(log N) tree)", "No (O(N) Filter / tree)", "Yes (arbitrary N)", "Yes (arbitrary N)"],
                ["Starvation Freedom", "Yes (B=1 via turn)", "Yes (B=1 via turn)", "FIFO queue: yes; Weak: no", "Entry/Cond FIFO dependent"],
                ["Condition Sync", "Manual polling only", "Manual polling only", "Yes (Counting P/V)", "Yes (Condition Variables)"],
                ["Composability", "Very Low", "Very Low", "Low (P/V deadlocks)", "High (OOP encapsulation)"],
                ["BFS Model Complexity", "134 states (v5)", "42 states (SC) / 200 (TSO)", "12 states (2T binary)", "17 states (Mesa while)"],
                ["Best Production Use", "Historical / bare-metal", "Bare-metal 2-core IPC", "Resource pools / interrupts", "Application / runtime locks"],
            ],
            widths=[3.2, 3.5, 3.5, 3.5, 3.5],
            caption="Eight-row engineering comparison across correctness, OS runtime, and software architecture criteria.",
        ),
        rk.table(
            ["Deployment Scenario", "Recommended Primitive", "Engineering Justification"],
            [
                ["Interrupt handler / ultra-short kernel spin (<20 ns) on SMP", "Hardware Spinlock (Ticket / MCS) or Fenced Peterson", "Sub-microsecond hold is shorter than a kernel sleep/wake transition"],
                ["Counting finite resources (buffer slots, DB connections, worker pool)", "Counting Semaphore", "Direct integer permit tracking with zero redundant condition wakeups"],
                ["Complex shared invariants (queues, caches, state machines)", "Mesa Monitor (Mutex + Condition while-loop)", "Lexical lock scoping + explicit multi-condition waiting prevents P/V leaks"],
                ["Hard real-time tasks sharing resources under RM/EDF", "Priority-Ceiling / Priority-Inheritance Mutex", "Bounds priority inversion strictly to 1 critical section duration"],
                ["User-space lock-free single-producer/single-consumer ring", "Acquire-Release Atomics (seq_cst / memory fences)", "Wait-free progress without mutual exclusion stalls or kernel syscalls"],
            ],
            widths=[5.4, 4.4, 7.4],
            caption="Actionable engineering selection matrix across five OS and systems deployment domains.",
        ),

        # =====================================================================
        # CHAPTER 15 — BFS COUNTEREXAMPLE PROOFS (EXACT TRACES)
        # =====================================================================
        rk.ptitle("15. Formal BFS Counterexample Traces: Step-by-Step Bug Proofs"),
        rk.para(
            "Rather than merely reporting aggregate error counts, our explicit-state BFS model checker records the "
            "exact shortest execution trace from the initial state to every discovered safety violation or deadlock. "
            "Examining these machine-verified counterexamples demonstrates precisely which interleaving triggers "
            "each defect across software locks, weak-memory CPUs, and misused Mesa monitors."
        ),
        rk.h1("15.1 Counterexample #1: Dekker v2 TOCTOU Mutual Exclusion Race (7 Steps)"),
        rk.table(
            ["Step", "BFS State (pc0, pc1, f0, f1)", "Interleaving Transition & Defect Mechanism"],
            ed.counterexample_rows(d, "Dekker v2 (Check-Then-Set)", [
                "Initial state: both threads outside CS, flags cleared",
                "P0 moves to check flag[1] == 0",
                "P0 reads flag[1] == 0 and passes guard (PREEMPTED before setting flag[0]=1!)",
                "P1 enters check state while flag[0] is STILL 0",
                "P1 also reads flag[0] == 0 and passes guard!",
                "P0 writes flag[0] = 1 and enters CS (pc0 = 3)",
                "P1 writes flag[1] = 1 and enters CS TOO (pc1 = 3) -> DUAL CS VIOLATION!",
            ]),
            widths=[1.4, 4.4, 11.4],
            caption="Exact shortest BFS counterexample proving mutual exclusion violation in Dekker v2.",
        ),
        rk.h1("15.2 Counterexample #2: Dekker v3 Symmetric Deadlock (5 Steps)"),
        rk.table(
            ["Step", "BFS State (pc0, pc1, f0, f1)", "Interleaving Transition & Defect Mechanism"],
            ed.counterexample_rows(d, "Dekker v3 (Set-Then-Wait)", [
                "Initial state: both threads outside CS, flags cleared",
                "P0 intends to enter and prepares to write flag[0] = 1",
                "P0 writes flag[0] = 1, moves to spin guard while flag[1]",
                "P1 intends to enter and prepares to write flag[1] = 1",
                "P1 writes flag[1] = 1 -> BOTH hold flag == 1 and wait forever (0 outgoing edges: DEADLOCK!)",
            ]),
            widths=[1.4, 4.4, 11.4],
            caption="Exact shortest BFS counterexample proving symmetric deadlock in Dekker v3.",
        ),
        rk.h1("15.3 Counterexample #3: Peterson Under x86 TSO Store Buffering (9 Steps)"),
        rk.table(
            ["Step", "BFS State (pc0,pc1,mf0,mf1,bf0,bf1,turn)", "Store-Buffer Reordering Execution Trace"],
            ed.counterexample_rows(d, "Peterson (TSO Store Buffer, No Fence)", [
                "Initial state: coherent RAM mf0=0, mf1=0; empty store buffers",
                "Core 0 begins Peterson acquire",
                "Core 0 writes flag[0]=1 into local Store Buffer (bf0=1, RAM mf0 STILL 0!)",
                "Core 0 sets turn = 1 and inspects RAM mf1 == 0",
                "Core 0 bypasses guard and enters CS (pc0=4) while mf0 remains 0 in RAM!",
                "Core 1 begins Peterson acquire before Core 0's store buffer drains",
                "Core 1 writes flag[1]=1 into its local Store Buffer (bf1=1, RAM mf1 STILL 0!)",
                "Core 1 sets turn = 0 and reads stale RAM mf0 == 0",
                "Core 1 ALSO enters CS (pc1=4) -> DUAL CS VIOLATION (both bf0=1, bf1=1 un-flushed)!",
            ]),
            widths=[1.3, 5.5, 10.4],
            caption="Exact BFS counterexample showing why Peterson fails on x86 TSO without MFENCE.",
        ),
        rk.h1("15.4 Counterexample #4: Mesa Monitor 'if' Underflow Steal-Lock (6 Steps)"),
        rk.table(
            ["Step", "BFS State (c0, c1, buf, prod)", "Mesa Signaling Execution Trace"],
            ed.counterexample_rows(d, "Monitor (Mesa 'if' Bug)", [
                "Initial state: empty buffer (buf = 0), two idle consumers c0, c1",
                "Producer inserts one item (buf = 1)",
                "Consumer c0 enters check (c0=3 ready to consume buf=1, preempted before pop)",
                "Consumer c1 enters check while buf is STILL 1 (c1=3 also ready!)",
                "Consumer c1 executes first and pops the single item (buf -> 0)",
                "Consumer c0 resumes WITHOUT re-checking 'while (buf == 0)' -> pc=99 UNDERFLOW BUG!",
            ]),
            widths=[1.4, 4.4, 11.4],
            caption="Exact BFS counterexample showing why 'while (!cond)' is mandatory in Mesa monitors.",
        ),

        # =====================================================================
        # CHAPTER 16 — PRODUCTION KERNEL & CACHE COHERENCE ENGINEERING
        # =====================================================================
        rk.ptitle("16. Cache Coherence (MESI), Linux Futex & C11/POSIX Production Mapping"),
        rk.para(
            "Understanding synchronization primitives at the bare-metal hardware level explains why modern kernels "
            "abandon raw Dekker/Peterson loops once thread counts or cache domains expand across sockets. Under "
            "MESI/MOESI cache coherence protocols, a spinning core polling 'while (flag[other] && turn == other)' "
            "repeatedly reads a shared cache line. Whenever any remote thread modifies turn or flag[other], the "
            "coherence controller broadcasts an Invalidate transaction across the interconnect, forcing every waiting "
            "core to incur a 40-150 ns L3/NUMA cache-miss stall ('cache-line ping-pong')."
        ),
        rk.h1("16.1 From Peterson Spinlocks to Ticket Locks, MCS Queues & Linux Futex"),
        rk.table(
            ["Modern Synchronization Primitive", "Lineage / Design Principle", "Cache Traffic per Waiter", "Kernel Syscall Policy"],
            [
                ["C11 Fenced Peterson Lock", "Peterson + atomic_thread_fence(seq_cst)", "Global flag/turn bouncing O(N)", "0 syscalls (pure spin)"],
                ["Linux Ticket Spinlock", "FIFO fair next_ticket / now_serving", "All spinners share 1 cache line", "0 syscalls (kernel IRQ safe)"],
                ["MCS Queue Spinlock (Linux qspinlock)", "Per-CPU local node spin (next pointer)", "O(1) local cache-line spin!", "0 syscalls (NUMA optimal)"],
                ["POSIX pthread_mutex (Linux futex)", "User atomic CAS + kernel wait queue", "0 contention wakeups until lock", "Syscall ONLY on contention"],
                ["POSIX sem_t (Named/Unnamed)", "Counting atomic + futex(FUTEX_WAIT)", "Zero spin traffic while blocked", "Syscall ONLY when count <= 0"],
                ["C++ std::mutex + std::condition_variable", "Mesa Monitor encapsulation", "Zero spin traffic while waiting", "Futex wait/wake pair"],
            ],
            widths=[4.4, 4.6, 4.2, 4.0],
            caption="Evolution from classical textbook algorithms to production Linux kernel and C++20/POSIX primitives.",
        ),
        rk.h1("16.2 Canonical Production Equivalents (C11 / C++20 / POSIX)"),
        rk.code([
            "// 1. Memory-Safe Fenced Peterson (C11 <stdatomic.h>)",
            "atomic_store_explicit(&flag[i], true, memory_order_relaxed);",
            "atomic_store_explicit(&turn, other, memory_order_seq_cst); // full fence!",
            "while (atomic_load_explicit(&flag[other], memory_order_acquire)",
            "       && atomic_load_explicit(&turn, memory_order_relaxed) == other) {",
            "    cpu_relax(); // x86 PAUSE / ARM YIELD reduces pipeline power & memory stalls",
            "}",
            "",
            "// 2. Mesa Monitor Pattern (C++20 / POSIX pthread_cond_t)",
            "pthread_mutex_lock(&m->lock);",
            "while (m->count == 0) {           // MANDATORY 'while', never 'if'!",
            "    pthread_cond_wait(&m->not_empty, &m->lock);",
            "}",
            "item = ring_pop(&m->buf);",
            "pthread_cond_signal(&m->not_full);",
            "pthread_mutex_unlock(&m->lock);",
        ], caption="Production C11 fenced Peterson vs. POSIX Mesa Monitor idiom with mandatory while-loop."),

        # =====================================================================
        # CHAPTER 17 — CLASSICAL CONCURRENCY PROBLEMS & BRIDGE TO EXERCISE 5
        # =====================================================================
        rk.ptitle("17. Classical Synchronization Problems & Bridge to Exercise 5"),
        rk.para(
            "Evaluating Dekker, Peterson, Semaphores, and Monitors against canonical OS concurrency problems reveals "
            "why high-level abstractions dominate complex protocols while also previewing Exercise 5 (Readers-Writers)."
        ),
        rk.table(
            ["Classical OS Problem", "Why Dekker / Peterson Fail Practically", "Semaphore Solution Structure", "Monitor Solution Advantage"],
            [
                ["Producer-Consumer (Bounded Buffer)", "No condition sleep -> wastes CPU polling full/empty", "3 semaphores: mutex(1), empty(N), full(0)", "1 lock + 2 condition vars (not_full, not_empty)"],
                ["Dining Philosophers (5 Forks)", "Cannot express multi-resource wait without polling", "Asymmetric odd/even pickup or waiter mutex", "State array [THINK, HUNGRY, EATING] + self[5] conds"],
                ["Sleeping Barber / Worker Pool", "Awkward spin polling across N clients & chairs", "customers(0), barber(0), seat_mutex(1)", "Clean FIFO queue length invariant inside Monitor"],
                ["Readers-Writers (Exercise 5)", "Must synthesize shared rw_count inside coarse spinlock", "read_count + rw_mutex + turnstile (Fair)", "Explicit active_readers, waiting_writers + ok_to_read/write"],
            ],
            widths=[3.6, 4.4, 4.5, 4.7],
            caption="Structural mapping across the four canonical OS synchronization problems (bridging to Exercise 5).",
        ),

        # =====================================================================
        # CHAPTER 18 — COMPLETE CODE WALKTHROUGH: PRIMITIVES
        # =====================================================================
        rk.ptitle("18. Annotated Reference Code: Synchronization Primitives (sync_primitives.py)"),
        rk.para(
            "For complete auditability and direct study, Chapters 18 and 19 reproduce the complete verified Python "
            "implementations used across every model-checking experiment and OS benchmark in Exercise 4."
        ),
        rk.code(ed.code_slice("exercise-4/code/sync_primitives.py", 15, 49),
                caption="DekkerLock 2-thread implementation (exercise-4/code/sync_primitives.py, lines 15-49)."),
        rk.code(ed.code_slice("exercise-4/code/sync_primitives.py", 122, 165),
                caption="BinarySemaphoreLock, MesaMonitorLock & Hoare semantics reference (lines 122-165)."),

        # =====================================================================
        # CHAPTER 19 — COMPLETE CODE WALKTHROUGH: MODEL CHECKER & BENCHMARKS
        # =====================================================================
        rk.ptitle("19. Annotated Verification Code: BFS Model Checker & OS Benchmarks"),
        rk.para(
            "All 10 formal state-space models (including counterexample path reconstruction) and 45 live OS thread "
            "benchmark executions are produced deterministically by exercise-4/code/run_experiments.py."
        ),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 35, 70),
                caption="Exact BFS model checker with shortest counterexample path recovery (lines 35-70)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 71, 106),
                caption="BFS loop, deadlock detection, and non-CS spin cycle counting (lines 71-106)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 107, 142),
                caption="Dekker v1 (Strict Alternation) and v2 (Check-Then-Set) state transitions (lines 107-142)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 143, 178),
                caption="Dekker v3 (Set-Then-Wait) and v4 (Symmetric Backoff) state transitions (lines 143-178)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 179, 214),
                caption="Dekker v5 (Correct Final) transition rules verified safe across 134 states (lines 179-214)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 222, 257),
                caption="Peterson Sequential Consistency vs. TSO Store-Buffer transition rules (lines 222-257)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 258, 293),
                caption="TSO transition completion & Binary Semaphore BFS model (lines 258-293)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 294, 330),
                caption="Mesa Monitor 'if' bug vs. 'while' guard BFS model (lines 294-330)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 345, 382),
                caption="Live multi-threaded OS contention and CPU burn benchmark harness (lines 345-382)."),
        # =====================================================================
        # CHAPTER 20 — LOCK-FREE ATOMICS, LL/SC & LANGUAGE RUNTIME SURVEY
        # =====================================================================
        rk.ptitle("20. Beyond Mutual Exclusion: Hardware Atomics & Modern Language Runtimes"),
        rk.para(
            "While Dekker, Peterson, Semaphores, and Monitors span the foundational synchronization curriculum, "
            "modern multiprocessor operating systems also rely on hardware Read-Modify-Write (RMW) instructions "
            "including Compare-And-Swap (x86 CMPXCHG), Fetch-And-Add (x86 LOCK XADD), and Load-Linked / "
            "Store-Conditional (ARM64 LDAXR/STLXR, RISC-V LR/SC). These single-instruction atomic primitives "
            "eliminate the multi-step store-load ordering window that defeated raw Dekker and Peterson locks, "
            "providing consensus number infinity (Herlihy 1991) compared to consensus number 1 for ordinary reads/writes."
        ),
        rk.table(
            ["Synchronization Tier", "Consensus No.", "Blocking Behavior", "Key Advantage", "Primary Failure / Hazard"],
            [
                ["Atomic Read/Write (Dekker, Peterson)", "1 (2T only)", "User spin-wait", "No RMW ALU required", "Store-buffer reordering; O(N) scaling"],
                ["Atomic RMW Spinlock (Ticket / MCS)", "Infinity", "Local/cache spin", "O(1) per CPU core (MCS)", "Unfair/deadlock on single-core RTOS"],
                ["Lock-Free CAS (Treiber / Michael-Scott)", "Infinity", "Retry loop (non-blocking)", "System-wide progress if thread halts", "ABA pointer reuse (needs epoch/hazard ptr)"],
                ["Kernel Semaphore (P/V, Futex)", "N/A (OS)", "Kernel sleep queue", "Zero CPU burn under contention", "Unscoped P/V mismatches; priority inv."],
                ["Mesa Monitor (Mutex + Condvar)", "N/A (OS)", "Kernel sleep + condvar", "Scoped invariant + multi-condition", "Spurious wakeups if 'if' used for 'while'"],
            ],
            widths=[4.4, 2.0, 2.8, 4.0, 4.0],
            caption="Herlihy consensus hierarchy and systems trade-off spectrum from atomic loads/stores to Monitors.",
        ),
        rk.h1("20.1 Language-Runtime Mapping Across C/C++, Rust, Java, Go, and Linux Kernel"),
        rk.para(
            "Every mainstream systems language embeds specific design choices distilled directly from our four "
            "studied primitives. Java synchronized blocks implement reentrant Mesa monitors backed by biased/thin "
            "spinlocks before inflating to OS monitors; C++20 std::mutex + std::condition_variable delegates to "
            "POSIX pthreads / Linux futex; Rust's parking_lot::Mutex compresses a user spin phase plus futex "
            "sleep bit into a single atomic byte; and Go's runtime mutex combines user-space adaptive spinning "
            "with OS futex/sema sleep queues integrated into the M:N goroutine scheduler."
        ),
        rk.table(
            ["Platform / Runtime", "Primary Mutex Primitive", "Condition Primitive", "Adaptive Spin?", "Memory Model Default"],
            [
                ["Linux Kernel (v6.x)", "mutex / qspinlock (MCS)", "wait_queue_head_t", "Yes (optimistic spin)", "Explicit smp_mb() / READ_ONCE"],
                ["POSIX / glibc", "pthread_mutex_t (futex)", "pthread_cond_t (Mesa)", "Optional ADAPTIVE_NP", "Seq-cst on locks; P/V atomic"],
                ["C++20 Standard Lib", "std::mutex / std::atomic", "std::condition_variable", "Implementation-defined", "std::memory_order_seq_cst default"],
                ["Rust (std / parking_lot)", "Mutex<T> (RAII guard)", "Condvar (Mesa loop)", "Yes (40-iteration pause)", "Acquire-Release lock invariants"],
                ["Java HotSpot JVM", "synchronized / ReentrantLock", "Object.wait() / Condition", "Yes (adaptive tiered)", "Java Memory Model happens-before"],
                ["Go Runtime (1.2x)", "sync.Mutex (starvation mode)", "sync.Cond / channels", "Yes (4 rounds on SMP)", "Channel happens-before guarantees"],
            ],
            widths=[3.2, 3.8, 3.6, 3.0, 3.6],
            caption="Production realization of Monitor, Semaphore, and Spinlock principles across six major runtimes.",
        ),
        rk.h1("20.2 Bounded-Buffer Harness Walkthrough (run_bb_bench)"),
        rk.para(
            "Below is the exact Producer-Consumer comparative harness executed in Chapter 12, showing side-by-side "
            "how Semaphore counting (empty/full/mutex), Mesa Condition guarding (while len == cap), and Peterson "
            "polling implement identical ring-buffer correctness under radically different synchronization abstractions."
        ),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 412, 449),
                caption="Bounded-buffer harness: Semaphore and Mesa Condition setups (lines 412-449)."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 450, 487),
                caption="Bounded-buffer harness: Peterson polling fallback and thread execution (lines 450-487)."),

        # =====================================================================
        # CHAPTER 21 — PRACTICAL LAB GUIDE & FINAL SYNTHESIS
        # =====================================================================
        rk.ptitle("21. Engineering Guidelines, Pitfall Checklist & Final Synthesis"),
        rk.para(
            "We conclude Exercise 4 with a field-ready diagnostic checklist covering the top concurrency defects "
            "encountered in operating systems labs and production multithreaded services, mapped directly to the "
            "quantitative evidence established across our 10 BFS state-space audits and 45 live OS benchmark runs."
        ),
        rk.bullets([
            "Never deploy raw Dekker or Peterson in C/C++/Rust without atomic_thread_fence(memory_order_seq_cst): hardware store buffers violate Sequential Consistency and produce silent dual-CS corruption (8/200 error states measured in our TSO BFS checker).",
            "Never busy-wait in application code holding locks across blocking I/O, page faults, or unpredictable preemptions: spinning wastes ~98% of a physical CPU core (404.9 ms wall / 396.1 ms CPU at 10 ms hold), whereas blocking Semaphores and Monitors burn ~1% CPU (2.0 ms) and yield cores cleanly.",
            "Never replace 'while (!cond) wait()' with 'if (!cond) wait()' in POSIX, Java, Python, or C++ Mesa Monitors: barging threads and spurious wakeups caused 6/40 reachable buffer-underflow states in our BFS audit.",
            "Do not stack multiple semaphores without a global acquisition order: always acquire resource-count semaphores (empty/full) BEFORE mutex semaphores, or migrate complex multi-condition invariants into a scoped Monitor.",
            "For multi-core scalability beyond 2 threads, avoid flat O(N) Filter Locks (which drop to 239k ops/s at N=8); select kernel futex Monitors/Semaphores (581k-733k ops/s) or O(log N) Tournament Trees / MCS Queue Spinlocks.",
        ]),
        rk.h1("21.1 Hoare vs. Mesa Pseudocode Contrast & Reproducibility Suite"),
        rk.para(
            "For clarity when contrasting Hoare (1974) monitors with POSIX/Java Mesa monitors, the exact structural "
            "difference between signal-and-wait urgent-queue scheduling and Mesa while-guarded entry queues appears "
            "below, followed by the final experiment driver and automated pytest verification gate."
        ),
        rk.code([
            "// Hoare Monitor (Signal-and-Wait with Urgent Queue)",
            "monitor BoundedBufferHoare {",
            "    int count = 0; condition not_full, not_empty;",
            "    void put(Item x) {",
            "        if (count == N) not_full.wait();     // 'if' suffices: signal transfers lock",
            "        insert(x); count++;",
            "        not_empty.signal();                  // suspends caller in urgent queue if waiter ready",
            "    }",
            "    Item get() {",
            "        if (count == 0) not_empty.wait();",
            "        Item x = remove(); count--;",
            "        not_full.signal();",
            "        return x;",
            "    }",
            "}",
        ], caption="Canonical Hoare monitor pseudocode where single 'if' guards suffice due to immediate lock transfer."),
        rk.code(ed.code_slice("exercise-4/code/run_experiments.py", 488, 524),
                caption="Experiment driver aggregation and JSON serialization (exercise-4/code/run_experiments.py, lines 488-524)."),
        rk.code(ed.code_slice("exercise-4/tests/test_ex4.py", 1, 36),
                caption="Automated concurrency stress verifier (exercise-4/tests/test_ex4.py, lines 1-36)."),
        rk.code(ed.code_slice("exercise-4/tests/test_ex4.py", 37, 74),
                caption="Automated BFS invariant, CPU-burn & 40+ page deliverable test suite (lines 37-74)."),
        rk.code([
            "python3 exercise-4/code/run_experiments.py   # generates all 10 BFS models + 45 OS trials",
            "python3 exercise-4/code/plot_diagrams.py     # builds 10 Okabe-Ito comparative diagrams",
            "python3 tools/build_report.py ex4_en exercise-4 REPORT_EN",
            "python3 tools/build_report.py ex4_fa exercise-4 REPORT_FA",
            "python3 -m pytest exercise-4/tests -v",
        ], caption="Complete end-to-end reproduction commands for Exercise 4."),
        rk.table(
            ["Deliverable Artifact", "Technical Role", "Automated Verification Gate"],
            [
                ["exercise-4/code/sync_primitives.py", "6 executable synchronization classes", "Zero lost updates across all tests"],
                ["exercise-4/code/run_experiments.py", "10 BFS FSM checks + 4 OS benchmark suites", "JSON schema + safety invariants"],
                ["exercise-4/code/plot_diagrams.py", "10 Okabe-Ito publication diagrams", "All 10 PNGs verified visually"],
                ["exercise-4/docs/REPORT_{EN,FA}.{pdf,docx}", "40+ page dense bilingual comparative monographs", "Zero overflow, zero glyphs, >= 40p"],
                ["exercise-4/tests/test_ex4.py", "End-to-end automated verification test suite", "All unit & artifact tests pass"],
            ],
            widths=[5.8, 6.2, 5.2],
            caption="Complete Exercise 4 deliverable inventory and automated verification gates.",
        ),
    ]

    rep.pack_flow(blocks, figures_dir=fig_dir, max_fill=0.89)
    return rep
