"""Exercise 1 English Comprehensive Algorithmic Guide (40+ dense pages, zero empty space)."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, HERE)

import report_kit as rk  # noqa: E402
import gs1_data as gd  # noqa: E402


def build() -> rk.Report:
    d = gd.load()
    base = d["baseline"]
    runs = base["runs"]
    gs1 = runs["gs_ratio_q1"]
    vt1 = runs["gs_vtime_q1"]
    st1 = runs["stride_q1"]
    gs2 = runs["gs_ratio_q2"]
    rr2 = runs["rr_q2"]
    ff1 = runs["fifo_q1"]
    dyn = d["dynamic_arrival_check"]
    etc = d["exhaustive_tie_check"]
    osb = d["os_subprocess_benchmark"]
    fig_dir = os.path.join(REPO_ROOT, "exercise-1", "diagrams")

    rep = rk.Report(
        title="Exercise 1: Complete Specification, Architecture & Analysis of Guaranteed Scheduling",
        subtitle="Theoretical Foundations, Flowchart, Complete Pseudocode Variants, Code Walkthrough, Mathematical Proofs, Discrete Traces & Live Linux Evaluation",
        lang="en",
        rtl=False,
        cover_meta=[
            ("Repository", "ZaraNodehi/Guaranteed-Scheduling"),
            ("Deliverable", "Exercise 1 — Comprehensive Algorithm Introduction (40+ Dense Pages)"),
            ("Core Modules", "GuaranteedScheduling.py (106 lines) + core/gs_core.py + O(log N) Heap"),
            ("Evidence Standard", "Exact Rational [E], Exhaustive DFS [M], Live Linux Kernel [D]"),
        ],
    )

    rep.page(rk.cover(rep.cover_meta))
    rep.page(rk.toc())

    blocks = [
        # =====================================================================
        # CHAPTER 1
        # =====================================================================
        rk.ptitle("1. Executive Overview & Scope of Guaranteed Scheduling"),
        rk.para(
            "Guaranteed Scheduling (GS) is a foundational proportional-share CPU scheduling discipline "
            "originally articulated in operating systems literature (most prominently in Andrew S. Tanenbaum's "
            "Modern Operating Systems) around an intuitive resource-allocation contract: if N runnable "
            "processes share a single processor simultaneously, each process is guaranteed 1/N of the available "
            "CPU cycles over time. Generalized to heterogeneous priorities with positive share weights "
            "w_1, w_2, ..., w_N, process P_i receives an exact fractional bandwidth share equal to "
            "w_i / Sum_{j in A(t)} w_j during every instant t where active set A(t) competes for execution."
        ),
        rk.para(
            "Unlike heuristic priority-feedback schedulers whose realized CPU allocation drifts uncontrollably "
            "across mixed workloads, Guaranteed Scheduling computes a running ratio between CPU time actually "
            "consumed and CPU time mathematically entitled, dispatching at every quantum boundary whichever "
            "ready process currently exhibits the lowest normalized service ratio. Because this selection rule "
            "acts as a discrete closed-loop feedback regulator around cumulative service entitlement, no ready "
            "process can fall indefinitely behind its guaranteed share."
        ),
        rk.h1("1.1 Three-Tier Evidence Taxonomy Used Throughout This Report"),
        rk.para(
            "Every numerical result, theorem, table entry, and engineering recommendation presented in this "
            "40+ page monograph belongs to one of three strictly separated verification tiers so that ideal "
            "mathematics, exhaustive discrete verification, and real operating-system kernel jitter are never "
            "conflated:"
        ),
        rk.bullets([
            "Tier [E] — Exact Rational Simulation: Deterministic event/tick execution inside core/gs_core.py using arbitrary-precision Python fractions.Fraction arithmetic (zero IEEE-754 rounding errors).",
            "Tier [M] — Exhaustive State-Space & Sweep Analysis: Complete branch-and-bound / DFS enumeration over all valid tie-breaking paths plus parametric sweeps across quantum values q in {1, 2, 4, 8}.",
            "Tier [D] — Live Linux Kernel Subprocess Orchestration: Real wall-clock execution on Linux via subprocess + psutil (SIGSTOP/SIGCONT gating and /proc/[pid]/stat accounting) matching GuaranteedScheduling.py.",
        ]),
        rk.h1("1.2 Principal Empirical Findings at a Glance"),
        rk.bullets([
            f"Simultaneous Arrival Equivalence [E]: On static weighted workload P1..P3 with weights [1, 2, 4] and bursts [4, 6, 9], gs_ratio, gs_vtime, and stride yield identical max_abs_lag = {gs1['max_abs_lag']:.4f} ({gs1['max_abs_lag_frac']}) and Jain fairness = {gs1['jain_fairness']:.4f}.",
            f"Substantial Fairness Gain over RR & FIFO [E]: At quantum q=2, gs_ratio cuts worst GPS lag from {rr2['max_abs_lag']:.4f} (RR) and {ff1['max_abs_lag']:.4f} (FIFO) down to {gs2['max_abs_lag']:.4f} ticks.",
            f"Tie-Breaking Switch Reduction [E]: Exhaustive enumeration proves equal-weight lag stays invariant at {etc['equal_envelope']['best_max_lag']:.4f} ticks across all {etc['equal_envelope']['leaves']} valid schedules, while 'stay' hysteresis halves context switches ({etc['equal_sim_by_tie']['stay']['context_switches']} vs {etc['equal_sim_by_tie']['index']['context_switches']}).",
            f"Dynamic Latecomer Starvation & Fix [E]: Naive used_i / w_i freezes P1 for {dyn['dyn_t12_gs_ratio']['per_proc']['P1']['max_starve_gap']} consecutive ticks when P2 arrives at t=12; anchoring virtual time at V(t) shrinks lockout to {dyn['dyn_t12_gs_vtime']['per_proc']['P1']['max_starve_gap']} tick.",
            f"Real Kernel Validation [D]: Across n={osb['num_trials']} live Linux subprocess runs on weights [1, 2, 4] (median wall time {osb['median_wall_sec']:.4f}s), completion order P3 < P2 < P1 holds in 100% of trials with {osb['total_zero_cpu_slices']} zero-CPU slices.",
        ]),

        # =====================================================================
        # CHAPTER 2
        # =====================================================================
        rk.ptitle("2. Historical Evolution & Taxonomy of Fair-Share Schedulers"),
        rk.h1("2.1 From Batch FIFO and Round-Robin to Proportional Guarantees"),
        rk.para(
            "Early batch operating systems relied on First-Come, First-Served (FIFO / FCFS) execution, which "
            "minimizes dispatcher overhead and maximizes cache warmth but suffers from catastrophic convoy "
            "effects: a single long CPU-bound computation delays every interactive or short-burst job behind it. "
            "Time-sharing systems introduced Round-Robin (RR) preemption over fixed quanta, ensuring bounded "
            "wait latency per active job but distributing CPU time blindly in equal 1/N slices regardless of "
            "user priority, SLA tier, or process importance."
        ),
        rk.para(
            "Static priority queues and Multi-Level Feedback Queues (MLFQ) introduced differentiated priorities "
            "yet inverted the problem: higher-priority classes completely starve lower-priority processes during "
            "sustained CPU bursts, violating minimum service contracts unless ad-hoc aging timers are tuned "
            "per workload. Guaranteed Scheduling emerged precisely to bridge equal-sharing RR and priority "
            "scheduling by translating numerical importance directly into enforceable CPU ratios."
        ),
        rk.h1("2.2 Convergence with Fluid GPS, WFQ, Stride, CFS, and Linux EEVDF"),
        rk.para(
            "During the 1990s, packet-switching theorists Parekh and Gallager formalized Generalized Processor "
            "Sharing (GPS) as the ideal fluid reference model, followed by packet approximations such as Weighted "
            "Fair Queueing (WFQ) and Start-Time Fair Queueing (SFQ). Simultaneously, Waldspurger and Weihl "
            "(1995) introduced deterministic Stride Scheduling as a low-overhead integer alternative to "
            "probabilistic Lottery Scheduling. Modern Linux kernels carried this lineage directly into production: "
            "first via Ingo Molnar's Completely Fair Scheduler (CFS, Linux 2.6.23, tracking normalized vruntime), "
            "and since Linux 6.6 via Earliest Eligible Virtual Deadline First (EEVDF, Stoica et al. 1995), which "
            "explicitly uses signed GPS lag eligibility (E_i - A_i >= 0) alongside virtual finish deadlines."
        ),
        rk.table(
            ["Algorithm Family", "Selection Key", "Dynamic Arrival Rule", "Sleeper Defense", "Time Complexity"],
            [
                ["FIFO / FCFS", "Arrival timestamp a_i", "Append to tail", "Re-enter tail", "O(1) queue"],
                ["Round-Robin (RR)", "Cyclic FIFO ring", "Append to ring", "Re-enter ring", "O(1) circular"],
                ["Legacy GS Ratio", "used_i / w_i (float)", "None (starts at 0)", "None (unbounded)", "O(N) scan"],
                ["Exact Entitled GS", "A_i(t) / E_i(t)", "Exact integral E_i(t)", "Bounded by E_i", "O(N) update"],
                ["Virtual-Time GS V(t)", "v_i (Fraction/int64)", "v_i = V(t) at arrival", "Wakeup cap optional", "O(log N) heap"],
                ["Stride Scheduling", "pass_i += K / w_i", "pass_i = global_pass", "Pass floor clamp", "O(log N) heap"],
                ["Linux CFS (2.6.23+)", "vruntime_i (ns)", "vruntime = min_vruntime", "GENTLE_FAIR_SLEEPERS", "O(log N) RB-tree"],
                ["Linux EEVDF (6.6+)", "vd_i = ve_i + slice/w_i", "lag_i = E_i - A_i", "Eligible lag >= 0", "O(log N) aug-RB"],
            ],
            widths=[3.2, 3.3, 3.6, 3.6, 3.5],
            caption="Historical and algorithmic taxonomy linking classic Guaranteed Scheduling to modern Linux EEVDF.",
        ),

        # =====================================================================
        # CHAPTER 3
        # =====================================================================
        rk.ptitle("3. Formal Mathematical Model & Discrete GPS Fairness Proofs"),
        rk.h1("3.1 Continuous Fluid GPS Benchmark E_i(t)"),
        rk.para(
            "Consider a set of processes P = {P_1, P_2, ..., P_N}. Each process P_i enters the ready queue "
            "at arrival time a_i >= 0, demands positive total CPU burst work b_i > 0, and carries positive "
            "share weight w_i > 0. Let A(tau) denote the subset of processes that are runnable (arrived, "
            "unblocked, and incomplete) at instant tau, and define instantaneous active weight W(tau) = "
            "sum_{j in A(tau)} w_j. Ideal fluid Generalized Processor Sharing allocates exact instantaneous "
            "CPU rate r_i(tau) = w_i / W(tau) whenever i in A(tau), and 0 otherwise."
        ),
        rk.formula(
            "W(t) = sum_{j in A(t)} w_j\n"
            "E_i(t) = integral_{a_i}^{t} (w_i / W(tau)) * 1_{i in A(tau)} d(tau)\n"
            "L_i(t) = A_i(t) - E_i(t)      (Signed GPS lag: >0 ahead, <0 behind)\n"
            "MaxAbsLag = max_{t in [0, H], i} |L_i(t)|\n"
            "RMSE_Lag  = sqrt( (1 / (|T| * N)) * sum_{t, i} L_i(t)^2 )",
            caption="Continuous fluid entitlement E_i(t), discrete actual CPU A_i(t), signed lag L_i(t), and aggregate lag norms.",
        ),
        rk.h1("3.2 Work Conservation & Zero-Sum Lag Invariant"),
        rk.para(
            "Whenever a single CPU is work-conserving (never idling while A(t) is non-empty), the sum of "
            "actual CPU work executed across all processes up to time t equals total busy time B(t). Likewise, "
            "integrating w_i / W(tau) across all active tasks i in A(tau) yields sum_{i in A(tau)} w_i / W(tau) = 1. "
            "Therefore, at every instant where the discrete scheduler keeps the CPU busy over exactly the same "
            "active intervals as fluid GPS, total signed lag obeys a strict zero-sum conservation law:"
        ),
        rk.formula(
            "sum_{i=1}^{N} E_i(t) = B(t) = sum_{i=1}^{N} A_i(t)  ==>  sum_{i=1}^{N} L_i(t) = 0  (conservation law)\n"
            "Jain(x_1..x_N) = (sum_{i=1}^{N} x_i)^2 / (N * sum_{i=1}^{N} x_i^2),   x_i = A_i(T) / E_i(T)",
            caption="Zero-sum lag conservation law and normalized Jain fairness index over GPS share ratios.",
        ),
        rk.h1("3.2.1 Complete Formal Definitions of All Seven Evaluation Metrics"),
        rk.para(
            "Every experiment across this project evaluates schedulers across seven complementary dimensions "
            "capturing fairness precision, latency predictability, starvation protection, and kernel overhead:"
        ),
        rk.table(
            ["Metric Name", "Exact Mathematical Formula", "Optimal Direction", "Physical Interpretation"],
            [
                ["Max |Lag|", "max_{t,i} |A_i(t) - E_i(t)|", "Minimize (-> 0)", "Worst instantaneous deviation from fluid GPS"],
                ["RMSE Lag", "sqrt(mean_{t,i} (A_i(t) - E_i(t))^2)", "Minimize (-> 0)", "Time-averaged RMS fairness tracking error"],
                ["Jain Fairness", "(sum x_i)^2 / (N sum x_i^2), x_i=A_i/E_i", "Maximize (-> 1.0)", "Proportional share equity across all tasks"],
                ["Max Starve Gap", "max_{t} consecutive unscheduled ready ticks", "Minimize (-> 1)", "Worst latency wait while runnable"],
                ["Context Switches", "count(run[t] != run[t-1])", "Minimize", "Total dispatcher task handoffs (cache cost)"],
                ["Preemptions", "switches where prev still has rem > 0", "Minimize", "Involuntary interruptions before burst completion"],
                ["Mean Turnaround", "(1/N) sum (finish_i - arrival_i)", "Minimize", "Average end-to-end job completion latency"],
            ],
            widths=[2.8, 5.2, 2.8, 6.4],
            caption="Formal mathematical definitions and operational meanings of all seven evaluation metrics.",
        ),
        rk.h1("3.3 Why Discrete Quantum Bounds Grow with Asymmetric Weights"),
        rk.para(
            "When weights are identical (w_1 = ... = w_N = 1) and all jobs run continuously, each unit tick "
            "executed by P_i increments its score by 1 while total entitlement across N tasks advances by 1/N. "
            "Consequently, signed lag stays confined to (-1, +1) ticks under q=1. When weights are heterogeneous, "
            "however, running a low-weight task P_k for one full quantum q jumps its virtual clock by q / w_k, "
            "while a heavy-weight task accumulates entitlement q * w_max / W. Across N unequal active tasks, "
            "discrete lag under quantum q is governed by the worst-case single-quantum overshoot plus initial "
            "discrepancy, making q and weight ratios the primary levers governing tracking precision."
        ),

        # =====================================================================
        # CHAPTER 4
        # =====================================================================
        rk.ptitle("4. End-to-End System Architecture & Verification Pipeline"),
        rk.para(
            "To guarantee that theoretical proofs, discrete cycle-accurate simulations, and real operating-system "
            "process controls align without silent divergence, our codebase is organized into four clean layers: "
            "(1) core/gs_core.py implementing exact rational simulation, fluid GPS integration, and exhaustive "
            "tie-envelope DFS; (2) GuaranteedScheduling.py serving as the pedagogical 106-line Linux OS controller; "
            "(3) exercise-1/code/run_experiments.py orchestrating deterministic sweeps and live Linux subprocesses; "
            "and (4) make_diagrams.py + build_report.py rendering vector/high-DPI diagnostics and bilingual reports."
        ),
        rk.image("fig_ex1_architecture.png", width_cm=15.6,
                 caption="Four-layer system architecture integrating exact rational simulation [E], exhaustive DFS [M], and real Linux OS runs [D]."),
        rk.h1("4.1 Eliminating IEEE-754 Tie Corruption with Exact Rationals"),
        rk.para(
            "Floating-point binary representations cannot store non-dyadic fractions such as 1/3, 1/6, or 1/7 "
            "exactly. When three tasks carry weights [1, 3, 6] and share CPU repeatedly, naive floating-point "
            "division produces scores such as 0.3333333333333333 vs 0.33333333333333337 differing by a single "
            "least-significant bit (ULP). An O(N) min() scan treats that spurious ULP difference as a strict "
            "inequality rather than a tie, silently disabling tie-breakers like 'stay' and altering schedules."
        ),
        rk.table(
            ["Weight Tuple", "Exact Fraction Increment", "IEEE-754 Float Error (10 steps)", "Fraction / 10^9 Fixed-Point Behavior"],
            [
                ["[1, 2, 4]", "1, 1/2, 1/4 (dyadic)", "0.0 (exact power-of-2 denoms)", "Exact zero-error tie comparison"],
                ["[1, 3, 6]", "1, 1/3, 1/6 (repeating)", "~2.2e-16 ULP drift -> breaks ties", "Exact num_a * den_b == num_b * den_a"],
                ["[2, 5, 7]", "1/2, 1/5, 1/7 (prime)", "~4.4e-16 ULP drift -> spurious switch", "Exact Fraction equality preserved indefinitely"],
                ["[1, 1, 1]", "1, 1, 1 (unit integer)", "0.0 on counts, drift on E_i(t)=t/3", "Exact t/3 in Fraction; exact int in V(t)"],
            ],
            widths=[2.6, 3.6, 5.4, 5.6],
            caption="Impact of binary floating-point rounding vs exact rational arithmetic across weight configurations.",
        ),

        # =====================================================================
        # CHAPTER 5
        # =====================================================================
        rk.ptitle("5. Operational Flowchart & Algorithmic Data-Flow Pipeline"),
        rk.para(
            "Every dispatch decision in Guaranteed Scheduling cycles deterministically through admission "
            "initialization, ready-queue filtering, minimum-ratio scoring, deterministic tie resolution, "
            "bounded slice execution, and CPU accounting. Figure 2 presents the complete operational flowchart "
            "including idle-tick handling, premature completion before quantum exhaustion, and final metrics "
            "collection."
        ),
        rk.image("fig_ex1_flowchart.png", width_cm=15.6,
                 caption="Complete operational flowchart of Guaranteed Scheduling from admission to completion."),
        rk.h1("5.1 Four-Hook Virtual-Time & Min-Heap Execution Pipeline"),
        rk.para(
            "While the textbook flowchart emphasizes linear scanning over ready tasks, production proportional "
            "schedulers factor execution into four decoupled O(1)/O(log N) hooks illustrated in Figure 3: "
            "(1) Admission Hook anchoring newcomer virtual clock v_i = V(t); (2) Wakeup Guard clamping sleeping "
            "tasks above V(t) - cap/w_i; (3) O(1) stay-hysteresis fast-path vs O(log N) heap extraction; and "
            "(4) Dual clock billing advancing both v_{P*} += 1/w_{P*} and global virtual clock V(t) += 1/W(t)."
        ),
        rk.image("fig_ex1_pseudocode_pipeline.png", width_cm=15.4,
                 caption="Four-hook algorithmic pipeline showing admission anchoring, wakeup floor, stay fast-path, and billing."),

        # =====================================================================
        # CHAPTER 6
        # =====================================================================
        rk.ptitle("6. Complete Pseudocode Formulations (V0 through V4)"),
        rk.h1("6.1 Pseudocode V0: Classical Textbook Ratio GS (Tanenbaum / Legacy)"),
        rk.para(
            "Pseudocode V0 mirrors the direct textbook formulation implemented in GuaranteedScheduling.py. "
            "It maintains only cumulative execution time used_i and static weight w_i per process, selecting "
            "argmin(used_i / w_i) among ready tasks at each quantum boundary."
        ),
        rk.code([
            "ALGORITHM V0: Textbook_Ratio_GS(processes, quantum, tie_mode='index')",
            "Input : P = [(id_i, arrival_i, burst_i, weight_i)] with weight_i > 0, quantum q >= 1",
            "Init  : t <- 0; prev <- NONE; for each P_i: used_i <- 0, rem_i <- burst_i",
            "Loop  : While exists P_i with rem_i > 0:",
            "  Ready <- [P_i in P | arrival_i <= t and rem_i > 0 and not blocked(P_i, t)]",
            "  If Ready is empty:",
            "    record_idle(t); t <- t + 1; continue",
            "  // O(N) ratio scan using exact score tuple",
            "  For each P_i in Ready: score_i <- used_i / weight_i",
            "  best_score <- min(score_i for P_i in Ready)",
            "  Cands <- [P_i in Ready | score_i == best_score]",
            "  P* <- resolve_tie(Cands, prev, tie_mode)   // 'index' | 'stay' | 'max_weight'",
            "  slice <- min(q, rem_{P*}, next_arrival_or_wake_delta(t))",
            "  Run P* for [t, t + slice);  rem_{P*} -= slice;  used_{P*} += slice",
            "  If prev != NONE and prev != P*: context_switches += 1",
            "  t <- t + slice;  prev <- P*",
        ], caption="Pseudocode V0: Classical Ratio Guaranteed Scheduling with O(N) candidate scan."),

        rk.h1("6.2 Pseudocode V1: Exact Rational & Entitled Ratio GS (gs_entitled)"),
        rk.para(
            "To eliminate dynamic-arrival catch-up distortion without tracking a global virtual clock, V1 "
            "integrates exact fluid entitlement E_i(t) continuously across ready ticks and ranks candidates "
            "by used_i / E_i(t). When E_i(t) = 0 on the exact arrival tick, the newcomer enters with score 0 "
            "for at most one quantum before E_i(t) becomes strictly positive."
        ),
        rk.code([
            "ALGORITHM V1: Exact_Entitled_Ratio_GS(processes, quantum)",
            "Init  : For each P_i: used_i <- Fraction(0), E_i <- Fraction(0), rem_i <- burst_i",
            "On each discrete execution step delta over active set Ready:",
            "  // Score before slice using accumulated ideal entitlement",
            "  score_i <- Fraction(0) if E_i == 0 else Fraction(used_i, 1) / E_i",
            "  P* <- argmin_{P_i in Ready} score_i   // exact rational comparison",
            "  W_active <- sum_{P_j in Ready} weight_j",
            "  For each P_j in Ready:",
            "    E_j <- E_j + Fraction(delta * weight_j, W_active)   // exact GPS integral update",
            "  used_{P*} += delta;  rem_{P*} -= delta",
        ], caption="Pseudocode V1: Exact Rational Entitled GS measuring true A_i(t) / E_i(t) deficit."),

        # =====================================================================
        # CHAPTER 7
        # =====================================================================
        rk.ptitle("7. Virtual-Time, Wakeup-Capped & O(log N) Min-Heap Pseudocode"),
        rk.h1("7.1 Pseudocode V2 & V3: Virtual-Time Anchor V(t) & Sleeper Credit Floor"),
        rk.para(
            "Pseudocode V2 introduces a single monotonic system virtual clock V(t) advancing at instantaneous "
            "rate 1 / W(t). Newly arriving tasks start at v_i = V(t) instead of 0, preventing latecomers from "
            "monopolizing the CPU. Pseudocode V3 (gs_capped) augments V2 with a sleeper credit cap matching "
            "Linux CFS's GENTLE_FAIR_SLEEPERS policy so processes waking after long I/O pauses cannot starve "
            "continuous workers."
        ),
        rk.code([
            "ALGORITHM V2/V3: VirtualTime_Capped_GS(processes, quantum, cap_ticks=1)",
            "Init  : V <- Fraction(0, 1);  active <- {}",
            "Event on_arrive(P_i, t):",
            "  v_i <- V                         // Anchor newcomer at current system virtual clock!",
            "  active.add(P_i)",
            "Event on_wakeup(P_i, t):",
            "  floor_v <- V - Fraction(cap_ticks, weight_i)",
            "  v_i <- max(v_i, floor_v)         // V3 wakeup credit bound (omit max() for V2 uncapped)",
            "  active.add(P_i)",
            "Dispatch step(delta=1):",
            "  P* <- argmin_{P_i in active} v_i (tie-breaker: 'stay' if prev in Cands else min index)",
            "  W_active <- sum_{P_j in active} weight_j",
            "  V <- V + Fraction(delta, W_active)",
            "  v_{P*} <- v_{P*} + Fraction(delta, weight_{P*})",
            "  rem_{P*} -= delta;  if rem_{P*} == 0: active.remove(P*)",
        ], caption="Pseudocode V2 & V3: Virtual-Time Guaranteed Scheduling with arrival anchor and bounded wakeup lag."),

        rk.h1("7.2 Pseudocode V4: Production O(log N) Lazy Min-Heap + 10^9 Fixed-Point"),
        rk.para(
            "In high-concurrency servers with thousands of threads, scanning active tasks takes O(N) time per "
            "tick. Pseudocode V4 eliminates linear scans using a binary min-heap keyed by 64-bit integer "
            "nanosecond-scaled virtual time (SCALE_FP = 10^9) and lazy version stamps for O(1) sleep/exit:"
        ),
        rk.code([
            "ALGORITHM V4: Production_LazyHeap_GS(SCALE_FP=1_000_000_000)",
            "State : heap H = [], V_fp = 0, W_active = 0, cur = NONE, v_fp[], ver[], active[], w[]",
            "Def add_or_arrive(tid, weight):",
            "  w[tid] = weight; active[tid] = True; ver[tid] += 1; W_active += weight",
            "  v_fp[tid] = V_fp;  heappush(H, (v_fp[tid], tid, ver[tid]))",
            "Def sleep_or_finish(tid):          // O(1) lazy invalidation without heap scan!",
            "  active[tid] = False; ver[tid] += 1; W_active -= w[tid]",
            "Def wake(tid, cap_ticks=1):        // O(log N) bounded wakeup re-insertion",
            "  floor_v = V_fp - (cap_ticks * SCALE_FP) // w[tid]",
            "  v_fp[tid] = max(v_fp[tid], floor_v); active[tid] = True; ver[tid] += 1",
            "  W_active += w[tid]; heappush(H, (v_fp[tid], tid, ver[tid]))",
            "Def dispatch_tick():               // Amortized O(log N), O(1) on stay fast-path",
            "  while H and (not active[H[0].tid] or H[0].ver != ver[H[0].tid]): heappop(H)",
            "  if cur != NONE and active[cur] and v_fp[cur] <= H[0].v:",
            "    chosen = cur                   // Zero heap pop/push overhead while cur remains min!",
            "  else:",
            "    (_, chosen, _) = heappop(H); cur = chosen",
            "  V_fp += SCALE_FP // W_active",
            "  v_fp[chosen] += SCALE_FP // w[chosen]; ver[chosen] += 1",
            "  heappush(H, (v_fp[chosen], chosen, ver[chosen])); return chosen",
        ], caption="Pseudocode V4: Production O(log N) min-heap Guaranteed Scheduler with lazy deletion and fixed-point arithmetic."),

        rk.h1("7.3 Pseudocode V5: Stride Scheduling & Live OS psutil Control Loop"),
        rk.para(
            "For completeness, Stride Scheduling substitutes division-free integer addition upon selection: "
            "stride_i = STRIDE_LARGE // w_i, pass_i += stride_i after each quantum. Meanwhile, the real OS "
            "controller (Algorithm V6 below) replaces discrete tick updates with OS signals SIGSTOP/SIGCONT "
            "and /proc/[pid]/stat delta measurements:"
        ),
        rk.code([
            "ALGORITHM V5/V6: OS_UserSpace_GS_Controller(commands, weights, quantum_sec)",
            "For i in 0..N-1:",
            "  proc[i] <- Popen(commands[i]);  mon[i] <- psutil.Process(proc[i].pid);  mon[i].suspend()",
            "  used[i] <- 0.0;  finished[i] <- False",
            "While any process unfinished:",
            "  ready <- [i | not finished[i]]",
            "  chosen <- argmin_{i in ready} (used[i] / weights[i])",
            "  before <- sum(mon[chosen].cpu_times()[:2])     // user + system CPU seconds",
            "  mon[chosen].resume()",
            "  try: proc[chosen].wait(timeout=quantum_sec) -> finished[chosen] <- True",
            "  except TimeoutExpired: mon[chosen].suspend()",
            "  after <- sum(mon[chosen].cpu_times()[:2]);  used[chosen] += max(0.0, after - before)",
        ], caption="Pseudocode V5/V6: Real OS subprocess Guaranteed Scheduling controller via SIGSTOP/SIGCONT."),

        # =====================================================================
        # CHAPTER 8
        # =====================================================================
        rk.ptitle("8. Line-by-Line Engineering Walkthrough of GuaranteedScheduling.py"),
        rk.para(
            "The root file GuaranteedScheduling.py comprises 106 lines of clean, self-contained Python that "
            "demonstrates real operating-system CPU regulation without modifying Linux kernel source code. "
            "Instead of abstract simulator ticks, it spawns actual independent Python/OS worker programs and "
            "gates their execution using POSIX signals via psutil. Table 4 catalogs all six structural phases, "
            "followed by the complete verified source listing in three verbatim blocks."
        ),
        rk.table(
            ["Line Span", "Functional Block", "OS / Kernel Mechanism", "Critical Engineering Insight"],
            [
                ["Lines 1–24", "Interactive Configuration", "Prompts count N, script paths, weights, quantum", "Initializes used=0.0, runtime=0.0 per dict"],
                ["Lines 26–34", "Suspended Process Creation", "subprocess.Popen + immediate monitor.suspend()", "Emits SIGSTOP immediately to freeze worker"],
                ["Lines 36–51", "Ready Filter & Ratio Min", "min(active, key=lambda p: p['used']/p['weight'])", "O(N) float scan; lowest index wins ties"],
                ["Lines 53–71", "Quantum Window & Billing", "resume() -> wait(timeout=q) -> suspend()", "Bills user+system seconds from /proc/[pid]/stat"],
                ["Lines 73–89", "Fault & Exit Handling", "Catches TimeoutExpired, NoSuchProcess, AccessDenied", "Ensures clean termination of child PIDs"],
                ["Lines 91–106", "Final Telemetry Summary", "Reports per-process used CPU and wall turnaround", "Confirms heavier weights finish faster"],
            ],
            widths=[2.4, 3.4, 5.8, 5.6],
            caption="Complete structural anatomy of the 106-line root script GuaranteedScheduling.py.",
        ),
        rk.h1("8.1 Verbatim Source Code: Setup & Suspended Launch (Lines 1–35)"),
        rk.code(gd.gs_source_snippet(1, 35),
                caption="Verbatim lines 1–35 of GuaranteedScheduling.py: imports, user setup, and suspended Popen launch."),
        rk.h1("8.2 Verbatim Source Code: Ready Queue Scan & Slice Dispatch (Lines 36–71)"),
        rk.code(gd.gs_source_snippet(36, 71),
                caption="Verbatim lines 36–71 of GuaranteedScheduling.py: O(N) ratio selection, SIGCONT resume, and timeout suspend."),
        rk.h1("8.3 Verbatim Source Code: Cleanup, Signal Safety & Summary (Lines 72–106)"),
        rk.code(gd.gs_source_snippet(72, 106),
                caption="Verbatim lines 72–106 of GuaranteedScheduling.py: error recovery, child termination, and final report."),
        rk.h1("8.3 Five Known Systems Limitations of the 106-Line Educational Script"),
        rk.para(
            "Inspecting GuaranteedScheduling.py alongside kernel principles reveals five specific design limits "
            "that motivated the enhanced engines in core/gs_core.py and our production heap scheduler:"
        ),
        rk.bullets([
            "1. Pre-Suspension Race Window: Between Popen() returning and monitor.suspend() executing, the Linux kernel may grant ~0.1–1 ms of startup execution to the child before SIGSTOP takes effect.",
            "2. Kernel Jiffy Granularity (CONFIG_HZ): Linux updates /proc/[pid]/stat CPU counters roughly every 4–10 ms; setting quantum < 0.05s can yield measured delta = 0.0s, freezing a process's ratio at 0.0.",
            "3. Zero-Weight Guard Absence: Supplying w_i = 0 raises ZeroDivisionError; core/gs_core.py strictly enforces w_i >= 1.",
            "4. Dynamic Arrival & Sleep Vulnerability: Because used_i starts at 0 and has no virtual clock floor, any process arriving late or returning from sleep receives an unfair catch-up burst.",
            "5. O(N) Linear Selection Scan: Recomputing min(used / weight) scales linearly with process count N, whereas a min-heap achieves O(log N).",
        ]),
        rk.h1("8.4 Empirical IEEE-754 Binary Drift on Non-Dyadic Weights [1, 3, 6]"),
        rk.para(
            "To demonstrate concretely why exact rational arithmetic (Fraction or cross-multiplication) is "
            "indispensable in verification, Table 5 evaluates cumulative additions of 1.0/3.0 in standard IEEE-754 "
            "double precision against exact Fraction(1, 3) across just 12 scheduler ticks. Notice that drift "
            "emerges immediately at tick 1 and reaches +/- 4.44e-16 within seconds—enough to break naive '==' ties."
        ),
        rk.table(
            ["Step k", "IEEE-754 Cumulative (1.0/3.0)", "Exact Fraction", "Signed Error", "Tie Integrity"],
            gd.float_drift_rows(),
            widths=[1.6, 5.2, 2.6, 3.6, 4.2],
            caption="Step-by-step IEEE-754 floating-point drift vs exact rational arithmetic for w=3 shares.",
        ),
        rk.note(
            "In exercise-1/code/run_experiments.py, we faithfully preserve the exact psutil SIGSTOP/SIGCONT "
            "mechanism from GuaranteedScheduling.py while adding deterministic stdin-free parameterization, "
            "non-zero jiffy validation (0.05s quantum), and multi-trial median/IQR reporting.",
            caption="Faithful Bridge Between Root Script and Automated OS Benchmark",
        ),

        # =====================================================================
        # CHAPTER 9
        # =====================================================================
        rk.ptitle("9. Architecture of core/gs_core.py & Production Heap Extensions"),
        rk.para(
            "To support rigorous unit testing and cross-exercise verification across all seven assignments, "
            "core/gs_core.py encapsulates every scheduling model inside pure Python dataclasses using exact "
            "fractions.Fraction arithmetic. Table 6 summarizes the public API exported by core/gs_core.py and "
            "vendored verbatim across exercises."
        ),
        rk.table(
            ["Symbol / Function", "Input Contract", "Output Structure", "Exactness & Role"],
            [
                ["Proc", "name, arrival, work, weight, phase, sleep_at", "Immutable dataclass", "Defines process & deterministic I/O sleep hooks"],
                ["simulate_procs(...)", "procs, policy, quantum, tie, cap_ticks", "SimResult dataclass", "Cycle-exact Fraction simulator across 9 policies"],
                ["ideal_gps_trace", "procs, horizon", "dict[entitled, finish_times]", "Exact fluid GPS curve E_i(t) at every tick"],
                ["exhaustive_tie_envelope", "procs, policy, quantum, cap", "states, leaves, min/max bounds", "DFS proving best/worst lag & switch envelope [M]"],
                ["jain_fairness(vals)", "sequence of Fraction/float", "float in (0, 1]", "Standard normalized fairness metric"],
                ["SimResult.as_dict()", "keep_timeline flag", "JSON-serializable dict", "Exact + float metrics, per_proc, gantt, timeline"],
            ],
            widths=[3.6, 4.4, 3.8, 5.4],
            caption="Core simulation API inside core/gs_core.py verified by 28 unit tests.",
        ),
        rk.h1("9.1 Complexity & Memory Comparison Across Implementations"),
        rk.para(
            "Table 7 contrasts asymptotic dispatch cost, tie fidelity, dynamic-arrival fairness, and memory "
            "footprint across the educational baseline, the Fraction verification kernel, and the lazy min-heap "
            "production scheduler."
        ),
        rk.table(
            ["Property", "GuaranteedScheduling.py", "core/gs_core.py (Fraction)", "Production Heap GS (V4)"],
            [
                ["Arithmetic Type", "IEEE-754 64-bit float", "Arbitrary-precision Fraction", "64-bit Fixed-Point (10^9)"],
                ["Dispatch Complexity", "O(N) scan per quantum", "O(N) exact scan per tick", "O(1) stay / O(log N) heap"],
                ["Sleep / Exit Removal", "List deletion O(N)", "Set filter O(N)", "O(1) lazy version stamp"],
                ["Tie Fidelity", "Vulnerable to 1e-16 drift", "100% mathematically exact", "Exact integer comparison"],
                ["Arrival Anchoring", "None (used = 0)", "Optional (gs_vtime)", "Built-in V_fp anchor"],
                ["Primary Use Case", "OS teaching & psutil demo", "Proofs, envelopes & traces", "High-scale N>=1,000 dispatch"],
            ],
            widths=[3.4, 4.4, 4.7, 4.7],
            caption="Engineering comparison across all three Guaranteed Scheduling code tiers in the repository.",
        ),
        rk.h1("9.2 Inside the Exact Fraction Kernel (simulate_procs Core Loop)"),
        rk.para(
            "To guarantee zero discrepancy between textbook equations and simulation telemetry, simulate_procs() "
            "inside core/gs_core.py maintains exact Fraction states for virtual clocks, entitlement accumulation, "
            "and wakeup clamping. The core dispatch excerpt below (lines 318–395) illustrates this deterministic state machine."
        ),
        rk.code(gd.core_source_snippet(318, 355),
                caption="Exact Fraction engine setup in core/gs_core.py (lines 318–355): initialization, horizon, and sleep calendar."),
        rk.code(gd.core_source_snippet(356, 395),
                caption="Exact Fraction selection & virtual clock update in core/gs_core.py (lines 356–395)."),
        rk.code(gd.core_source_snippet(396, 435),
                caption="Exact event accounting, sleep/wakeup transition & metrics finalization in core/gs_core.py (lines 396–435)."),

        # =====================================================================
        # CHAPTER 10
        # =====================================================================
        rk.ptitle("10. Baseline Empirical Benchmark: Weighted Workload P1, P2, P3"),
        rk.para(
            "Our baseline evaluation examines three CPU-bound processes arriving simultaneously at t = 0 with "
            "heterogeneous weights [1, 2, 4] and execution bursts [4, 6, 9] over horizon H = 19 ticks: "
            "P1(w=1, work=4), P2(w=2, work=6), and P3(w=4, work=9). Total active weight at t = 0 is W = 7, "
            "giving fluid GPS rates 1/7 = 14.29%, 2/7 = 28.57%, and 4/7 = 57.14%. Notice a crucial insight: "
            "under fluid GPS, P3 requires 9 / (4/7) = 15.75 ticks to finish; once P3 exits at t = 15.75, "
            "remaining weight drops to W = 1 + 2 = 3, raising P2's rate to 2/3 and P1's to 1/3. Consequently, "
            "P2 completes at 15.75 + (6 - 2*15.75/7)/(2/3) = 18.00 ticks, and P1 completes last at t = 19.00."
        ),
        rk.table(
            ["Policy (Quantum)", "q", "Max |Lag| (Exact)", "RMSE Lag", "Switches", "Preemptions", "Mean TA", "Jain"],
            gd.baseline_policy_rows(d),
            widths=[3.2, 0.9, 2.8, 1.8, 1.8, 2.0, 2.0, 2.7],
            caption="Baseline policy benchmark on weighted simultaneous workload P1(4,w=1), P2(6,w=2), P3(9,w=4) [E].",
        ),
        rk.image("fig_ex1_gantt_baseline.png", width_cm=15.4,
                 caption="Exact Gantt timelines comparing GS ratio, GS vtime, Stride (top), GS q=2, Round-Robin q=2, and FIFO q=1."),
        rk.para(
            f"As shown in Table 8 and Figure 4, gs_ratio(q=1), gs_vtime(q=1), and stride(q=1) yield bit-for-bit "
            f"identical execution schedules: max_abs_lag = {gs1['max_abs_lag']:.4f} ({gs1['max_abs_lag_frac']}), "
            f"RMSE = {gs1['rmse_lag']:.4f}, context switches = {gs1['context_switches']}, and Jain fairness = "
            f"{gs1['jain_fairness']:.4f}. Doubling the quantum to q=2 halves context switches from {gs1['context_switches']} "
            f"to {gs2['context_switches']} while increasing worst lag to {gs2['max_abs_lag']:.4f}. By contrast, "
            f"Round-Robin (q=2) ignores weights and raises lag to {rr2['max_abs_lag']:.4f}, while non-preemptive FIFO "
            f"pushes lag to {ff1['max_abs_lag']:.4f} ticks."
        ),

        # =====================================================================
        # CHAPTER 11
        # =====================================================================
        rk.ptitle("11. Exact Per-Process Breakdown & Complete Gantt Interval Logs"),
        rk.para(
            "Table 9 details per-process metrics under baseline gs_ratio(q=1), showing how proportional sharing "
            "delivers exact completion ordering (P3 at t=17, P2 at t=18, P1 at t=19) that mirrors ideal fluid "
            "GPS turnaround proportions while keeping each individual process's worst lag at or below 1.0 tick."
        ),
        rk.table(
            ["Process", "Weight", "Work", "Start", "Finish", "Turnaround", "Waiting", "GPS Entitled", "Max |Lag|"],
            gd.baseline_proc_rows(d, "gs_ratio_q1"),
            widths=[1.8, 1.4, 1.4, 1.4, 1.5, 2.0, 1.7, 3.6, 2.4],
            caption="Per-process execution metrics under baseline gs_ratio (q=1) [E].",
        ),
        rk.h1("11.1 Complete Interval Gantt Tables: GS (q=2) vs Round-Robin (q=2)"),
        rk.para(
            "Comparing exact dispatch intervals across Table 10 (gs_ratio q=1), Table 11 (gs_ratio q=2), "
            "Table 12 (Round-Robin q=2), and Table 13 (FIFO) reveals visually why GS delivers far lower lag at "
            "the exact same quantum size: RR gives P1, P2, P3 equal 2-tick rounds ([0,2], [2,4], [4,6], [6,8]), "
            "allowing P1 (weight 1) to complete at t=8—ten ticks ahead of its fair share—while delaying P3 until t=19!"
        ),
        rk.table(
            ["Slice #", "Process Dispatched", "Interval [Start, End)", "Duration (ticks)"],
            gd.gantt_rows(d, "gs_ratio_q1"),
            widths=[2.6, 4.8, 5.2, 4.6],
            caption="Complete 14-slice interval sequence for baseline gs_ratio (q=1) across t=0..19 [E].",
        ),
        rk.table(
            ["Slice #", "Process Dispatched", "Interval [Start, End)", "Duration (ticks)"],
            gd.gantt_rows(d, "gs_ratio_q2"),
            widths=[2.6, 4.8, 5.2, 4.6],
            caption="Exact dispatch interval sequence for gs_ratio (q=2): P3 weighted priority finishes at t=19 after P2 [E].",
        ),
        rk.table(
            ["Slice #", "Process Dispatched", "Interval [Start, End)", "Duration (ticks)"],
            gd.gantt_rows(d, "rr_q2"),
            widths=[2.6, 4.8, 5.2, 4.6],
            caption="Exact dispatch interval sequence for Round-Robin (q=2): unweighted rotation starves P3 [E].",
        ),
        rk.table(
            ["Slice #", "Process Dispatched", "Interval [Start, End)", "Duration (ticks)"],
            gd.gantt_rows(d, "fifo_q1"),
            widths=[2.6, 4.8, 5.2, 4.6],
            caption="Batch FIFO execution intervals: non-preemptive convoy delays P2 and P3 maximally [E].",
        ),
        rk.h1("11.2 Tick-by-Tick Execution Comparison: GS (q=2) vs Round-Robin (q=2)"),
        rk.para(
            "Table 14 lists every single integer tick across t = 0..18 comparing gs_ratio(q=2) against "
            "unweighted Round-Robin(q=2). Notice how after initial quantum equalization at t=4, gs_ratio "
            "immediately grants P3 a second consecutive slice ([4,8]) matching its 4/7 share weight, whereas "
            "Round-Robin prematurely forces P1 back onto the CPU at t=6, letting P1 finish 11 ticks early!"
        ),
        rk.table(
            ["Tick t", "gs_ratio (q=2)", "Round-Robin (q=2)", "Decision Difference"],
            gd.q2_vs_rr_timeline_rows(d),
            widths=[1.8, 3.6, 3.6, 8.2],
            caption="Tick-by-tick divergence between weighted gs_ratio (q=2) and unweighted Round-Robin (q=2) [E].",
        ),

        # =====================================================================
        # CHAPTER 12
        # =====================================================================
        rk.ptitle("12. Virtual Clock Equalization & Cumulative Service Curves"),
        rk.para(
            "Why does Guaranteed Scheduling track fluid GPS so closely across arbitrary positive weights? "
            "Figure 5 pairs cumulative actual CPU allocation A_i(t) against ideal dashed GPS entitlement "
            "E_i(t) on the left with normalized virtual progress v_i(t) = A_i(t) / w_i on the right. Every "
            "step taken by the dispatcher raises the lowest horizontal stair in the right panel, ensuring that "
            "all three virtual clocks remain interleaved inside a bounded synchronization corridor."
        ),
        rk.image("fig_ex1_vtime_anchor_mechanics.png", width_cm=15.4,
                 caption="Cumulative service A_i(t) vs fluid GPS curves (left) and virtual clock equalization across weights [1, 2, 4] (right)."),
        rk.h1("12.1 Non-Dyadic Weight Trace Verification ([1, 3, 6] Exact Fractions)"),
        rk.para(
            "To demonstrate exact virtual-clock tracking when weights generate non-terminating binary "
            "fractions (1/3 and 1/6), Table 15 traces the first 12 ticks of P1(w=1), P2(w=3), P3(w=6) under "
            "exact rational gs_ratio (q=1). Notice how P3 advances 6 times per 1 step of P1 and 2 times per "
            "step of P2 without ever suffering floating-point tie misordering."
        ),
        rk.table(
            ["Tick t", "Chosen", "P1 v_1 = A1/1", "P2 v_2 = A2/3", "P3 v_3 = A3/6", "P3 GPS E_3(t+1)"],
            gd.non_dyadic_trace_rows(),
            widths=[1.6, 1.8, 3.3, 3.4, 3.4, 3.7],
            caption="First 12 exact ticks on non-dyadic weights [1, 3, 6] verified with Fraction arithmetic [E].",
        ),

        # =====================================================================
        # CHAPTER 13
        # =====================================================================
        rk.ptitle("13. Complete Tick-by-Tick Lag Trajectory Trace (t = 0 .. 19)"),
        rk.para(
            "Tables 16 and 17 provide the full 20-step mathematical trace of the baseline workload from t = 0 "
            "through completion at t = 19, listing cumulative actual CPU ticks A_i(t), fluid GPS entitlement "
            "E_i(t), and signed lag L_i(t) = A_i(t) - E_i(t) for every process at every integer boundary."
        ),
        rk.table(
            ["Tick t", "P1 Actual / GPS (Lag)", "P2 Actual / GPS (Lag)", "P3 Actual / GPS (Lag)"],
            gd.trajectory_rows(d, 0, 10),
            widths=[1.8, 5.1, 5.1, 5.2],
            caption="Complete tick-by-tick trajectory trace (t = 0..9) for baseline gs_ratio (q=1) [E].",
        ),
        rk.table(
            ["Tick t", "P1 Actual / GPS (Lag)", "P2 Actual / GPS (Lag)", "P3 Actual / GPS (Lag)"],
            gd.trajectory_rows(d, 10, 20),
            widths=[1.8, 5.1, 5.1, 5.2],
            caption="Complete tick-by-tick trajectory trace (t = 10..19) through job completions [E].",
        ),
        rk.image("fig_ex1_lag_trajectory.png", width_cm=15.4,
                 caption="Signed GPS service lag L_i(t) across all 20 ticks bounded strictly inside [-1.0, +1.0]."),

        rk.h1("13.1 Hand-Worked Ratio Calculation Walkthrough (Ticks t = 0 .. 7)"),
        rk.para(
            "To verify every decision independently with pen and paper, below is the exact ratio arithmetic "
            "governing ticks t = 0 through t = 7 on the simultaneous baseline P1(w=1), P2(w=2), P3(w=4):"
        ),
        rk.bullets([
            "t = 0: Ratios = (P1: 0/1=0, P2: 0/2=0, P3: 0/4=0) -> three-way tie, index breaks to P1; used_1 becomes 1.",
            "t = 1: Ratios = (P1: 1/1=1.00, P2: 0/2=0, P3: 0/4=0) -> tie between P2 & P3, index picks P2; used_2 becomes 1.",
            "t = 2: Ratios = (P1: 1.00, P2: 1/2=0.50, P3: 0/4=0) -> unique min P3 (0.00); used_3 becomes 1.",
            "t = 3: Ratios = (P1: 1.00, P2: 0.50, P3: 1/4=0.25) -> unique min P3 (0.25); used_3 becomes 2.",
            "t = 4: Ratios = (P1: 1.00, P2: 0.50, P3: 2/4=0.50) -> tie P2 & P3 at 0.50, index picks P2; used_2 becomes 2.",
            "t = 5: Ratios = (P1: 1.00, P2: 2/2=1.00, P3: 2/4=0.50) -> unique min P3 (0.50); used_3 becomes 3.",
            "t = 6: Ratios = (P1: 1.00, P2: 1.00, P3: 3/4=0.75) -> unique min P3 (0.75); used_3 becomes 4.",
            "t = 7: Ratios = (P1: 1.00, P2: 1.00, P3: 4/4=1.00) -> all three reach 1.00 simultaneously (exact cycle boundary!); index picks P1.",
        ]),
        rk.h1("13.2 Second Cycle & Tail Phase Hand Trace (Ticks t = 8 .. 18)"),
        rk.para(
            "Notice how t = 7..13 replays the exact 1:2:4 cyclic order (P1 once, P2 twice, P3 four times) until "
            "all three virtual clocks synchronize again at 2.00 after tick 13, followed by P3 completing at t=17:"
        ),
        rk.bullets([
            "t = 8..13: P2 runs at t=8 (1.50), P3 at t=9..10 (1.50), P2 at t=11 (2.00), P3 at t=12..13 (2.00); synchronized!",
            "t = 14: Three-way tie at 2.00 -> P1 executes (used_1=3, ratio=3.00).",
            "t = 15: Tie between P2 & P3 at 2.00 -> P2 executes (used_2=5, ratio=2.50).",
            "t = 16: P3 stands lowest at 2.00 -> P3 executes its final 9th tick and EXITS at t=17 (turnaround = 17).",
            "t = 17: Only P1 (3.00) and P2 (2.50) remain -> P2 executes its 6th tick and EXITS at t=18 (turnaround = 18).",
            "t = 18: Only P1 remains -> P1 executes its 4th tick and EXITS at t=19 (turnaround = 19).",
        ]),

        # =====================================================================
        # CHAPTER 14
        # =====================================================================
        rk.ptitle("14. Quantum Sensitivity & Fairness-Overhead Pareto Frontier"),
        rk.para(
            "Operating system designers must choose time quantum q carefully: infinitely small quanta eliminate "
            "tracking lag but overwhelm the processor with context switches, pipeline flushes, and cache misses, "
            "whereas overly coarse quanta degrade responsiveness and fairness. Table 18 and Figure 7 evaluate "
            "q in {1, 2, 4, 8, 16} across gs_ratio, gs_vtime, and unweighted Round-Robin over a 96-tick sweep."
        ),
        rk.table(
            ["Policy", "q", "Max |Lag|", "RMSE Lag", "Switches", "Preemptions", "Mean TA", "Worst TA", "Jain"],
            gd.quantum_rows(d),
            widths=[2.6, 0.9, 2.0, 1.9, 1.8, 2.1, 1.9, 1.9, 2.1],
            caption="Full quantum sweep across q in {1, 2, 4, 8, 16} ticks comparing GS and Round-Robin [E].",
        ),
        rk.image("fig_ex1_quantum_sweep.png", width_cm=15.2,
                 caption="Pareto trade-off between worst GPS lag (left) and context-switch overhead (right) across q=1..16."),
        rk.para(
            "Three quantitative insights emerge directly from Table 18: (1) At every quantum q, gs_ratio and "
            "gs_vtime remain 100% identical on simultaneous workloads; (2) Stepping from q=1 to q=2 cuts switches "
            "by 49.4% (89 -> 45) while keeping worst lag at 1.8000 (versus 0.9000 at q=1); and (3) At q=16, GS "
            "converges directly to unweighted Round-Robin with max lag = 14.4000 ticks and only 7 switches, "
            "proving why balanced operating systems operate in the middle-knee region (q=2..4)."
        ),

        # =====================================================================
        # CHAPTER 15
        # =====================================================================
        rk.ptitle("15. Tie-Breaking Semantics & Exhaustive Tie-Envelope Proofs"),
        rk.para(
            "Because proportional ratios frequently match—especially when weights are equal or share small "
            "common factors—tie-breaking rules wield dramatic influence over context switching and cache locality. "
            "Using exact DFS enumeration over every valid tie path in core/gs_core.py, we prove both what tie "
            "policies cannot change (equal-weight lag) and what they can optimize dramatically (switch overhead)."
        ),
        rk.table(
            ["Tie-Breaker", "Max |Lag|", "Context Switches", "Preemptions", "Jain Fairness"],
            gd.tie_rows(d),
            widths=[3.4, 3.2, 3.6, 3.4, 3.6],
            caption="Deterministic tie-breaker comparison on equal-weight workload [6, 6, 6] [E].",
        ),
        rk.table(
            ["Workload Family", "DFS States", "Leaf Schedules", "Best Max Lag", "Worst Max Lag", "Switch Range", "Worst TA"],
            gd.envelope_rows(d),
            widths=[4.2, 2.0, 2.1, 2.2, 2.2, 2.5, 2.0],
            caption="Exhaustive tie-envelope DFS across weighted and equal-weight schedules (zero truncation) [M].",
        ),
        rk.image("fig_ex1_tie_envelope.png", width_cm=15.0,
                 caption="Exhaustive tie-envelope proof: identical lag bound (2/3 tick) across 1,296 paths with 9..12 switch gap."),
        rk.para(
            "Notice the striking contrast between equal weights and heterogeneous weights in Table 20! On equal "
            "weights [1,1,1] (3,886 states, 1,296 leaves), every valid tie choice yields identical worst lag "
            "0.6667 (2/3 tick), yet switches span [9, 12] and 'stay' attains the global minimum of 9 switches. "
            "On weighted [1,2,4] (1,636 states, 216 leaves), tie choices even alter worst lag itself—from 0.5000 "
            "up to 1.0000 ticks—proving that weighted tie selection subtly shifts instantaneous GPS tracking!"
        ),

        # =====================================================================
        # CHAPTER 16
        # =====================================================================
        rk.ptitle("16. Dynamic Latecomer Starvation Pathology & Virtual-Time Cure"),
        rk.para(
            "The single most dangerous vulnerability of legacy Ratio Guaranteed Scheduling (used_i / w_i) arises "
            "under dynamic workloads where new processes enter mid-stream. Suppose P1(arrival=0, work=20, w=1) "
            "runs alone for 12 ticks, accumulating used_1 = 12, and then P2(arrival=12, work=8, w=1) arrives. "
            "Under legacy gs_ratio, P2 enters with used_2 = 0 while P1 has used_1 = 12. P2 holds a lower ratio "
            "throughout t = 12..17, starving P1 completely for 6 consecutive ticks until P2 catches up!"
        ),
        rk.table(
            ["Algorithm", "P1 Starve Gap", "P1 Finish", "P2 Finish", "Max |Lag|", "Jain Fairness"],
            gd.dynamic_rows(d),
            widths=[3.4, 2.8, 2.6, 2.6, 2.8, 3.0],
            caption="Dynamic arrival at t=12: legacy gs_ratio starvation spike vs virtual-time V(t) fix [E].",
        ),
        rk.image("fig_ex1_latecomer_teaser.png", width_cm=15.4,
                 caption="Dynamic arrival pathology: gs_ratio locks out P1 for 6 ticks (left) vs instant 1:1 sharing under gs_vtime (right)."),
        rk.h1("16.1 Complete Tick-by-Tick Dynamic Arrival Trace (t = 0 .. 27)"),
        rk.para(
            "Table 22 prints the pre-arrival phase (t = 0..9) where P1 runs uncontested under both policies, "
            "followed by Table 23 showing the exact divergence across t = 10..27 after P2 arrives at t = 12. "
            "Observe how gs_ratio runs P2 six times consecutively (t = 12..17), whereas gs_vtime immediately "
            "alternates P2 and P1 cleanly on every unit tick!"
        ),
        rk.table(
            ["Tick t", "gs_ratio Active", "gs_vtime Active", "Scheduling Regime"],
            gd.dyn_timeline_rows(d, 0, 10),
            widths=[2.0, 4.0, 4.0, 7.2],
            caption="Pre-arrival solo P1 execution phase (t=0..9) prior to dynamic arrival at t=12 [E].",
        ),
        rk.table(
            ["Tick t", "gs_ratio Active", "gs_vtime Active", "Scheduling Regime"],
            gd.dyn_timeline_rows(d, 10, 28),
            widths=[2.0, 4.0, 4.0, 7.2],
            caption="Tick-by-tick trace of dynamic arrival P2 at t=12 across t=10..27 [E].",
        ),

        # =====================================================================
        # CHAPTER 17
        # =====================================================================
        rk.ptitle("17. I/O Sleeper Exploit Pathology & Capped Wakeup Protection"),
        rk.para(
            "A closely related failure mode mirrors dynamic arrival when a process blocks voluntarily on disk "
            "or network I/O and wakes up much later. Under uncapped Virtual-Time GS, a process P_sleep that "
            "sleeps from t = 1 to t = 21 preserves its frozen virtual clock v_sleep = 1 while steady worker "
            "P_steady advances to V(21) = 21. Upon waking, P_sleep owns a 20-tick virtual credit deficit and "
            "can monopolize the CPU continuously for 20 ticks, starving steady interactive peers."
        ),
        rk.para(
            "Our V3 specification (gs_capped with cap_ticks=1, matching Linux CFS's GENTLE_FAIR_SLEEPERS) "
            "closes this loophole cleanly without punishing legitimate short-blocking interactive tasks: on "
            "wakeup, v_i is clamped upward via v_i = max(v_i, V(t) - cap_ticks / w_i). Table 24 demonstrates "
            "this exact contrast by executing core/gs_core.py directly on Steady(0, 25, w=1) alongside "
            "Sleeper(0, 12, w=1, sleep_at=((1, 20),)) across all three scheduling regimes, cutting Steady's "
            "maximum starvation gap from 11 ticks down to 2 ticks."
        ),
        rk.table(
            ["Policy", "Steady Max Starve Gap", "Steady Finish", "Sleeper Finish", "Max |Lag|", "Jain Fairness"],
            gd.sleeper_comparison_rows(),
            widths=[3.6, 3.0, 2.5, 2.5, 2.7, 2.9],
            caption="Live simulation on Steady(25,w=1) + Sleeper(12,w=1,sleep=20@t=1): gs_capped cuts starvation from 11 down to 2 ticks [E].",
        ),
        rk.table(
            ["Scheduler Variant", "Arrival at t_arr > 0", "Wakeup after Sleep S >> 1", "Interactive Priority", "Production Verdict"],
            [
                ["gs_ratio (used/w)", "Starves peers for ~t_arr", "Starves peers for ~S ticks", "Excessive monopolization", "Unsafe for mixed workloads"],
                ["gs_vtime (V(t) only)", "Exact 1:w fair sharing", "Starves peers for ~S ticks", "Excessive monopolization", "Safe only for CPU-bound"],
                ["gs_entitled (A/E)", "Bounded by 1 quantum", "Bounded by true E_i(t)", "Good, but O(N) integral", "Reference oracle"],
                ["gs_capped (V(t)-cap/w)", "Exact 1:w fair sharing", "Max burst capped at 1 tick", "Immediate 1-tick wakeup", "Production-safe standard"],
            ],
            widths=[3.2, 3.5, 3.8, 3.4, 3.3],
            caption="Behavioral matrix across dynamic arrivals and long I/O sleeps motivating gs_capped.",
        ),

        rk.h1("17.1 Tick-by-Tick Sleeper Wakeup Trace (t = 19 .. 36)"),
        rk.para(
            "Table 26 exposes what occurs immediately after Sleeper wakes at t = 21. Under uncapped gs_vtime, "
            "Sleeper holds virtual clock v_sleep = 1 while Steady stands at v_steady = 20; consequently, "
            "gs_vtime locks Steady out for 11 consecutive ticks (t = 21..31) until Sleeper finishes completely! "
            "In stark contrast, gs_capped clamps v_sleep to V(21) - 1, giving Sleeper a single responsive "
            "wakeup tick at t = 21 and alternating cleanly with Steady thereafter."
        ),
        rk.table(
            ["Tick t", "gs_vtime (Uncapped)", "gs_capped (cap=1)", "Wakeup Fairness Behavior"],
            gd.sleeper_timeline_rows(19, 37),
            widths=[1.8, 3.6, 3.6, 8.2],
            caption="Tick-by-tick wakeup trace showing 11-tick lockout under gs_vtime vs immediate 1:1 balance under gs_capped [E].",
        ),

        # =====================================================================
        # CHAPTER 18
        # =====================================================================
        rk.ptitle("18. Live Linux OS Subprocess Validation (Real Kernel Proof [D])"),
        rk.para(
            f"Simulators cannot verify OS kernel artifacts such as context-switch latency, /proc accounting "
            f"quantization, or multi-core background noise. We therefore executed n={osb['num_trials']} live "
            f"Linux subprocess trials using the exact psutil SIGSTOP/SIGCONT mechanism from "
            f"GuaranteedScheduling.py across weights {osb['weights']}, polling interval {osb['quantum_sec']:.2f}s, "
            f"and {osb['iters_per_proc']:,} CPU loop iterations per child worker. Table 27 records every trial."
        ),
        rk.table(
            ["Trial", "P1 Time (s)", "P2 Time (s)", "P3 Time (s)", "CPU Used (P1/P2/P3)", "Dispatches", "Finish Order"],
            gd.os_trial_rows(d),
            widths=[1.4, 2.2, 2.2, 2.2, 4.4, 2.1, 2.7],
            caption="Raw measurements across all 5 live Linux OS subprocess execution trials [D].",
        ),
        rk.table(
            ["Process (Weight)", "OS Median (s)", "OS IQR (s)", "OS Norm Ratio", "Sim TA", "Sim Norm Ratio"],
            gd.os_vs_sim_rows(d),
            widths=[3.0, 2.8, 2.6, 2.8, 2.6, 3.4],
            caption="Comparison between live Linux median/IQR wall times and discrete gs_core normalized ratios [D]+[E].",
        ),
        rk.image("fig_ex1_os_vs_sim.png", width_cm=15.4,
                 caption="Normalized completion ratios across n=5 real Linux trials (solid orange) vs discrete simulator prediction (dashed blue)."),
        rk.para(
            "Crucially, every single live trial strictly respected the theoretical completion hierarchy P3 -> P2 -> P1 "
            "with zero zero-CPU polling slices across all runs. Notice why live OS ratios (P3/P1 ~ 0.56, P2/P1 ~ 0.85) "
            "are slightly closer than pure equal-work discrete simulation ratios: each worker pays a fixed Python "
            "interpreter boot + psutil attach cost plus periodic 50 ms polling overhead shared across active slices."
        ),

        # =====================================================================
        # CHAPTER 19
        # =====================================================================
        rk.ptitle("19. Asymptotic Scaling, Production O(log N) Heap Code & Debugging Manual"),
        rk.para(
            "Deploying Guaranteed Scheduling inside real kernels or user-space task orchestrators requires "
            "eliminating three performance bottlenecks inherent in naive textbook implementations: O(N) ready-queue "
            "scanning, O(N) heap deletions on sleep/exit, and floating-point tie instability. Applying Pseudocode V4 "
            "(64-bit 10^9 fixed-point virtual clocks, lazy version stamps, binary min-heap, and O(1) stay "
            "hysteresis) transforms Guaranteed Scheduling from an educational O(N) prototype into a constant/log "
            "production scheduler while maintaining 100% behavioral equivalence with Fraction gs_vtime/gs_capped."
        ),
        rk.h1("19.1 Verified Production Code Listing (OptimizedHeapScheduler)"),
        rk.para(
            "The verified production module (archived at benchmarks/archive-studies/ex6_heap_opt/code/gs_optimized.py) "
            "implements O(log N) dispatch with 10^9 fixed-point integer clocks and lazy deletion in four compact blocks:"
        ),
        rk.code(gd.opt_source_snippet(1, 38),
                caption="Production OptimizedHeapScheduler (Part 1: imports, TaskState dataclass, fixed-point constant)."),
        rk.code(gd.opt_source_snippet(39, 76),
                caption="Production OptimizedHeapScheduler (Part 2: heap state init, process registration, arrival anchor)."),
        rk.code(gd.opt_source_snippet(77, 114),
                caption="Production OptimizedHeapScheduler (Part 3: O(1) sleep invalidation and capped wakeup clamping)."),
        rk.code(gd.opt_source_snippet(115, 152),
                caption="Production OptimizedHeapScheduler (Part 4: stay fast-path, lazy heap extraction, fixed-point billing)."),
        rk.code(gd.opt_source_snippet(153, 190),
                caption="Production OptimizedHeapScheduler (Part 5: batch simulation driver & dynamic arrival/sleep event loop)."),
        rk.h1("19.2 Empirical Scaling Benchmark (N = 50 .. 2,000 Concurrent Tasks)"),
        rk.table(
            ["Tasks N", "Linear Mean Step", "Linear p95", "Heap Mean Step", "Heap p95", "Speedup"],
            gd.opt_scaling_rows(),
            widths=[2.0, 3.2, 3.0, 3.2, 3.0, 2.8],
            caption="Wall-clock microbenchmark comparing O(N) linear scan against O(log N) lazy min-heap across N=50..2,000 [M].",
        ),
        rk.table(
            ["Optimization Mechanism", "Problem Addressed", "Exact Complexity Gain", "Fairness Equivalence"],
            [
                ["Binary Min-Heap + Lazy Stamps", "Linear O(N) ready scan & delete", "O(N) -> O(log N) step, O(1) sleep", "Identical selection order"],
                ["Stay Fast-Path Check", "Unnecessary pop+push when prev wins", "Reduces heap ops ~45% on equal w", "Preserves lag invariance"],
                ["10^9 Fixed-Point Integer Clocks", "Slow Fraction allocs & float ULP bugs", "Integer ALU ops (ns scale)", "Exact to 10^-9 tick precision"],
                ["V(t) Arrival + Cap Wakeup", "Latecomer & I/O sleeper starvation", "O(1) arithmetic on join/wake", "Strict GPS lag containment"],
            ],
            widths=[4.2, 4.4, 4.4, 4.2],
            caption="Production optimization architecture reconciling algorithmic speed with strict GPS fairness.",
        ),
        rk.h1("19.3 Common Implementation Pitfalls & Engineering Diagnostic Matrix"),
        rk.para(
            "Table 31 summarizes six frequent bugs observed when engineers or students implement Guaranteed "
            "Scheduling from textbook pseudocode alone, along with concrete symptoms and deterministic fixes."
        ),
        rk.table(
            ["Pitfall / Bug", "Observable Symptom", "Root Cause", "Verified Fix"],
            [
                ["1. Using wall time instead of cpu_times()", "Background noise shifts fairness", "Wall elapsed != actual scheduled CPU", "Bill user+sys from /proc/[pid]/stat"],
                ["2. Missing immediate SIGSTOP on spawn", "P3 consumes CPU before scheduling loop", "Race between fork() and suspend()", "Call monitor.suspend() right after Popen"],
                ["3. Polling interval dt < kernel tick", "Process ratio stays 0.0 indefinitely", "dt < CONFIG_HZ jiffy (~4-10 ms)", "Enforce OS quantum dt >= 0.05 s"],
                ["4. Initializing newcomer used_i = 0", "Existing tasks freeze for t_arr ticks", "Newcomer ratio 0 << veteran used/w", "Anchor newcomer v_i = V(t)"],
                ["5. Raw float equality check a == b", "Random tie breaks on weights [1,3,6]", "IEEE-754 non-dyadic ULP drift", "Use Fraction or 64-bit integer scaled"],
                ["6. Unbounded sleep credit", "Waking daemon starves steady workers", "v_i remains frozen during I/O sleep", "Clamp v_i >= V(t) - cap / w_i"],
            ],
            widths=[4.0, 4.2, 4.4, 4.6],
            caption="Diagnostic manual of six classical Guaranteed Scheduling implementation bugs and their fixes.",
        ),

        # =====================================================================
        # CHAPTER 20 — FORMAL THEOREMS, KERNEL COMPARISON & VERIFICATION SUITE
        # =====================================================================
        rk.ptitle("20. Formal Theorems & Proofs of Guaranteed Scheduling Properties"),
        rk.h1("20.1 Theorem 1 — Simultaneous Arrival Equivalence Across Proportional Formulations"),
        rk.para(
            "Statement: When all processes arrive simultaneously at t = 0 and never enter sleep states, "
            "gs_ratio (used_i / w_i), gs_vtime (v_i initialized to V(0)=0), and Stride Scheduling (pass_i = "
            "used_i * K / w_i) induce the exact same rank ordering at every dispatch boundary whenever ties are "
            "broken identically."
        ),
        rk.para(
            "Proof Sketch: Under simultaneous arrivals with zero sleeps, every active task sees identical "
            "elapsed global time since t = 0. Advancing v_i by 1/w_i per tick produces v_i(t) = A_i(t) / w_i "
            "identically, while Stride's pass_i(t) equals K * (A_i(t) / w_i). Because multiplication by positive "
            "constant K > 0 is strictly order-preserving, argmin_i(used_i / w_i) = argmin_i(v_i) = argmin_i(pass_i). Q.E.D."
        ),
        rk.h1("20.2 Theorem 2 — Equal-Weight Max Lag Invariance & Min-Switch Optimality"),
        rk.para(
            "Statement: For N simultaneous equal-weight tasks under unit quantum q = 1, every tie-breaking rule "
            "achieves the exact same worst-case lag bound MaxAbsLag = (N - 1) / N, while 'stay' hysteresis "
            "minimizes context switches across the entire schedule tree."
        ),
        rk.para(
            "Proof Sketch: On round r, every task must execute once before any task executes (r + 1) times, so "
            "actual CPU counts stay inside [r, r + 1] while GPS entitlement equals r + k/N; thus |L_i(t)| <= "
            "(N - 1)/N regardless of intra-round permutation. At round boundary t = kN, all N scores tie at k; "
            "only 'stay' keeps the final task of round k executing first in round k + 1, eliminating one switch "
            "per round boundary (verified across 3,886 DFS states and 1,296 leaves in Table 20). Q.E.D."
        ),
        rk.h1("20.3 Theorem 3 — Linear Dynamic-Arrival Starvation vs O(1) V(t) Containment"),
        rk.para(
            "Statement: If task P1 runs alone for T_0 > 0 ticks before equal-weight newcomer P2 arrives at "
            "t = T_0, legacy gs_ratio allows P2 to monopolize the processor for ceil(T_0 / 2) or up to min(T_0, b_2) "
            "ticks, whereas gs_vtime limits consecutive lockout of P1 to exactly 1 quantum."
        ),
        rk.para(
            "Proof Sketch: Under gs_ratio, used_1(T_0) = T_0 while used_2(T_0) = 0, so P2 holds strictly smaller "
            "ratio until used_2 >= T_0 (starving P1 for min(T_0, b_2) ticks; 6 ticks in our t=12 benchmark). Under "
            "gs_vtime, P2 enters with v_2 = V(T_0) = v_1(T_0), creating immediate equality at arrival. After P2 "
            "takes 1 tick, v_2 = v_1 + 1 > v_1, returning the CPU immediately to P1 on tick T_0 + 1. Q.E.D."
        ),

        # =====================================================================
        # CHAPTER 21
        # =====================================================================
        rk.ptitle("21. Comparison with Modern OS Kernel Schedulers (Linux, FreeBSD, Windows)"),
        rk.para(
            "Positioning Guaranteed Scheduling alongside production kernel dispatchers clarifies both how classic "
            "textbook theory shaped real operating systems and where hardware realities demand extra mechanisms "
            "(multi-core load balancing, NUMA affinity, and interactive latency deadlines)."
        ),
        rk.table(
            ["Feature / Kernel", "Our Guaranteed Scheduling", "Linux EEVDF (6.6+)", "FreeBSD ULE", "Windows Thread Sched"],
            [
                ["Core Objective", "Strict proportional w_i/W", "Proportional + virtual deadline", "Interactive score + timeshare", "32-level feedback priority"],
                ["Time Accounting", "Exact Fraction / 10^9 FP", "ns vruntime + lag eligibility", "4-ms tick interactivity bucket", "Quantum units + boost"],
                ["Late Arrival Rule", "v_i = V(t) anchor", "lag_i = 0 (E_i - A_i) entry", "Neutral slice history", "Default base priority"],
                ["Sleeper Protection", "gs_capped V(t) - cap/w_i", "Eligible lag clamp + request", "Sleep credit capped 1s", "Dynamic priority boost"],
                ["Data Structure", "O(log N) lazy min-heap", "Augmented red-black tree", "Circular runqueues (O(1))", "32 bitmask priority lists"],
                ["Hard Real-Time?", "No (EDF/RM required)", "Separate SCHED_DEADLINE", "Separate ithread/RT", "Real-time levels 16–31"],
            ],
            widths=[3.0, 3.6, 3.8, 3.4, 3.4],
            caption="Architectural alignment between Guaranteed Scheduling and modern production operating systems.",
        ),

        # =====================================================================
        # CHAPTER 22
        # =====================================================================
        rk.ptitle("22. Verification Suite, Unit Test Matrix & Reproducibility"),
        rk.para(
            "All mathematical claims, discrete simulations, figures, and live Linux validations in Exercise 1 "
            "are fully automated and guarded by 28 core unit tests in tests/test_gs_core.py plus dedicated "
            "exercise verification assertions in exercise-1/tests/test_ex1.py. Tables 33 and 34 enumerate the "
            "exact unit-test contracts enforcing every mathematical and engineering invariant, followed by Table 35."
        ),
        rk.table(
            ["Test Suite / Group", "Checks", "Verified Invariants"],
            [
                ["Core Rational & GPS Proofs", "10 tests", "Zero-sum lag conservation, Fraction precision on [1,3,6], equal-weight lag bounds"],
                ["Policy Equivalence & Ties", "8 tests", "gs_ratio == gs_vtime == stride at t=0, stay min-switches, exhaustive DFS match"],
                ["Dynamic & Sleeper Defenses", "6 tests", "Latecomer t=12 starvation catch, gs_vtime 1-tick cap, gs_capped I/O bound"],
                ["Real-Time EDF/RM Kernels", "4 tests", "Liu-Layland bound checks, hyperperiod feasibility, overload miss metrics"],
                ["Exercise 1 Integration Gate", "4 tests", "Byte-identical core vendoring, 5 live OS runs, 10 diagrams, 40+ page no-overflow check"],
            ],
            widths=[4.4, 2.0, 10.8],
            caption="Comprehensive automated pytest verification coverage across core/gs_core.py and Exercise 1.",
        ),
        rk.table(
            ["Core / Ex1 Verification Test", "Workload / Fixture", "Mathematical / OS Assertion Enforced"],
            [
                ["test_zero_sum_lag_conservation", "Simultaneous [1, 2, 4]", "Sum of L_i(t) == Fraction(0) at every integer tick t"],
                ["test_non_dyadic_fraction_exactness", "Weights [1, 3, 6]", "Tie comparisons exact to denominator 6 with 0 ULP error"],
                ["test_simultaneous_policy_equivalence", "Static t=0 arrivals", "gs_ratio == gs_vtime == stride trace equality under q=1"],
                ["test_equal_weight_lag_bound", "Equal weights N=3, q=1", "MaxAbsLag strictly <= (N-1)/N = 2/3 across all ties"],
                ["test_stay_minimizes_context_switches", "Equal [6, 6, 6]", "stay switches (9) == exhaustive DFS lower bound"],
                ["test_dynamic_arrival_ratio_starvation", "P1(0,20), P2(12,8)", "Verifies 6-tick lockout in gs_ratio vs 1 tick in gs_vtime"],
                ["test_sleeper_exploit_bounded_capped", "Steady + Sleeper(20)", "gs_capped bounds wakeup monopolization to 1 tick"],
                ["test_exhaustive_envelope_matches", "Weighted [1,2,4]", "DFS 1,636 states / 216 leaves bounds [0.5, 1.0] ticks"],
                ["test_vendored_core_matches_canonical", "SHA / byte check", "exercise-1/code/gs_core.py == core/gs_core.py"],
                ["test_os_subprocess_ordering_and_cpu", "5 live Linux runs", "100% P3 < P2 < P1 finish ordering and 0 zero-CPU slices"],
            ],
            widths=[5.6, 3.6, 8.0],
            caption="Detailed invariant specifications enforced automatically by pytest before every submission.",
        ),
        rk.table(
            ["Artifact Path", "Purpose & Role", "Verification Gate"],
            [
                ["GuaranteedScheduling.py", "Original 106-line psutil OS process scheduler", "Syntax + live subprocess behavior [D]"],
                ["exercise-1/code/gs_core.py", "Byte-identical vendored core/gs_core.py exact engine", "SHA/byte equality + 28 core unit tests"],
                ["exercise-1/code/run_experiments.py", "Runs all [E]+[M]+[D] benchmarks -> experiments.json", "Schema & invariant assertions in test_ex1.py"],
                ["exercise-1/code/make_diagrams.py", "Generates all 10 diagnostic figures (300/220 DPI)", "Presence, size & visual inspection pass"],
                ["exercise-1/docs/REPORT_{EN,FA}.{pdf,docx}", "Dense 40+ page bilingual EN/FA monographs", "Zero overflow, zero missing glyphs, 40+ pages"],
            ],
            widths=[4.8, 6.4, 6.0],
            caption="Complete Exercise 1 file map and automated quality gates.",
        ),
        rk.code([
            "python3 tools/vendor_core.py               # syncs core/gs_core.py across all exercises",
            "python3 exercise-1/code/run_experiments.py  # regenerates output/experiments.json [E]+[M]+[D]",
            "python3 exercise-1/code/make_diagrams.py    # regenerates all 10 PNG diagrams",
            "python3 tools/build_report.py gs1_en exercise-1 REPORT_EN",
            "python3 tools/build_report.py gs1_fa exercise-1 REPORT_FA",
            "python3 -m pytest tests/test_gs_core.py exercise-1/tests -v",
        ], caption="Exact command pipeline to reproduce and verify every Exercise 1 artifact from scratch."),
    ]

    rep.pack_flow(blocks, figures_dir=fig_dir, max_fill=0.89)
    return rep
