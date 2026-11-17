"""Exercise 6 English Capstone Monograph: Unified CPU Scheduling, Sync & Readers-Writers."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, HERE)

import report_kit as rk  # noqa: E402
import ex6_data as ed  # noqa: E402


def build() -> rk.Report:
    d = ed.load()
    pi = {r["mode"]: r for r in d["priority_inversion_audits"]}
    pipe = {f"{r['primitive']}_{r['policy']}": r for r in d["rt_rw_pipeline"]}
    hyb = d["gs_rt_hybrid"]
    ms = d["cross_exercise_milestones"]
    fig_dir = os.path.join(REPO_ROOT, "exercise-6", "diagrams")

    rep = rk.Report(
        title="Exercise 6: Integrated Real-Time Scheduling, Synchronization & Readers-Writers Capstone",
        subtitle="Unified Systems Engineering Monograph Connecting Guaranteed Scheduling (Ex 1-2), Hard Real-Time RM/EDF (Ex 3), Mutual Exclusion & BFS Verification (Ex 4), and Readers-Writers (Ex 5) Through Priority Inheritance (PIP), Spin-Lock Deadlock Audits & Live RT Pipelines",
        lang="en",
        rtl=False,
        cover_meta=[
            ("Repository", "ZaraNodehi/Guaranteed-Scheduling"),
            ("Deliverable", "Exercise 6 — Capstone Integration Monograph, Slide Decks & Speaker Scripts"),
            ("Core Experiments", "Mars Pathfinder Priority Inversion (PIP vs. No-PIP vs. Spin) + Live 5-Thread RT RW Pipeline"),
            ("Companion Decks", "PRESENTATION_EN.pptx, PRESENTATION_FA.pptx & SPEAKER_SCRIPT_{EN,FA}.md (10 Slides)"),
        ],
    )

    rep.page(rk.cover(rep.cover_meta))
    rep.page(rk.toc())

    blocks = [
        # =====================================================================
        # CHAPTER 1
        # =====================================================================
        rk.ptitle("1. Capstone Executive Synthesis Across Exercises 1 Through 6"),
        rk.para(
            "Operating-systems textbooks normally isolate CPU scheduling from concurrency control: chapters 5-6 analyze "
            "CPU queues assuming independent runnable jobs, while chapters 7-8 analyze mutexes, semaphores, monitors, "
            "and Readers-Writers assuming benign scheduler behavior. In real kernels, however, the scheduler and the "
            "synchronizer collide every millisecond—producing catastrophic anomalies such as unbounded priority "
            "inversion (infamously resetting NASA's 1997 Mars Pathfinder spacecraft), preemptive spin-lock deadlocks, "
            "and real-time tail-latency collapse behind coarse serial locks."
        ),
        rk.para(
            "Exercise 6 unifies all six modules of this repository inside an integrated experimental testbed. By "
            "coupling Exercise 1-3 schedulers (Guaranteed Scheduling, Rate Monotonic, Earliest Deadline First) with "
            "Exercise 4-5 locks (Peterson, Dekker, Semaphore, Mesa Monitor, and 3-policy Readers-Writers), we "
            "quantify four fundamental scheduler-lock interactions:"
        ),
        rk.kv([
            ("Priority Inversion Rescue", f"Without PIP, T_Medium blocked T_High for {pi['no_pip']['high_blocked_ticks']} ticks ({pi['no_pip']['high_misses']} miss, max resp {pi['no_pip']['high_max_response_ticks']}); PIP cut blocking to {pi['pip']['high_blocked_ticks']} ticks (0 misses, max resp {pi['pip']['high_max_response_ticks']})"),
            ("Preemptive Spin-Lock Deadlock", f"Under preemptive priority scheduling, spinning T_High on Peterson held by T_Low burned {pi['spin_hazard']['spin_stall_ticks']} ticks and missed {pi['spin_hazard']['high_misses']} deadlines"),
            ("Live 5-Thread RT + RW Pipeline", f"CoarseMutex collapsed RT deadline hits (D=1.6 ms) to {pipe['CoarseMutex_serial']['rt_hit_rate_pct']:.2f}% ({pipe['CoarseMutex_serial']['total_throughput_ops_s']:,.0f} ops/s); blocking RW achieved 100.00% hits (~3,450-3,556 ops/s)"),
            ("Cross-Repo Milestones", f"Ex 3 Set B (RM {ms['ex3_rm_misses_set_b']} vs. EDF {ms['ex3_edf_misses_set_b']}), Ex 4 Dekker v5 ({ms['ex4_dekker_v5_states']} BFS states, TSO Peterson {ms['ex4_peterson_tso_errors']} errs), Ex 5 RW {ms['ex5_rw_max_speedup_95']}x speedup"),
        ]),
        rk.image("ex6_fig6_end_to_end_architecture.png", width_cm=16.8,
                 caption="End-to-end architecture connecting Exercises 1 through 6 into a single verified kernel model."),

        # =====================================================================
        # CHAPTER 2
        # =====================================================================
        rk.ptitle("2. Mars Pathfinder Priority Inversion & Priority Inheritance Protocol (PIP)"),
        rk.para(
            "Consider three periodic real-time threads sharing one CPU and one blocking mutex M: T_Low (prio 1, locks "
            "M for 4 ticks at release), T_High (prio 3, deadline 8, wakes at t=2 needing M after 1 tick), and "
            "T_Medium (prio 2, pure CPU loop waking at t=3). Under fixed-priority RM without inheritance, T_Low "
            "never regains the CPU while T_Medium runs, creating unbounded priority inversion and breaking T_High's "
            "deadline at t=10. Under the Priority Inheritance Protocol (PIP), T_Low transiently inherits prio(T_High)=3 "
            "the instant T_High blocks on M, completes its critical section at t=5, and lets T_High finish at t=7."
        ),
        rk.formula(
            "No-PIP Bound:   B_high  =  C_low_rem  +  sum_{j in Medium} C_j   [Unbounded by intermediate jobs!]\n"
            "PIP Bound:      B_high  =  max_{k in LowerLocks} C_crit(k)      [Bounded to 1 critical section!]"
        ),
        rk.image("ex6_fig1_priority_inversion_timeline.png", width_cm=16.8,
                 caption="Discrete-tick trace of the Mars Pathfinder scenario: No-PIP misses at t=10 vs. PIP rescue at t=7."),
        rk.image("ex6_fig2_spin_vs_pip_comparison.png", width_cm=16.8,
                 caption="Quantitative comparison of blocking delay, spin deadlock stalls, and missed deadlines across lock policies."),
        rk.table(
            ["Scheduler-Lock Mode", "Total Misses", "T_High Misses", "T_High Block Ticks", "Spin Stall Ticks", "T_High Max Resp"],
            ed.pi_rows(d),
            widths=[3.6, 2.4, 2.6, 2.8, 2.8, 3.0],
            caption="Discrete-tick (H=60) Priority Inversion, PIP, and Spin-Hazard comparison.",
        ),

        # =====================================================================
        # CHAPTER 3
        # =====================================================================
        rk.ptitle("3. Live 5-Thread Real-Time Control + Readers-Writers Telemetry Pipeline"),
        rk.para(
            "To test whether Readers-Writers locks improve real-time deadline adherence under concurrent data-plane "
            "traffic, we deployed 3 telemetry readers (0.35 ms scans), 1 route writer (0.8 ms exclusive updates), and "
            "1 deadline-sensitive RT control thread (D = 1.6 ms) sharing a protected routing table across 7 backends."
        ),
        rk.image("ex6_fig3_rw_rt_pipeline.png", width_cm=16.8,
                 caption="Live 5-thread RT pipeline: CoarseMutex collapses to 14.3% RT hit rate vs. 100.0% on blocking Fair RW locks."),
        rk.table(
            ["Backend (Policy)", "RT Hit Rate", "Mean Lat (ms)", "P95 Lat (ms)", "Max Lat (ms)", "Throughput (ops/s)"],
            ed.pipe_rows(d),
            widths=[3.6, 2.4, 2.6, 2.6, 2.6, 3.4],
            caption="Live 5-thread telemetry + RT control measurements (D = 1.6 ms across 200 ms run).",
        ),

        # =====================================================================
        # CHAPTER 4
        # =====================================================================
        rk.ptitle("4. Bridging Fairness & Deadlines: RM vs. EDF vs. Guaranteed Scheduling"),
        rk.para(
            "On the Exercise 3 Set B workload (utilization U = 0.9583 > Liu-Layland bound LL(3) = 0.7798), static Rate "
            "Monotonic misses 1 deadline (worst response 10 ticks), whereas EDF and Weighted Guaranteed Scheduling "
            "(vtime:stay) both hit 0 deadline misses (worst response 7 ticks)—with GS achieving the highest Jain "
            f"fairness index ({hyb['gs_vtime:stay']['jain_fairness']:.4f} vs. {hyb['edf']['jain_fairness']:.4f} for EDF)."
        ),
        rk.image("ex6_fig4_hybrid_gs_rt.png", width_cm=16.8,
                 caption="Exercise 1-3 bridge comparing deadline compliance, worst response time, and Jain proportional equity."),
        rk.table(
            ["Policy", "Utilization U", "Deadline Misses", "Worst Response", "Context Switches", "Jain Fairness"],
            ed.gs_hybrid_rows(d),
            widths=[3.4, 2.8, 2.6, 2.8, 2.8, 2.8],
            caption="Unified RT + GS metrics on the Set B periodic task triad (H = 24 ticks).",
        ),

        # =====================================================================
        # CHAPTER 5
        # =====================================================================
        rk.ptitle("5. Unified Operating Systems Decision Architecture & Kernel Code"),
        rk.image("ex6_fig5_capstone_radar.png", width_cm=16.8,
                 caption="Five-axis architectural scorecard across integrated CPU scheduler + lock combinations."),
        rk.table(
            ["Workload Profile", "Recommended Scheduler", "Recommended Sync / Lock", "Verified Evidence"],
            [
                ["Interactive / Multi-Tenant CPU", "Exact Rational GS + Wakeup Cap", "Per-task private / Ticket Mutex", "Jain 0.990+, Ex 1-2"],
                ["Hard Real-Time Periodic (U <= 1)", "EDF + Admission Control", "Blocking Monitor + PIP / SRP", "0 misses at U=0.958, Ex 3+6"],
                ["Producer-Consumer Bounded Q", "CFS / Preemptive Blocking OS", "Mesa Monitor ('while' loop)", "0 underflows, 1% CPU, Ex 4"],
                ["Read-Heavy Routing / Config", "Preemptive Fair Scheduler", "Ticket Monitor RW / RCU", "4.03x speedup, no barging, Ex 5-6"],
            ],
            widths=[4.2, 4.4, 4.4, 4.2],
            caption="Production OS engineering prescription matrix distilled from Exercises 1 through 6.",
        ),
        rk.code(ed.code_slice("exercise-6/code/integrated_kernel.py", 75, 111),
                caption="Priority Inheritance Protocol (PIP) priority boost & blocking logic (integrated_kernel.py, lines 75-111)."),
        rk.code(ed.code_slice("exercise-6/code/integrated_kernel.py", 120, 156),
                caption="Preemptive Spin-Lock deadlock hazard vs. lock acquisition (integrated_kernel.py, lines 120-156)."),
        rk.code(ed.code_slice("exercise-6/code/integrated_kernel.py", 197, 234),
                caption="Live 5-thread RT Control + Readers-Writers telemetry pipeline benchmark (lines 197-234)."),
        rk.table(
            ["Exercise 6 Deliverable", "Role", "Status"],
            [
                ["exercise-6/code/integrated_kernel.py", "PIP + Spin-Hazard + Live RT/RW + GS-RT Bridge", "Verified"],
                ["exercise-6/code/run_experiments.py", "Unified experiments & 10-slide bilingual deck spec", "experiments.json built"],
                ["exercise-6/code/plot_diagrams.py", "6 Okabe-Ito Capstone diagrams", "All 6 PNGs verified"],
                ["exercise-6/docs/REPORT_EN / FA (.pdf, .docx)", "Capstone bilingual monographs", "Zero overflow / glyphs"],
                ["exercise-6/docs/PRESENTATION_EN / FA.pptx", "10-slide 16:9 executive decks + speaker notes", "Built via make_decks.py"],
                ["exercise-6/docs/SPEAKER_SCRIPT_EN / FA.md", "Full bilingual presenter scripts", "Synchronized 10 slides"],
            ],
            widths=[6.8, 6.4, 4.0],
            caption="Complete Exercise 6 Capstone artifact inventory.",
        ),
    ]

    rep.pack_flow(blocks, figures_dir=fig_dir, max_fill=0.89)
    return rep
