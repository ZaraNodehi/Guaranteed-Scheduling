# Speaker Script (English)

## Slide 1. Algorithmic Optimization, O(log N) Lazy Heap & Anti-Sleeper Hardening

- Research Question 1: Can a lazy min-heap eliminate O(N) linear scan bottlenecks up to N = 4,000?
- Research Question 2: How badly does IEEE-754 float accumulation corrupt virtual-time ties over 100k steps?
- Research Question 3: Does gs_capped + V(t) stop both simulated S=160 monopolies and live Linux I/O exploits?
- Artifact: exercise-6/code/gs_optimized.py (OptimizedHeapScheduler + live Linux controllers).

**Speaker notes:** Welcome to this seminar on Exercise 6 of the Guaranteed Scheduling project. Whereas Exercises 1 through 5 diagnosed linear-scan bottlenecks, floating-point drift, latecomer starvation, and sleeper credit hoarding, Exercise 6 engineers and verifies a unified production scheduler that fixes all four defects simultaneously.

## Slide 2. Before/After Refactoring: Legacy GuaranteedScheduling.py -> V4 Heap

- Upgrade 1 — Complexity: O(N) scan (135.7 us @ 4k) -> O(log N) heap (0.66 us).
- Upgrade 2 — Arithmetic: float64 (47,996 mismatches) -> 10^9 fixed-point (0 errors).
- Upgrade 3 — Dynamic Arrival: unanchored 0 -> global clock V(t_arr) anchoring + stay fast path.
- Upgrade 4 — Wakeup Cap: uncapped credit (159t burst @ S=160) -> 1-tick floor.

**Speaker notes:** Figure 1 contrasts the legacy unanchored linear-scan architecture on the left against our refactored Version 4 hardened heap scheduler on the right. Every single defect receives an exact algorithmic remedy, delivering a 200x dispatch speedup at four thousand tasks and a 4.9x improvement in live Linux accuracy.

*Figure: `fig_ex6_refactor_architecture.png`*

## Slide 3. Bench 1: O(log N) Heap Hits 112.1x @ 2k and 206.6x @ 4k [M]

- At N = 50: heap is already 3.23x faster than linear scan.
- At N = 2,000: linear climbs to 68.10 us/step vs heap 0.608 us (112.1x).
- At N = 4,000: linear balloons to 135.72 us/step while heap stays 0.657 us (206.6x).
- stay fast path skips heap pop entirely when the running task ties with heap minimum.

**Speaker notes:** Wall-clock dispatch microbenchmarks confirm clean asymptotic separation across seven concurrency levels from 50 up to 4,000 active tasks. While linear-scan latency climbs linearly past 165 microseconds per decision, the lazy min-heap remains flat under 1 microsecond, achieving a 200x speedup at N equals 4,000.

*Figure: `fig_ex6_complexity_scaling.png`*

## Slide 4. Bench 2: 120-Workload Incremental Engineering Ablation V0 -> V3 [M]

- V0 (gs_ratio): mean lag 5.231, worst sleeper burst 13 ticks.
- V1 (+V(t) Anchor): cuts mean lag down to 4.799, sleeper burst still 13t.
- V2 (+stay Hysteresis): trims switches (42.6 -> 41.1) with lag 4.791.
- V3 (+gs_capped): breaks worst sleeper lockout 3.25x (13t -> 4t) at lowest lag 4.750!

**Speaker notes:** Running an ablation across 120 mixed dynamic and sleeper workloads isolates each optimization independently. Adding V(t) arrival anchoring lowers mean lag; adding stay hysteresis cuts extra switches; and finally enabling gs_capped slashes the worst sleeper lockout burst from 13 ticks down to just 4 ticks.

*Figure: `fig_ex6_ablation_ladder.png`*

## Slide 5. Bench 3: Breaking 159-Tick Sleeper Monopoly Down to 1 Tick [E]+[M]

- Adversarial Sleeper blocks for S in {5, 10, 20, 40, 80, 160} ticks alongside Steady worker.
- Both gs_ratio and uncapped gs_vtime surrender S - 1 = 159 straight ticks at S=160!
- Root cause: sleeper's virtual time stays frozen while active processes advance V(t).
- gs_capped sets floor V(t) - cap/w, capping burst strictly at 1 tick for all S!

**Speaker notes:** Figure 4 scales an adversarial I/O sleeper up to 160 ticks. Even virtual-time scheduling without a wakeup floor inherits the legacy sleeper bug and locks out the steady worker for 159 straight ticks. Clamping waking tasks to a 1-tick credit floor freezes post-wakeup monopoly at 1 tick indefinitely.

*Figure: `fig_ex6_sleeper_mitigation.png`*

## Slide 6. Exact Gantt Contrast: 10-Tick Monopoly vs Clean 1:1 Interleaving [E]

- Sleeper runs 1 tick, sleeps t=2..12 while Steady runs 10 ticks, then wakes at t=12.
- Uncapped gs_vtime: Sleeper seizes 10 consecutive ticks (t=12..22), starving Steady completely.
- Capped gs_capped: Sets Sleeper clock to V(12) - 1 = 11, restoring 1:1 alternation immediately.
- Directly implements the mathematical core behind Linux CFS GENTLE_FAIR_SLEEPERS.

**Speaker notes:** This exact tick-by-tick Gantt trace visualizes what happens at wakeup time t equals 12. Uncapped virtual time traps the steady worker inside the shaded 10-tick blackout zone, whereas gs_capped restores clean one-to-one alternation on the very next tick.

*Figure: `fig_ex6_timeline_sleeper.png`*

## Slide 7. Cap Knee (cap = 1) & O(1) Lazy Deletion Under Heavy Churn (77.3x) [E]+[M]

- Cap sweep 0..40: cap=0 inflates S=40 lag (20.5 vs 20.0); cap>=4 permits burst growth.
- Optimal knee at wakeup_cap = 1 preserves exact zero lag penalty (20.0) and <= 2t burst.
- Under 800 rapid sleep/wake cycles at N=2,000, versioned lazy heap runs 77.3x faster.
- Version tags invalidate sleeping entries in O(1) without scanning heap arrays.

**Speaker notes:** Two practical implementation details govern production quality. First, on the left, sweeping the wakeup cap from 0 to 40 proves cap equals 1 sits at the exact sweet spot avoiding cap-0 wakeup delay while capping bursts. Second, on the right, lazy version counters maintain a 76x speedup even under continuous sleep-wake churn.

*Figure: `fig_ex6_cap_tradeoff_and_churn.png`*

## Slide 8. Bench 5 & 4: Zero Fixed-Point Drift & Live Linux Sleeper Defense [E]+[D]

- Decimal weights [2, 5, 10] over 100k steps: float64 drifts 47,996 times; 10^9 FP scores 0!
- Prime weights [3, 7, 11]: float64 mismatches 12,606 times; LCM(1..16)=720,720 eliminates prime remainder too.
- Live Linux 0.8s SIGSTOP sleeper [D]: uncapped gives Sleeper 100% (15 consecutive steps).
- Live Linux gs_capped [D]: restores balanced [46.3%, 53.7%] within 3.66%!

**Speaker notes:** Left, Bench 5 exposes a subtle real-world bug: naive IEEE-754 floats diverge 47,996 times across 100,000 steps on decimal weights [2, 5, 10], whereas 10-to-the-9 fixed point matches exact rational Fractions with zero errors. Right, our live Linux sleeper exploit confirms uncapped scheduling surrenders 100% CPU upon wakeup, while gs_capped restores 50-50 balance.

*Figure: `fig_ex6_fp_drift_and_live_sleeper.png`*

## Slide 9. Bench 4: 8.6x Lower Real-Linux Latecomer Distortion [D]

- Two steady workers start at t=0; P3 spawns dynamically at t=0.6s on real Linux psutil.
- Legacy (dt=0.10s, used/w = 0): P3 grabs 58.6%, starving P1 to 20.7% (25.23% err).
- Refactored (dt=0.05s, V(t)+stay): shares stay [35.2%, 30.4%, 34.4%] (2.93% err).
- Directly bridges simulation theory into kernel-level subprocess CPU control.

**Speaker notes:** When worker P3 spawns dynamically at 0.6 seconds on real Linux, the legacy unanchored controller awards it 58.6 percent of all remaining CPU, producing a 25.2 percent fairness error. Enabling V(t) arrival anchoring and stay hysteresis cuts real-OS distortion 8.6x down to 2.9 percent.

*Figure: `fig_ex6_os_refactor_validation.png`*

## Slide 10. Production Checklist, Threats to Validity & Transition to Exercise 7

- Rule 1: Use lazy versioned min-heap for O(log N) dispatch and O(1) sleep/wake invalidation.
- Rule 2: Scale weights by LCM-aligned fixed-point integer (avoid raw float64 cumulative drift).
- Rule 3: Combine V(t_arr) arrival anchoring, stay hysteresis, and wakeup_cap = 1 credit floor.
- Next (Exercise 7 Capstone): Unify all 7 exercises into a single six-regime selector & EEVDF roadmap.

**Speaker notes:** In summary, Exercise 6 upgrades Guaranteed Scheduling into a hardened O(log N) engine immune to float drift, latecomer starvation, and sleeper hoarding both in exact simulation and live Linux subprocesses. Remaining scope limits such as single-core focus and fixed slices transition directly into our Exercise 7 capstone. Thank you.
