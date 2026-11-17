"""Exercise 3 English Monograph: Hand-Worked Paper Scheduling of EDF & RM with 3 Processes."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, HERE)

import report_kit as rk  # noqa: E402
import ex3_data as ed  # noqa: E402


def build() -> rk.Report:
    d = ed.load()
    sa = d["set_a"]
    sb = d["set_b"]
    sc = d["set_c"]
    fig_dir = os.path.join(REPO_ROOT, "exercise-3", "diagrams")

    rep = rk.Report(
        title="Exercise 3: Hand-Worked Paper Scheduling of EDF & RM with Three Processes",
        subtitle="Complete Tick-by-Tick Ready-Queue Traces, Printable Paper Worksheet, Fixed-Point Response-Time Analysis (RTA), Processor Demand Bounds (dbf), Overload Audits & Programmatic Parity with gs_core.py",
        lang="en",
        rtl=False,
        cover_meta=[
            ("Repository", "ZaraNodehi/Guaranteed-Scheduling"),
            ("Deliverable", "Exercise 3 — 3-Process Paper EDF vs. RM Trace + Programmatic Verification"),
            ("Canonical Task Sets", "Set A (H=12, U=11/12=0.917), Set B (H=24, U=23/24=0.958), Set C (2H=24, U=7/6=1.167)"),
            ("Verification Standard", "Zero-Shared-Code Paper Simulator vs. core/gs_core.py (100% Tick-by-Tick Parity)"),
        ],
    )

    rep.page(rk.cover(rep.cover_meta))
    rep.page(rk.toc())

    blocks = [
        # =====================================================================
        # CHAPTER 1
        # =====================================================================
        rk.ptitle("1. Executive Overview & Paper Scheduling Methodology"),
        rk.para(
            "Hand-worked scheduling on paper remains one of the clearest pedagogical instruments in operating systems "
            "and real-time engineering because it forces every decision—job arrivals, absolute deadline calculation, "
            "preemption triggers, ready-queue tie-breaking, and deadline misses—to be resolved explicitly at discrete "
            "integer ticks t = 0, 1, ..., H - 1 without relying on black-box simulator output. Exercise 3 provides a "
            "complete dual-dataset pen-and-paper master study comparing Earliest Deadline First (EDF) and Rate "
            "Monotonic (RM) across three periodic processes P1, P2, and P3."
        ),
        rk.para(
            "Rather than presenting an arbitrary workload where EDF and RM produce identical schedules, we construct "
            "and verify two canonical 3-process real-time task sets plus an overload control reference: (1) Set A "
            "(H = 12, U = 11/12 = 0.9167), which crosses the 3-process Liu-Layland bound (0.7798) yet passes cleanly "
            "under both EDF and RM while exhibiting an instructive dynamic-vs-static divergence at t = 4 and t = 5; "
            "(2) Set B (H = 24, U = 23/24 = 0.9583), a classic textbook separator where EDF achieves zero deadline "
            "misses whereas RM misses P3#0 exactly at t = 8 because static priority favors P2#1 at ticks 6 and 7; "
            "and (3) Set C (2H = 24, U = 7/6 = 1.1667), demonstrating overload domino failure vs. static starvation."
        ),
        rk.kv([
            ("Set A (Harmonic / Feasible)", f"P1(3,1), P2(4,1), P3(6,2) | H={sa['horizon']} | U={sa['utilization_frac']}={sa['utilization']:.4f} | EDF={sa['edf']['missed_count']} misses, RM={sa['rm']['missed_count']} misses"),
            ("Set B (EDF-vs-RM Separator)", f"P1(4,1), P2(6,2), P3(8,3) | H={sb['horizon']} | U={sb['utilization_frac']}={sb['utilization']:.4f} | EDF={sb['edf']['missed_count']} misses, RM={sb['rm']['missed_count']} miss (P3#0 @ t=8)"),
            ("Set C (Overload Reference)", f"P1(3,1), P2(4,2), P3(6,2) | 2H={sc['horizon']} | U={sc['utilization_frac']}={sc['utilization']:.4f} | EDF={sc['edf']['missed_count']} misses (domino), RM={sc['rm']['missed_count']} misses (P3 only)"),
            ("Printable Worksheet", "exercise-3/WORKSHEET_PAPER_TEMPLATE.pdf (2 A4 sheets) + exercise-3/handwritten_scan/"),
            ("Independent Parity", "Zero-shared-code hand trace matches core/gs_core.py::simulate_rt 100% tick-for-tick"),
        ]),
        rk.table(
            ["Dataset", "3-Process Parameters (T_i, C_i, D_i)", "H", "U = sum(C_i/T_i)", "EDF Misses", "RM Misses", "Divergent Ticks"],
            [
                ["Set A", "P1(3,1,3), P2(4,1,4), P3(6,2,6)", str(sa["horizon"]), f"{sa['utilization_frac']} ({sa['utilization']:.4f})", str(sa["edf"]["missed_count"]), str(sa["rm"]["missed_count"]), str(len(sa["edf_vs_rm_diff_ticks"]))],
                ["Set B", "P1(4,1,4), P2(6,2,6), P3(8,3,8)", str(sb["horizon"]), f"{sb['utilization_frac']} ({sb['utilization']:.4f})", str(sb["edf"]["missed_count"]), str(sb["rm"]["missed_count"]), str(len(sb["edf_vs_rm_diff_ticks"]))],
                ["Set C", "P1(3,1,3), P2(4,2,4), P3(6,2,6)", str(sc["horizon"]), f"{sc['utilization_frac']} ({sc['utilization']:.4f})", str(sc["edf"]["missed_count"]), str(sc["rm"]["missed_count"]), str(len(sc["edf_vs_rm_diff_ticks"]))],
            ],
            widths=[1.8, 5.4, 1.0, 2.8, 2.0, 2.0, 2.2],
            caption="Master summary of the three 3-process real-time workloads evaluated in Exercise 3.",
        ),
        rk.h1("1.1 Formal Discrete-Tick Pen-and-Paper Protocol"),
        rk.para(
            "To guarantee unambiguous manual transcription that matches real-time kernel semantics and "
            "core/gs_core.py exactly, every tick t in [0, H - 1] follows a strict four-step order on paper:"
        ),
        rk.bullets([
            "Step 1 — Periodic Job Release: Any task P_i satisfying t mod T_i == 0 releases job P_i#k with remaining execution rem = C_i and absolute deadline d = t + D_i (where k = t / T_i).",
            "Step 2 — Deadline Miss Audit: Before selecting a job for interval [t, t + 1), inspect all active jobs in the ready queue. If any uncompleted job has t >= d and rem > 0, record a deadline miss at tick t (under standard drop_on_miss=False semantics, the tardy job remains in the queue to expose cumulative domino lag).",
            "Step 3 — Priority Selection: EDF selects the ready job minimizing absolute deadline d (tie-breaker: smallest task index P1 < P2 < P3). RM selects the ready job belonging to the task with shortest period T_i (static priority P1 > P2 > P3).",
            "Step 4 — Tick Consumption: Write the chosen job ID in box [t, t + 1) on the paper Gantt grid, decrement rem by 1, and retire the job when rem reaches 0.",
        ]),
        rk.image("ex3_fig7_paper_decision_tree.png", width_cm=16.5,
                 caption="Tick-by-tick paper scheduling decision protocol highlighting Set A divergence and Set B RM failure."),

        # =====================================================================
        # CHAPTER 2
        # =====================================================================
        rk.ptitle("2. Mathematical Foundations: Liu-Layland, Exact RTA & Baruah dbf(L)"),
        rk.para(
            "Before filling a single box on paper, real-time scheduling theory predicts the outcome of each task set "
            "through three complementary algebraic tests. First, the Liu-Layland (1973) sufficient utilization bound "
            "for Rate Monotonic with n = 3 tasks is U_LL(3) = 3 * (2^(1/3) - 1) = 0.779763. Whenever U > 0.7798, RM is "
            "no longer guaranteed by the simple utilization test alone and requires exact fixed-point Response-Time "
            "Analysis (RTA). Second, because implicit deadlines (D_i = T_i) hold in Sets A, B, and C, EDF achieves "
            "exact 100% schedulability if and only if U <= 1.0 (equivalently dbf(L) <= L for all L in [1, H])."
        ),
        rk.formula(
            "U_LL(n) = n * (2^(1/n) - 1)   =>   U_LL(3) = 0.779763   |   U_EDF <= 1.0000\n"
            "R_i^(k+1) = C_i + sum_{j < i} ceil(R_i^(k) / T_j) * C_j\n"
            "dbf(L) = sum_{i=1..n} max(0, floor((L + T_i - D_i) / T_i)) * C_i <= L"
        ),
        rk.h1("2.1 Utilization Regions Across All Three Task Sets"),
        rk.para(
            "Notice how cleanly our three task sets partition the utilization spectrum: Set A (0.9167) and Set B "
            "(0.9583) both lie inside the critical middle zone (0.7798 < U <= 1.000) where Liu-Layland is inconclusive "
            "for RM! Exact RTA separates them: Set A converges within deadline (R_3* = 6 <= D_3 = 6), whereas Set B "
            "diverges beyond P3's deadline (R_3* = 9 > D_3 = 8). Set C (U = 1.1667) enters Zone 3 (U > 1.0), where no "
            "uniprocessor scheduler can satisfy all deadlines over infinite horizons."
        ),
        rk.image("ex3_fig6_utilization_regions.png", width_cm=16.5,
                 caption="Location of Sets A, B, and C across the three real-time schedulability regions for n = 3 processes."),
        rk.image("ex3_fig3_rta_fixed_point.png", width_cm=16.5,
                 caption="Step-by-step RM fixed-point Response-Time Analysis (RTA) trajectories for Sets A and B."),

        # =====================================================================
        # CHAPTER 3
        # =====================================================================
        rk.ptitle("3. Set A Complete Hand-Worked Study (H = 12, U = 11/12 = 0.9167)"),
        rk.para(
            "Set A consists of P1(T=3, C=1, D=3), P2(T=4, C=1, D=4), and P3(T=6, C=2, D=6). The hyperperiod is "
            "H = lcm(3, 4, 6) = 12 ticks. Total CPU utilization is U = 1/3 + 1/4 + 2/6 = 11/12 = 0.9167, leaving "
            "exactly 1 idle tick per hyperperiod (at t = 11). This makes Set A an ideal warm-up exercise on paper: "
            "students experience both ready-queue contention and a genuine EDF-vs-RM divergence at ticks t = 4 and t = 5, "
            "yet both schedules close cleanly before tick t = 12 with zero misses."
        ),
        rk.table(
            ["Process", "Period T_i", "WCET C_i", "Deadline D_i", "Utilization C_i/T_i", "RM Priority Rank"],
            ed.task_rows(sa),
            widths=[2.0, 2.0, 2.0, 2.2, 4.2, 4.8],
            caption="Set A task parameters and static Rate-Monotonic priority assignment.",
        ),
        rk.image("ex3_fig1_paper_gantt_setA.png", width_cm=16.8,
                 caption="Set A Gantt comparison (H=12): EDF vs. RM diverge at t=4..5 (red borders) with 0 misses each."),
        rk.h1("3.1 Tick-by-Tick Ready-Queue Trace for Set A — EDF Schedule (t = 0..11)"),
        rk.table(
            ["Tick", "Arrivals", "Ready Queue (rem, abs_d)", "Chosen", "Rem After", "Miss"],
            ed.trace_rows_slice(sa, "edf", 0, 12),
            widths=[1.2, 2.5, 7.0, 2.0, 2.5, 2.0],
            caption="Complete Set A hand-worked trace under Earliest Deadline First (EDF), t = 0..11.",
        ),
        rk.h1("3.2 Tick-by-Tick Ready-Queue Trace for Set A — RM Schedule (t = 0..11)"),
        rk.table(
            ["Tick", "Arrivals", "Ready Queue (rem, abs_d)", "Chosen", "Rem After", "Miss"],
            ed.trace_rows_slice(sa, "rm", 0, 12),
            widths=[1.2, 2.5, 7.0, 2.0, 2.5, 2.0],
            caption="Complete Set A hand-worked trace under Rate Monotonic (RM), t = 0..11.",
        ),
        rk.h1("3.3 Anatomy of the Set A Divergence at t = 4 and t = 5"),
        rk.para(
            "Examine tick t = 4 carefully: P1#1 consumed tick [3, 4) and retired at t = 4, when P2#1 arrives with "
            "absolute deadline d = 4 + 4 = 8 while P3#0 (released at t = 0, already executed 1 tick at [2, 3)) "
            "still needs 1 remaining tick before d = 6. Under EDF, d(P3#0) = 6 < d(P2#1) = 8, so EDF lets P3#0 "
            "finish during [4, 5) and assigns [5, 6) to P2#1. Under RM, static priority always prefers T_2 = 4 "
            "over T_3 = 6; therefore RM preempts P3#0 immediately at t = 4, executes P2#1 at [4, 5), and returns "
            "to finish P3#0 at [5, 6), just in time for its deadline at t = 6."
        ),
        rk.table(
            ["Tick", "Arrivals", "EDF Choice", "RM Choice", "GS_vtime Choice", "Divergence / Miss Audit"],
            ed.side_by_side_slice(sa, 0, 12),
            widths=[1.2, 2.8, 2.5, 2.5, 3.0, 5.2],
            caption="Set A side-by-side comparison across EDF, RM, and GS_vtime (exact match except t=4..5 swap).",
        ),
        rk.table(
            ["Task", "RM Prio", "Parameters", "Fixed-Point Iterations", "R_i*", "RTA Verdict"],
            ed.rta_rows(sa),
            widths=[1.6, 1.6, 4.0, 4.8, 1.6, 3.6],
            caption="Set A exact RM Response-Time Analysis (RTA): all three tasks converge within deadline.",
        ),

        # =====================================================================
        # CHAPTER 4
        # =====================================================================
        rk.ptitle("4. Set B Complete Hand-Worked Study (H = 24, U = 23/24 = 0.9583)"),
        rk.para(
            "Set B is the cornerstone separation example of Exercise 3: P1(T=4, C=1, D=4), P2(T=6, C=2, D=6), "
            "and P3(T=8, C=3, D=8). Its hyperperiod is H = lcm(4, 6, 8) = 24 ticks, and utilization reaches "
            "U = 1/4 + 2/6 + 3/8 = 6/24 + 8/24 + 9/24 = 23/24 = 0.958333 (exactly 1 idle tick per 24 ticks, at "
            "t = 23). Because U <= 1.0, EDF schedules every job without missing a single deadline. Under RM, however, "
            "the initial critical-instant release at t = 0 combined with P2#1 arriving at t = 6 starves P3#0 of its "
            "third tick before t = 8."
        ),
        rk.table(
            ["Process", "Period T_i", "WCET C_i", "Deadline D_i", "Utilization C_i/T_i", "RM Priority Rank"],
            ed.task_rows(sb),
            widths=[2.0, 2.0, 2.0, 2.2, 4.2, 4.8],
            caption="Set B task parameters and static Rate-Monotonic priority assignment (H=24).",
        ),
        rk.image("ex3_fig2_paper_gantt_setB.png", width_cm=16.8,
                 caption="Set B Gantt comparison (H=24): EDF achieves 0 misses while RM fails P3#0 exactly at t=8."),
        rk.h1("4.1 Set B Hand-Worked EDF Trace (Part 1: t = 0..11, Critical First Half)"),
        rk.table(
            ["Tick", "Arrivals", "Ready Queue (rem, abs_d)", "Chosen", "Rem After", "Miss"],
            ed.trace_rows_slice(sb, "edf", 0, 12),
            widths=[1.2, 2.5, 7.0, 2.0, 2.5, 2.0],
            caption="Set B EDF hand-worked ready-queue trace, first half (t = 0..11).",
        ),
        rk.h1("4.2 Set B Hand-Worked EDF Trace (Part 2: t = 12..23, Second Half)"),
        rk.table(
            ["Tick", "Arrivals", "Ready Queue (rem, abs_d)", "Chosen", "Rem After", "Miss"],
            ed.trace_rows_slice(sb, "edf", 12, 24),
            widths=[1.2, 2.5, 7.0, 2.0, 2.5, 2.0],
            caption="Set B EDF hand-worked ready-queue trace, second half (t = 12..23).",
        ),
        rk.h1("4.3 Set B Hand-Worked RM Trace (Part 1: t = 0..11 — Exact Failure at t = 8)"),
        rk.table(
            ["Tick", "Arrivals", "Ready Queue (rem, abs_d)", "Chosen", "Rem After", "Miss"],
            ed.trace_rows_slice(sb, "rm", 0, 12),
            widths=[1.2, 2.5, 7.0, 2.0, 2.5, 2.0],
            caption="Set B RM hand-worked ready-queue trace, first half (t = 0..11): P3#0 misses at t = 8.",
        ),
        rk.h1("4.4 Set B Hand-Worked RM Trace (Part 2: t = 12..23)"),
        rk.table(
            ["Tick", "Arrivals", "Ready Queue (rem, abs_d)", "Chosen", "Rem After", "Miss"],
            ed.trace_rows_slice(sb, "rm", 12, 24),
            widths=[1.2, 2.5, 7.0, 2.0, 2.5, 2.0],
            caption="Set B RM hand-worked ready-queue trace, second half (t = 12..23).",
        ),
        rk.h1("4.5 Algebraic Proof of Why RM Fails at t = 8 While EDF Passes"),
        rk.para(
            "Trace the critical interval [0, 8) by hand: at t = 0 all three tasks release simultaneously. "
            "During [0, 6), both EDF and RM make identical choices because P1#0 (t=0), P2#0 (t=1,2), P3#0 (t=3), "
            "P1#1 (t=4), and P3#0 (t=5) leave P3#0 with rem = 1 tick and deadline d = 8. At tick t = 6, P2#1 enters "
            "with T_2 = 6 and abs_d = 12. EDF compares d(P3#0) = 8 against d(P2#1) = 12, selects P3#0 at [6, 7) to "
            "complete P3#0 cleanly with 1 tick of slack, and gives [7, 8) to P2#1. By contrast, RM compares static "
            "periods T_2 = 6 < T_3 = 8, preempts P3#0 for two full ticks [6, 8) to finish P2#1, and at t = 8 sees "
            "P3#0 still holding rem = 1 while t >= d = 8 — triggering an unavoidable deadline miss! Exact RTA "
            "independently proves R_3 = 3 -> 6 -> 7 -> 9 > D_3 = 8 (failing by exactly 1 tick)."
        ),
        rk.table(
            ["Task", "RM Prio", "Parameters", "Fixed-Point Iterations", "R_i*", "RTA Verdict"],
            ed.rta_rows(sb),
            widths=[1.6, 1.6, 4.0, 4.8, 1.6, 3.6],
            caption="Set B exact RM RTA proof: P3 fails because R_3* = 9 > D_3 = 8.",
        ),

        # =====================================================================
        # CHAPTER 5
        # =====================================================================
        rk.ptitle("5. Processor Demand Bound Function (dbf) & Job Completion Audits"),
        rk.para(
            "Baruah's Processor Demand Bound Function dbf(L) computes the maximum total CPU time required by all "
            "jobs whose release and deadline both lie within an interval of length L: dbf(L) = sum max(0, "
            "floor((L + T_i - D_i)/T_i)) * C_i. For implicit deadlines (D_i = T_i), this simplifies to sum "
            "floor(L / T_i) * C_i. A task set is EDF-feasible if and only if dbf(L) <= L for all integers "
            "L in [1, H]. Below we tabulate the exact hand-computed values for both Set A and Set B."
        ),
        rk.image("ex3_fig4_dbf_curve.png", width_cm=16.8,
                 caption="Processor Demand Bound Function dbf(L) vs. supply line L for Set A (H=12) and Set B (H=24)."),
        rk.table(
            ["L", "dbf(L)", "Slack L - dbf(L)", "Status", "Per-Task Demand Breakdown"],
            ed.dbf_rows(sa, 0, 12),
            widths=[1.4, 2.0, 3.0, 2.2, 8.6],
            caption="Set A complete Baruah dbf(L) table for L = 1..12 (minimum slack = 1 at L = 12).",
        ),
        rk.table(
            ["L", "dbf(L)", "Slack L - dbf(L)", "Status", "Per-Task Demand Breakdown"],
            ed.dbf_rows(sb, 0, 12),
            widths=[1.4, 2.0, 3.0, 2.2, 8.6],
            caption="Set B Baruah dbf(L) table (Part 1: L = 1..12; note L=8 gives dbf(8)=7 <= 8).",
        ),
        rk.table(
            ["L", "dbf(L)", "Slack L - dbf(L)", "Status", "Per-Task Demand Breakdown"],
            ed.dbf_rows(sb, 12, 24),
            widths=[1.4, 2.0, 3.0, 2.2, 8.6],
            caption="Set B Baruah dbf(L) table (Part 2: L = 13..24; peak demand ratio = 23/24 at L = 24).",
        ),
        rk.h1("5.1 Job-Level Response-Time Audit (Set B: EDF vs. RM)"),
        rk.table(
            ["Process", "Jobs", "Min/Max RT", "Mean RT", "Tardy", "Completed Intervals [release->finish]"],
            ed.completion_rows(sb, "edf"),
            widths=[1.6, 1.4, 2.2, 2.0, 1.5, 8.5],
            caption="Set B job completion audit under EDF (0 tardy jobs across all 13 jobs in H = 24).",
        ),
        rk.table(
            ["Process", "Jobs", "Min/Max RT", "Mean RT", "Tardy", "Completed Intervals [release->finish]"],
            ed.completion_rows(sb, "rm"),
            widths=[1.6, 1.4, 2.2, 2.0, 1.5, 8.5],
            caption="Set B job completion audit under RM (P3#0 takes [0->10], exceeding D_3 = 8).",
        ),

        # =====================================================================
        # CHAPTER 6
        # =====================================================================
        rk.ptitle("6. Set C Overload Control Study (2H = 24, U = 7/6 = 1.1667)"),
        rk.para(
            "To complete the paper scheduling curriculum, Set C tests what happens when a 3-process workload is "
            "pushed past 100% capacity: P1(3,1,3), P2(4,2,4), and P3(6,2,6) yield U = 1/3 + 2/4 + 2/6 = 7/6 = 1.1667. "
            "Over two hyperperiods (2H = 24 ticks), total demand equals 28 ticks inside 24 available slots, creating "
            "an unavoidable deficit of 4 CPU ticks. Hand tracing reveals a profound structural contrast: RM isolates "
            "every single failure onto lowest-priority P3 (misses at t = 6, 12, 18) while keeping P1 and P2 100% "
            "timely; conversely, EDF propagates tardiness forward across tasks (domino effect), registering 5 misses "
            "across P3#1 (t=12), P2#3 (t=16), P3#2 (t=18), P2#4 (t=20), and even high-rate P1#6 (t=21)."
        ),
        rk.image("ex3_fig5_overload_domino_setC.png", width_cm=16.8,
                 caption="Set C overload audit (U=7/6=1.167, 2H=24): EDF domino failure (5 misses) vs. RM P3 starvation (3 misses)."),
        rk.table(
            ["Tick", "Arrivals", "EDF Choice", "RM Choice", "GS_vtime Choice", "Divergence / Miss Audit"],
            ed.side_by_side_slice(sc, 0, 12),
            widths=[1.2, 2.8, 2.5, 2.5, 3.0, 5.2],
            caption="Set C side-by-side comparison across EDF, RM, and GS_vtime (Part 1: t = 0..11).",
        ),
        rk.table(
            ["Tick", "Arrivals", "EDF Choice", "RM Choice", "GS_vtime Choice", "Divergence / Miss Audit"],
            ed.side_by_side_slice(sc, 12, 24),
            widths=[1.2, 2.8, 2.5, 2.5, 3.0, 5.2],
            caption="Set C side-by-side comparison across EDF, RM, and GS_vtime (Part 2: t = 12..23).",
        ),

        # =====================================================================
        # CHAPTER 7
        # =====================================================================
        rk.ptitle("7. Bridge to Guaranteed Scheduling & Printable Paper Worksheet"),
        rk.para(
            "Connecting Exercise 3 back to the Guaranteed Scheduling core of Exercises 1 and 2, we evaluated "
            "gs_vtime:stay (weighted proportional sharing where each task receives weight w_i equal to its WCET C_i "
            "or bandwidth share) on Set B without giving the scheduler any deadline metadata. Strikingly, on Set B "
            "(H = 24), GS_vtime keeps all 3 periodic jobs synchronized near their ideal GPS entitlement and records "
            "0 deadline misses—whereas RM misses P3#0 at t = 8! Notice, however, that this relies on periodic arrival "
            "cadence matching weight ratios; on arbitrary constrained deadlines (D_i < T_i), EDF remains strictly "
            "more general."
        ),
        rk.image("ex3_fig8_gs_vtime_bridge.png", width_cm=16.8,
                 caption="Three-way Gantt comparison on Set B (H=24): EDF (0 misses), RM (1 miss @ t=8), and GS_vtime (0 misses)."),
        rk.h1("7.1 How to Use the Printable Paper Worksheet & Handwritten Upload Folder"),
        rk.para(
            "A dedicated 2-page A4 printable template has been generated at exercise-3/WORKSHEET_PAPER_TEMPLATE.pdf "
            "(with PNG reference previews in exercise-3/handwritten_scan/PAPER_WORKSHEET_P1.png and P2.png). "
            "Page 1 provides blank 12-tick Gantt grids and ready-queue transcription tables for Set A; Page 2 provides "
            "blank 24-tick Gantt grids and critical-window trace boxes for Set B. Once you complete the worksheet by "
            "hand on paper, scan or photograph the sheets and save them inside exercise-3/handwritten_scan/."
        ),

        # =====================================================================
        # CHAPTER 8
        # =====================================================================
        rk.ptitle("8. Engineering Appendix: Independent Hand Simulator & Parity Audit"),
        rk.para(
            "All tables and diagrams in Exercise 3 are computed dynamically from exercise-3/output/experiments.json "
            "and cross-checked tick-for-tick against core/gs_core.py::simulate_rt via a zero-shared-code paper trace "
            "engine (indep_hand_trace_rt). All three datasets verify exact timeline and miss-count parity (100% match)."
        ),
        rk.code(ed.code_slice("exercise-3/code/run_experiments.py", 22, 58),
                caption="Independent hand-trace simulator (lines 22-58): periodic release and miss audit."),
        rk.code(ed.code_slice("exercise-3/code/run_experiments.py", 59, 95),
                caption="Independent hand-trace simulator (lines 59-95): EDF/RM selection and ready-queue logging."),
        rk.code(ed.code_slice("exercise-3/code/run_experiments.py", 125, 160),
                caption="Exact fixed-point Rate-Monotonic RTA solver (exercise-3/code/run_experiments.py, lines 125-160)."),
        rk.table(
            ["Artifact Path", "Role in Exercise 3", "Verification Gate"],
            [
                ["exercise-3/code/gs_core.py", "Canonical Fraction GS + RT simulator", "Vendor SHA parity check"],
                ["exercise-3/code/run_experiments.py", "Independent paper tracer + RTA + dbf + JSON export", "100% tick parity assert"],
                ["exercise-3/code/plot_diagrams.py", "Generates 8 Okabe-Ito analytical diagrams", "All 8 PNGs > 100 KB"],
                ["exercise-3/WORKSHEET_PAPER_TEMPLATE.pdf", "Printable 2-page blank pen-and-paper worksheet", "2-page A4 PDF + PNGs"],
                ["exercise-3/handwritten_scan/", "Upload dropbox for student handwritten paper scans", "README + sheet previews"],
                ["exercise-3/docs/REPORT_{EN,FA}.{pdf,docx}", "Complete bilingual reference monographs", "Zero overflow / glyphs"],
            ],
            widths=[5.6, 7.0, 4.6],
            caption="Complete deliverable inventory and verification checklist for Exercise 3.",
        ),
    ]

    rep.pack_flow(blocks, figures_dir=fig_dir, max_fill=0.89)
    return rep
