# Speaker Script (English)

## Slide 1. Exercise 5: Monte Carlo & Quantum-Pareto Sweep

- 240 dynamic random workloads across N in {2,3,4,6,8} processes.
- gs_vtime:stay cuts mean lag to 0.908 vs ratio 3.36, RR 4.98, FIFO 9.63.
- Combines exact discrete sweeps with real Linux psutil OS sweeps [M]+[D].

**Speaker notes:** Exercise 5 scales our exact proofs across 240 randomized dynamic workloads plus live Linux OS sampling.

*Figure: `fig_ex5_mc_lag_cdf.png`*

## Slide 2. Quantum Sweep: q = 2 Cuts Switches 44.4%

- At q=1: gs_vtime:stay lag=0.905, switches=47.9.
- At q=2: switches drop 44.4% to 26.6 with lag=1.743.
- stay tie hysteresis dominates index across all quanta q=1..12.

**Speaker notes:** Doubling q from 1 to 2 under stay achieves the optimal knee of the fairness-overhead Pareto frontier.

*Figure: `fig_ex5_quantum_pareto.png`*

## Slide 3. Concurrency Scaling N = 2..16 Under 1:4 Skew

- At N=16: skew gs_vtime lag=1.429 vs gs_ratio lag=2.811.
- Starvation gap drops cleanly (38.8 vs 48.4 ticks).
- Validates asymptotic O(1) lag stability as workload concurrency grows.

**Speaker notes:** Increasing N from 2 to 16 preserves tight bounded lag under virtual time while legacy ratio degrades.

*Figure: `fig_ex5_n_scaling.png`*

## Slide 4. Live Linux Controller Sweep (dt = 0.02s .. 0.10s)

- dt=0.02s: 45 switches, max err=1.03%.
- dt=0.05s: 16 switches (64% fewer!), err=1.43%.
- dt=0.10s: drops to 8 switches, error jumps to 6.75%.

**Speaker notes:** dt = 0.05s mirrors the simulation q = 2 Pareto knee directly on real Linux processes.

*Figure: `fig_ex5_os_interval_sweep.png`*
