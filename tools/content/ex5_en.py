"""Exercise 5 English Monograph: Readers-Writers Across Semaphore, Monitor, Peterson & Dekker."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, HERE)

import report_kit as rk  # noqa: E402
import ex5_data as ed  # noqa: E402


def build() -> rk.Report:
    d = ed.load()
    cpu_map = {r["primitive"]: r for r in d["cpu_burn_audits"]}
    mix03_95 = {r["primitive"]: r for r in d["mix_sweep"] if r["cs_sleep_ms"] == 0.3 and r["read_pct"] == 95}
    fig_dir = os.path.join(REPO_ROOT, "exercise-5", "diagrams")

    rep = rk.Report(
        title="Exercise 5: Readers-Writers Across Semaphore, Monitor, Peterson, and Dekker",
        subtitle="Complete Comparative Analysis of Readers-Preference, Writers-Preference, and Fair/Turnstile Policies — Concurrent Safety, Starvation Stress Tests, Read/Write Crossover Speedups, CPU Burn & Formal BFS Verification",
        lang="en",
        rtl=False,
        cover_meta=[
            ("Repository", "ZaraNodehi/Guaranteed-Scheduling"),
            ("Deliverable", "Exercise 5 — Readers-Writers Comparative Matrix (4 Primitives x 3 Policies)"),
            ("Evaluated Matrix", "Semaphore, Mesa Monitor, Peterson (Filter Lock), Dekker (Tournament) x {Readers-Pref, Writers-Pref, Fair}"),
            ("Verification Standard", "Live Concurrent Safety + 120 ms Flood Stress + 0.3 ms Read-Scan Crossover + BFS Audit"),
        ],
    )

    rep.page(rk.cover(rep.cover_meta))
    rep.page(rk.toc())

    blocks = [
        # =====================================================================
        # CHAPTER 1
        # =====================================================================
        rk.ptitle("1. Executive Overview: The Readers-Writers Synchronization Matrix"),
        rk.para(
            "While mutual exclusion forces every thread to enter a critical section one at a time, shared data "
            "structures in operating systems—routing tables, page caches, symbol tables, and configuration stores—are "
            "overwhelmingly read-dominated. Serializing non-mutating readers behind an exclusive mutex wastes CPU "
            "parallelism unnecessarily. The classical Readers-Writers (RW) problem relaxes mutual exclusion into an "
            "asymmetric invariant: ANY number of readers may hold the lock simultaneously (concurrent reads), whereas "
            "every writer requires strictly exclusive access (no concurrent readers, no other writers)."
        ),
        rk.para(
            "Exercise 5 implements and benchmarks all three canonical Readers-Writers policies—(1) First RW "
            "(Readers-Preference), (2) Second RW (Writers-Preference), and (3) Third RW (Fair FIFO / Turnstile)—"
            "across all four synchronization mechanisms studied in Exercise 4: Dijkstra Semaphores, Mesa Monitors "
            "(Condition Variables + Ticket Queue), N-thread Peterson Filter Locks, and Tournament Dekker Locks, "
            "alongside a CoarseMutex baseline. Evaluating this complete 4 x 3 = 12 implementation matrix uncovers "
            "three pivotal empirical findings:"
        ),
        rk.kv([
            ("Full Concurrent Safety", "All 12 RW variants achieved peak 4 simultaneous readers (CoarseMutex = 1) with ZERO read/write overlap violations"),
            ("Starvation & Sem Barging", "Readers-Pref starved writers completely (0 ops in 120 ms flood); under Writer-Flood, unfair Semaphore barged (0 reader ops) whereas Monitor Ticket & Peterson/Dekker Deque delivered 12 fair reader ops!"),
            ("4.03x Read-Heavy Speedup", f"At 95% reads (0.3 ms read scan), Fair Semaphore ({mix03_95['Semaphore']['throughput_ops_s']:,.0f} ops/s) and Dekker ({mix03_95['Dekker']['throughput_ops_s']:,.0f}) run up to 4.03x faster than CoarseMutex ({mix03_95['CoarseMutex']['throughput_ops_s']:,.0f})"),
            ("CPU Burn Under Slow Readers", f"Waiting writers behind 5 ms readers burned {cpu_map['Semaphore']['cpu_ms']:.1f} ms CPU on Semaphore vs. {cpu_map['Peterson']['cpu_ms']:.1f} ms on Peterson and {cpu_map['Dekker']['cpu_ms']:.1f} ms on Dekker (~300x more CPU!)"),
        ]),
        rk.image("ex5_fig7_three_policies_architecture.png", width_cm=16.8,
                 caption="Architectural summary of the three classical Readers-Writers scheduling policies and observed starvation behavior."),

        # =====================================================================
        # CHAPTER 2
        # =====================================================================
        rk.ptitle("2. Safety Invariant, Policy Taxonomy & 12-Way Concurrency Audit"),
        rk.para(
            "Every valid Readers-Writers lock must enforce two core safety invariants across all interleavings: "
            "(1) active_writers <= 1, and (2) (active_writers > 0) ==> (active_readers == 0). At the same time, it "
            "must actually permit active_readers > 1 when multiple readers overlap; otherwise it degrades into a "
            "degenerate serial mutex."
        ),
        rk.formula(
            "Safety Invariant:  (W_active <= 1)  AND  (W_active == 1  ==>  R_active == 0)\n"
            "Concurrency Goal:  max(R_active) == N_readers   [Strictly > 1; CoarseMutex = 1]\n"
            "Amdahl Speedup:    S(r) = 1 / ((1 - r) + r / N_readers)   =>   S(0.95, 4) = 3.48x"
        ),
        rk.image("ex5_fig1_concurrency_safety.png", width_cm=16.8,
                 caption="Live 6-thread concurrency audit: all 12 RW combinations permit 4 simultaneous readers with zero violations."),
        rk.table(
            ["Primitive", "Policy", "Peak Readers", "Peak Writers", "Overlap Violations", "Final Write Counter", "Elapsed (ms)"],
            ed.safety_rows(d),
            widths=[2.6, 2.2, 2.2, 2.2, 2.8, 2.8, 2.4],
            caption="Complete 13-row safety and concurrency audit (4 readers x 60 ops + 2 writers x 25 ops = 50 updates).",
        ),

        # =====================================================================
        # CHAPTER 3
        # =====================================================================
        rk.ptitle("3. Real-World Starvation Stress Tests: Reader-Flood vs. Writer-Flood"),
        rk.para(
            "Formal definitions often overlook how OS thread wakeups interact with fairness queues in practice. "
            "We constructed two adversarial 120 ms continuous flood benchmarks: (A) Reader-Flood (4 overlapping "
            "readers continuously holding 2 ms read windows against 1 victim writer), and (B) Writer-Flood "
            "(4 continuous writers holding 2 ms write windows against 1 victim reader)."
        ),
        rk.image("ex5_fig2_starvation_reader_flood.png", width_cm=16.8,
                 caption="Reader-Flood stress audit: Readers-Pref starves the writer completely (0 ops, 120 ms wait) across all 4 primitives."),
        rk.table(
            ["Primitive", "Policy", "Flood R Ops", "Victim W Ops", "Mean Wait (ms)", "Max Wait (ms)", "P90 Wait (ms)"],
            ed.starvation_rows(d, "reader_flood"),
            widths=[2.6, 2.2, 2.2, 2.2, 2.6, 2.7, 2.7],
            caption="Reader-Flood starvation results (120 ms window): Writers-Pref and Fair protect writers identically (~2.2 ms max).",
        ),
        rk.h1("3.1 The Barging Discovery Under Writer-Flood"),
        rk.para(
            "Under Writer-Flood, an extraordinary real-world subtlety emerged! While Readers-Pref and Writers-Pref "
            "both starved the victim reader completely (0 completed reads in 120 ms across all primitives), look at "
            "the Fair/Turnstile row: Monitor Fair (explicit FIFO ticket counter) and Peterson/Dekker Fair (explicit "
            "deque token) guaranteed 12 victim reader completions with bounded wait ~8.1-8.6 ms! Conversely, "
            "Semaphore Turnstile still recorded 0 reader completions because Python's non-FIFO Condition-backed "
            "Semaphore permits newly arriving writers to 'barge' ahead of the awakened waiter between turnstile.release() "
            "and thread scheduling! Only explicit ticket/queue fairness defeats barging completely."
        ),
        rk.image("ex5_fig3_starvation_writer_flood.png", width_cm=16.8,
                 caption="Writer-Flood stress audit: Monitor Ticket & Spin Deque deliver 12 fair reads while unfair Semaphore suffers barging."),
        rk.table(
            ["Primitive", "Policy", "Flood W Ops", "Victim R Ops", "Mean Wait (ms)", "Max Wait (ms)", "P90 Wait (ms)"],
            ed.starvation_rows(d, "writer_flood"),
            widths=[2.6, 2.2, 2.2, 2.2, 2.6, 2.7, 2.7],
            caption="Writer-Flood starvation results (120 ms window): exposing Semaphore turnstile barging vs. explicit ticket/deque fairness.",
        ),

        # =====================================================================
        # CHAPTER 4
        # =====================================================================
        rk.ptitle("4. Read:Write Ratio Sweep & Crossover Against Coarse Mutex"),
        rk.para(
            "When should systems engineers deploy a Readers-Writers lock instead of a plain single mutex? Sweeping "
            "the Read:Write percentage across 95:5, 80:20, 50:50, and 20:80 under two critical-section durations "
            "(0.0 ms zero-work vs. 0.3 ms realistic read traversal) pinpoints the exact crossover boundary."
        ),
        rk.image("ex5_fig4_read_write_mix_speedup.png", width_cm=16.8,
                 caption="Read:Write throughput crossover across 0.0 ms zero-work (left) vs. 0.3 ms realistic read scan (right, 4.03x speedup)."),
        rk.table(
            ["Workload Mix", "Primitive", "Wall (ms)", "CPU (ms)", "Throughput (ops/s)"],
            ed.mix_rows(d, 0.0),
            widths=[3.4, 3.6, 2.8, 2.8, 4.6],
            caption="Zero-work (0.0 ms) mix sweep (6 threads x 120 ops = 720 ops): CoarseMutex wins due to lower lock bookkeeping.",
        ),
        rk.table(
            ["Workload Mix", "Primitive", "Wall (ms)", "CPU (ms)", "Throughput (ops/s)"],
            ed.mix_rows(d, 0.3),
            widths=[3.4, 3.6, 2.8, 2.8, 4.6],
            caption="Realistic read-scan (0.3 ms) mix sweep (6 threads x 40 ops = 240 ops): Fair RW locks reach 4.03x speedup at 95% reads.",
        ),

        # =====================================================================
        # CHAPTER 5
        # =====================================================================
        rk.ptitle("5. Writer-Wait CPU Burn & Formal BFS Starvation Model Checking"),
        rk.para(
            "When a writer arrives while two slow readers hold the lock for 5 ms each, blocking RW locks (Semaphore "
            "and Monitor) yield the core immediately—burning just ~2.0 ms of CPU across the entire 46 ms run. By "
            "contrast, polling Peterson and Dekker spin locks keep waiting threads churning in busy loops, burning "
            "396-615 ms of CPU (~97-98% core waste) and stretching wall latency over 10x!"
        ),
        rk.image("ex5_fig5_writer_wait_cpu_burn.png", width_cm=16.8,
                 caption="Writer waiting behind slow 5 ms readers: ~2 ms CPU in Semaphore/Monitor vs. ~396-615 ms CPU in spin RW locks."),
        rk.table(
            ["Primitive", "Reader Hold", "Wall Time (ms)", "CPU Burned (ms)", "CPU / Wall Ratio"],
            ed.cpu_burn_rows(d),
            widths=[3.6, 2.8, 3.4, 3.6, 3.8],
            caption="Writer-wait CPU burn audit across all four Fair RW synchronization primitives.",
        ),
        rk.h1("5.1 Formal BFS Verification of Starvation Freedom"),
        rk.para(
            "Exploring all reachable interleavings of a 2-reader, 1-writer discrete automaton proves mathematically "
            "why the three policies diverge: all three achieve 0 safety errors and permit 2 dual-reader concurrent "
            "states, yet Readers-Preference contains 2 starvation bypass states where readers endlessly cycle while "
            "the writer waits—states completely eliminated under Writers-Preference (22 states) and Fair Gate (30 states)."
        ),
        rk.image("ex5_fig6_bfs_rw_states.png", width_cm=16.8,
                 caption="Formal 2-reader + 1-writer BFS state-space audit proving zero safety violations and elimination of writer bypass."),
        rk.table(
            ["RW Policy", "Reachable States", "Transitions", "Dual-Reader States", "Safety Errors", "Writer Bypass States"],
            ed.bfs_rows(d),
            widths=[2.8, 2.8, 2.4, 3.0, 2.8, 3.4],
            caption="Exhaustive BFS model-checking metrics for the three Readers-Writers policies.",
        ),

        # =====================================================================
        # CHAPTER 6
        # =====================================================================
        rk.ptitle("6. Systems Engineering Scorecard, Linux Kernel RCU/rwsem & Code Walkthrough"),
        rk.image("ex5_fig8_four_mechanisms_matrix.png", width_cm=16.8,
                 caption="Comparative scorecard across anti-barging fairness, CPU efficiency, read speedup, and code clarity."),
        rk.table(
            ["Mechanism", "Concurrency & Safety", "True Anti-Barging", "CPU Energy Efficiency", "Production Mapping (Linux / POSIX)"],
            [
                ["Semaphore RW", "4x readers, 0 errors", "Weak (turnstile barging)", "Excellent (~2 ms CPU)", "Linux rw_semaphore / POSIX sem_t"],
                ["Mesa Monitor RW", "4x readers, 0 errors", "Exact (FIFO ticket)", "Excellent (~2 ms CPU)", "pthread_rwlock_t / std::shared_mutex"],
                ["Peterson Filter RW", "4x readers, 0 errors", "Exact (explicit deque)", "Poor (98% spin burn)", "Educational / 2-core bare-metal spin"],
                ["Dekker Tree RW", "4x readers, 0 errors", "Exact (explicit deque)", "Poor (97% spin burn)", "Tournament software spin reference"],
            ],
            widths=[3.0, 3.2, 3.4, 3.2, 4.4],
            caption="Final comparative synthesis across all four Readers-Writers synchronization backends.",
        ),
        rk.note(
            "Production Note on Read-Copy-Update (RCU): For read-mostly kernel structures (99%+ reads, such as "
            "Linux routing tables and VFS dcache), modern OS kernels go beyond rwlock_t via RCU—letting readers "
            "execute with literally ZERO atomic lock writes or cache-line bouncing while writers publish new versions "
            "and reclaim old memory after one quiescent grace period."
        ),
        rk.code(ed.code_slice("exercise-5/code/rw_locks.py", 97, 132),
                caption="Semaphore Readers-Preference & Writers-Preference implementations (rw_locks.py, lines 97-132)."),
        rk.code(ed.code_slice("exercise-5/code/rw_locks.py", 170, 205),
                caption="Semaphore Fair Turnstile implementation (rw_locks.py, lines 170-205)."),
        rk.code(ed.code_slice("exercise-5/code/rw_locks.py", 272, 308),
                caption="Mesa Monitor Fair Ticket RW implementation defeating barging (lines 272-308)."),
        rk.code(ed.code_slice("exercise-5/code/rw_locks.py", 316, 352),
                caption="Generic Spin-State RW adapter backing Peterson FilterLock and Tournament Dekker (lines 316-352)."),
        rk.code(ed.code_slice("exercise-5/code/run_experiments.py", 277, 313),
                caption="Formal 2-reader + 1-writer BFS starvation model checker (run_experiments.py, lines 277-313)."),
        rk.table(
            ["Artifact Path", "Technical Role", "Verification Gate"],
            [
                ["exercise-5/code/rw_locks.py", "12 RW locks (4 primitives x 3 policies) + CoarseMutex", "0 overlap violations"],
                ["exercise-5/code/run_experiments.py", "Safety + Starvation + Mix Sweep + CPU Burn + BFS", "experiments.json verified"],
                ["exercise-5/code/plot_diagrams.py", "8 Okabe-Ito publication diagrams", "All 8 PNGs verified"],
                ["exercise-5/docs/REPORT_{EN,FA}.{pdf,docx}", "Comprehensive bilingual monographs", "Zero overflow / glyphs"],
                ["exercise-5/tests/test_ex5.py", "Automated RW test suite", "All assertions pass"],
            ],
            widths=[5.6, 6.8, 4.8],
            caption="Complete Exercise 5 deliverable inventory and verification checklist.",
        ),
    ]

    rep.pack_flow(blocks, figures_dir=fig_dir, max_fill=0.89)
    return rep
