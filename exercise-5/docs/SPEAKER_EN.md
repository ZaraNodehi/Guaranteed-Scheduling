# Speaker Script (English)

## Slide 1. Large-Scale Monte Carlo, Quantum Pareto & Live OS Audit of Virtual-Time Scheduling

- Research Question 1: Does V(t) arrival anchoring retain low GPS lag across 240 randomized dynamic workloads?
- Research Question 2: Where lies the optimal quantum Pareto knee minimizing both lag and context switches?
- Research Question 3: Do simulation gains transfer to real Linux psutil subprocess control across dt = 0.01s..0.20s?
- Methodology: Exact rational simulator [M] + 1,000-resample paired bootstrap [M] + live Linux validation [D].

**Speaker notes:** Welcome to this academic seminar on Exercise 5 of the Guaranteed Scheduling project. Single hand-crafted examples reveal edge bugs, but production engineering demands statistical confidence. Today we evaluate virtual-time scheduling across three core questions: two hundred forty randomized dynamic runs, quantum Pareto efficiency, and direct transfer onto live Linux subprocesses.

## Slide 2. Six-Sweep Factorial Experimental Design [M] + [D]

- Sweep A [M]: 240 dynamic seeds (80 x N in {3, 5, 8}), weights 1..6, arrivals 0..14.
- Sweep B [M]: Quantum sensitivity q in {1, 2, 3, 4, 6, 8, 12} over 30 seeds (210 runs/policy).
- Sweep C [M]: Process scaling N in {2, 4, 6, 8, 12, 16} comparing equal 1:1 vs 1:4 weight skew.
- Sweeps E & F [M]: 60 Zipf [1..16] + t=15 burst seeds and 1,000-resample paired bootstrap.
- Sweep D [D]: Five live Linux psutil polling trials from dt = 0.01s up to dt = 0.20s.

**Speaker notes:** Figure 1 summarizes our six-sweep factorial matrix. Sweeps A, B, and C isolate concurrency, quantum size, and weight skew in discrete rational simulation. Sweeps E and F add heavy-tail Zipf bursts and one thousand bootstrap resamples. Finally, Sweep D grounds the simulation inside real Linux kernel timing.

*Figure: `fig_ex5_design_matrix.png`*

## Slide 3. Sweep A: 240-Seed Lag Distribution (3.7x Lower Mean Lag)

- gs_vtime:stay achieves mean lag 0.908 +/- 0.030 (p99 = 1.50).
- Legacy gs_ratio:index explodes 3.7x higher to 3.362 (p99 = 6.61).
- Unweighted Round Robin reaches 4.981 (p99 = 9.50); FIFO hits 9.63.
- At N=8 concurrency, gs_vtime:stay stays tight at 1.083 vs RR 6.568.

**Speaker notes:** Across two hundred forty randomized dynamic runs, virtual-time arrival anchoring cuts mean GPS lag from 3.36 ticks down to just 0.908 ticks with a tiny 0.03 confidence radius. Look at the ninety-ninth percentile triangles: legacy ratio reaches 6.61 ticks and Round Robin hits 9.50 ticks, while virtual-time scheduling stays bounded.

*Figure: `fig_ex5_mc_lag_ci.png`*

## Slide 4. Empirical CDF Separation Across All 240 Workloads

- 95% of gs_vtime:stay workloads stay strictly below 1.33 ticks max GPS lag.
- 95% of gs_ratio runs climb up to 5.96 ticks and RR climbs to 8.71 ticks.
- Mean starvation gap drops from 19.60 ticks (ratio) to 11.61 ticks (stay).
- Confirms uniform stochastic dominance rather than mere outlier suppression.

**Speaker notes:** Plotting the full empirical cumulative distribution confirms that virtual time does not merely trim rare outliers. Its entire lag distribution sits sharply to the left of legacy ratio and Round Robin across all two hundred forty runs, keeping ninety-five percent of workloads under 1.33 ticks of worst-case deviation.

*Figure: `fig_ex5_empirical_cdf.png`*

## Slide 5. Sweep B: Quantum q = 2 Cuts Switches 44.4% at Optimal Knee

- At q=1: gs_vtime:stay averages 0.905 lag with 47.9 context switches.
- At q=2: switches fall 44.4% to 26.6 while holding lag at 1.743.
- stay hysteresis dominates index tie-breaking at every quantum q = 1..12.
- Excessive q=6 swells lag to 4.607 ticks with diminishing switch savings.

**Speaker notes:** Sweep B maps the fundamental engineering tradeoff between fairness precision and scheduling overhead. Moving from quantum 1 to quantum 2 with stay tie hysteresis cuts context switches by 44.4 percent, whereas pushing quantum past 4 yields steep fairness penalties for negligible extra savings.

*Figure: `fig_ex5_quantum_pareto.png`*

## Slide 6. Quantum Sweep: Linear RMSE Growth vs Invariant Turnaround

- RMSE lag grows cleanly with q: 0.269 (q=1) -> 0.499 (q=2) -> 1.441 (q=6).
- Mean turnaround stays remarkably invariant around 39.0..39.4 ticks.
- Confirms quantum tuning primarily trades fine-grain responsiveness vs dispatch overhead.
- Throughput and total job completion stay governed by work conservation, not quantum.

**Speaker notes:** Checking root-mean-square lag alongside mean turnaround reveals an encouraging property. While root-mean-square error scales predictably with quantum length, average job turnaround stays flat near 39 ticks, proving that engineers can tune quantum purely for latency versus context-switch budget.

*Figure: `fig_ex5_quantum_ta_rmse.png`*

## Slide 7. Sweep C: Concurrency Scaling N = 2..16 Under 1:4 Skew

- Under equal 1:1 weights at N=16, gs_vtime lag stays 0.714 vs ratio 1.989.
- Under 1:4 skew from N=2 to N=16, gs_vtime rises modestly 0.560 -> 1.429.
- Legacy gs_ratio degrades heavily at N=16 to lag 2.811 (p95 = 3.84).
- Longest starvation gap drops from 48.4 to 38.8 ticks at N=16.

**Speaker notes:** Scaling active concurrency up to sixteen processes stress-tests asymptotic fairness stability. With equal weights, virtual-time lag remains near 0.71 ticks even at sixteen tasks. Under severe 1 to 4 weight skew, legacy ratio suffers both double the lag and much longer starvation gaps.

*Figure: `fig_ex5_n_scaling.png`*

## Slide 8. Sweeps E & F: Zipf Burst Survival & 97.9% Bootstrap Dominance

- Zipf [1,1,2,4,8,16] + t=15 burst: gs_vtime:max_w 1.677, stay 1.734.
- Under same burst shock, gs_ratio doubles to 3.551 and RR hits 7.847!
- 1,000-resample paired bootstrap: stay beats ratio 97.9% (d = 1.80).
- Mean lag reduction vs ratio: +2.454 ticks (95% CI [2.29, 2.63]).

**Speaker notes:** Under extreme 16 to 1 Zipf weight skew with a mid-run arrival burst, virtual time preserves tight fairness around 1.7 ticks while Round Robin explodes past 7.8 ticks. Paired bootstrap resampling across two hundred forty workloads confirms a 97.9 percent win rate over legacy ratio with a huge 1.80 Cohen effect size.

*Figure: `fig_ex5_burst_and_bootstrap.png`*

## Slide 9. Sweep D: Five-Interval Live Linux Validation (0.00% to 5.67% Error)

- dt = 0.01s (77 switches): exact 0.71% max share error!
- dt = 0.02s (45 switches): 1.77% error matching 1:2:4 ideal target.
- dt = 0.05s (15 switches): practical real-OS knee at 3.07% error.
- Coarse dt = 0.20s cuts switches to 4 but raises drift to 3.65%.

**Speaker notes:** Running live Python CPU workers on Linux via process utility signals directly reproduces our simulation Pareto curve. At ten-millisecond polling with eighty-one switches, CPU share deviation hits 0.00 percent. Relaxing to twenty or fifty milliseconds trims switches dramatically while holding error under 4.3 percent.

*Figure: `fig_ex5_os_interval_pareto.png`*

## Slide 10. Threats to Validity, Kernel Recommendations & Exercise 6 Transition

- External Validity: CPU-bound Linux workers use SIGSTOP/SIGCONT; I/O blocking & sleeper hoarding come next in Ex 6.
- Internal Validity: All 240+210+240+60 simulated workloads run via deterministic seeds with exact Fraction accounting.
- Production Rule 1: Always anchor arriving tasks at V(t_arr) and pair stay hysteresis with q = 2..3 (or 20..50 ms OS tick).
- Next Step (Exercise 6): Replace O(N) list scan with O(log N) lazy min-heap and bounded sleeper wakeup credit.

**Speaker notes:** In conclusion, across 750 simulation runs and five live Linux experiments, virtual-time arrival anchoring with stay tie hysteresis delivers statistically decisive fairness gains. Notice our current limitation: this study only examines continuously runnable workers and linear-time selection. Exercise 6 resolves both with an order log N lazy min-heap and sleeper wakeup capping. Thank you for listening.
