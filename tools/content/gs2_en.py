"""Exercise 2 English Comprehensive Comparative Monograph (GS vs EDF vs RM, 40+ dense pages)."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, HERE)

import report_kit as rk  # noqa: E402
import gs2_data as gd  # noqa: E402


def build() -> rk.Report:
    d = gd.load()
    ra = d["regime_a_proportional"]["runs"]
    rb = d["regime_b_constrained_cases"]
    b1 = rb["b1_dm_vs_rm"]
    b2 = rb["b2_edf_vs_dm_gs"]
    b3 = rb["b3_u_under_1_infeasible"]
    sw = d["regime_b_sweep_120"]
    ex30 = sw["exhaustive_audit_30"]
    ov = d["regime_c_overload"]
    fig_dir = os.path.join(REPO_ROOT, "exercise-2", "diagrams")

    rep = rk.Report(
        title="Exercise 2: Comprehensive Comparison of Guaranteed Scheduling vs EDF & Rate Monotonic",
        subtitle="Proportional Fairness vs Real-Time Feasibility, RTA & Processor Demand Analysis, 120-Set Parametric Sweeps, Overload Domino Effects, Jitter, Complexity & Systems Engineering",
        lang="en",
        rtl=False,
        cover_meta=[
            ("Repository", "ZaraNodehi/Guaranteed-Scheduling"),
            ("Deliverable", "Exercise 2 — All-Angles Comparison: GS vs EDF vs RM (40+ Dense Pages)"),
            ("Evaluated Policies", "GS (ratio, vtime, entitled, density), EDF, DM, RM, Stride, Round-Robin"),
            ("Evidence Standard", "Exact Rational [E], 120-Set & 30-Set Exhaustive [M], Independent RT Audit"),
        ],
    )

    rep.page(rk.cover(rep.cover_meta))
    rep.page(rk.toc())

    blocks = [
        # =====================================================================
        # CHAPTER 1
        # =====================================================================
        rk.ptitle("1. Executive Overview: Three Fundamental Scheduling Philosophies"),
        rk.para(
            "Operating system schedulers do not optimize a single universal objective; instead, every scheduler "
            "embeds a mathematical contract defining what constitutes 'correct' execution under contention. "
            "Exercise 2 conducts a rigorous, multi-dimensional comparison across three foundational paradigms: "
            "(1) Guaranteed Scheduling (GS) and Stride/GPS fair-share schedulers, which guarantee each runnable "
            "process its exact fractional bandwidth w_i / W(t); (2) Earliest Deadline First (EDF), the provably "
            "optimal dynamic-priority real-time scheduler minimizing deadline misses; and (3) Rate Monotonic (RM) "
            "and Deadline Monotonic (DM), the canonical static-priority real-time disciplines used across embedded "
            "and safety-critical microkernels."
        ),
        rk.para(
            "Because comparing a fair-share scheduler and a real-time scheduler solely on throughput or solely "
            "on latency creates misleading conclusions, we evaluate all algorithms across three distinct operational "
            "regimes: Regime A (aperiodic weighted proportional sharing), Regime B (periodic constrained-deadline "
            "real-time task sets spanning n=120 random benchmarks and exhaustive feasibility proofs), and Regime C "
            "(sustained CPU overload at utilization U = 1.3333). Every result is verified by exact Fraction/integer "
            "simulation and audited by an independent real-time deadline verifier."
        ),
        rk.bullets([
            f"Regime A Dominance [E]: On weighted aperiodic workloads [1, 2, 4], GS variants hold worst GPS lag to {ra['gs_vtime_q1']['max_abs_lag']:.4f} ({ra['gs_vtime_q1']['max_abs_lag_frac']}) vs {ra['rr_q1']['max_abs_lag']:.4f} for Round-Robin and {ra['fifo_q1']['max_abs_lag']:.4f} for FIFO.",
            f"Regime B Real-Time Optimality [E]+[M]: Across 120 constrained-deadline task sets (D <= T) and 30 exhaustive feasibility audits, EDF achieves {ex30['edf_feasible']}/{ex30['n_sets']} (100% of theoretically feasible sets), strictly outperforming DM ({ex30['dm_feasible']}/{ex30['n_sets']}), RM, and GS.",
            f"Why Weighted GS Fails Hard Deadlines [E]: Even when GS weights match bandwidth demand w_i ~ C_i/D_i in Case B2, gs_vtime_density misses deadlines because virtual-clock fairness advances low-demand long-period shares ahead of urgent short-deadline bursts.",
            f"Regime C Overload Reversal [E]: At U = 1.3333 overload, priority-rigid RM completely starves low-priority T3 (min share ratio = {ov['runs_matched']['rm']['min_task_share_ratio']:.4f}, Jain = {ov['runs_matched']['rm']['jain_fairness']:.4f}), whereas gs_vtime degrades gracefully with Jain = {ov['runs_matched']['gs_vtime']['jain_fairness']:.4f}.",
            f"No Universal Winner Principle: Choosing among GS, EDF, and RM requires matching scheduler semantics to the failure mode that matters most—fair progress under contention, zero deadline misses under feasibility, or starvation resistance under overload.",
        ]),

        # =====================================================================
        # CHAPTER 2
        # =====================================================================
        rk.ptitle("2. Algorithmic Taxonomy & Structural Classification"),
        rk.para(
            "Figure 1 establishes the structural taxonomy connecting proportional-share algorithms (GS, Stride, RR) "
            "with real-time priority dispatchers (EDF, DM, RM). The pivotal architectural divide separates dynamic "
            "time-indexed priority keys (GS virtual time v_i and EDF absolute deadline d_k = r_k + D_i) from static "
            "task-level priority tables (RM 1/T_i and DM 1/D_i) that remain constant once a task set is admitted."
        ),
        rk.image("fig_ex2_taxonomy.png", width_cm=15.6,
                 caption="Structural taxonomy separating proportional-share (GS/Stride), dynamic real-time (EDF), and fixed-priority (DM/RM) schedulers."),
        rk.table(
            ["Dimension", "Guaranteed Scheduling (GS VTime)", "Earliest Deadline First (EDF)", "Rate / Deadline Monotonic (RM/DM)"],
            [
                ["Primary Objective", "Equalize normalized service v_i = A_i/w_i", "Meet every job's deadline d_k", "Predictable fixed-priority RT response"],
                ["Priority Key", "Dynamic virtual time v_i", "Dynamic job deadline d_k = r_k + D_i", "Static task rank (1/T_i or 1/D_i)"],
                ["Optimality Domain", "Optimal GPS lag tracking", "Optimal single-core RT feasibility", "Optimal among fixed-priority policies"],
                ["Utilization Bound (D=T)", "100% work-conserving, 0 RT guarantee", "100% necessary & sufficient (U <= 1)", "Liu-Layland n(2^(1/n)-1) -> 69.31%"],
                ["Constrained D < T Test", "Sim / bandwidth lag only", "Exact Processor Demand dbf(L) <= L", "Exact Response-Time Analysis (RTA)"],
                ["Overload Behavior (U>1)", "Graceful proportional throttling", "Domino cascade / miss spread", "Hard starvation of lowest priority"],
                ["Dispatch Complexity", "O(log N) lazy min-heap", "O(log N) deadline heap / RB-tree", "O(1) priority bitmap (fixed levels)"],
                ["Linux Kernel Counterpart", "CFS / EEVDF (SCHED_NORMAL)", "SCHED_DEADLINE (CBS + EDF)", "SCHED_FIFO / SCHED_RR (99 levels)"],
            ],
            widths=[3.4, 4.6, 4.6, 4.6],
            caption="All-angles architectural and theoretical comparison across GS, EDF, and RM/DM.",
        ),

        # =====================================================================
        # CHAPTER 3
        # =====================================================================
        rk.ptitle("3. Theoretical Utilization Bounds & Real-Time Feasibility Criteria"),
        rk.h1("3.1 Implicit Deadlines (D_i = T_i): Liu–Layland vs EDF U <= 1.0"),
        rk.para(
            "Consider n independent periodic tasks tau_i = (C_i, T_i, D_i) with worst-case execution time C_i, "
            "period T_i, and relative deadline D_i. Define task utilization u_i = C_i / T_i and total CPU "
            "utilization U = sum_{i=1}^n u_i. When deadlines equal periods (D_i = T_i), Liu and Layland (1973) "
            "proved two landmark theorems: (1) EDF schedules every task set if and only if U <= 1.00; and "
            "(2) Rate Monotonic guarantees schedulability whenever U <= n * (2^(1/n) - 1), converging monotonically "
            "to ln(2) = 69.31% as n grows large."
        ),
        rk.formula(
            "U_EDF_implicit <= 1.00   (necessary & sufficient when D_i = T_i)\n"
            "U_RM_LL(n) = n * (2^(1/n) - 1)   -->   ln(2) = 0.693147... as n -> inf\n"
            "Hyperbolic Bound (Bini-Buttazzo):  prod_{i=1}^n (u_i + 1) <= 2\n"
            "Harmonic Task Periods (T_j | T_k):  U_RM_harmonic <= 1.00",
            caption="Classical utilization bounds for EDF (D=T) and Rate Monotonic (general, hyperbolic, and harmonic).",
        ),
        rk.table(
            ["Task Count n", "RM Liu–Layland Bound", "EDF Exact Implicit Bound", "Capacity Gap (EDF - RM)"],
            gd.ll_bound_rows(),
            widths=[3.2, 4.6, 4.6, 4.8],
            caption="Numerical progression of the Liu–Layland schedulability threshold vs EDF 100% capacity.",
        ),
        rk.image("fig_ex2_utilization_bounds.png", width_cm=15.6,
                 caption="Theoretical utilization gap between EDF and RM (left) and measured constrained-deadline feasibility across 120 sets (right)."),

        rk.h1("3.2 Constrained Deadlines (D_i <= T_i): Exact RTA & Processor Demand Tests"),
        rk.para(
            "Once deadlines decouple from periods (D_i < T_i), simple utilization formulas fail for ALL three "
            "policies: even a task set with U = 0.60 can fail both RM and EDF if short deadlines overlap simultaneously "
            "(demonstrated explicitly in Case B3!). Evaluating exact feasibility requires two distinct mathematical tools:"
        ),
        rk.bullets([
            "Response-Time Analysis (RTA, Joseph & Pandya 1986) for Fixed-Priority RM/DM: Task i's worst-case response R_i satisfies the fixed-point recurrence R_i^(k+1) = C_i + sum_{j in hp(i)} ceil(R_i^(k) / T_j) * C_j starting from R_i^(0) = C_i. Feasible iff R_i <= D_i for all i.",
            "Processor Demand Criterion (Baruah et al. 1990) for Dynamic EDF: Compute demand bound function dbf(L) = sum_{i=1}^n max(0, floor((L - D_i) / T_i) + 1) * C_i across synchronous busy interval deadlines L <= L_max. Feasible iff dbf(L) <= L for every checkpoint L.",
            "Why GS Has No Closed-Form Deadline Guarantee: Because GS allocates fractional rate w_i / W(t) evenly rather than concentrating the entire CPU on an imminent burst, a task with C=1, D=2 competing against three heavy tasks can wait beyond D=2 unless its weight dominates the entire active denominator W(t).",
        ]),
        rk.h1("3.3 Worked RTA & dbf(L) Verification on Case B1 and Case B2"),
        rk.para(
            "Applying RTA and dbf(L) directly to Case B1 (T1=(C=2,T=4,D=4), T2=(C=2,T=6,D=3); U=0.8333) proves "
            "mathematically why RM fails while DM and EDF pass. Notice how both exact equations yield closed-form "
            "verdicts without needing discrete tick-by-tick simulation:"
        ),
        rk.table(
            ["Case & Policy", "Formal Test Formula / Recurrence", "Step-by-Step Evaluation", "Theoretical Verdict"],
            [
                ["Case B1 — RM", "R_2^(k+1) = C_2 + ceil(R_2^(k)/T_1)*C_1", "R2(0)=2 -> 2+ceil(2/4)*2=4 -> 4 > D2=3", "FAIL (miss at t=3)"],
                ["Case B1 — DM", "T2 top prio (D2=3<D1=4); R1=C1+ceil(R1/6)*2", "R2=2<=3; R1(0)=2 -> 2+2=4 <= D1=4", "PASS (both safe)"],
                ["Case B1 — EDF", "dbf(L) for L in {3, 4, 6, 8, 12}", "dbf(3)=2<=3, dbf(4)=4<=4, dbf(12)=10<=12", "PASS (0 misses)"],
                ["Case B2 — DM", "R3(0)=1 -> 1+ceil(1/6)*3+ceil(1/8)*3=7; coll at t=15", "Secondary busy period pushes T2 miss", "FAIL (DM misses)"],
                ["Case B2 — EDF", "dbf(L) at all L <= 24 (U=23/24=0.9583)", "dbf(4)=3<=4, dbf(7)=6<=7, dbf(24)=23<=24", "PASS (optimal)"],
                ["Case B3 — Any", "dbf(L) at synchronous tight deadline L=D_min", "Simultaneous burst sum exceeds tight D window", "INFEASIBLE (U=0.60)"],
            ],
            widths=[2.6, 5.0, 5.8, 3.8],
            caption="Worked analytical verification using Response-Time Analysis (RTA) and Processor Demand dbf(L).",
        ),
        rk.h1("3.4 Explicit Baruah Processor Demand Table dbf(L) for Case B2 & Case B3"),
        rk.para(
            "Below are the exact computed Baruah Processor Demand checkpoints for Case B2 (feasible up to "
            "U=0.9583) vs Case B3 (infeasible at U=0.600), directly illustrating why dbf(L) <= L is both "
            "necessary and sufficient for EDF:"
        ),
        rk.table(
            ["Checkpoint L", "Per-Task Demand Breakdown", "Total dbf(L)", "Feasibility Check (dbf <= L)"],
            gd.dbf_profile_rows(d, "b2_edf_vs_dm_gs"),
            widths=[2.4, 6.2, 2.8, 5.8],
            caption="Exact Baruah Processor Demand dbf(L) checkpoints for Case B2 confirming EDF zero-miss feasibility.",
        ),
        rk.table(
            ["Checkpoint L", "Per-Task Demand Breakdown", "Total dbf(L)", "Feasibility Check (dbf <= L)"],
            gd.dbf_profile_rows(d, "b3_u_under_1_infeasible"),
            widths=[2.4, 6.2, 2.8, 5.8],
            caption="Exact Baruah Processor Demand dbf(L) checkpoints for Case B3 exposing sub-unity infeasibility.",
        ),

        # =====================================================================
        # CHAPTER 4
        # =====================================================================
        rk.ptitle("4. All-Angles Comparative Matrix: Twelve Engineering Dimensions"),
        rk.para(
            "Before diving into detailed regime simulations, Table 6 synthesizes twelve operational and mathematical "
            "properties across GS, EDF, RM, DM, Stride, and Round-Robin—highlighting precisely where proportional-share "
            "fairness diverges from real-time deadline optimality."
        ),
        rk.table(
            ["Comparison Criterion", "GS VTime / Capped", "EDF", "RM / DM", "Round-Robin"],
            [
                ["1. Primary Contract", "Proportional share w_i/W", "Zero deadline misses", "Fixed priority response", "Equal quantum turns"],
                ["2. Priority Mutability", "Dynamic continuous clock", "Dynamic per-job d_k", "Static per-task table", "Dynamic FIFO ring"],
                ["3. Implicit D=T Max U", "No RT bound (best-effort)", "100% optimal", "69.31% general / 100% harm.", "No RT bound"],
                ["4. Constrained D<T Opt.", "Suboptimal (ignores D_i)", "100% optimal (11/30)", "Suboptimal (DM 8/30, RM lower)", "Suboptimal"],
                ["5. Overload Fairness", "Jain ~ 0.99 (graceful)", "Jain ~ 0.97 (spreads)", "Jain ~ 0.56 (starves low)", "Jain = 1.00 (unweighted)"],
                ["6. Starvation Risk", "Zero (guaranteed progress)", "Moderate in overload", "100% on low task if U>1", "Zero (unweighted)"],
                ["7. Preemption Count", "High if q=1 (tunable q)", "Low (only at releases)", "Low (strict priority)", "Highest (every q)"],
                ["8. Response Jitter", "High when weights equal", "Moderate (deadline shift)", "Zero on top task, high low", "Proportional to N*q"],
                ["9. Dynamic Join Safety", "Safe via V(t) anchor", "Safe if admission test passes", "Requires full RTA re-test", "Immediate cyclic turn"],
                ["10. Sleeper Vulnerability", "Safe with gs_capped", "Immune (deadline resets)", "Immune (fixed priority)", "Immune (cyclic reset)"],
                ["11. Tie-Break Sensitivity", "Large switch impact (stay)", "Minimal (FIFO/index ok)", "None if distinct P_i", "Cyclic deterministic"],
                ["12. Kernel Cost", "O(log N) heap / O(1) stay", "O(log N) RB-tree / heap", "O(1) priority bitmask", "O(1) FIFO queue"],
            ],
            widths=[3.2, 3.6, 3.6, 3.6, 3.2],
            caption="Twelve-axis synthesis contrasting Guaranteed Scheduling, EDF, RM/DM, and Round-Robin.",
        ),

        # =====================================================================
        # CHAPTER 5
        # =====================================================================
        rk.ptitle("5. Pseudocode Formulations & Verification Engine Architecture"),
        rk.para(
            "To ensure a strict apples-to-apples comparison inside a single unified discrete-time engine, "
            "core/gs_core.py implements all eight policies inside simulate_rt() alongside an exact "
            "branch-and-bound feasibility prover exhaustive_feasible() and an independent trace validator."
        ),
        rk.h1("5.1 Unified Dispatch Key Formulations & Production Pseudocode"),
        rk.code([
            "UNIFIED DISPATCH RULE AT TICK t OVER RUNNABLE JOBS J(t):",
            "  - EDF      : pick j in J(t) minimizing (abs_deadline_j, release_t_j, task_idx_j)",
            "  - DM       : pick j in J(t) minimizing (rel_deadline_i, task_idx_i)",
            "  - RM       : pick j in J(t) minimizing (period_i, task_idx_i)",
            "  - GS_RATIO : pick task i minimizing Fraction(used_i, weight_i)",
            "  - GS_VTIME : pick task i minimizing v_i  (v_i <- V(t) at join; v_i += 1/w_i per tick)",
            "  - GS_DENSE : same as GS_VTIME with w_i <- scaled demand weight proportional to C_i / D_i",
            "  - STRIDE   : pick task i minimizing pass_i (pass_i += K / w_i per tick)",
            "  - RR (q)   : cyclic queue rotation every q ticks",
        ], caption="Unified priority keys compared inside core/gs_core.py simulate_rt()."),
        rk.code([
            "PSEUDOCODE: Production EDF vs Production RM vs Production GS",
            "1) Production EDF (O(log N) RB-Tree / Min-Heap):",
            "   on_release(job): heappush(H_edf, (job.abs_deadline, job.seq, job))",
            "   dispatch():      return H_edf[0]  // preempt current if new job deadline strictly earlier",
            "2) Production RM / DM (O(1) 64-bit Bitmask):",
            "   on_release(job): set_bit(bitmap, task.prio); append(fifo[task.prio], job)",
            "   dispatch():      p = count_trailing_zeros(bitmap); return fifo[p][0]",
            "3) Production GS VTime (O(log N) Lazy Heap + 10^9 Fixed-Point):",
            "   on_join(task):   v[task] = V_fp; push(H_gs, (V_fp, task))",
            "   dispatch():      pick min v[task]; V_fp += 10^9 // W; v[task] += 10^9 // w[task]",
        ], caption="Kernel implementation pseudocode comparing EDF, RM bitmask, and GS virtual-time heap."),

        rk.h1("5.2 Core Real-Time Simulation & Exhaustive Feasibility Engine (core/gs_core.py)"),
        rk.code(gd.core_snippet(655, 692),
                caption="Verbatim simulate_rt() setup in core/gs_core.py (lines 655–692): hyperperiod, job queues, and state."),
        rk.code(gd.core_snippet(693, 730),
                caption="Verbatim simulate_rt() tick arrivals & miss detector (lines 693–730)."),
        rk.code(gd.core_snippet(731, 768),
                caption="Verbatim simulate_rt() RT vs GS candidate filtering (lines 731–768)."),
        rk.code(gd.core_snippet(769, 806),
                caption="Verbatim simulate_rt() score & virtual-clock update branches (lines 769–806)."),
        rk.code(gd.core_snippet(807, 845),
                caption="Verbatim simulate_rt() execution accounting & preemption logger (lines 807–845)."),
        rk.code(gd.core_snippet(846, 877),
                caption="Verbatim simulate_rt() jitter & Jain summary builder (lines 846–877)."),
        rk.code(gd.core_snippet(894, 932),
                caption="Verbatim exhaustive_feasible() DFS prover in core/gs_core.py (lines 894–932)."),
        rk.code(gd.core_snippet(933, 974),
                caption="Verbatim exhaustive_feasible() memoized state pruning (lines 933–974)."),
        rk.code(gd.core_snippet(975, 1014),
                caption="Verbatim verify_rt_schedule_independent() trace audit (lines 975–1014)."),

        # =====================================================================
        # CHAPTER 6
        # =====================================================================
        rk.ptitle("6. Regime A: Aperiodic Proportional-Share Benchmark [1, 2, 4]"),
        rk.para(
            "Before introducing real-time deadlines, Regime A validates our proportional baseline over three "
            "simultaneous processes P1(work=4,w=1), P2(work=6,w=2), P3(work=9,w=4) with total work = 19 ticks. "
            "Table 7 and Figure 3 demonstrate why proportional schedulers dominate unweighted time-slicing when "
            "exact bandwidth shares matter."
        ),
        rk.table(
            ["Policy", "q", "Max |Lag| (Exact)", "RMSE Lag", "Switches", "Preemptions", "Mean TA", "Jain Fairness"],
            gd.regime_a_rows(d),
            widths=[2.6, 0.8, 3.0, 2.0, 2.0, 2.2, 2.0, 2.6],
            caption="Regime A proportional-share comparison across 8 configurations on weighted [1, 2, 4] workload [E].",
        ),
        rk.image("fig_ex2_regime_a_proportional.png", width_cm=15.4,
                 caption="Regime A baseline: GS variants and Stride lock GPS lag to 1.0 tick vs 3.0 (RR) and 5.0 (FIFO)."),
        rk.para(
            f"Crucially, gs_ratio, gs_vtime, gs_entitled, and stride at q=1 produce identical lag "
            f"({ra['gs_vtime_q1']['max_abs_lag']:.4f} ticks, RMSE {ra['gs_vtime_q1']['rmse_lag']:.4f}, Jain "
            f"{ra['gs_vtime_q1']['jain_fairness']:.4f}). Note that EDF, RM, and DM are undefined in pure "
            f"aperiodic proportional mode unless artificial deadlines or periods are assigned—highlighting the "
            f"first major structural boundary between fair-share and real-time schedulers."
        ),
        rk.h1("6.1 Complete 19-Tick Regime A Trace: GS VTime vs Stride vs Round-Robin"),
        rk.table(
            ["Tick t", "gs_vtime (q=1)", "Stride (q=1)", "Round-Robin (q=1)", "Equivalence Check"],
            gd.regime_a_trace_rows(),
            widths=[1.8, 3.2, 3.2, 3.4, 5.6],
            caption="Full 19-tick Regime A equivalence trace proving gs_vtime == Stride vs RR divergence [E].",
        ),

        # =====================================================================
        # CHAPTER 7
        # =====================================================================
        rk.ptitle("7. Regime B Case Studies: B1 (DM > RM), B2 (EDF > DM & GS) & B3"),
        rk.para(
            "To dissect precisely where RM, DM, EDF, and GS separate on real-time constrained-deadline task sets "
            "(D <= T), Regime B evaluates three carefully constructed periodic benchmarks audited by exhaustive DFS:"
        ),
        rk.h1("7.1 Case B1: T1(C=2,T=4,D=4), T2(C=2,T=6,D=3) — DM Passes Where RM Fails"),
        rk.para(
            "Total utilization is U = 2/4 + 2/6 = 0.8333 > Liu–Layland bound (82.84% for n=2). Because T1 has "
            "a shorter period (4 < 6) yet looser deadline (4 > 3), RM prioritizes T1 and causes T2 to miss its "
            "t=3 deadline. DM and EDF both execute T2 first and achieve 0/5 misses (100% pass), whereas equal-weight "
            "GS alternates ticks and misses T2's tight deadline!"
        ),
        rk.table(
            ["Policy", "Missed/Released", "Miss Rate", "Worst Resp.", "Jitter", "Switches", "Jain", "Independent Audit"],
            gd.rt_case_rows(b1),
            widths=[3.2, 2.2, 1.7, 1.8, 1.4, 1.8, 1.7, 3.4],
            caption="Case B1 results: DM & EDF achieve 0 misses while RM and GS miss constrained deadlines [E].",
        ),
        rk.h1("7.2 Case B2: T1(3,6,4), T2(3,8,7), T3(1,12,10) — EDF Passes Where DM & GS Fail"),
        rk.para(
            "Here U = 3/6 + 3/8 + 1/12 = 23/24 = 0.9583 across hyperperiod H = 24. Exhaustive DFS confirms the set "
            "is schedulable, yet fixed-priority DM fails when simultaneous release at t = 0 combined with T2's "
            "second release collides around t = 15. Only dynamic EDF adjusts job urgency at runtime to hit 0/9 "
            "misses! Even demand-weighted GS (w ~ C/D) fails 2/9 jobs because proportional pacing splits CPU rather "
            "than racing to clear T1 and T2 bursts before t = 4 and t = 7."
        ),
        rk.table(
            ["Policy", "Missed/Released", "Miss Rate", "Worst Resp.", "Jitter", "Switches", "Jain", "Independent Audit"],
            gd.rt_case_rows(b2),
            widths=[3.2, 2.2, 1.7, 1.8, 1.4, 1.8, 1.7, 3.4],
            caption="Case B2 results: dynamic EDF achieves 0/9 misses while DM, RM, and demand-weighted GS fail [E].",
        ),
        rk.image("fig_ex2_constrained_gantt.png", width_cm=15.6,
                 caption="Exact Gantt timelines for Cases B1 (top) and B2 (bottom) pinpointing deadline-miss mechanics."),
        rk.h1("7.3 Tick-by-Tick Case B1 Trace: How RM Causes T2 to Miss at t = 3"),
        rk.para(
            "Table 11 prints all 12 ticks of Case B1 across EDF, DM, RM, and GS_vtime (followed by DM and RM "
            "interval logs in Tables 12 and 13). At t = 0..2, RM executes "
            "T1#0 first (since period 4 < period 6), finishing T1#0 at t = 2 and leaving only 1 tick before "
            "T2#0's tight relative deadline D2 = 3. DM and EDF execute T2#0 during [0, 2) and complete T1#0 during "
            "[2, 4), comfortably meeting every deadline across the entire hyperperiod."
        ),
        rk.table(
            ["Tick t", "EDF", "DM", "RM", "GS_vtime", "Case B1 Mechanism"],
            gd.b1_tick_comparison_rows(d),
            widths=[1.4, 2.1, 2.1, 2.1, 2.4, 7.1],
            caption="Complete 12-tick trace of Case B1 illustrating why DM/EDF succeed where RM and GS fail [E].",
        ),
        rk.table(
            ["Slice #", "Job (Case B1 DM)", "Interval [Start, End)", "Duration"],
            gd.gantt_table_rows(b1, "dm"),
            widths=[2.4, 5.2, 5.4, 4.2],
            caption="Case B1 Deadline-Monotonic dispatch intervals achieving zero deadline misses [E].",
        ),
        rk.table(
            ["Slice #", "Job (Case B1 RM)", "Interval [Start, End)", "Duration"],
            gd.gantt_table_rows(b1, "rm"),
            widths=[2.4, 5.2, 5.4, 4.2],
            caption="Case B1 Rate-Monotonic dispatch intervals showing T2#0 starvation at t=0..1 [E].",
        ),

        # =====================================================================
        # CHAPTER 8
        # =====================================================================
        rk.ptitle("8. Complete Tick-by-Tick Execution & Gantt Logs for Case B2"),
        rk.para(
            "Tables 14 and 15 trace all 24 ticks of Case B2 across EDF, RM, and GS_vtime side by side, alongside "
            "the exact dispatch interval logs for EDF, GS_vtime_density, and RM (Tables 16 to 18). Observe at t = 1..2 "
            "how EDF dedicates full CPU to T1#0 so T1 completes within D1=4, whereas GS immediately switches "
            "away from T1 at t = 1 to give T2#0 and T3#0 fractional fairness turns—causing T1#0 to miss at t = 4!"
        ),
        rk.table(
            ["Tick t", "EDF Active", "RM Active", "GS_vtime Active", "Scheduling Contrast"],
            gd.b2_tick_comparison_rows(d, 0, 12),
            widths=[1.6, 3.0, 3.0, 3.2, 6.4],
            caption="Case B2 tick-by-tick trace (t = 0..11) showing why GS preempts T1#0 at t=1 while EDF completes T1#0 [E].",
        ),
        rk.table(
            ["Tick t", "EDF Active", "RM Active", "GS_vtime Active", "Scheduling Contrast"],
            gd.b2_tick_comparison_rows(d, 12, 24),
            widths=[1.6, 3.0, 3.0, 3.2, 6.4],
            caption="Case B2 tick-by-tick trace (t = 12..23) through hyperperiod H = 24 [E].",
        ),
        rk.table(
            ["Slice #", "Job Dispatched (EDF)", "Interval [Start, End)", "Duration"],
            gd.gantt_table_rows(b2, "edf"),
            widths=[2.4, 5.2, 5.4, 4.2],
            caption="Complete EDF dispatch interval log on Case B2 achieving zero misses across H=24 [E].",
        ),
        rk.table(
            ["Slice #", "Job Dispatched (GS w~C/D)", "Interval [Start, End)", "Duration"],
            gd.gantt_table_rows(b2, "gs_vtime_density"),
            widths=[2.4, 5.2, 5.4, 4.2],
            caption="Complete demand-weighted GS interval log on Case B2 illustrating interleaved preemption misses [E].",
        ),
        rk.table(
            ["Slice #", "Job Dispatched (RM)", "Interval [Start, End)", "Duration"],
            gd.gantt_table_rows(b2, "rm"),
            widths=[2.4, 5.2, 5.4, 4.2],
            caption="Complete RM interval log on Case B2 contrasting static period ordering against EDF [E].",
        ),

        # =====================================================================
        # CHAPTER 9
        # =====================================================================
        rk.ptitle("9. Case B3: Sub-Unity Infeasibility Counterexample (U = 0.600 < 1.0)"),
        rk.para(
            "A pervasive misconception states that EDF schedules any periodic task set whenever U <= 1.00. While "
            "true for implicit deadlines (D_i = T_i), it is FALSE when deadlines are constrained (D_i < T_i)! "
            "Case B3 demonstrates this counterexample cleanly: three tasks with U = 0.6000 collide synchronously at "
            "t = 0 with total demand exceeding the earliest tight deadline window. Exhaustive DFS across the entire "
            "decision tree proves zero valid zero-miss schedules exist for ANY deterministic algorithm."
        ),
        rk.table(
            ["Policy", "Missed/Released", "Miss Rate", "Worst Resp.", "Jitter", "Switches", "Jain", "Independent Audit"],
            gd.rt_case_rows(b3),
            widths=[3.2, 2.2, 1.7, 1.8, 1.4, 1.8, 1.7, 3.4],
            caption="Case B3 infeasible counterexample (U = 0.600 < 1.0): every scheduler misses deadlines [E]+[M].",
        ),
        rk.h1("9.1 Tick-by-Tick Collision Trace in Case B3 (t = 0 .. 11)"),
        rk.table(
            ["Tick t", "EDF Active", "DM Active", "RM Active", "GS_vtime Active"],
            gd.b3_tick_comparison_rows(d),
            widths=[2.2, 3.6, 3.6, 3.8, 4.0],
            caption="Case B3 synchronous busy-period collision trace proving structural infeasibility below U=1 [E].",
        ),
        rk.note(
            "Case B3 verifies Baruah's Processor Demand Criterion dbf(L) <= L: total CPU utilization U = 0.60 is "
            "necessary but NOT sufficient for constrained deadlines (D < T). Admission controllers must check dbf(L) "
            "rather than relying blindly on U <= 1.0.",
            caption="Critical Real-Time Admission Rule for Constrained Deadlines",
        ),

        # =====================================================================
        # CHAPTER 10
        # =====================================================================
        rk.ptitle("10. Large-Scale Sweep: 120 Constrained Sets & 30 Exhaustive Audits"),
        rk.para(
            f"To generalize beyond cherry-picked examples, Regime B sweeps {sw['total_sets']} constrained-deadline "
            f"periodic task sets stratified evenly across four high-utilization bands ([0.65,0.75), [0.75,0.85), "
            f"[0.85,0.95), [0.95,1.00]), plus an exact exhaustive feasibility audit on {ex30['n_sets']} sets. "
            f"Table 21 reports zero-miss feasibility rates and Table 22 reports mean miss rates and response jitter."
        ),
        rk.table(
            ["U Band", "Mean U", "EDF", "DM", "RM", "GS (w~C/D)", "GS VTime", "Stride", "RR (q=1)"],
            gd.sweep_success_rows(d),
            widths=[2.2, 1.6, 1.7, 1.7, 1.7, 2.2, 2.1, 1.9, 2.1],
            caption="Zero-miss feasibility rate (%) across 120 constrained-deadline periodic task sets [M].",
        ),
        rk.table(
            ["U Band", "EDF Miss/Jit", "DM Miss/Jit", "RM Miss/Jit", "GS(C/D) Miss/Jit", "GS VTime Miss/Jit", "RR Miss/Jit"],
            gd.sweep_jitter_rows(d),
            widths=[2.0, 2.5, 2.5, 2.5, 2.6, 2.6, 2.5],
            caption="Mean miss rate (%) and response-time jitter across all four utilization bands [M].",
        ),
        rk.image("fig_ex2_constrained_sweep.png", width_cm=15.6,
                 caption="120-set sweep (left: zero-miss rate; middle: miss rate) plus 30-set exhaustive optimality proof (right)."),
        rk.para(
            f"Two powerful statistical conclusions emerge: (1) Across all {ex30['n_sets']} sets verified by "
            f"exhaustive DFS, EDF succeeded on {ex30['edf_feasible']}/{ex30['n_sets']}—achieving 100.0% of the "
            f"theoretical optimum—while DM managed {ex30['dm_feasible']}/{ex30['n_sets']}; and (2) Demand-weighted "
            f"GS (w ~ C/D) boosts feasibility in [0.65, 0.75) from 63.3% (equal-weight GS) up to 83.3%, yet still "
            f"lags far behind EDF's 100.0% because proportional sharing cannot defer low-urgency shares completely."
        ),
        rk.h1("10.1 Stratified Per-Band Performance Breakdown (All 4 Utilization Regimes)"),
        rk.para(
            "Tables below expose the complete per-band breakdown (feasible counts out of 30 sets, zero-miss "
            "percentage, mean deadline miss rate, and response-time jitter) across every evaluated policy."
        ),
        rk.table(
            ["Policy", "Feasible Sets", "Feasible %", "Mean Miss Rate", "Mean Jitter"],
            gd.band_detail_rows(d, 0),
            widths=[4.2, 3.0, 3.0, 3.5, 3.5],
            caption="Band 1 [0.65, 0.75) detailed 30-set breakdown: EDF hits 30/30 (100%) while GS needs C/D weighting [M].",
        ),
        rk.table(
            ["Policy", "Feasible Sets", "Feasible %", "Mean Miss Rate", "Mean Jitter"],
            gd.band_detail_rows(d, 1),
            widths=[4.2, 3.0, 3.0, 3.5, 3.5],
            caption="Band 2 [0.75, 0.85) detailed 30-set breakdown: DM/RM separate sharply from proportional GS [M].",
        ),
        rk.table(
            ["Policy", "Feasible Sets", "Feasible %", "Mean Miss Rate", "Mean Jitter"],
            gd.band_detail_rows(d, 2),
            widths=[4.2, 3.0, 3.0, 3.5, 3.5],
            caption="Band 3 [0.85, 0.95) detailed 30-set breakdown: EDF more than doubles DM/RM feasibility [M].",
        ),
        rk.table(
            ["Policy", "Feasible Sets", "Feasible %", "Mean Miss Rate", "Mean Jitter"],
            gd.band_detail_rows(d, 3),
            widths=[4.2, 3.0, 3.0, 3.5, 3.5],
            caption="Band 4 [0.95, 1.00] detailed 30-set breakdown: extreme contention under constrained D < T [M].",
        ),

        # =====================================================================
        # CHAPTER 11
        # =====================================================================
        rk.ptitle("11. Regime C: Overload Collapse, Domino Cascade vs Fair Throttling"),
        rk.para(
            f"What happens when demand permanently exceeds CPU capacity (U = {ov['utilization']:.4f} > 1.0)? "
            "Regime C subjects all schedulers to sustained overload across horizon 24 in two sub-experiments: "
            "(1) demand-matched weights [6, 3, 2] where each task's GS share mirrors its overload demand, and "
            "(2) asymmetric weights [1, 2, 4] inverting RM priorities so low-priority T3 holds highest weight."
        ),
        rk.table(
            ["Policy", "Missed/Rel.", "Jain Fairness", "Min Share Ratio", "CPU Used (T1/T2/T3)", "Switches"],
            gd.overload_rows(d, "runs_matched"),
            widths=[2.8, 2.4, 2.6, 2.8, 4.4, 2.2],
            caption="Regime C overload with demand-matched weights [6, 3, 2] at U = 1.3333 [E].",
        ),
        rk.table(
            ["Policy", "Missed/Rel.", "Jain Fairness", "Min Share Ratio", "CPU Used (T1/T2/T3)", "Switches"],
            gd.overload_rows(d, "runs_asym"),
            widths=[2.8, 2.4, 2.6, 2.8, 4.4, 2.2],
            caption="Regime C overload with inverted asymmetric weights [1, 2, 4] at U = 1.3333 [E].",
        ),
        rk.image("fig_ex2_overload_domino.png", width_cm=15.6,
                 caption="Overload U=1.333 behavior: RM/DM completely starve T3 (0 CPU) while GS preserves proportional sharing."),
        rk.h1("11.1 Four-Task Domino Overload Benchmark (U = 1.1357)"),
        rk.para(
            "To examine transient overload across four distinct period classes [T=4, 5, 7, 10] with U = 1.1357, "
            "Table 29 evaluates EDF, RM, DM, GS VTime, and Round-Robin over a 35-tick window (with tick-by-tick "
            "traces in Tables 30 and 31). Under RM/DM, "
            "tasks T1 and T2 preserve 0% miss rates while pushing total overload onto T4; under EDF, misses spread "
            "across jobs as deadlines cross; and under GS VTime, Jain fairness remains highest across all four tasks."
        ),
        rk.table(
            ["Policy", "Missed/Rel.", "Miss Rate", "Jain Fairness", "Min Share Ratio", "CPU (T1/T2/T3/T4)"],
            gd.edf_domino_demo_rows(),
            widths=[2.8, 2.3, 2.1, 2.7, 2.9, 4.4],
            caption="Four-task overload comparison (U = 1.1357, H = 35): EDF miss spreading vs RM starvation vs GS equity [E].",
        ),
        rk.table(
            ["Tick t", "EDF Active", "RM Active", "GS_vtime Active"],
            gd.domino_tick_rows(0, 20),
            widths=[2.4, 4.8, 4.8, 5.2],
            caption="First 20 ticks of the 4-task U=1.1357 overload trace showing T4 suppression in RM vs GS sharing [E].",
        ),
        rk.table(
            ["Tick t", "EDF Active", "RM Active", "GS_vtime Active"],
            gd.domino_tick_rows(20, 35),
            widths=[2.4, 4.8, 4.8, 5.2],
            caption="Remaining ticks (t = 20..34) of the 4-task U=1.1357 overload run completing the 35-tick window [E].",
        ),

        # =====================================================================
        # CHAPTER 12
        # =====================================================================
        rk.ptitle("12. Tick-by-Tick Overload Trace & Five-Axis Synthesis"),
        rk.para(
            "Tables 32 and 33 expose all 24 integer ticks of the overload asymmetric run across gs_vtime, EDF, "
            "and RM. Observe how RM allocates 100% of available ticks to T1 and T2 while locking out heavy T3 "
            "completely (0/24 ticks!), whereas gs_vtime smoothly delivers balanced slices to all three processes."
        ),
        rk.table(
            ["Tick t", "gs_vtime Active", "EDF Active", "RM Active", "Overload Regime Observation"],
            gd.overload_tick_rows(d, 0, 12),
            widths=[1.6, 3.0, 2.8, 2.8, 7.0],
            caption="Overload U=1.333 tick-by-tick trace (t = 0..11) contrasting GS, EDF, and RM starvation [E].",
        ),
        rk.table(
            ["Tick t", "gs_vtime Active", "EDF Active", "RM Active", "Overload Regime Observation"],
            gd.overload_tick_rows(d, 12, 24),
            widths=[1.6, 3.0, 2.8, 2.8, 7.0],
            caption="Overload U=1.333 tick-by-tick trace (t = 12..23) through horizon 24 (asymmetric weights) [E].",
        ),
        rk.h1("12.1 Matched-Weight Overload Trace (t = 0 .. 23, Weights = [6, 3, 2])"),
        rk.para(
            "Even when GS weights are calibrated directly to periodic workload demand ([6, 3, 2] matching "
            "C_i/T_i proportions), RM continues to starve T3 (0/24 ticks) while GS maintains continuous "
            "proportional progress across all three tasks throughout t = 0..23:"
        ),
        rk.table(
            ["Tick t", "gs_vtime Active", "EDF Active", "RM Active", "Matched Overload Contrast"],
            gd.overload_matched_tick_rows(d, 0, 12),
            widths=[1.6, 3.0, 2.8, 2.8, 7.0],
            caption="Matched-weight overload trace (t = 0..11) contrasting GS proportional share vs RM starvation [E].",
        ),
        rk.table(
            ["Tick t", "gs_vtime Active", "EDF Active", "RM Active", "Matched Overload Contrast"],
            gd.overload_matched_tick_rows(d, 12, 24),
            widths=[1.6, 3.0, 2.8, 2.8, 7.0],
            caption="Matched-weight overload trace (t = 12..23) through horizon 24 [E].",
        ),
        rk.image("fig_ex2_tradeoff_profile.png", width_cm=15.4,
                 caption="Pareto frontier: Real-Time zero-miss feasibility (X) vs Overload Jain equity (Y)."),
        rk.image("fig_ex2_multidim_radar.png", width_cm=15.4,
                 caption="Normalized five-axis measured comparison across GS, EDF, RM, DM, and Round-Robin."),

        # =====================================================================
        # CHAPTER 13
        # =====================================================================
        rk.ptitle("13. Overhead, Context Switches, Response Jitter & Cache Behavior"),
        rk.para(
            "Beyond feasibility and fairness, real operating systems pay heavy hardware costs whenever a scheduler "
            "switches threads prematurely. Comparing context-switch counts across our regimes highlights an "
            "important operational contrast:"
        ),
        rk.bullets([
            "Context-Switch Efficiency: Fixed-priority RM/DM and dynamic EDF switch only when a newly released job strictly beats the running job (e.g., 5 switches for DM in B1, 9 switches for EDF in B2). Fine-grained GS (q=1) switches frequently (up to 16+ switches per hyperperiod) unless tuned with stay hysteresis or larger quanta.",
            "Response-Time Jitter: RM minimizes jitter completely on the highest-priority task (jitter = 0) at the expense of unbounded jitter on lower priorities. EDF shifts job priorities dynamically as deadlines approach, creating moderate symmetric jitter. GS distributes latency continuously, yielding higher jitter on short bursts.",
            "Implementation Footprint: RM/DM require only a tiny O(1) priority bitmap (e.g., 64-bit bitmask + FIFO per level), making them ideal for tiny microcontrollers. Both EDF and production GS require O(log N) balanced trees or min-heaps.",
        ]),
        rk.table(
            ["Workload Profile", "Recommended Scheduler", "Rationale & Trade-Off"],
            [
                ["Hard Real-Time Safety-Critical (U <= 69% or Harmonic)", "RM / DM", "O(1) bitmask dispatch, deterministic RTA bounds, zero highest-task jitter"],
                ["High-Utilization Dynamic Real-Time (D <= T, U up to 100%)", "EDF (+ CBS bandwidth cap)", "Provably optimal feasibility; pair with CBS reservation to isolate overload"],
                ["General-Purpose Server / Interactive Multi-Tenant OS", "GS VTime + Capped Wakeup", "Exact proportional shares, dynamic arrival fairness, immune to overload starvation"],
                ["Mixed Real-Time + Batch Desktop / Cloud Host", "Hierarchical: EDF (RT) + GS (Normal)", "Strict deadline guarantees for RT tier + proportional bandwidth for remaining capacity"],
            ],
            widths=[5.2, 4.4, 7.6],
            caption="Engineering decision matrix selecting the optimal scheduler architecture per system class.",
        ),

        # =====================================================================
        # CHAPTER 14
        # =====================================================================
        rk.ptitle("14. Hybrid Architecture: Combining EDF + GS (Linux SCHED_DEADLINE & CBS)"),
        rk.para(
            "Notice from Figure 7 and Figure 8 that neither pure EDF nor pure GS wins across all axes: EDF excels "
            "at meeting constrained deadlines below capacity but can suffer domino cascades under overload, whereas "
            "GS excels at fair proportional bandwidth isolation under overload yet misses tight deadlines under "
            "sub-capacity contention. Modern operating systems solve this exact dilemma by unifying both algorithms "
            "inside a Constant Bandwidth Server (CBS) + EDF hierarchy (implemented in Linux's SCHED_DEADLINE):"
        ),
        rk.bullets([
            "Budget & Period Reservation: Every task receives a guaranteed runtime budget Q_i per reservation period P_i (exactly proportional share w_i = Q_i / P_i, mirroring GS!).",
            "EDF Virtual Deadline Dispatch: As long as a task consumes <= Q_i within its current window, it runs under EDF with deadline d_k, enjoying optimal real-time schedulability up to sum(Q_i / P_i) <= 1.0.",
            "Automatic Overload Throttling: The instant an overloaded or misbehaving task exhausts budget Q_i, CBS postpones its deadline by +P_i (throttling it cleanly, exactly like GS!), completely preventing EDF domino cascades and RM low-priority starvation.",
        ]),
        rk.h1("14.3 Real-Time Admission Control & Hyperperiod Scaling Engineering"),
        rk.para(
            "Whenever a new periodic task joins a running system, admission latency differs vastly across the "
            "three paradigms: GS requires only an O(log N) insertion at V(t) with zero hyperperiod coupling; "
            "EDF demands evaluating Baruah's dbf(L) across synchronous busy intervals (pseudo-polynomial in "
            "utilization < 1.0); and RM/DM require iterating Joseph–Pandya RTA fixed points across every "
            "lower-priority task already present in the priority table."
        ),
        rk.table(
            ["Admission Operation", "GS VTime (Proportional)", "EDF (Dynamic Deadline)", "RM / DM (Static Priority)"],
            [
                ["Task Arrival Check", "Always admissible; weight scaling", "Exact dbf(L) <= L check across L*", "RTA fixed-point R_i <= D_i loop"],
                ["O(N) Complexity Class", "O(log N) heap insertion at V(t)", "Pseudo-polynomial for U < 1.0", "Pseudo-polynomial per priority row"],
                ["Overload Behavior", "Automatic linear rate reduction", "Domino cascade unless CBS-capped", "Deterministic low-priority starvation"],
                ["Runtime Budget Enforcement", "Inherent via virtual time advance", "Requires CBS (sched_runtime Q_i)", "Optional sporadic server / slack"],
            ],
            widths=[3.6, 4.4, 4.6, 4.6],
            caption="Admission-control complexity and runtime enforcement comparison across the three schedulers.",
        ),
        rk.h1("14.2 Linux SCHED_DEADLINE Configuration Trade-Offs (Q_i / P_i Tuning)"),
        rk.para(
            "In Linux kernels 3.14+, configuring SCHED_DEADLINE requires selecting three runtime parameters per "
            "thread: sched_runtime (Q_i), sched_deadline (D_i <= P_i), and sched_period (P_i). Setting D_i = P_i "
            "maximizes total admission up to 100% of CPU bandwidth while preserving strict bandwidth isolation, "
            "whereas tightening D_i < P_i reduces tail latency at the cost of processor demand pressure analyzed "
            "in Section 3.4. Unlike legacy POSIX real-time policies SCHED_FIFO and SCHED_RR, a runaway thread "
            "under CBS+EDF can never lock up the kernel or starve SCHED_NORMAL (CFS/EEVDF) workloads."
        ),
        rk.h1("14.1 Formal Constant Bandwidth Server (CBS) State Equations"),
        rk.formula(
            "On job release (t):  if c >= (d_k - t) * (Q_i / P_i) or t >= d_k:\n"
            "  d_k <- t + P_i;   c <- Q_i       (reset clean bandwidth window)\n"
            "During execution (+dt):   c <- c - dt\n"
            "On budget exhaustion (c == 0):  d_k <- d_k + P_i;  c <- Q_i   (postpone deadline -> fair throttle!)",
            caption="Constant Bandwidth Server (Abeni & Buttazzo 1998) rules unifying EDF optimality with GS overload isolation.",
        ),
        rk.para(
            "Notice how the CBS equations mirror both ancestors simultaneously: while budget c > 0, the server "
            "dispatches purely by earliest absolute deadline d_k (preserving EDF's 100% schedulability); once "
            "c hits zero under overload, postponing d_k by +P_i guarantees no greedy task can steal CPU from "
            "other servers beyond its Q_i / P_i share—the exact proportional isolation property of Guaranteed Scheduling!"
        ),

        # =====================================================================
        # CHAPTER 15 — DEEP SYSTEMS DIMENSIONS: SPORADIC, LOCKS, MULTICORE
        # =====================================================================
        rk.ptitle("15. Sporadic/Aperiodic Arrivals, Synchronization & Multicore Scaling"),
        rk.h1("15.1 Handling Aperiodic & Sporadic Bursts (Servers vs V(t) Anchors)"),
        rk.para(
            "Real systems mix periodic real-time control loops with unpredictable sporadic or interactive "
            "aperiodic requests. Under fixed-priority RM, sporadic bursts either run in a low-priority background "
            "slot (suffering massive starvation during periodic busy intervals) or require a Polling Server / "
            "Deferrable Server / Sporadic Server with dedicated capacity C_s and period T_s. Under EDF, aperiodic "
            "requests fit inside a Constant Bandwidth Server (CBS) or Total Bandwidth Server (TBS) that assigns "
            "safe synthetic deadlines d_k = max(r_k, d_{k-1}) + C_k / U_s. Under Virtual-Time GS, every newly "
            "arriving interactive job is admitted instantaneously via v_i = V(t) without pre-reserving server "
            "periods, though with zero deadline guarantee."
        ),
        rk.h1("15.2 Resource Locks & Priority Inversion (PIP/PCP/SRP vs Share Inheritance)"),
        rk.para(
            "When tasks share mutex-protected kernel structures or I/O devices, scheduling algorithms behave "
            "fundamentally differently under lock contention:"
        ),
        rk.bullets([
            "Rate Monotonic + PIP/PCP: Unprotected RM suffers unbounded Priority Inversion (famous Mars Pathfinder bug) when a medium-priority task preempts a low-priority lock holder blocking a high-priority task. Priority Inheritance Protocol (PIP) or Priority Ceiling Protocol (PCP) restores bounded blocking.",
            "EDF + Stack Resource Policy (SRP): Under Baker's SRP, each resource holds a preemption ceiling equal to the maximum static preemption level of users; EDF blocks higher-preemption jobs cleanly before lock acquisition, guaranteeing deadlock freedom and single-block bounds.",
            "Guaranteed Scheduling + Bandwidth Inheritance (BWI): Because virtual-time GS ties scheduling to per-task CPU usage rather than fixed priority levels, a high-weight task blocked on a low-weight mutex holder stalls unless the lock holder inherits the waiter's share weight (Bandwidth Inheritance, Lipari & Lamastra 2002).",
        ]),
        rk.h1("15.3 Multicore Scaling: Dhall's Effect vs Partitioned RM/EDF vs Multicore GS"),
        rk.para(
            "Moving from single-core (m = 1) to multiprocessor systems (m >= 2) reveals surprising pathologies. "
            "Under Global EDF or Global RM, Dhall's Effect proves that even utilization barely above U = 1.0 (e.g., "
            "m small tasks C=2*eps, T=1 plus one long task C=1, T=1+eps on m cores) can miss deadlines completely! "
            "Therefore production RT kernels default to Partitioned EDF/RM (binding tasks to cores via First-Fit "
            "bin packing) or Pfair / EDF^(k) hybrids. Conversely, multicore GS / Linux CFS scales smoothly across "
            "cores via periodic work-stealing load balancers that equalize per-CPU weighted load W_core."
        ),
        rk.table(
            ["Systems Dimension", "GS VTime / Capped", "EDF (+ CBS / SRP)", "RM / DM (+ PIP / PCP)"],
            [
                ["Aperiodic / Interactive", "Native V(t) anchor (zero config)", "Needs TBS / CBS server", "Background / Polling Server"],
                ["Mutex Contention", "Bandwidth Inheritance (BWI)", "Stack Resource Policy (SRP)", "Priority Inheritance / Ceiling"],
                ["Multicore Pathology", "Smooth work-stealing load balance", "Dhall's Effect in Global EDF", "Dhall's Effect in Global RM"],
                ["Dynamic Task Admission", "Instant O(log N) heap insert", "O(N) dbf(L) or O(1) U check", "O(N * iter) full RTA recompute"],
                ["Energy / DVFS Friendliness", "Pacing distributes slack evenly", "Dynamic slack reclaiming (GRUB)", "Static frequency ceiling"],
            ],
            widths=[3.4, 4.6, 4.6, 4.6],
            caption="Extended systems comparison across sporadic handling, mutex locking, multicore scaling, admission, and DVFS.",
        ),

        # =====================================================================
        # CHAPTER 16
        # =====================================================================
        rk.ptitle("16. Formal Proofs of Key Comparative Theorems"),
        rk.h1("15.1 Theorem 1 — EDF Optimality Under Arbitrary Preemptive Periodic Releases"),
        rk.para(
            "Proof Sketch (Exchange Argument): Consider any feasible schedule S that misses zero deadlines. Let t be "
            "the earliest tick where S executes a job J_2 whose absolute deadline d_2 > d_1 exceeds that of an "
            "available job J_1. Swapping one tick of J_2 with the subsequent tick of J_1 (since J_1 was ready and "
            "d_1 < d_2) preserves J_1's completion <= d_1 and cannot move J_2 past d_2 because J_1 originally ran "
            "before d_1 < d_2. Repeating finitely transforms S into pure EDF with zero misses. Q.E.D."
        ),
        rk.h1("15.2 Theorem 2 — Why Pure Fair-Share GS Cannot Guarantee Arbitrary Hard Deadlines"),
        rk.para(
            "Proof Sketch: Under GS, whenever W(t) > w_i, task i receives instantaneous fraction strictly less than "
            "1.0, forcing completion time >= D_i whenever C_i / (w_i / W) > D_i even though total CPU remains idle "
            "later—confirmed empirically in Case B1 and Case B2 where demand-weighted GS still missed deadlines "
            "while EDF succeeded with 0 misses. Q.E.D."
        ),
        rk.h1("15.3 Theorem 3 — RM Priority Starvation vs GS Guaranteed Lower Bound Under U > 1"),
        rk.para(
            "Proof Sketch: Under fixed-priority RM, whenever higher-priority tasks satisfy sum_{j in hp(k)} "
            "(C_j / T_j) >= 1.0, total higher-priority demand consumes 100% of every hyperperiod, forcing task k's "
            "share to 0 identically (Table 15: T3 receives 0 ticks!). Under GS VTime, every runnable task's virtual "
            "clock only increases when it runs, guaranteeing at least w_k / W fraction of total cycles. Q.E.D."
        ),

        rk.h1("16.4 Theorem 4 — Liu–Layland Bound Tightness & Bini Hyperbolic Refinement"),
        rk.para(
            "Statement: For n periodic tasks with equal individual utilizations (2^(1/n) - 1) and consecutive "
            "period ratios T_k = T_1 * 2^((k-1)/n), Rate Monotonic fully saturates the processor at exact threshold "
            "U = n*(2^(1/n) - 1); adding even an infinitesimal delta causes a deadline miss. However, when task "
            "utilizations are uneven—for instance u_1 = 0.60, u_2 = 0.25 giving U = 0.85 > 0.8284—Bini's Hyperbolic "
            "Bound verifies prod(1 + u_i) = (1.60)(1.25) = 2.00 <= 2.00, proving RM still succeeds cleanly!"
        ),
        rk.h1("16.5 Theorem 5 — Sub-Capacity Constrained Infeasibility & Processor Demand"),
        rk.para(
            "Statement: Whenever D_i < T_i is permitted, no utilization threshold U* > 0 is sufficient by itself "
            "to guarantee feasibility. Specifically, given arbitrarily small U_target > 0, setting n synchronous "
            "tasks with C_i = 1, D_i = n - 1, and large period T_i >> n forces U < U_target yet dbf(n-1) = n > n-1, "
            "causing every scheduler (GS, EDF, RM, and DM) to miss at least one deadline during [0, n-1]. Q.E.D."
        ),

        # =====================================================================
        # CHAPTER 17 — DEEP DIVE: KERNEL OVERHEAD, JITTER & APPLICATION MATRIX
        # =====================================================================
        rk.ptitle("17. Kernel Complexity, Cache Footprints & Real-World Domain Mapping"),
        rk.h1("17.1 Data-Structure Costs: O(1) Bitmasks vs O(log N) Trees & Heaps"),
        rk.para(
            "Even when two schedulers match in deadline success, their implementation complexity inside an OS "
            "kernel or RTOS differs sharply. Rate Monotonic and Deadline Monotonic assign fixed integer priorities "
            "at admission time, enabling O(1) dispatch via a single 64-bit integer readiness bitmask paired with "
            "per-priority FIFO rings (CTZ/FFS single CPU instruction). By contrast, both EDF (keyed on moving "
            "absolute deadlines d_k) and production GS (keyed on advancing virtual time v_i) require dynamic "
            "ordered queues (binary min-heaps or red-black trees) costing O(log N) per enqueue/rebalance."
        ),
        rk.table(
            ["Kernel Mechanism", "GS VTime (Heap)", "EDF (RB-Tree / Heap)", "RM / DM (Bitmask)"],
            [
                ["Ready Structure", "Binary min-heap + version array", "Red-black tree / min-heap", "64-bit word + static FIFO heads"],
                ["Pick Next Task", "O(1) stay or O(log N) pop", "O(1) leftmost RB peek", "O(1) single CTZ instruction"],
                ["Tick Accounting", "2 integer adds (V_fp, v_fp)", "1 decrement (runtime budget)", "1 decrement (time slice optional)"],
                ["Admission / Join", "O(log N) anchor at V_fp", "O(N) dbf check + O(log N) push", "O(N * iter) RTA + bitmask slot"],
                ["Hardware Cache Effect", "Higher switch rate unless stay/q>=2", "Low switches (releases only)", "Minimal switches; zero top jitter"],
            ],
            widths=[3.2, 4.6, 4.6, 4.8],
            caption="Kernel implementation overhead and data-structure comparison across GS, EDF, and RM/DM.",
        ),
        rk.h1("17.2 Response Jitter, Control Loop Stability & Case B2 Per-Task Telemetry"),
        rk.para(
            "In digital control loops (flight actuators, motor PWM inverters, medical ventilators), response-time "
            "jitter directly degrades phase margin and control stability. Table 39 compares per-task CPU "
            "allocations, worst response latency, preemptions, context switches, and response jitter across "
            "Case B2, showing why RM/DM shield short-period loops while EDF trades modest jitter for optimality."
        ),
        rk.table(
            ["Policy", "CPU (T1/T2/T3)", "Missed/Rel.", "Worst Resp.", "Jitter", "Preemptions", "Switches"],
            gd.b2_per_task_comparison_rows(d),
            widths=[2.8, 3.4, 2.3, 2.2, 1.9, 2.3, 2.3],
            caption="Per-policy Case B2 response latency, jitter, preemption, and switch trade-off profile [E].",
        ),
        rk.h1("17.3 Real-World System Selection Guide Across 10 Engineering Domains"),
        rk.table(
            ["Application Domain", "Primary Metric", "Best Policy", "Technical Justification"],
            [
                ["Avionics / ABS Hard Control", "Worst-case predictability", "RM / DM + PCP", "O(1) bitmask, deterministic RTA proof, zero top-task jitter"],
                ["Automotive ADAS Sensor Fusion", "High-U constrained D<=T", "EDF + CBS", "Hits near-100% capacity while CBS isolates sensor overruns"],
                ["Cloud Container CPU Quotas", "Weighted fairness & scaling", "GS VTime (O(log N))", "Exact proportional shares, dynamic join V(t), 113x heap scaling"],
                ["Interactive Linux Desktop", "Fair share + wakeup latency", "GS Capped / EEVDF", "Protects steady tasks from sleepers while granting instant UI wakes"],
                ["Real-Time Audio / Video DSP", "Bounded latency + overload grace", "CBS + EDF (Hybrid)", "Guarantees frame deadlines below U=1 and smooth throttling above U=1"],
                ["Database OLTP Thread Pool", "Zero starvation & cache warm", "GS Stay + q>=2", "Stay hysteresis eliminates half of switches while protecting tail shares"],
                ["Ultra-Low-Power MCU IoT", "RAM footprint (< 1 KB)", "RM static bitmask", "Requires no dynamic tree pointers or 64-bit virtual clock division"],
                ["Multi-Tenant GPU/Batch Queue", "Weighted share conservation", "GS Entitled / Stride", "Strict proportional accounting without deadline assumptions"],
            ],
            widths=[4.4, 3.4, 3.6, 5.8],
            caption="Domain-by-domain engineering selection guide synthesizing GS, EDF, RM/DM, and hybrid CBS+EDF.",
        ),

        # =====================================================================
        # CHAPTER 18
        # =====================================================================
        rk.ptitle("18. Independent Audit Protocol, Test Gateways & Reproducibility"),
        rk.para(
            "Every mathematical invariant, exhaustive DFS verification, independent trace check, diagram, and "
            "report claim in Exercise 2 is guarded automatically by exercise-2/tests/test_ex2.py and "
            "tests/test_gs_core.py. Below is the tail implementation of the independent trace verifier followed "
            "by the complete verification matrix (Table 41) and Exercise 2 artifact map (Table 42)."
        ),
        rk.code(gd.core_snippet(1000, 1025),
                caption="Independent schedule audit check lines 1000–1025 in core/gs_core.py verifying zero missed deadlines."),
        rk.table(
            ["Verification Gate", "Scope / Input", "Mathematical Contract Enforced"],
            [
                ["test_vendored_core_matches_canonical", "SHA / byte parity", "exercise-2/code/gs_core.py == core/gs_core.py verbatim"],
                ["Regime A Equivalence Assertion", "Static weighted [1, 2, 4]", "gs_ratio == gs_vtime == stride lag < RR lag strictly"],
                ["Case B1 Separation Proof", "T1(2,4,4), T2(2,6,3)", "Exhaustive feasible == True; DM passes (0 miss); RM fails (>0)"],
                ["Case B2 Optimality Proof", "U=0.9583, H=24", "EDF 0 misses; DM and GS w~C/D miss deadlines"],
                ["Case B3 Sub-Unity Proof", "U=0.600 < 1.0", "Exhaustive feasible == False across entire search tree"],
                ["120-Set & 30-Set Exhaustive Audit", "4 U-bands x 30 sets", "EDF matches exhaustive DFS optimum on 30/30 (100.0%)"],
                ["Regime C Overload Proof", "U=1.3333 matched & asym", "RM starves T3 (min_share=0.0); GS preserves high Jain equity"],
                ["Independent Trace Verifier", "All zero-miss schedules", "Independent deadline check passes 100% of zero-miss runs"],
                ["Report & Visual Quality Gate", "8 diagrams + EN/FA PDFs", "Zero overflow, zero missing glyphs, 40+ dense pages"],
            ],
            widths=[4.8, 3.6, 8.8],
            caption="Complete automated verification contract enforced by pytest for Exercise 2.",
        ),
        rk.table(
            ["Deliverable Path", "Technical Content", "Automated Verification Gate"],
            [
                ["exercise-2/code/gs_core.py", "Byte-identical Fraction GS + RT + DFS engine", "SHA parity + 28 unit tests"],
                ["exercise-2/code/run_experiments.py", "Regime A, B1–B3, 120-set sweep, 30-set DFS, Regime C", "Invariant + independent RT verifier"],
                ["exercise-2/code/make_diagrams.py", "8 publication-grade Okabe-Ito comparative plots", "Existence, byte size & visual audit"],
                ["exercise-2/docs/REPORT_{EN,FA}.{pdf,docx}", "40+ page dense bilingual comparative monographs", "Zero overflow, zero missing glyphs, 40+ pages"],
            ],
            widths=[4.8, 6.4, 6.0],
            caption="Complete Exercise 2 artifact map and automated verification gates.",
        ),
        rk.para(
            "Executive Synthesis: Across every benchmarked dimension—aperiodic proportional lag (Regime A), "
            "constrained-deadline feasibility across 120 task sets and 30 exhaustive DFS audits (Regime B), "
            "sustained overload survival at U = 1.3333 and U = 1.1357 (Regime C), response-time jitter, "
            "priority-inversion lock protocols, multicore scalability, and kernel dispatch cost—Guaranteed "
            "Scheduling, Earliest Deadline First, and Rate Monotonic trace an exact Pareto frontier rather than "
            "a single linear hierarchy. Guaranteed Scheduling serves as the proportional bandwidth reference, "
            "EDF acts as the dynamic real-time optimum, RM/DM deliver O(1) fixed-priority predictability, and "
            "CBS + EDF unifies deadline guarantees with proportional overload containment."
        ),
        rk.code([
            "python3 exercise-2/code/run_experiments.py  # regenerates all Regimes A/B/C + 120-set sweep",
            "python3 exercise-2/code/make_diagrams.py    # builds all 8 high-DPI comparative diagrams",
            "python3 tools/build_report.py gs2_en exercise-2 REPORT_EN",
            "python3 tools/build_report.py gs2_fa exercise-2 REPORT_FA",
            "python3 -m pytest exercise-2/tests -v",
        ], caption="Complete end-to-end reproduction sequence for Exercise 2."),
    ]

    rep.pack_flow(blocks, figures_dir=fig_dir, max_fill=0.89)
    return rep
