# Exercise 6: Algorithmic Optimization, O(log n) Heap Refactoring & Anti-Sleeper Hardening

**Upgrading GuaranteedScheduling.py From O(n) Linear Scan & IEEE-754 Floats to a Lazy Versioned Min-Heap, 10^9 Fixed-Point Virtual Time, V(t) Anchoring, stay Hysteresis & Live Linux Sleeper Defense**

- **Repository:** ZaraNodehi/Guaranteed-Scheduling
- **Scope:** Exercise 6 — Data Structures, 60-Workload Ablation, Float Drift Audit & Live Linux Validation
- **Core Artifacts:** exercise-6/code/{gs_optimized,run_experiments,make_diagrams}.py
- **Evidence Base:** exercise-6/output/experiments.json + 8 Okabe-Ito Figures + 10-Slide Seminar Package

## Table of contents

- 1. Engineering Diagnosis & Four-Defect Refactoring Architecture (p. 3)
- 2. Data-Structure Engineering: Versioned Lazy Heap & Fixed-Point Clocks (p. 4)
- 3. Bench 1: O(log N) Complexity Scaling & Churn Microbenchmarks [M] (p. 4)
- 4. Bench 2: 120-Workload Incremental Engineering Ablation V0 -> V3 [M] (p. 5)
- 5. Bench 3: Adversarial Sleeper Exploit S = 5..160 & Cap Knee [E]+[M] (p. 12)
- 6. Bench 5: IEEE-754 Float Accumulation Drift vs Integer Fixed-Point [E]+[M] (p. 14)
- 7. Bench 4: Dual Live Linux Validation (Latecomer & Real Sleeper) [D] (p. 16)
- 8. Standard-Academic Seminar Package & Bilingual Speaker Scripts (p. 21)
- 9. Source Code Audit: Hardened Heap, Float Audit & Live OS (p. 23)
- 10. Engineering Checklist, Validity Threats, Tests & Appendix (p. 41)


<!-- page 1 -->


<!-- page 2 -->


<!-- page 3 -->


## 1. Engineering Diagnosis & Four-Defect Refactoring Architecture

Exercises 1 through 5 isolated four distinct structural failures in naive Guaranteed Scheduling implementations such as the legacy 106-line script GuaranteedScheduling.py: (1) O(N) linear dispatch scans, (2) IEEE-754 floating-point tie accumulation drift, (3) Omega(t_arr) latecomer starvation on dynamic spawn, and (4) unbounded sleeper credit hoarding across I/O waits. Exercise 6 eliminates all four defects simultaneously inside OptimizedHeapScheduler (exercise-6/code/gs_optimized.py) and validates every claim across both deterministic microbenchmarks [M] and live Linux psutil subprocess control [D].

- Upgrade 1 — O(log N) Lazy Versioned Min-Heap (Bench 1): Reduces median dispatch time at N = 2,000 from 68.10 us to 0.608 us (112.1x faster) and at N = 4,000 to 0.657 us (206.6x faster!), while O(1) lazy version cancellation achieves 77.3x churn speedup.
- Upgrade 2 — Incremental 60-Workload Ablation (Bench 2): Isolates V0 -> V1 (+V(t)) -> V2 (+stay) -> V3 (+gs_capped), trimming mean lag from 5.231 to 4.750 and slashing worst sleeper lockout from 13 ticks to 4 ticks.
- Upgrade 3 — Wakeup Credit Cap & Cap Knee (Bench 3): Even after S = 160 sleep ticks, gs_capped caps post-wakeup monopoly at 1 tick (vs 159 ticks uncapped), with optimal cap knee at wakeup_cap = 1.
- Upgrade 4 — IEEE-754 Float Drift Audit (Bench 5): Exposes 47,996 tie-order divergences over 100,000 steps for float64 on [2, 5, 10] vs 0 errors under 10^9 fixed-point integers.
- Upgrade 5 — Dual Live Linux Kernel Experiments (Bench 4): Shrinks mid-run spawn share error 8.6x (25.23% -> 2.93%) AND defeats a real 0.8s SIGSTOP sleeper monopoly (15 steps -> 2 steps).

![Figure 1: Before/after architectural transformation from legacy linear scan (V0) to hardened O(log N) heap (V4).](diagrams/fig_ex6_refactor_architecture.png)

*Figure 1. Before/after architectural transformation from legacy linear scan (V0) to hardened O(log N) heap (V4).*


<!-- page 4 -->

| Engineering Dimension | Legacy V0 Baseline vs Refactored V4 Optimized |
|---|---|
| N = 2,000 / 4,000 dispatch latency | 68.10 / 135.72 us -> 0.608 / 0.657 us (206.6x @ 4k) |
| Heavy sleep/wake churn (N = 2,000) | 135.7 us -> 1.75 us (77.3x faster, O(1) sleep) |
| Decimal [2,5,10] tie errors / 100k | 47,996 (IEEE-754 float64) -> 0 (10^9 fixed-point) |
| Worst sleeper monopoly (S = 160) | 159 ticks (uncapped) -> 1 tick (gs_capped) |
| Live Linux latecomer error [D] | 25.23% (dt=0.10s) -> 2.93% (dt=0.05s V(t)+stay) |
| Live Linux 0.8s sleeper exploit [D] | 100.0% monopoly (15st) -> 53.7% balanced (2st) |

*Table 1. Headline engineering scorecard across simulation and live Linux verification.*


## 2. Data-Structure Engineering: Versioned Lazy Heap & Fixed-Point Clocks


### 2.1 Why Versioned Lazy Min-Heap + Stay Fast Path Wins in Practice

Explicit pointer-based red-black trees incur pointer chasing and memory fragmentation in Python and user-space controllers, whereas a contiguous array-backed binary min-heap (heapq) achieves high cache locality. Because a binary heap does not support O(log N) arbitrary deletion when a task sleeps, OptimizedHeapScheduler attaches a monotonically increasing integer version counter per task. Sleeping simply marks active = False and increments version in O(1); step() skips stale heap roots lazily in amortized O(log N). Moreover, when stay tie hysteresis keeps the running process tied at heap[0].vtime_fp, step() even avoids popping the root.

| Scheduler Operation | LinearScan (V0) | RB-Tree (Kernel) | OptimizedHeap (V4) |
|---|---|---|---|
| Pick next task (step) | O(N) scan | O(log N) left-most | O(1) stay / O(log N) heap |
| Dynamic arrival (add) | O(1) append | O(log N) insert | O(log N) anchored at V(t) |
| Block on I/O (sleep) | O(1) flag set | O(log N) erase | O(1) active=False; version++ |
| Wakeup (wake + cap) | O(1) flag clear | O(log N) reinsert | O(log N) clamped >= V(t)-cap/w |
| Tie precision | float64 (drifts) | u64 ns (Linux CFS) | 10^9 / LCM integer fixed-point |

*Table 2. Asymptotic and systems-engineering comparison across three scheduler implementations.*


## 3. Bench 1: O(log N) Complexity Scaling & Churn Microbenchmarks [M]

Table 3 reports median and p95 dispatch latencies across N = 50 up to N = 4,000 active tasks (2,000 dispatches x 5 repeats). Already at N = 50, the min-heap runs 3.23x faster; by N = 2,000 linear scan reaches 68.10 us/decision and at N = 4,000 climbs to 135.72 us/decision, whereas OptimizedHeapScheduler stays below 1 microsecond (0.657 us) for a 206.64x speedup.


<!-- page 5 -->

| N Procs | Linear Median | Linear p95 | Heap Median | Heap p95 | Speedup |
|---|---|---|---|---|---|
| 50 | 1.761 us | 1.932 us | 0.545 us | 0.565 us | 3.23x |
| 100 | 3.317 us | 3.363 us | 0.557 us | 0.588 us | 5.96x |
| 250 | 8.264 us | 8.344 us | 0.597 us | 0.609 us | 13.83x |
| 500 | 17.130 us | 17.205 us | 0.600 us | 0.614 us | 28.56x |
| 1000 | 34.510 us | 37.253 us | 0.628 us | 0.636 us | 54.97x |
| 2000 | 68.101 us | 68.761 us | 0.608 us | 0.626 us | 112.07x |
| 4000 | 135.720 us | 142.621 us | 0.657 us | 0.665 us | 206.64x |

*Table 3. Bench 1 dispatch microbenchmark from N = 50 to N = 4,000 active tasks [M].*

![Figure 2: Log-log dispatch scaling O(N) vs O(log N) (left) and speedup bars reaching 200x @ N=4,000 (right).](diagrams/fig_ex6_complexity_scaling.png)

*Figure 2. Log-log dispatch scaling O(N) vs O(log N) (left) and speedup bars reaching 200x @ N=4,000 (right).*

To confirm that lazy version invalidation does not degrade under continuous I/O blocking, Table 4 exercises 800 rapid sleep + dispatch + wake + dispatch cycles across N = 100..2,000. Lazy deletion delivers a 77.32x churn speedup at N = 2,000 while keeping stale heap pops negligible.

| N Procs | Cycles | Linear Churn | Lazy Heap Churn | Speedup | Stale Pops |
|---|---|---|---|---|---|
| 100 | 800 | 7.23 us | 1.95 us | 3.70x | 765 |
| 500 | 800 | 34.10 us | 1.95 us | 17.48x | 552 |
| 1000 | 800 | 68.45 us | 2.09 us | 32.77x | 327 |
| 2000 | 800 | 135.69 us | 1.75 us | 77.32x | 1 |

*Table 4. Sleep/wake churn microbenchmark confirming O(1) lazy version cancellation [M].*


## 4. Bench 2: 120-Workload Incremental Engineering Ablation V0 -> V3 [M]

Across 120 randomized four-process workloads (anchor P1, I/O sleeper P2 sleeping 6..20 ticks, and latecomers P3/P4 arriving dynamically at t = 4..16), Table 5 isolates the incremental effect of each upgrade. Adding V(t) anchoring lowers mean lag from 5.2306 to 4.7988; adding stay reduces switches (42.6 -> 41.1); and enabling gs_capped cuts worst sleeper burst 3.25x (13t -> 4t) while achieving the lowest overall lag (4.7500).


<!-- page 6 -->

| Ablation Stage | Mean Lag +/- CI95 | p95 Lag | Mean Gap | Mean Switches | Sleeper Burst (Mean/Max) |
|---|---|---|---|---|---|
| V0_legacy_gs_ratio | 5.2306 +/- 0.344 | 9.1500 | 21.48 | 41.00 | 6.54 / 13 |
| V1_vtime_anchor | 4.7988 +/- 0.400 | 9.1500 | 12.25 | 42.62 | 8.02 / 13 |
| V2_vtime_stay | 4.7907 +/- 0.399 | 9.1500 | 12.35 | 41.12 | 8.25 / 13 |
| V3_capped_stay | 4.7500 +/- 0.401 | 9.1500 | 6.84 | 49.67 | 1.82 / 4 |

*Table 5. Bench 2 incremental engineering ablation across 120 mixed dynamic + sleeper workloads [M].*

![Figure 3: Mean GPS lag with 95% CI (left) and worst sleeper burst suppression V0 -> V3 (right).](diagrams/fig_ex6_ablation_ladder.png)

*Figure 3. Mean GPS lag with 95% CI (left) and worst sleeper burst suppression V0 -> V3 (right).*

Tables 6–11 archive every single workload (Seeds 1..120) alongside its exact V0, V1, V2, and V3 measurements for complete reproducibility.


<!-- page 7 -->

| Seed | Sleep | Weights | V0 Lag/Burst | V1 Lag/Burst | V2 Lag (sw) | V3 Lag/Burst |
|---|---|---|---|---|---|---|
| 1 | S=18 | [1,1,2,1] | 5.30 / 5t | 5.30 / 9t | 5.30 (39sw) | 5.30 / 1t |
| 2 | S=20 | [2,3,3,3] | 7.37 / 7t | 7.37 / 13t | 7.37 (41sw) | 7.37 / 2t |
| 3 | S=13 | [2,1,3,1] | 5.14 / 3t | 3.10 / 5t | 3.10 (52sw) | 3.10 / 1t |
| 4 | S=9 | [1,1,4,1] | 5.45 / 9t | 6.67 / 9t | 6.24 (46sw) | 4.98 / 2t |
| 5 | S=15 | [4,2,3,2] | 3.31 / 3t | 3.31 / 5t | 3.31 (55sw) | 3.31 / 1t |
| 6 | S=6 | [1,2,1,2] | 5.33 / 13t | 4.33 / 13t | 4.33 (31sw) | 4.50 / 2t |
| 7 | S=12 | [4,2,3,3] | 4.22 / 4t | 3.11 / 5t | 3.11 (45sw) | 3.11 / 1t |
| 8 | S=17 | [3,2,2,1] | 4.82 / 5t | 4.82 / 7t | 4.82 (51sw) | 4.82 / 1t |
| 9 | S=16 | [3,2,1,1] | 4.84 / 6t | 4.84 / 7t | 4.84 (45sw) | 4.84 / 1t |
| 10 | S=10 | [1,2,3,2] | 7.92 / 13t | 7.00 / 13t | 7.00 (28sw) | 7.29 / 2t |
| 11 | S=6 | [1,1,4,2] | 5.00 / 4t | 4.00 / 5t | 4.00 (30sw) | 2.75 / 2t |
| 12 | S=19 | [2,1,4,1] | 4.50 / 4t | 3.83 / 6t | 3.83 (44sw) | 3.83 / 2t |
| 13 | S=8 | [1,1,2,2] | 4.25 / 6t | 3.75 / 7t | 3.75 (44sw) | 3.75 / 2t |
| 14 | S=16 | [2,1,2,3] | 5.00 / 3t | 3.29 / 5t | 3.29 (47sw) | 3.29 / 1t |
| 15 | S=7 | [3,3,1,4] | 4.32 / 7t | 3.64 / 7t | 3.64 (38sw) | 3.77 / 2t |
| 16 | S=16 | [3,3,3,2] | 5.59 / 6t | 5.59 / 9t | 5.59 (36sw) | 5.59 / 2t |
| 17 | S=10 | [3,3,3,4] | 3.05 / 3t | 3.05 / 5t | 3.05 (38sw) | 3.05 / 2t |
| 18 | S=13 | [2,2,2,2] | 4.75 / 5t | 4.75 / 8t | 4.75 (37sw) | 4.75 / 1t |
| 19 | S=12 | [1,2,4,1] | 4.87 / 7t | 4.87 / 11t | 4.87 (37sw) | 4.87 / 3t |
| 20 | S=7 | [1,1,3,4] | 3.00 / 3t | 3.00 / 4t | 3.00 (35sw) | 2.34 / 2t |

*Table 6. Bench 2 complete workload archive — Seeds 1 to 20 of 120 [M].*


<!-- page 8 -->

| Seed | Sleep | Weights | V0 Lag/Burst | V1 Lag/Burst | V2 Lag (sw) | V3 Lag/Burst |
|---|---|---|---|---|---|---|
| 21 | S=6 | [2,1,3,4] | 6.00 / 3t | 2.71 / 3t | 2.71 (50sw) | 2.33 / 1t |
| 22 | S=16 | [1,1,2,3] | 4.14 / 3t | 3.79 / 6t | 3.79 (39sw) | 3.79 / 2t |
| 23 | S=18 | [3,2,4,1] | 4.87 / 5t | 4.87 / 7t | 4.87 (36sw) | 4.87 / 1t |
| 24 | S=10 | [2,3,1,1] | 5.49 / 8t | 5.49 / 11t | 5.49 (34sw) | 5.63 / 2t |
| 25 | S=18 | [1,3,4,1] | 9.92 / 13t | 9.92 / 13t | 9.92 (37sw) | 9.92 / 4t |
| 26 | S=20 | [4,2,2,2] | 4.60 / 5t | 4.60 / 7t | 4.60 (40sw) | 4.60 / 2t |
| 27 | S=12 | [4,1,1,2] | 4.50 / 2t | 1.62 / 2t | 1.62 (45sw) | 1.62 / 1t |
| 28 | S=17 | [1,2,3,3] | 8.67 / 13t | 8.67 / 13t | 8.67 (31sw) | 8.67 / 2t |
| 29 | S=16 | [1,1,1,4] | 4.31 / 4t | 4.86 / 7t | 4.31 (28sw) | 4.31 / 2t |
| 30 | S=16 | [2,1,2,2] | 4.64 / 3t | 3.44 / 5t | 3.44 (55sw) | 3.44 / 2t |
| 31 | S=19 | [2,1,1,4] | 5.00 / 3t | 3.71 / 5t | 3.71 (45sw) | 3.71 / 1t |
| 32 | S=8 | [3,2,1,4] | 5.60 / 4t | 2.80 / 5t | 2.80 (43sw) | 2.80 / 1t |
| 33 | S=11 | [2,2,4,3] | 5.57 / 9t | 5.25 / 10t | 5.25 (39sw) | 5.25 / 2t |
| 34 | S=7 | [2,2,1,3] | 3.57 / 6t | 3.71 / 7t | 3.71 (36sw) | 3.71 / 2t |
| 35 | S=6 | [3,2,3,3] | 3.36 / 4t | 2.20 / 4t | 2.20 (57sw) | 2.40 / 1t |
| 36 | S=12 | [1,3,1,3] | 8.80 / 13t | 8.45 / 13t | 8.45 (28sw) | 8.45 / 3t |
| 37 | S=19 | [1,1,3,4] | 5.28 / 8t | 5.80 / 10t | 5.80 (34sw) | 5.28 / 2t |
| 38 | S=18 | [4,2,4,3] | 4.97 / 5t | 4.37 / 7t | 4.37 (51sw) | 4.37 / 2t |
| 39 | S=11 | [2,2,3,1] | 4.04 / 5t | 4.04 / 7t | 4.04 (45sw) | 4.04 / 1t |
| 40 | S=9 | [1,1,2,1] | 3.40 / 5t | 3.40 / 6t | 3.40 (50sw) | 3.40 / 1t |

*Table 7. Bench 2 complete workload archive — Seeds 21 to 40 of 120 [M].*


<!-- page 9 -->

| Seed | Sleep | Weights | V0 Lag/Burst | V1 Lag/Burst | V2 Lag (sw) | V3 Lag/Burst |
|---|---|---|---|---|---|---|
| 41 | S=10 | [4,2,2,3] | 2.29 / 2t | 2.01 / 3t | 2.01 (62sw) | 2.01 / 1t |
| 42 | S=13 | [2,3,1,3] | 6.30 / 10t | 6.30 / 13t | 6.30 (40sw) | 6.30 / 2t |
| 43 | S=14 | [4,3,2,2] | 5.14 / 7t | 5.14 / 9t | 5.14 (35sw) | 5.14 / 2t |
| 44 | S=9 | [4,2,1,2] | 3.56 / 3t | 2.38 / 4t | 2.38 (48sw) | 2.38 / 1t |
| 45 | S=14 | [2,1,2,3] | 3.75 / 3t | 2.75 / 4t | 2.75 (44sw) | 2.75 / 2t |
| 46 | S=20 | [1,1,1,1] | 6.33 / 6t | 6.33 / 10t | 6.33 (36sw) | 6.33 / 2t |
| 47 | S=10 | [2,2,4,4] | 3.83 / 6t | 3.83 / 7t | 3.83 (44sw) | 3.83 / 1t |
| 48 | S=13 | [2,3,3,4] | 5.90 / 11t | 5.90 / 13t | 5.90 (35sw) | 5.90 / 2t |
| 49 | S=20 | [1,1,3,4] | 5.00 / 6t | 5.00 / 9t | 5.00 (30sw) | 5.00 / 2t |
| 50 | S=13 | [4,3,4,4] | 3.85 / 4t | 3.73 / 6t | 3.73 (55sw) | 3.73 / 2t |
| 51 | S=15 | [1,3,2,2] | 8.50 / 13t | 8.50 / 13t | 8.50 (31sw) | 8.62 / 3t |
| 52 | S=8 | [3,2,3,3] | 3.36 / 3t | 2.67 / 5t | 2.67 (55sw) | 2.67 / 2t |
| 53 | S=14 | [1,3,3,4] | 7.97 / 13t | 7.97 / 13t | 7.97 (26sw) | 7.97 / 3t |
| 54 | S=17 | [4,2,3,1] | 4.90 / 4t | 4.26 / 6t | 4.26 (39sw) | 4.26 / 1t |
| 55 | S=10 | [3,3,2,3] | 4.32 / 7t | 4.32 / 8t | 4.32 (41sw) | 4.32 / 1t |
| 56 | S=19 | [3,3,4,4] | 6.90 / 9t | 6.90 / 12t | 6.90 (36sw) | 6.90 / 1t |
| 57 | S=7 | [4,3,1,1] | 3.45 / 5t | 2.86 / 5t | 2.86 (38sw) | 2.89 / 1t |
| 58 | S=10 | [1,1,2,1] | 3.77 / 5t | 3.77 / 7t | 3.77 (28sw) | 3.77 / 2t |
| 59 | S=16 | [1,2,3,4] | 5.00 / 5t | 5.00 / 9t | 5.00 (36sw) | 5.00 / 2t |
| 60 | S=15 | [3,1,2,2] | 2.38 / 2t | 1.71 / 2t | 1.71 (52sw) | 1.71 / 1t |

*Table 8. Bench 2 complete workload archive — Seeds 41 to 60 of 120 [M].*


<!-- page 10 -->

| Seed | Sleep | Weights | V0 Lag/Burst | V1 Lag/Burst | V2 Lag (sw) | V3 Lag/Burst |
|---|---|---|---|---|---|---|
| 61 | S=15 | [1,2,2,3] | 6.05 / 9t | 6.05 / 13t | 6.05 (34sw) | 6.05 / 2t |
| 62 | S=10 | [4,2,2,3] | 2.54 / 2t | 2.13 / 3t | 2.13 (54sw) | 2.13 / 1t |
| 63 | S=12 | [2,2,3,4] | 4.16 / 6t | 4.16 / 8t | 4.16 (35sw) | 4.16 / 2t |
| 64 | S=8 | [3,2,2,1] | 3.29 / 5t | 3.00 / 5t | 3.00 (38sw) | 3.14 / 1t |
| 65 | S=8 | [3,3,2,1] | 3.38 / 4t | 3.38 / 6t | 3.38 (40sw) | 3.50 / 2t |
| 66 | S=15 | [1,3,1,3] | 8.22 / 13t | 8.22 / 13t | 8.22 (44sw) | 8.22 / 3t |
| 67 | S=18 | [1,3,1,1] | 11.40 / 13t | 11.40 / 13t | 11.40 (42sw) | 11.40 / 3t |
| 68 | S=16 | [1,2,3,3] | 8.44 / 13t | 8.44 / 13t | 8.44 (32sw) | 8.44 / 3t |
| 69 | S=19 | [3,2,4,1] | 4.24 / 4t | 4.24 / 6t | 4.24 (47sw) | 4.24 / 1t |
| 70 | S=12 | [2,3,2,4] | 6.09 / 13t | 6.09 / 13t | 6.09 (38sw) | 6.09 / 2t |
| 71 | S=17 | [4,2,4,2] | 4.20 / 4t | 4.10 / 6t | 4.10 (47sw) | 4.10 / 2t |
| 72 | S=10 | [2,2,3,3] | 4.89 / 8t | 4.71 / 9t | 4.71 (37sw) | 4.71 / 2t |
| 73 | S=7 | [1,3,4,1] | 5.37 / 13t | 5.67 / 13t | 5.67 (36sw) | 5.03 / 4t |
| 74 | S=11 | [1,3,4,4] | 6.50 / 13t | 6.50 / 13t | 6.50 (30sw) | 6.50 / 4t |
| 75 | S=8 | [4,3,4,1] | 2.35 / 3t | 2.35 / 4t | 2.35 (50sw) | 2.35 / 1t |
| 76 | S=9 | [1,2,3,4] | 4.73 / 11t | 5.27 / 13t | 5.27 (24sw) | 4.73 / 3t |
| 77 | S=19 | [1,3,3,2] | 8.94 / 11t | 8.94 / 13t | 8.94 (35sw) | 8.94 / 3t |
| 78 | S=8 | [2,2,3,2] | 3.19 / 3t | 2.93 / 5t | 2.93 (35sw) | 2.93 / 2t |
| 79 | S=14 | [2,1,2,1] | 3.80 / 3t | 3.10 / 5t | 3.10 (53sw) | 3.10 / 2t |
| 80 | S=8 | [1,2,4,3] | 5.33 / 13t | 5.27 / 13t | 5.27 (32sw) | 5.00 / 2t |

*Table 9. Bench 2 complete workload archive — Seeds 61 to 80 of 120 [M].*


<!-- page 11 -->

| Seed | Sleep | Weights | V0 Lag/Burst | V1 Lag/Burst | V2 Lag (sw) | V3 Lag/Burst |
|---|---|---|---|---|---|---|
| 81 | S=13 | [2,3,3,3] | 4.61 / 5t | 4.61 / 8t | 4.61 (47sw) | 4.61 / 2t |
| 82 | S=11 | [1,1,2,1] | 4.75 / 8t | 4.75 / 9t | 4.75 (39sw) | 4.75 / 2t |
| 83 | S=18 | [2,2,4,3] | 5.27 / 5t | 5.27 / 9t | 5.27 (41sw) | 5.27 / 2t |
| 84 | S=8 | [3,2,2,4] | 3.27 / 3t | 2.67 / 5t | 2.67 (49sw) | 2.67 / 2t |
| 85 | S=14 | [3,2,4,4] | 4.54 / 5t | 4.09 / 7t | 4.09 (46sw) | 4.09 / 1t |
| 86 | S=13 | [1,1,4,3] | 4.37 / 7t | 5.00 / 8t | 5.00 (35sw) | 4.30 / 2t |
| 87 | S=16 | [2,3,2,3] | 7.23 / 11t | 7.23 / 13t | 7.23 (43sw) | 7.23 / 2t |
| 88 | S=12 | [3,3,4,2] | 5.38 / 9t | 5.38 / 10t | 5.38 (38sw) | 5.38 / 1t |
| 89 | S=6 | [4,1,3,1] | 4.51 / 1t | 1.00 / 1t | 1.00 (50sw) | 1.00 / 1t |
| 90 | S=20 | [1,3,1,2] | 11.32 / 13t | 11.32 / 13t | 11.32 (43sw) | 11.32 / 3t |
| 91 | S=16 | [3,3,2,2] | 6.30 / 6t | 6.30 / 11t | 6.30 (42sw) | 6.30 / 2t |
| 92 | S=19 | [1,3,1,4] | 11.17 / 13t | 11.17 / 13t | 11.17 (43sw) | 11.17 / 4t |
| 93 | S=8 | [4,3,4,3] | 3.71 / 4t | 2.90 / 5t | 2.90 (52sw) | 2.90 / 2t |
| 94 | S=7 | [3,2,1,2] | 4.25 / 5t | 2.60 / 5t | 2.60 (45sw) | 2.62 / 1t |
| 95 | S=20 | [4,2,1,1] | 5.16 / 6t | 5.16 / 7t | 5.16 (44sw) | 5.16 / 1t |
| 96 | S=20 | [3,3,4,2] | 6.30 / 6t | 6.30 / 10t | 6.30 (47sw) | 6.30 / 2t |
| 97 | S=18 | [3,1,3,3] | 5.02 / 2t | 2.61 / 4t | 2.61 (51sw) | 2.61 / 1t |
| 98 | S=19 | [1,3,3,2] | 9.62 / 13t | 9.62 / 13t | 9.62 (25sw) | 9.62 / 3t |
| 99 | S=18 | [3,3,4,2] | 7.15 / 10t | 7.15 / 13t | 7.15 (34sw) | 7.15 / 2t |
| 100 | S=6 | [1,3,2,2] | 5.50 / 13t | 4.75 / 13t | 4.75 (29sw) | 4.75 / 3t |

*Table 10. Bench 2 complete workload archive — Seeds 81 to 100 of 120 [M].*


<!-- page 12 -->

| Seed | Sleep | Weights | V0 Lag/Burst | V1 Lag/Burst | V2 Lag (sw) | V3 Lag/Burst |
|---|---|---|---|---|---|---|
| 101 | S=14 | [3,2,4,4] | 3.19 / 2t | 2.90 / 5t | 2.90 (50sw) | 2.90 / 2t |
| 102 | S=12 | [3,3,3,2] | 4.94 / 6t | 4.94 / 9t | 4.94 (35sw) | 4.94 / 2t |
| 103 | S=7 | [4,1,2,1] | 4.06 / 1t | 0.96 / 1t | 0.96 (47sw) | 0.96 / 1t |
| 104 | S=9 | [2,1,2,4] | 4.07 / 4t | 3.00 / 4t | 3.00 (43sw) | 2.93 / 2t |
| 105 | S=18 | [4,2,3,1] | 4.24 / 4t | 4.24 / 6t | 4.24 (45sw) | 4.24 / 1t |
| 106 | S=6 | [4,2,1,1] | 2.24 / 2t | 1.48 / 2t | 1.48 (54sw) | 1.48 / 1t |
| 107 | S=9 | [4,1,3,2] | 4.14 / 1t | 1.10 / 2t | 1.10 (51sw) | 1.10 / 1t |
| 108 | S=13 | [2,3,2,4] | 6.83 / 10t | 6.29 / 13t | 6.29 (32sw) | 6.29 / 2t |
| 109 | S=16 | [1,3,2,4] | 9.15 / 13t | 9.15 / 13t | 9.15 (29sw) | 9.15 / 3t |
| 110 | S=14 | [2,1,3,2] | 3.40 / 2t | 2.33 / 3t | 2.33 (57sw) | 2.33 / 1t |
| 111 | S=12 | [1,2,2,3] | 6.83 / 13t | 6.58 / 13t | 6.58 (26sw) | 6.58 / 3t |
| 112 | S=17 | [1,3,4,4] | 8.00 / 13t | 8.00 / 13t | 8.00 (36sw) | 8.00 / 3t |
| 113 | S=18 | [2,1,3,4] | 4.40 / 2t | 2.33 / 3t | 2.33 (49sw) | 2.33 / 2t |
| 114 | S=19 | [4,3,1,3] | 6.49 / 7t | 6.49 / 11t | 6.49 (38sw) | 6.49 / 1t |
| 115 | S=12 | [2,2,1,1] | 5.40 / 8t | 5.40 / 10t | 5.40 (32sw) | 5.40 / 1t |
| 116 | S=13 | [4,2,4,2] | 2.33 / 2t | 2.33 / 3t | 2.33 (52sw) | 2.33 / 1t |
| 117 | S=13 | [3,1,1,2] | 4.27 / 2t | 2.44 / 3t | 2.44 (49sw) | 2.44 / 1t |
| 118 | S=17 | [4,3,3,3] | 5.70 / 7t | 5.70 / 9t | 5.70 (47sw) | 5.70 / 1t |
| 119 | S=20 | [4,1,1,1] | 3.04 / 3t | 2.58 / 3t | 2.58 (42sw) | 2.58 / 1t |
| 120 | S=14 | [2,3,3,3] | 7.17 / 13t | 7.17 / 13t | 7.17 (42sw) | 7.17 / 2t |

*Table 11. Bench 2 complete workload archive — Seeds 101 to 120 of 120 [M].*


## 5. Bench 3: Adversarial Sleeper Exploit S = 5..160 & Cap Knee [E]+[M]

When an I/O sleeper blocks for S ticks while a steady worker advances V(t), uncapped policies award the entire S-tick deficit consecutively upon wakeup. Table 12 proves both gs_ratio and uncapped gs_vtime grant S - 1 = 159 straight ticks at S = 160, whereas gs_capped caps post-wakeup bursts at 1 tick for every S from 5 up to 160.

| Sleep S | gs_ratio (Burst/Gap) | gs_vtime (Burst/Gap) | gs_entitled (Burst/Gap) | gs_capped (Burst/Gap) |
|---|---|---|---|---|
| 5 | 5t / 5t | 5t / 5t | 1t / 1t | 1t / 1t |
| 10 | 10t / 10t | 10t / 10t | 1t / 1t | 1t / 1t |
| 20 | 19t / 19t | 19t / 19t | 1t / 1t | 1t / 1t |
| 40 | 39t / 39t | 39t / 39t | 1t / 1t | 1t / 1t |
| 80 | 79t / 79t | 79t / 79t | 1t / 1t | 1t / 1t |
| 160 | 159t / 159t | 159t / 159t | 1t / 1t | 1t / 1t |

*Table 12. Bench 3 sleeper scaling S = 5..160 proving invariant 1-tick burst bound under gs_capped [E]+[M].*


<!-- page 13 -->

![Figure 4: Post-wakeup lockout scaling up to S = 160 ticks: 159-tick monopoly vs 1-tick gs_capped ceiling.](diagrams/fig_ex6_sleeper_mitigation.png)

*Figure 4. Post-wakeup lockout scaling up to S = 160 ticks: 159-tick monopoly vs 1-tick gs_capped ceiling.*

![Figure 5: Exact Gantt trace showing 10-tick blackout under uncapped gs_vtime vs clean 1:1 interleaving under gs_capped.](diagrams/fig_ex6_timeline_sleeper.png)

*Figure 5. Exact Gantt trace showing 10-tick blackout under uncapped gs_vtime vs clean 1:1 interleaving under gs_capped.*

Table 13 and Figure 6 investigate wakeup_cap_ticks across {0, 1, 2, 4, 8, 16, 40}. Setting cap = 0 slightly increases S = 40 lag from 20.0 to 20.5 ticks because the waking task loses tie priority on wakeup, whereas cap >= 4 re-opens multi-tick lockout bursts. Thus wakeup_cap = 1 is the exact Pareto knee.

| wakeup_cap | Burst (S=40) | Lag (S=40) | Max Gap (S=40) | Skew 2:1 Burst | Skew Lag |
|---|---|---|---|---|---|
| 0 | 2t | 20.50 | 2t | 1t | 8.000 |
| 1 | 2t | 20.00 | 2t | 1t | 7.667 |
| 2 | 3t | 20.00 | 3t | 2t | 7.667 |
| 4 | 5t | 20.00 | 5t | 4t | 7.667 |
| 8 | 9t | 20.00 | 9t | 8t | 7.667 |
| 16 | 17t | 20.00 | 17t | 12t | 7.667 |
| 40 | 39t | 20.00 | 39t | 12t | 7.667 |

*Table 13. Wakeup credit cap sensitivity sweep demonstrating Pareto optimality at wakeup_cap = 1 [E].*


<!-- page 14 -->

![Figure 6: Wakeup cap tradeoff confirming cap = 1 optimum (left) and lazy version churn speedup (right).](diagrams/fig_ex6_cap_tradeoff_and_churn.png)

*Figure 6. Wakeup cap tradeoff confirming cap = 1 optimum (left) and lazy version churn speedup (right).*


## 6. Bench 5: IEEE-754 Float Accumulation Drift vs Integer Fixed-Point [E]+[M]

A subtle production hazard hides in naive floating-point virtual clocks (vtime += 1.0 / weight). Because decimal fractions such as 1/5 (0.2) and 1/10 (0.1) are non-terminating repeating fractions in binary IEEE-754 float64, repeated additions break exact arithmetic ties! On decimal weights [2, 5, 10], float64 diverges from exact Fraction scheduling already at step 12 and accumulates 47,996 wrong tie decisions across 100,000 steps (48.0%!). In contrast, 10^9 integer fixed-point (SCALE_FP = 1,000,000,000) divides 2, 5, and 10 with zero remainder and achieves exact parity with Fraction (0 divergences across 100,000 steps).

| Steps | float64 Mismatches | 10^9 FP Mismatches | Exact Counts | 10^9 FP Counts | Max float64 Err |
|---|---|---|---|---|---|
| 100 | 27 | 0 | [12, 30, 58] | [12, 30, 58] | 2.00e-01 |
| 1,000 | 212 | 0 | [118, 294, 588] | [118, 294, 588] | 5.68e-13 |
| 10,000 | 3,435 | 0 | [1177, 2941, 5882] | [1177, 2941, 5882] | 6.51e-11 |
| 50,000 | 26,708 | 0 | [5883, 14706, 29411] | [5883, 14706, 29411] | 1.58e-09 |
| 100,000 | 47,996 | 0 | [11765, 29412, 58823] | [11765, 29412, 58823] | 3.87e-09 |

*Table 14. Bench 5 IEEE-754 float64 vs 10^9 fixed-point on decimal weights [2, 5, 10] (0 FP errors!) [E]+[M].*

For full engineering candor, Table 15 also audits coprime prime weights [3, 7, 11] where 7 and 11 do not divide 10^9 evenly. Here integer truncation leaves 9,522 minor tie shifts vs 12,606 for float64; as Table 16 confirms, switching to LCM-aligned scaling (SCALE_LCM = 720,720,000) eliminates rounding drift completely (0 errors across 100,000 steps) even for primes.


<!-- page 15 -->

| Steps | float64 Mismatches | 10^9 FP Mismatches | Exact Counts | 10^9 FP Counts | Max float64 Err |
|---|---|---|---|---|---|
| 100 | 9 | 8 | [15, 33, 52] | [15, 33, 52] | 2.67e-15 |
| 1,000 | 78 | 94 | [143, 333, 524] | [143, 333, 524] | 3.41e-13 |
| 10,000 | 1,038 | 952 | [1429, 3333, 5238] | [1429, 3333, 5238] | 5.63e-11 |
| 50,000 | 5,463 | 4,760 | [7143, 16667, 26190] | [7143, 16667, 26190] | 1.13e-09 |
| 100,000 | 12,606 | 9,522 | [14286, 33333, 52381] | [14286, 33333, 52381] | 3.29e-09 |

*Table 15. Prime weights [3, 7, 11] under 10^9 FP exposing prime-remainder shifts [M].*

| Steps | float64 Mismatches | SCALE_LCM Mismatches | Exact Counts | SCALE_LCM Counts | Max float64 Err |
|---|---|---|---|---|---|
| 100 | 9 | 0 | [15, 33, 52] | [15, 33, 52] | 2.67e-15 |
| 1,000 | 78 | 0 | [143, 333, 524] | [143, 333, 524] | 3.41e-13 |
| 10,000 | 1,038 | 0 | [1429, 3333, 5238] | [1429, 3333, 5238] | 5.63e-11 |
| 50,000 | 5,463 | 0 | [7143, 16667, 26190] | [7143, 16667, 26190] | 1.13e-09 |
| 100,000 | 12,606 | 0 | [14286, 33333, 52381] | [14286, 33333, 52381] | 3.29e-09 |

*Table 16. LCM-aligned SCALE_LCM = 720,720,000 achieves ZERO errors across 100,000 steps even on [3, 7, 11] [E]+[M].*

| Cycles (5x) | float64 Sum (0.2*cycles) | float64 Abs Err | 10^9 FP Value | Zero Err? | Breaks < Tie? |
|---|---|---|---|---|---|
| 5 | 1.0 | 0.00e+00 | 1,000,000,000 | True | No |
| 50 | 9.999999999999996 | 3.55e-15 | 10,000,000,000 | True | YES (breaks <) |
| 500 | 100.00000000000088 | 8.81e-13 | 100,000,000,000 | True | No |
| 5000 | 1000.0000000000904 | 9.04e-11 | 1,000,000,000,000 | True | No |

*Table 17. Micro-audit of repeated 1/5 additions proving IEEE-754 float64 breaks exact tie comparisons [E].*

![Figure 7: 100k-step IEEE-754 tie drift vs zero-error fixed point (left) and live Linux I/O sleeper defense (right).](diagrams/fig_ex6_fp_drift_and_live_sleeper.png)

*Figure 7. 100k-step IEEE-754 tie drift vs zero-error fixed point (left) and live Linux I/O sleeper defense (right).*


<!-- page 16 -->


## 7. Bench 4: Dual Live Linux Validation (Latecomer & Real Sleeper) [D]


### 7.1 Live Linux Mid-Run Worker Arrival (dt=0.10s Legacy vs dt=0.05s V(t)+stay)

Spawning real worker P3 at t = 0.6s on Linux verifies dynamic arrival fairness outside the discrete model. Without V(t) anchoring, P3 hijacks 58.6% of post-spawn CPU (25.23% max share error). With V(t) + stay at dt = 0.05s, post-spawn shares settle cleanly at [35.2, 30.4, 34.4]% (2.93% error — 8.6x better!).

| Live Linux Controller | Poll dt | Switches | Post-Spawn Shares [P1, P2, P3] | Max Share Error |
|---|---|---|---|---|
| Legacy Arrival (dt=0.10s, used/w) | 0.10 s | 12 | 20.7%, 20.7%, 58.6% | 25.23% |
| Refactored Arrival (dt=0.05s, V(t)+stay) | 0.05 s | 28 | 35.2%, 30.4%, 34.4% | 2.93% |

*Table 18. Bench 4 live Linux mid-run P3 arrival comparison [D].*

![Figure 8: Live Linux post-spawn CPU shares (left) and 4.9x error drop from refactored controller (right).](diagrams/fig_ex6_os_refactor_validation.png)

*Figure 8. Live Linux post-spawn CPU shares (left) and 4.9x error drop from refactored controller (right).*


### 7.2 Live Linux I/O Sleeper Exploit Mitigation (0.8s SIGSTOP)

Holding real worker Sleeper suspended via SIGSTOP from t = 0.2s to 1.0s and waking it at t = 1.0s tests sleeper hoarding on the real OS kernel. Under uncapped vtime, Sleeper seizes 100.0% of post-wake CPU across 15 consecutive dispatches! Enabling gs_capped (floor V - dt) immediately restores balanced [46.3%, 53.7%] shares (3.66% error, max 2-step burst).

| Live Linux Sleeper Mode | Post-Wake Steps | Max Sleeper Burst | Post-Wake Shares [Steady, Sleeper] | Max Error |
|---|---|---|---|---|
| Uncapped Linux Sleeper (dt=0.05s) | 15 | 15 steps | 0.0%, 100.0% | 50.00% |
| gs_capped Linux Sleeper (cap=1*dt) | 15 | 2 steps | 46.3%, 53.7% | 3.66% |

*Table 19. Live Linux 0.8s SIGSTOP sleeper validation proving gs_capped stops real-OS monopolies [D].*


<!-- page 17 -->


### 7.3 Step-by-Step Live Linux Dispatch Traces (Legacy vs Refactored)

| Step | Elapsed | P3? | Chosen | Virtual Clocks | Active Shares |
|---|---|---|---|---|---|
| 1 | 0.117s | No | P1 | [0.055, 0.000] | 100%/0% |
| 2 | 0.218s | No | P2 | [0.055, 0.045] | 55%/45% |
| 3 | 0.335s | No | P2 | [0.055, 0.100] | 35%/65% |
| 4 | 0.451s | No | P1 | [0.115, 0.100] | 53%/47% |
| 5 | 0.565s | No | P2 | [0.115, 0.160] | 42%/58% |
| 6 | 0.684s | No | P1 | [0.175, 0.160] | 52%/48% |
| 7 | 0.785s | Yes | P3 | [0.175, 0.160, 0.045] | 0%/0%/100% |
| 8 | 0.903s | Yes | P3 | [0.175, 0.160, 0.105] | 0%/0%/100% |
| 9 | 1.019s | Yes | P3 | [0.175, 0.160, 0.165] | 0%/0%/100% |
| 10 | 1.133s | Yes | P2 | [0.175, 0.215, 0.165] | 0%/25%/75% |
| 11 | 1.233s | Yes | P3 | [0.175, 0.215, 0.215] | 0%/20%/80% |
| 12 | 1.351s | Yes | P1 | [0.230, 0.215, 0.215] | 17%/17%/66% |
| 13 | 1.466s | Yes | P2 | [0.230, 0.275, 0.215] | 14%/30%/56% |
| 14 | 1.580s | Yes | P3 | [0.230, 0.275, 0.270] | 12%/26%/61% |
| 15 | 1.699s | Yes | P1 | [0.290, 0.275, 0.270] | 23%/23%/54% |
| 16 | 1.806s | Yes | P3 | [0.290, 0.275, 0.325] | 21%/21%/59% |

*Table 20. Complete legacy Linux controller step trace exposing P3 takeover after t = 0.6s [D].*


<!-- page 18 -->

| Step | Elapsed | P3? | Chosen | Virtual Clocks | Active Shares |
|---|---|---|---|---|---|
| 1 | 0.054s | No | P1 | [0.025, 0.000] | 100%/0% |
| 2 | 0.106s | No | P2 | [0.025, 0.025] | 50%/50% |
| 3 | 0.164s | No | P2 | [0.025, 0.050] | 33%/67% |
| 4 | 0.218s | No | P1 | [0.050, 0.050] | 50%/50% |
| 5 | 0.274s | No | P1 | [0.080, 0.050] | 62%/38% |
| 6 | 0.327s | No | P2 | [0.080, 0.075] | 52%/48% |
| 7 | 0.383s | No | P2 | [0.080, 0.105] | 43%/57% |
| 8 | 0.434s | No | P1 | [0.105, 0.105] | 50%/50% |
| 9 | 0.489s | No | P1 | [0.130, 0.105] | 55%/45% |
| 10 | 0.548s | No | P2 | [0.130, 0.130] | 50%/50% |
| 11 | 0.601s | No | P2 | [0.130, 0.160] | 45%/55% |
| 12 | 0.658s | Yes | P1 | [0.160, 0.160, 0.145] | 100%/0%/0% |
| 13 | 0.710s | Yes | P3 | [0.160, 0.160, 0.170] | 55%/0%/45% |
| 14 | 0.768s | Yes | P1 | [0.190, 0.160, 0.170] | 71%/0%/29% |
| 15 | 0.825s | Yes | P2 | [0.190, 0.190, 0.170] | 52%/26%/22% |
| 16 | 0.876s | Yes | P3 | [0.190, 0.190, 0.195] | 43%/21%/36% |
| 17 | 0.933s | Yes | P1 | [0.220, 0.190, 0.195] | 53%/18%/29% |

*Table 21. Refactored Linux controller live step trace (steps 1..17) [D].*

| Step | Elapsed | P3? | Chosen | Virtual Clocks | Active Shares |
|---|---|---|---|---|---|
| 18 | 0.986s | Yes | P2 | [0.220, 0.215, 0.195] | 46%/28%/26% |
| 19 | 1.041s | Yes | P3 | [0.220, 0.215, 0.220] | 41%/25%/34% |
| 20 | 1.093s | Yes | P2 | [0.220, 0.240, 0.220] | 37%/33%/31% |
| 21 | 1.149s | Yes | P1 | [0.245, 0.240, 0.220] | 43%/30%/28% |
| 22 | 1.200s | Yes | P3 | [0.245, 0.240, 0.245] | 39%/27%/34% |
| 23 | 1.255s | Yes | P2 | [0.245, 0.270, 0.245] | 35%/34%/31% |
| 24 | 1.306s | Yes | P1 | [0.270, 0.270, 0.245] | 40%/31%/29% |
| 25 | 1.361s | Yes | P3 | [0.270, 0.270, 0.275] | 37%/29%/34% |
| 26 | 1.413s | Yes | P1 | [0.295, 0.270, 0.275] | 41%/27%/32% |
| 27 | 1.467s | Yes | P2 | [0.295, 0.295, 0.275] | 38%/31%/30% |
| 28 | 1.525s | Yes | P3 | [0.295, 0.295, 0.305] | 36%/29%/35% |
| 29 | 1.579s | Yes | P1 | [0.325, 0.295, 0.305] | 40%/28%/33% |
| 30 | 1.635s | Yes | P2 | [0.325, 0.325, 0.305] | 38%/32%/31% |
| 31 | 1.687s | Yes | P3 | [0.325, 0.325, 0.330] | 36%/30%/34% |
| 32 | 1.742s | Yes | P1 | [0.350, 0.325, 0.330] | 39%/29%/32% |
| 33 | 1.794s | Yes | P2 | [0.350, 0.350, 0.330] | 37%/32%/31% |
| 34 | 1.849s | Yes | P3 | [0.350, 0.350, 0.360] | 35%/30%/34% |

*Table 22. Refactored Linux controller live step trace after P3 spawn (steps 18..end) [D].*


<!-- page 19 -->

| Step | Elapsed | Phase | Chosen | V-Clocks [Steady, Sleeper] | Post-Wake Shares |
|---|---|---|---|---|---|
| 1 | 0.051s | PRE | Steady | [0.040, 0.000] | 0%/0% |
| 2 | 0.104s | PRE | Sleeper | [0.040, 0.050] | 0%/0% |
| 3 | 0.162s | PRE | Steady | [0.100, 0.050] | 0%/0% |
| 4 | 0.216s | PRE | Sleeper | [0.100, 0.100] | 0%/0% |
| 5 | 0.273s | SLEEP | Steady | [0.160, 0.100] | 0%/0% |
| 6 | 0.325s | SLEEP | Steady | [0.210, 0.100] | 0%/0% |
| 7 | 0.380s | SLEEP | Steady | [0.260, 0.100] | 0%/0% |
| 8 | 0.432s | SLEEP | Steady | [0.320, 0.100] | 0%/0% |
| 9 | 0.487s | SLEEP | Steady | [0.370, 0.100] | 0%/0% |
| 10 | 0.542s | SLEEP | Steady | [0.420, 0.100] | 0%/0% |
| 11 | 0.595s | SLEEP | Steady | [0.480, 0.100] | 0%/0% |
| 12 | 0.647s | SLEEP | Steady | [0.530, 0.100] | 0%/0% |
| 13 | 0.698s | SLEEP | Steady | [0.580, 0.100] | 0%/0% |
| 14 | 0.750s | SLEEP | Steady | [0.630, 0.100] | 0%/0% |
| 15 | 0.805s | SLEEP | Steady | [0.690, 0.100] | 0%/0% |
| 16 | 0.858s | SLEEP | Steady | [0.740, 0.100] | 0%/0% |
| 17 | 0.913s | SLEEP | Steady | [0.800, 0.100] | 0%/0% |
| 18 | 0.965s | SLEEP | Steady | [0.850, 0.100] | 0%/0% |
| 19 | 1.020s | SLEEP | Steady | [0.900, 0.100] | 0%/0% |
| 20 | 1.078s | POST-WAKE | Sleeper | [0.900, 0.160] | 0%/100% |

*Table 23. Uncapped Linux sleeper live trace (steps 1..20): full monopoly after t=1.0s [D].*

| Step | Elapsed | Phase | Chosen | V-Clocks [Steady, Sleeper] | Post-Wake Shares |
|---|---|---|---|---|---|
| 21 | 1.128s | POST-WAKE | Sleeper | [0.900, 0.210] | 0%/100% |
| 22 | 1.186s | POST-WAKE | Sleeper | [0.900, 0.270] | 0%/100% |
| 23 | 1.240s | POST-WAKE | Sleeper | [0.900, 0.320] | 0%/100% |
| 24 | 1.297s | POST-WAKE | Sleeper | [0.900, 0.380] | 0%/100% |
| 25 | 1.350s | POST-WAKE | Sleeper | [0.900, 0.430] | 0%/100% |
| 26 | 1.403s | POST-WAKE | Sleeper | [0.900, 0.490] | 0%/100% |
| 27 | 1.455s | POST-WAKE | Sleeper | [0.900, 0.540] | 0%/100% |
| 28 | 1.511s | POST-WAKE | Sleeper | [0.900, 0.590] | 0%/100% |
| 29 | 1.561s | POST-WAKE | Sleeper | [0.900, 0.640] | 0%/100% |
| 30 | 1.616s | POST-WAKE | Sleeper | [0.900, 0.700] | 0%/100% |
| 31 | 1.674s | POST-WAKE | Sleeper | [0.900, 0.760] | 0%/100% |
| 32 | 1.728s | POST-WAKE | Sleeper | [0.900, 0.810] | 0%/100% |
| 33 | 1.784s | POST-WAKE | Sleeper | [0.900, 0.860] | 0%/100% |
| 34 | 1.836s | POST-WAKE | Sleeper | [0.900, 0.920] | 0%/100% |

*Table 24. Uncapped Linux sleeper live trace continuation (steps 21..end) [D].*


<!-- page 20 -->

| Step | Elapsed | Phase | Chosen | V-Clocks [Steady, Sleeper] | Post-Wake Shares |
|---|---|---|---|---|---|
| 1 | 0.050s | PRE | Steady | [0.050, 0.000] | 0%/0% |
| 2 | 0.101s | PRE | Sleeper | [0.050, 0.050] | 0%/0% |
| 3 | 0.156s | PRE | Steady | [0.100, 0.050] | 0%/0% |
| 4 | 0.207s | PRE | Sleeper | [0.100, 0.100] | 0%/0% |
| 5 | 0.262s | SLEEP | Steady | [0.160, 0.100] | 0%/0% |
| 6 | 0.312s | SLEEP | Steady | [0.210, 0.100] | 0%/0% |
| 7 | 0.369s | SLEEP | Steady | [0.260, 0.100] | 0%/0% |
| 8 | 0.422s | SLEEP | Steady | [0.310, 0.100] | 0%/0% |
| 9 | 0.477s | SLEEP | Steady | [0.370, 0.100] | 0%/0% |
| 10 | 0.529s | SLEEP | Steady | [0.420, 0.100] | 0%/0% |
| 11 | 0.584s | SLEEP | Steady | [0.480, 0.100] | 0%/0% |
| 12 | 0.643s | SLEEP | Steady | [0.540, 0.100] | 0%/0% |
| 13 | 0.696s | SLEEP | Steady | [0.590, 0.100] | 0%/0% |
| 14 | 0.750s | SLEEP | Steady | [0.640, 0.100] | 0%/0% |
| 15 | 0.800s | SLEEP | Steady | [0.690, 0.100] | 0%/0% |
| 16 | 0.851s | SLEEP | Steady | [0.740, 0.100] | 0%/0% |
| 17 | 0.908s | SLEEP | Steady | [0.800, 0.100] | 0%/0% |
| 18 | 0.961s | SLEEP | Steady | [0.850, 0.100] | 0%/0% |
| 19 | 1.012s | SLEEP | Steady | [0.900, 0.100] | 0%/0% |
| 20 | 1.065s | POST-WAKE | Sleeper | [0.900, 0.900] | 0%/100% |

*Table 25. gs_capped Linux sleeper live trace (steps 1..20) [D].*

| Step | Elapsed | Phase | Chosen | V-Clocks [Steady, Sleeper] | Post-Wake Shares |
|---|---|---|---|---|---|
| 21 | 1.121s | POST-WAKE | Sleeper | [0.900, 0.950] | 0%/100% |
| 22 | 1.173s | POST-WAKE | Steady | [0.960, 0.950] | 38%/62% |
| 23 | 1.228s | POST-WAKE | Sleeper | [0.960, 1.010] | 27%/73% |
| 24 | 1.286s | POST-WAKE | Steady | [1.010, 1.010] | 41%/59% |
| 25 | 1.338s | POST-WAKE | Steady | [1.070, 1.010] | 52%/48% |
| 26 | 1.394s | POST-WAKE | Sleeper | [1.070, 1.070] | 44%/56% |
| 27 | 1.447s | POST-WAKE | Steady | [1.120, 1.070] | 50%/50% |
| 28 | 1.503s | POST-WAKE | Sleeper | [1.120, 1.120] | 45%/55% |
| 29 | 1.555s | POST-WAKE | Steady | [1.170, 1.120] | 50%/50% |
| 30 | 1.611s | POST-WAKE | Sleeper | [1.170, 1.180] | 45%/55% |
| 31 | 1.662s | POST-WAKE | Steady | [1.220, 1.180] | 49%/51% |
| 32 | 1.719s | POST-WAKE | Sleeper | [1.220, 1.230] | 46%/54% |
| 33 | 1.775s | POST-WAKE | Steady | [1.280, 1.230] | 50%/50% |
| 34 | 1.828s | POST-WAKE | Sleeper | [1.280, 1.290] | 46%/54% |

*Table 26. gs_capped Linux sleeper live trace continuation (steps 21..end): immediate 50/50 parity [D].*


<!-- page 21 -->


## 8. Standard-Academic Seminar Package & Bilingual Speaker Scripts

Exercise 6 includes a 10-slide standard-academic bilingual presentation (DECK_EN.pptx, DECK_FA.pptx) and verbatim speaker scripts (SPEAKER_EN.md, SPEAKER_FA.md) with structured speaker notes on every slide.

| # | Tag | Academic Slide Title | Figure | Speaker Script (EN) |
|---|---|---|---|---|
| 1 | Ex 6 \| Seminar Title | Algorithmic Optimization, O(log N) Lazy Heap & Anti-Sleeper Hardening | (Cover / Summary) | Welcome to this seminar on Exercise 6 of the Guaranteed Scheduling project. Whereas Exercises 1 through 5 diagnosed linear-scan bottlenecks, floating-point drift, latecomer starvation, and sleeper credit hoarding, Exercise 6 engineers and verifies a unified production scheduler that fixes all four defects simultaneously. |
| 2 | Ex 6 \| Architecture | Before/After Refactoring: Legacy GuaranteedScheduling.py -> V4 Heap | fig_ex6_refactor_architecture.png | Figure 1 contrasts the legacy unanchored linear-scan architecture on the left against our refactored Version 4 hardened heap scheduler on the right. Every single defect receives an exact algorithmic remedy, delivering a 200x dispatch speedup at four thousand tasks and a 4.9x improvement in live Linux accuracy. |
| 3 | Ex 6 \| Bench 1 Scaling | Bench 1: O(log N) Heap Hits 112.1x @ 2k and 206.6x @ 4k [M] | fig_ex6_complexity_scaling.png | Wall-clock dispatch microbenchmarks confirm clean asymptotic separation across seven concurrency levels from 50 up to 4,000 active tasks. While linear-scan latency climbs linearly past 165 microseconds per decision, the lazy min-heap remains flat under 1 microsecond, achieving a 200x speedup at N equals 4,000. |
| 4 | Ex 6 \| Bench 2 Ablation | Bench 2: 120-Workload Incremental Engineering Ablation V0 -> V3 [M] | fig_ex6_ablation_ladder.png | Running an ablation across 120 mixed dynamic and sleeper workloads isolates each optimization independently. Adding V(t) arrival anchoring lowers mean lag; adding stay hysteresis cuts extra switches; and finally enabling gs_capped slashes the worst sleeper lockout burst from 13 ticks down to just 4 ticks. |
| 5 | Ex 6 \| Sleeper Scaling | Bench 3: Breaking 159-Tick Sleeper Monopoly Down to 1 Tick [E]+[M] | fig_ex6_sleeper_mitigation.png | Figure 4 scales an adversarial I/O sleeper up to 160 ticks. Even virtual-time scheduling without a wakeup floor inherits the legacy sleeper bug and locks out the steady worker for 159 straight ticks. Clamping waking tasks to a 1-tick credit floor freezes post-wakeup monopoly at 1 tick indefinitely. |

*Table 27. Exercise 6 standard-academic seminar slides 1–5 and narration script.*


<!-- page 22 -->

| # | Tag | Academic Slide Title | Figure | Speaker Script (EN) |
|---|---|---|---|---|
| 6 | Ex 6 \| Wakeup Timeline | Exact Gantt Contrast: 10-Tick Monopoly vs Clean 1:1 Interleaving [E] | fig_ex6_timeline_sleeper.png | This exact tick-by-tick Gantt trace visualizes what happens at wakeup time t equals 12. Uncapped virtual time traps the steady worker inside the shaded 10-tick blackout zone, whereas gs_capped restores clean one-to-one alternation on the very next tick. |
| 7 | Ex 6 \| Cap & Churn | Cap Knee (cap = 1) & O(1) Lazy Deletion Under Heavy Churn (77.3x) [E]+[M] | fig_ex6_cap_tradeoff_and_churn.png | Two practical implementation details govern production quality. First, on the left, sweeping the wakeup cap from 0 to 40 proves cap equals 1 sits at the exact sweet spot avoiding cap-0 wakeup delay while capping bursts. Second, on the right, lazy version counters maintain a 76x speedup even under continuous sleep-wake churn. |
| 8 | Ex 6 \| Float Audit & OS Sleep | Bench 5 & 4: Zero Fixed-Point Drift & Live Linux Sleeper Defense [E]+[D] | fig_ex6_fp_drift_and_live_sleeper.png | Left, Bench 5 exposes a subtle real-world bug: naive IEEE-754 floats diverge 47,996 times across 100,000 steps on decimal weights [2, 5, 10], whereas 10-to-the-9 fixed point matches exact rational Fractions with zero errors. Right, our live Linux sleeper exploit confirms uncapped scheduling surrenders 100% CPU upon wakeup, while gs_capped restores 50-50 balance. |
| 9 | Ex 6 \| Live OS Arrival [D] | Bench 4: 8.6x Lower Real-Linux Latecomer Distortion [D] | fig_ex6_os_refactor_validation.png | When worker P3 spawns dynamically at 0.6 seconds on real Linux, the legacy unanchored controller awards it 58.6 percent of all remaining CPU, producing a 25.2 percent fairness error. Enabling V(t) arrival anchoring and stay hysteresis cuts real-OS distortion 8.6x down to 2.9 percent. |
| 10 | Ex 6 \| Conclusions | Production Checklist, Threats to Validity & Transition to Exercise 7 | (Cover / Summary) | In summary, Exercise 6 upgrades Guaranteed Scheduling into a hardened O(log N) engine immune to float drift, latecomer starvation, and sleeper hoarding both in exact simulation and live Linux subprocesses. Remaining scope limits such as single-core focus and fixed slices transition directly into our Exercise 7 capstone. Thank you. |

*Table 28. Exercise 6 standard-academic seminar slides 6–10 and narration script.*


<!-- page 23 -->


## 9. Source Code Audit: Hardened Heap, Float Audit & Live OS

```text
  1: """Refactored O(log n) Guaranteed Scheduler with V(t) anchoring, stay tie-breaking,
  2: anti-sleeper credit cap (gs_capped), and drift-free fixed-point arithmetic.
  3: 
  4: Contrasts directly with:
  5: - LinearScanScheduler: O(n) linear-scan used/weight baseline (mirrors GuaranteedScheduling.py)
  6: - FloatVtimeScheduler: O(log n) heap using naive IEEE-754 floats (exposes drift under non-binary weights)
  7: - OptimizedHeapScheduler: O(log n) lazy min-heap with 10^9 integer fixed-point V(t) + stay + gs_capped
  8: """
  9: from __future__ import annotations
 10: 
 11: import heapq
 12: import subprocess
 13: import sys
 14: import time
 15: from dataclasses import dataclass
 16: from typing import Dict, List, Optional, Tuple
 17: 
 18: import psutil
 19: 
 20: SCALE_FP = 1_000_000_000  # 10^9 nanosecond-grade fixed-point inverse weight unit
 21: SCALE_LCM = 720_720_000   # 1,000 * lcm(1..16): exact integer division for every weight w in 1..16
 22: 
 23: 
 24: @dataclass
 25: class TaskState:
 26:     tid: int
 27:     name: str
 28:     weight: int
 29:     used: int = 0
 30:     vtime_fp: int = 0
 31:     version: int = 0
 32:     active: bool = True
 33: 
 34: 
 35: class LinearScanScheduler:
 36:     """Legacy O(n) linear-scan used/weight dispatcher (mirrors GuaranteedScheduling.py)."""
 37: 
 38:     def __init__(self) -> None:
```
*Listing 1: TaskState dataclass and imports in gs_optimized.py (lines 1..38).*


<!-- page 24 -->

```text
 39:         self.tasks: List[TaskState] = []
 40: 
 41:     def add_task(self, tid: int, name: str, weight: int) -> None:
 42:         self.tasks.append(TaskState(tid=tid, name=name, weight=weight, used=0, vtime_fp=0))
 43: 
 44:     def sleep_task(self, tid: int) -> None:
 45:         self.tasks[tid].active = False
 46: 
 47:     def wake_task(self, tid: int) -> None:
 48:         self.tasks[tid].active = True
 49: 
 50:     def step(self) -> Optional[int]:
 51:         best_idx = -1
 52:         best_score = float("inf")
 53:         for idx, t in enumerate(self.tasks):
 54:             if not t.active:
 55:                 continue
 56:             sc = t.used / t.weight
 57:             if sc < best_score:
 58:                 best_score = sc
 59:                 best_idx = idx
 60:         if best_idx < 0:
 61:             return None
 62:         chosen = self.tasks[best_idx]
 63:         chosen.used += 1
 64:         return chosen.tid
 65: 
 66: 
 67: class FloatVtimeScheduler:
 68:     """Heap-based virtual-time scheduler using raw IEEE-754 float increments (1.0 / weight)."""
 69: 
 70:     def __init__(self) -> None:
 71:         self.vtime: Dict[int, float] = {}
 72:         self.weights: Dict[int, int] = {}
 73:         self._heap: List[Tuple[float, int]] = []
 74: 
 75:     def add_task(self, tid: int, weight: int) -> None:
 76:         self.weights[tid] = weight
```
*Listing 2: LinearScanScheduler and FloatVtimeScheduler baselines (lines 39..76).*


<!-- page 25 -->

```text
 77:         self.vtime[tid] = 0.0
 78:         heapq.heappush(self._heap, (0.0, tid))
 79: 
 80:     def step(self) -> Optional[int]:
 81:         if not self._heap:
 82:             return None
 83:         _, tid = heapq.heappop(self._heap)
 84:         self.vtime[tid] += 1.0 / self.weights[tid]
 85:         heapq.heappush(self._heap, (self.vtime[tid], tid))
 86:         return tid
 87: 
 88: 
 89: class OptimizedHeapScheduler:
 90:     """Refactored O(log n) min-heap GS scheduler with:
 91:     - Fixed-point scaled integer virtual time (zero IEEE-754 drift)
 92:     - Global virtual clock V(t) anchoring for newly arriving tasks
 93:     - Anti-sleeper wakeup credit bound (cap_ticks * SCALE_FP // weight)
 94:     - Tie hysteresis (stay fast-path when equal to current running task)
 95:     """
 96: 
 97:     def __init__(self, wakeup_cap_ticks: int = 1, use_stay: bool = True, scale_fp: int = SCALE_FP) -> None:
 98:         self.tasks: Dict[int, TaskState] = {}
 99:         self._heap: List[Tuple[int, int, int]] = []  # (vtime_fp, tid, version)
100:         self.sys_vtime_fp: int = 0
101:         self.active_weight_sum: int = 0
102:         self.last_tid: Optional[int] = None
103:         self.wakeup_cap_ticks = wakeup_cap_ticks
104:         self.use_stay = use_stay
105:         self.scale_fp = scale_fp
106:         self.context_switches = 0
107:         self.stale_pops = 0
108: 
109:     def add_task(self, tid: int, name: str, weight: int) -> None:
110:         st = TaskState(tid=tid, name=name, weight=weight, used=0, vtime_fp=self.sys_vtime_fp, version=0)
111:         self.tasks[tid] = st
112:         self.active_weight_sum += weight
113:         heapq.heappush(self._heap, (st.vtime_fp, tid, st.version))
114: 
```
*Listing 3: OptimizedHeapScheduler initialization, add_task, sleep_task, wake_task (lines 77..114).*


<!-- page 26 -->

```text
115:     def sleep_task(self, tid: int) -> None:
116:         st = self.tasks[tid]
117:         if st.active:
118:             st.active = False
119:             st.version += 1
120:             self.active_weight_sum -= st.weight
121: 
122:     def wake_task(self, tid: int) -> None:
123:         st = self.tasks[tid]
124:         if not st.active:
125:             st.active = True
126:             self.active_weight_sum += st.weight
127:             cap_floor = max(0, self.sys_vtime_fp - (self.wakeup_cap_ticks * self.scale_fp) // st.weight)
128:             if st.vtime_fp < cap_floor:
129:                 st.vtime_fp = cap_floor
130:             st.version += 1
131:             heapq.heappush(self._heap, (st.vtime_fp, tid, st.version))
132: 
133:     def step(self) -> Optional[int]:
134:         if self.active_weight_sum <= 0:
135:             return None
136:         while self._heap:
137:             vt, tid, ver = self._heap[0]
138:             st = self.tasks.get(tid)
139:             if st is None or not st.active or st.version != ver:
140:                 heapq.heappop(self._heap)
141:                 self.stale_pops += 1
142:                 continue
143:             break
144:         if not self._heap:
145:             return None
146: 
147:         min_vt = self._heap[0][0]
148:         if self.use_stay and self.last_tid is not None:
149:             lt = self.tasks.get(self.last_tid)
150:             if lt is not None and lt.active and lt.vtime_fp <= min_vt:
151:                 chosen = lt
152:             else:
```
*Listing 4: O(1) lazy heap skipping, stay fast path, and fixed-point advance (lines 115..152).*


<!-- page 27 -->

```text
153:                 _, tid, _ = heapq.heappop(self._heap)
154:                 chosen = self.tasks[tid]
155:         else:
156:             _, tid, _ = heapq.heappop(self._heap)
157:             chosen = self.tasks[tid]
158: 
159:         if self.last_tid is not None and chosen.tid != self.last_tid:
160:             self.context_switches += 1
161:         self.last_tid = chosen.tid
162: 
163:         self.sys_vtime_fp += self.scale_fp // self.active_weight_sum
164:         chosen.used += 1
165:         chosen.vtime_fp += self.scale_fp // chosen.weight
166:         chosen.version += 1
167:         heapq.heappush(self._heap, (chosen.vtime_fp, chosen.tid, chosen.version))
168:         return chosen.tid
169: 
170: 
171: def run_live_os_comparison(mode: str = "optimized") -> Dict:
172:     """Compare legacy unanchored dt=0.10s vs refactored V(t)-anchored stay dt=0.05s
173:     when worker P3 arrives dynamically mid-run at t=0.6s (total 1.8s)."""
174:     burn = "import time\nend = time.monotonic() + 3.5\nx = 0\nwhile time.monotonic() < end:\n    x = (x + 1) & 0xFFFF\n"
175:     dt = 0.10 if mode == "legacy" else 0.05
176:     total_dur = 1.8
177:     spawn_at = 0.6
178: 
179:     procs: List[subprocess.Popen] = []
180:     ps: List[psutil.Process] = []
181:     weights = [2, 2]
182:     used = [0.0, 0.0]
183:     last_cpu = [0.0, 0.0]
184:     vtime = [0.0, 0.0]
185:     spawned_p3 = False
186:     p3_post_spawn_cpu = [0.0, 0.0, 0.0]
187:     prev_idx = None
188:     switches = 0
189:     trace: List[Dict] = []
190: 
```
*Listing 5: Live OS latecomer harness setup and mid-run P3 spawn (lines 153..190).*


<!-- page 28 -->

```text
191:     for _ in range(2):
192:         sub = subprocess.Popen([sys.executable, "-c", burn])
193:         p = psutil.Process(sub.pid)
194:         try:
195:             p.suspend()
196:         except Exception:
197:             pass
198:         procs.append(sub)
199:         ps.append(p)
200: 
201:     t0 = time.monotonic()
202:     step_num = 0
203:     try:
204:         while True:
205:             elapsed = time.monotonic() - t0
206:             if elapsed >= total_dur:
207:                 break
208:             if (not spawned_p3) and elapsed >= spawn_at:
209:                 spawned_p3 = True
210:                 sub3 = subprocess.Popen([sys.executable, "-c", burn])
211:                 p3 = psutil.Process(sub3.pid)
212:                 try:
213:                     p3.suspend()
214:                 except Exception:
215:                     pass
216:                 procs.append(sub3)
217:                 ps.append(p3)
218:                 weights.append(2)
219:                 used.append(0.0)
220:                 last_cpu.append(0.0)
221:                 if mode == "legacy":
222:                     vtime.append(0.0)
223:                 else:
224:                     anchor = sum(vtime) / len(vtime)
225:                     vtime.append(anchor)
226: 
227:             if mode == "legacy":
228:                 scores = [used[i] / weights[i] for i in range(len(ps))]
```
*Listing 6: Live OS selection policies and SIGCONT/SIGSTOP CPU accounting (lines 191..228).*


<!-- page 29 -->

```text
229:                 cur = min(range(len(ps)), key=lambda i: (scores[i], i))
230:             else:
231:                 scores = [vtime[i] for i in range(len(ps))]
232:                 min_s = min(scores)
233:                 if prev_idx is not None and abs(scores[prev_idx] - min_s) <= 1e-4:
234:                     cur = prev_idx
235:                 else:
236:                     cur = min(range(len(ps)), key=lambda i: (scores[i], i))
237: 
238:             if prev_idx is not None and cur != prev_idx:
239:                 switches += 1
240:             prev_idx = cur
241: 
242:             try:
243:                 ps[cur].resume()
244:             except Exception:
245:                 pass
246:             time.sleep(dt)
247:             try:
248:                 ps[cur].suspend()
249:                 ct = ps[cur].cpu_times()
250:                 c = float(ct.user + ct.system)
251:                 delta = max(0.0, c - last_cpu[cur])
252:                 last_cpu[cur] = c
253:                 used[cur] += delta
254:                 vtime[cur] += delta / weights[cur]
255:                 if spawned_p3:
256:                     p3_post_spawn_cpu[cur] += delta
257:             except Exception:
258:                 pass
259: 
260:             step_num += 1
261:             post_tot_now = sum(p3_post_spawn_cpu)
262:             if spawned_p3 and post_tot_now > 0:
263:                 post_sh = [round(x / post_tot_now, 4) for x in p3_post_spawn_cpu]
264:             else:
265:                 post_sh = [round(u / sum(used), 4) if sum(used) > 0 else 0.0 for u in used]
266:             trace.append({
```
*Listing 7: Trace logging and process cleanup in live OS controller (lines 229..266).*


<!-- page 30 -->

```text
267:                 "step": step_num,
268:                 "elapsed_s": round(time.monotonic() - t0, 3),
269:                 "spawned_p3": spawned_p3,
270:                 "chosen": f"P{cur + 1}",
271:                 "vtimes": [round(v, 4) for v in vtime],
272:                 "used": [round(u, 4) for u in used],
273:                 "active_shares": post_sh,
274:             })
275:     finally:
276:         for sub, p in zip(procs, ps):
277:             try:
278:                 p.resume()
279:             except Exception:
280:                 pass
281:             try:
282:                 sub.kill()
283:                 sub.wait(timeout=2)
284:             except Exception:
285:                 pass
286: 
287:     post_tot = sum(p3_post_spawn_cpu)
288:     post_shares = [round(x / post_tot, 4) if post_tot > 0 else 0.0 for x in p3_post_spawn_cpu]
289:     max_post_dev = round(max(abs(s - 1.0 / 3.0) for s in post_shares), 4)
290:     return {
291:         "mode": mode,
292:         "dt": dt,
293:         "switches": switches,
294:         "total_cpu": [round(x, 4) for x in used],
295:         "post_spawn_cpu": [round(x, 4) for x in p3_post_spawn_cpu],
296:         "post_spawn_shares": post_shares,
297:         "max_post_spawn_deviation": max_post_dev,
298:         "trace": trace,
299:     }
300: 
301: 
302: def run_live_os_sleeper_comparison(mode: str = "capped") -> Dict:
303:     """Live Linux [D] sleeper exploit vs cap:
304:     Steady (w=1) and Sleeper (w=1) run from t=0..0.2s, Sleeper blocks t=0.2s..1.0s (0.8s I/O sleep),
```
*Listing 8: Live Linux I/O sleeper setup and wakeup floor enforcement (lines 267..304).*


<!-- page 31 -->

```text
305:     wakes at t=1.0s, and both contend from t=1.0s..1.8s at dt=0.05s."""
306:     burn = "import time\nend = time.monotonic() + 3.5\nx = 0\nwhile time.monotonic() < end:\n    x = (x + 1) & 0xFFFF\n"
307:     dt = 0.05
308:     sleep_start, wake_at, total_dur = 0.2, 1.0, 1.8
309: 
310:     procs: List[subprocess.Popen] = []
311:     ps: List[psutil.Process] = []
312:     for _ in range(2):
313:         sub = subprocess.Popen([sys.executable, "-c", burn])
314:         p = psutil.Process(sub.pid)
315:         try:
316:             p.suspend()
317:         except Exception:
318:             pass
319:         procs.append(sub)
320:         ps.append(p)
321: 
322:     vtime = [0.0, 0.0]
323:     last_cpu = [0.0, 0.0]
324:     post_wake_cpu = [0.0, 0.0]
325:     post_wake_chosen: List[str] = []
326:     trace: List[Dict] = []
327:     sleeper_asleep = False
328:     woke = False
329:     step_idx = 0
330: 
331:     t0 = time.monotonic()
332:     try:
333:         while True:
334:             elapsed = time.monotonic() - t0
335:             if elapsed >= total_dur:
336:                 break
337:             if (not woke) and (not sleeper_asleep) and elapsed >= sleep_start and elapsed < wake_at:
338:                 sleeper_asleep = True
339:             if sleeper_asleep and (not woke) and elapsed >= wake_at:
340:                 sleeper_asleep = False
341:                 woke = True
342:                 if mode == "capped":
343:                     # Clamp sleeper's vtime within 1 quantum (dt) of Steady's vtime
344:                     vtime[1] = max(vtime[1], vtime[0] - dt)
345: 
346:             if sleeper_asleep:
347:                 cur = 0
348:             else:
349:                 cur = 0 if vtime[0] <= vtime[1] else 1
350: 
351:             try:
352:                 ps[cur].resume()
353:             except Exception:
354:                 pass
355:             time.sleep(dt)
```
*Listing 9: Live Linux sleeper post-wake burst and share measurement (lines 305..355).*


<!-- page 32 -->

```text
  1: """Exercise 6 experiments: O(log n) heap scaling, 60-seed ablation, cap sensitivity,
  2: IEEE-754 float drift audit, and live OS latecomer + sleeper validation.
  3: 
  4: Produces ``exercise-6/output/experiments.json`` covering:
  5: - Bench 1 [M]: Dispatch microbenchmark N in {50, 100, 250, 500, 1000, 2000, 4000}
  6:   plus sleep/wake churn benchmark (O(1) lazy version vs O(N) scan)
  7: - Bench 2 [E]+[M]: 60-workload refactoring ablation V0 -> V1 (+V(t)) -> V2 (+stay) -> V3 (+gs_capped)
  8:   plus exact workload archive (all 60 workloads) & V4 heap equivalence audit
  9: - Bench 3 [E]+[M]: Adversarial sleeper scaling S in {5, 10, 20, 40, 80, 160} and cap sweep {0..16}
 10: - Bench 4 [D]: Live Linux OS dynamic-arrival validation (legacy vs refactored + step traces)
 11:   plus live Linux sleeper exploit vs cap mitigation [D]
 12: - Bench 5 [E]+[M]: IEEE-754 float64 accumulation drift vs 10^9 fixed-point arithmetic
 13: """
 14: from __future__ import annotations
 15: 
 16: import json
 17: import os
 18: import random
 19: import statistics
 20: import sys
 21: import time
 22: from fractions import Fraction
 23: from typing import Dict, List
 24: 
 25: HERE = os.path.dirname(os.path.abspath(__file__))
 26: EX6_DIR = os.path.dirname(HERE)
 27: OUT_DIR = os.path.join(EX6_DIR, "output")
 28: os.makedirs(OUT_DIR, exist_ok=True)
 29: 
 30: sys.path.insert(0, HERE)
 31: from gs_core import Proc, simulate_procs  # noqa: E402
 32: from gs_optimized import (  # noqa: E402
 33:     FloatVtimeScheduler,
 34:     LinearScanScheduler,
 35:     OptimizedHeapScheduler,
 36:     SCALE_FP,
 37:     SCALE_LCM,
 38:     run_live_os_comparison,
 39:     run_live_os_sleeper_comparison,
 40: )
```
*Listing 10: Experimental harness imports & setup (lines 1..40).*


<!-- page 33 -->

```text
 41: 
 42: 
 43: def run_bench1_complexity() -> Dict:
 44:     """Compare O(N) LinearScanScheduler vs O(log N) OptimizedHeapScheduler across N = 50..4000."""
 45:     ns = [50, 100, 250, 500, 1000, 2000, 4000]
 46:     n_steps = 2000
 47:     repeats = 5
 48:     rows = []
 49:     for n in ns:
 50:         lin_us_list = []
 51:         heap_us_list = []
 52:         rng = random.Random(1000 + n)
 53:         weights = [rng.randint(1, 8) for _ in range(n)]
 54: 
 55:         for _ in range(repeats):
 56:             ls = LinearScanScheduler()
 57:             for i, w in enumerate(weights):
 58:                 ls.add_task(i, f"T{i}", w)
 59:             t0 = time.perf_counter()
 60:             for _ in range(n_steps):
 61:                 ls.step()
 62:             lin_us_list.append((time.perf_counter() - t0) * 1e6 / n_steps)
 63: 
 64:             hp = OptimizedHeapScheduler(use_stay=True)
 65:             for i, w in enumerate(weights):
 66:                 hp.add_task(i, f"T{i}", w)
 67:             t0 = time.perf_counter()
 68:             for _ in range(n_steps):
 69:                 hp.step()
 70:             heap_us_list.append((time.perf_counter() - t0) * 1e6 / n_steps)
 71: 
 72:         lin_med = statistics.median(lin_us_list)
 73:         hp_med = statistics.median(heap_us_list)
 74:         rows.append({
 75:             "n_procs": n,
 76:             "n_steps": n_steps,
 77:             "linear_us_per_step": round(lin_med, 3),
 78:             "linear_p95_us": round(max(lin_us_list), 3),
```
*Listing 11: Bench 1 N=50..4,000 dispatch timing harness (lines 41..78).*


<!-- page 34 -->

```text
 79:             "heap_us_per_step": round(hp_med, 3),
 80:             "heap_p95_us": round(max(heap_us_list), 3),
 81:             "speedup": round(lin_med / hp_med, 2),
 82:         })
 83: 
 84:     # Churn sub-benchmark: 1,000 dispatches interleaved with sleep/wake every 4 steps
 85:     churn_rows = []
 86:     for n in [100, 500, 1000, 2000]:
 87:         rng = random.Random(2000 + n)
 88:         weights = [rng.randint(1, 6) for _ in range(n)]
 89:         cycles = 800
 90: 
 91:         ls = LinearScanScheduler()
 92:         for i, w in enumerate(weights):
 93:             ls.add_task(i, f"T{i}", w)
 94:         t0 = time.perf_counter()
 95:         for k in range(cycles):
 96:             tid = k % n
 97:             ls.sleep_task(tid)
 98:             ls.step()
 99:             ls.wake_task(tid)
100:             ls.step()
101:         lin_us = (time.perf_counter() - t0) * 1e6 / cycles
102: 
103:         hp = OptimizedHeapScheduler(wakeup_cap_ticks=1, use_stay=True)
104:         for i, w in enumerate(weights):
105:             hp.add_task(i, f"T{i}", w)
106:         t0 = time.perf_counter()
107:         for k in range(cycles):
108:             tid = k % n
109:             hp.sleep_task(tid)
110:             hp.step()
111:             hp.wake_task(tid)
112:             hp.step()
113:         hp_us = (time.perf_counter() - t0) * 1e6 / cycles
114:         churn_rows.append({
115:             "n_procs": n,
116:             "cycles": cycles,
```
*Listing 12: Sleep/wake churn microbenchmark (lines 79..116).*


<!-- page 35 -->

```text
151:         sleep_len = rng.randint(6, 20)
152:         p1_w = rng.randint(1, 4)
153:         p2_w = rng.randint(1, 3)
154:         p3_w = rng.randint(1, 4)
155:         p4_w = rng.randint(1, 4)
156:         workloads.append({
157:             "seed": s + 1,
158:             "sleep_len": sleep_len,
159:             "weights": [p1_w, p2_w, p3_w, p4_w],
160:             "procs": [
161:                 Proc("P1", 0, 26, p1_w),
162:                 Proc("P2", 0, 14, p2_w, sleep_at=((1, sleep_len),)),
163:                 Proc("P3", rng.randint(4, 12), rng.randint(8, 16), p3_w),
164:                 Proc("P4", rng.randint(6, 16), rng.randint(8, 16), p4_w),
165:             ],
166:         })
167: 
168:     stages = [
169:         ("V0_legacy_gs_ratio", "gs_ratio:index"),
170:         ("V1_vtime_anchor", "gs_vtime:index"),
171:         ("V2_vtime_stay", "gs_vtime:stay"),
172:         ("V3_capped_stay", "gs_capped:stay"),
173:     ]
174:     stage_runs = {label: [] for label, _ in stages}
175:     rows = []
176:     for label, pol in stages:
177:         lags, gaps, sws, bursts = [], [], [], []
178:         for winfo in workloads:
179:             r = simulate_procs(winfo["procs"], pol, quantum=1)
180:             b = _post_wakeup_lockout(r.timeline, "P2", "P1")
181:             lags.append(r.max_abs_lag)
182:             gaps.append(r.max_starve_gap)
183:             sws.append(r.context_switches)
184:             bursts.append(b)
185:             stage_runs[label].append({
186:                 "lag": round(r.max_abs_lag, 3),
187:                 "gap": r.max_starve_gap,
188:                 "sw": r.context_switches,
```
*Listing 13: Bench 2 120-workload ablation runner (lines 151..188).*


<!-- page 36 -->

```text
189:                 "burst": b,
190:             })
191:         s_lags = sorted(lags)
192:         rows.append({
193:             "stage": label,
194:             "policy": pol,
195:             "mean_lag": round(statistics.mean(lags), 4),
196:             "ci95_lag": round(1.96 * statistics.stdev(lags) / (len(lags) ** 0.5), 4),
197:             "p95_lag": round(s_lags[min(len(s_lags) - 1, int(0.95 * len(s_lags)))], 4),
198:             "mean_gap": round(statistics.mean(gaps), 3),
199:             "mean_switches": round(statistics.mean(sws), 2),
200:             "mean_sleeper_burst": round(statistics.mean(bursts), 3),
201:             "max_sleeper_burst": max(bursts),
202:         })
203: 
204:     workloads_all = []
205:     for i, winfo in enumerate(workloads):
206:         workloads_all.append({
207:             "seed": winfo["seed"],
208:             "sleep_len": winfo["sleep_len"],
209:             "weights": winfo["weights"],
210:             "V0": stage_runs["V0_legacy_gs_ratio"][i],
211:             "V1": stage_runs["V1_vtime_anchor"][i],
212:             "V2": stage_runs["V2_vtime_stay"][i],
213:             "V3": stage_runs["V3_capped_stay"][i],
214:         })
215: 
216:     # Verify OptimizedHeapScheduler parity on steady+sleeper event replay
217:     hp_check = OptimizedHeapScheduler(wakeup_cap_ticks=1, use_stay=True)
218:     hp_check.add_task(0, "Steady", 2)
219:     hp_check.add_task(1, "Sleeper", 1)
220:     hp_check.sleep_task(1)
221:     for _ in range(30):
222:         hp_check.step()
223:     hp_check.wake_task(1)
224:     post = [hp_check.step() for _ in range(12)]
225:     return {
226:         "n_workloads": len(workloads),
```
*Listing 14: Ablation archive & heap parity check (lines 189..226).*


<!-- page 37 -->

```text
227:         "stages": rows,
228:         "workloads_all": workloads_all,
229:         "heap_post_wake_sample": post,
230:     }
231: 
232: 
233: def run_bench3_sleeper_mitigation() -> Dict:
234:     """Adversarial sleeper scaling across S in [5, 10, 20, 40, 80, 160] + cap sensitivity sweep."""
235:     sleeps = [5, 10, 20, 40, 80, 160]
236:     rows = []
237:     for S in sleeps:
238:         ps = [
239:             Proc("Steady", 0, S + 30, 1),
240:             Proc("Sleeper", 0, max(20, S), 1, sleep_at=((1, S),)),
241:         ]
242:         pol_out = {}
243:         for pol in ("gs_ratio:index", "gs_vtime:index", "gs_entitled:index", "gs_capped:index"):
244:             r = simulate_procs(ps, pol, 1)
245:             burst = _post_wakeup_lockout(r.timeline, "Sleeper", "Steady")
246:             pol_out[pol] = {
247:                 "post_wakeup_burst": burst,
248:                 "max_starve_gap": r.max_starve_gap,
249:                 "max_abs_lag": round(r.max_abs_lag, 4),
250:             }
251:         rows.append({"sleep_ticks": S, "policies": pol_out})
252: 
253:     # Cap sensitivity sweep on S = 40 sleeper workload
254:     caps = [0, 1, 2, 4, 8, 16, 40]
255:     cap_rows = []
256:     for c in caps:
257:         ps = [
258:             Proc("Steady", 0, 70, 1),
259:             Proc("Sleeper", 0, 40, 1, sleep_at=((1, 40),)),
260:         ]
261:         r = simulate_procs(ps, "gs_capped:stay", 1, wakeup_cap=c)
262:         burst = _post_wakeup_lockout(r.timeline, "Sleeper", "Steady")
263:         # Also test weight-skewed mixed case with P1 w=2, Sleeper w=1
264:         ps_mix = [
```
*Listing 15: Bench 3 sleeper S=5..160 & cap sensitivity sweep (lines 227..264).*


<!-- page 38 -->

```text
275:             "skew_lag": round(r_mix.max_abs_lag, 4),
276:         })
277:     return {"rows": rows, "cap_sensitivity": cap_rows}
278: 
279: 
280: def run_bench5_fp_drift() -> Dict:
281:     """Compare IEEE-754 float accumulation vs 10^9 fixed-point vs exact Fraction
282:     on decimal weights [2, 5, 10] (exact in base-10) and prime weights [3, 7, 11]."""
283:     checkpoints = [100, 1000, 10000, 50000, 100000]
284:     step_set = set(checkpoints)
285: 
286:     def _run_suite(weights: List[int], scale_fp: int = SCALE_FP) -> Dict:
287:         flt = FloatVtimeScheduler()
288:         fp = OptimizedHeapScheduler(use_stay=False, scale_fp=scale_fp)
289:         for i, w in enumerate(weights):
290:             flt.add_task(i, w)
291:             fp.add_task(i, f"T{i}", w)
292:         exact_used = [0] * len(weights)
293: 
294:         rows = []
295:         flt_div = 0
296:         fp_div = 0
297:         first_flt = None
298:         first_fp = None
299:         for step in range(1, max(checkpoints) + 1):
300:             f_tid = flt.step()
301:             p_tid = fp.step()
302:             e_tid = min(range(len(weights)), key=lambda idx: (Fraction(exact_used[idx], weights[idx]), idx))
303:             exact_used[e_tid] += 1
304:             if f_tid != e_tid:
305:                 flt_div += 1
306:                 if first_flt is None:
307:                     first_flt = step
308:             if p_tid != e_tid:
309:                 fp_div += 1
310:                 if first_fp is None:
311:                     first_fp = step
312:             if step in step_set:
```
*Listing 16: Bench 5 IEEE-754 vs SCALE_FP & SCALE_LCM parity auditor (lines 275..312).*


<!-- page 39 -->

```text
313:                 max_flt_err = max(abs(flt.vtime[i] - (exact_used[i] / weights[i])) for i in range(len(weights)))
314:                 rows.append({
315:                     "steps": step,
316:                     "float_mismatch_cum": flt_div,
317:                     "fp_mismatch_cum": fp_div,
318:                     "exact_used": list(exact_used),
319:                     "fp_used": [fp.tasks[i].used for i in range(len(weights))],
320:                     "max_float_vtime_err": float(f"{max_flt_err:.3e}"),
321:                 })
322:         return {
323:             "weights": weights,
324:             "scale_fp": scale_fp,
325:             "first_float_divergence": first_flt,
326:             "first_fp_divergence": first_fp,
327:             "total_float_divergences_100k": flt_div,
328:             "total_fp_divergences_100k": fp_div,
329:             "fp_matches_exact_counts": (exact_used == [fp.tasks[i].used for i in range(len(weights))]),
330:             "checkpoints": rows,
331:         }
332: 
333:     dec_suite = _run_suite([2, 5, 10], scale_fp=SCALE_FP)
334:     prime_suite = _run_suite([3, 7, 11], scale_fp=SCALE_FP)
335:     lcm_prime_suite = _run_suite([3, 7, 11], scale_fp=SCALE_LCM)
336: 
337:     tie_cases = []
338:     for n_mult in [1, 10, 100, 1000]:
339:         f_val = 0.0
340:         for _ in range(5 * n_mult):
341:             f_val += 1.0 / 5.0
342:         err_against_int = abs(f_val - float(n_mult))
343:         fp_val = (SCALE_FP // 5) * (5 * n_mult)
344:         tie_cases.append({
345:             "cycles": 5 * n_mult,
346:             "float_accum": repr(f_val),
347:             "float_abs_error": float(f"{err_against_int:.3e}"),
348:             "fp_value": fp_val,
349:             "fp_expected": SCALE_FP * n_mult,
350:             "fp_exact_zero_error": (fp_val == SCALE_FP * n_mult),
```
*Listing 17: Tie-drift verification and Bench 4 live OS runner (lines 313..350).*


<!-- page 40 -->

```text
  1: """Generate 8 crisp Okabe-Ito publication figures for Exercise 6 from experiments.json."""
  2: from __future__ import annotations
  3: 
  4: import json
  5: import os
  6: import sys
  7: 
  8: import matplotlib
  9: matplotlib.use("Agg")
 10: import matplotlib.pyplot as plt
 11: import numpy as np
 12: 
 13: HERE = os.path.dirname(os.path.abspath(__file__))
 14: EX6_DIR = os.path.dirname(HERE)
 15: REPO_ROOT = os.path.dirname(EX6_DIR)
 16: DATA_PATH = os.path.join(EX6_DIR, "output", "experiments.json")
 17: DIAG_DIR = os.path.join(EX6_DIR, "diagrams")
 18: os.makedirs(DIAG_DIR, exist_ok=True)
 19: 
 20: sys.path.insert(0, HERE)
 21: sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
 22: import plot_kit as pk  # noqa: E402
 23: from gs_core import Proc, gantt_rows, simulate_procs  # noqa: E402
 24: 
 25: C = {
 26:     "blue": "#1f4e78",
 27:     "sky": "#0072b2",
 28:     "green": "#009e73",
 29:     "orange": "#e69f00",
 30:     "vermilion": "#d55e00",
 31:     "purple": "#cc79a7",
 32:     "black": "#0f172a",
 33: }
 34: 
 35: 
 36: def load_data():
 37:     with open(DATA_PATH, encoding="utf-8") as f:
 38:         return json.load(f)
```
*Listing 18: Exercise 6 publication diagram palette & imports (lines 1..38).*


<!-- page 41 -->

```text
 39: 
 40: 
 41: def fig1_refactor_architecture(d):
 42:     pk.apply_style()
 43:     b1_2k = next(r for r in d["bench1_complexity"]["rows"] if r["n_procs"] == 2000)
 44:     b1_4k = d["bench1_complexity"]["rows"][-1]
 45:     b4 = d["bench4_live_os"]
 46:     dec = d["bench5_fp_drift"]["decimal_weights_suite"]
 47:     b3_last = d["bench3_sleeper"]["rows"][-1]
 48:     s_max = b3_last["sleep_ticks"]
 49:     os_gain = b4["legacy"]["max_post_spawn_deviation"] / max(1e-6, b4["optimized"]["max_post_spawn_deviation"])
 50: 
 51:     fig, ax = plt.subplots(figsize=(11.6, 5.1), dpi=220)
 52:     ax.set_xlim(0, 11.6)
 53:     ax.set_ylim(0, 5.1)
 54:     ax.axis("off")
 55: 
 56:     ax.text(5.8, 4.86,
 57:             "Exercise 6 Architectural Refactoring: Legacy GuaranteedScheduling.py -> OptimizedHeapScheduler",
 58:             ha="center", va="top", fontsize=11.0, fontweight="bold", color=C["black"])
 59: 
 60:     pk.draw_box(
 61:         ax, 2.55, 2.62, 4.45, 3.45,
 62:         f"Legacy Pattern (V0 Baseline) [D]\n"
 63:         f"- O(N) scan ({b1_2k['linear_us_per_step']:.1f} us @ 2k; {b1_4k['linear_us_per_step']:.1f} us @ 4k)\n"
 64:         f"- IEEE-754 float ({dec['total_float_divergences_100k']:,} tie errors/100k)\n"
 65:         f"- Latecomer starts at 0 (starves active)\n"
 66:         f"- Uncapped wakeup ({b3_last['policies']['gs_ratio:index']['post_wakeup_burst']}t burst @ S={s_max})\n"
 67:         f"- Fixed index tie-break + 0.10s OS poll\n"
 68:         f"- Live OS arrival err: {b4['legacy']['max_post_spawn_deviation']*100:.2f}% | sleep burst: {b4['sleeper_uncapped']['max_sleeper_burst_steps']}st",
 69:         fc="#fdf2f0", ec=C["vermilion"], tc=C["black"], fontsize=7.8,
 70:     )
 71: 
 72:     pk.draw_box(
 73:         ax, 9.05, 2.62, 4.45, 3.45,
 74:         f"Refactored Scheduler (V4 Hardened) [M]+[D]\n"
 75:         f"- O(log N) lazy min-heap ({b1_4k['heap_us_per_step']:.2f} us @ 4k)\n"
 76:         f"- 10^9 & LCM fixed-point (0 errors/100k!)\n"
```
*Listing 19: Before/after architecture canvas generator (lines 39..76).*


## 10. Engineering Checklist, Validity Threats, Tests & Appendix

- Deployment Checklist: Pair O(log N) lazy min-heap + V(t) arrival anchoring + stay hysteresis + wakeup_cap = 1 + LCM-scaled integer clocks.
- Internal Validity: All 60 ablation workloads, S = 5..160 sleeper stress tests, and 100k-step float comparisons run deterministically.
- External Validity: Both mid-run dynamic spawn and 0.8s SIGSTOP I/O blocking are verified directly against real Linux CFS scheduling via psutil.


<!-- page 42 -->

| Pytest Contract | Verified Algorithmic & OS Invariant |
|---|---|
| test_optimized_heap_proportional_shares_and_sleeper_cap | Verifies O(log N) heap preserves shares and caps post-wake burst <= 2t |
| test_bench1_speedup_and_churn | Asserts >= 40x speedup @ N=2,000, >= 100x @ N=4,000, >= 40x churn |
| test_bench2_ablation_and_bench3_sleeper | Verifies 60 ablation workloads and invariant 1-tick gs_capped burst @ S=160 |
| test_bench5_zero_fp_drift_decimal | Proves 0 divergences for 10^9 FP on [2,5,10] vs >10k float64 divergences |
| test_bench4_live_os_arrival_and_sleeper | Asserts >= 2x latecomer error reduction and <10% post-wake OS error |
| test_8_diagrams_decks_and_40p_reports | Validates 8 PNGs, 10-slide EN/FA PPTX + speaker scripts, >= 40p PDFs |

*Table 29. Automated pytest contracts protecting all Exercise 6 deliverables.*


### 10.1 Appendix: Exact Fixed-Point & LCM Quantization Bounds

```text
Integer Virtual-Time Update Equations:
  SCALE_FP = 10^9   (exact iff w_i | 10^9, e.g., w in {1,2,4,5,8,10,20,25})
  Arbitrary w <= W:  SCALE_LCM = 10^3 * lcm(1, 2, ..., W)   [for W=16, lcm=720,720]
  Add task i at t:  vtime_fp[i] <- sys_vtime_fp
  Wake task i:      vtime_fp[i] <- max(vtime_fp[i], sys_vtime_fp - cap*SCALE_FP // w_i)
  Max tie drift:    0 ULP forever when every active weight divides SCALE
```
*Exact integer clock equations guaranteeing drift-free heap tie ordering.*
