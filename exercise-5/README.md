# Exercise 5 — Large-Scale Simulation Sweeps, Sensitivity & Pareto Analysis

## Scope & Four Parameter Sweeps
1. **Sweep A — 240-Seed Monte Carlo (`[M]`):** Evaluates 7 schedulers (`N in {3, 5, 8}`, 80 seeds/N) with 95% CIs and `p95`/`p99` tails: `gs_vtime:stay` cuts mean lag **3.7x** vs `gs_ratio` (`0.908` vs `3.362`) and **5.5x** vs Round Robin (`4.981`).
2. **Sweep B — Quantum Pareto Frontier (`[M]`):** `q in {1, 2, 3, 4, 6, 8, 12}` (30 seeds): `q = 2` with `stay` identifies the optimal Pareto knee, slashing context switches **44.1%** (`47.7 -> 26.7`) while keeping lag under `1.8` ticks.
3. **Sweep C — Scaling `N = 2..16` & `1:4` Skew (`[M]`):** Demonstrates flat lag asymptotes on `gs_vtime` (`0.71` equal, `1.43` skewed at `N = 16`) vs high-variance distortion on `gs_ratio` (`2.81`).
4. **Sweep D — Live OS `psutil` Poll Interval Trials (`[D]`):** Real Linux `SIGSTOP`/`SIGCONT` workers (`w = [1, 2, 4]`) show CPU share error plunging from `6.75%` (`0.10s`) to `1.43%` (`0.05s`) and `1.03%` (`0.02s`).

## Re-run Commands
```bash
python3 exercise-5/code/run_experiments.py
python3 exercise-5/code/make_diagrams.py
python3 tools/build_report.py gs5_en exercise-5 REPORT_EN
python3 tools/build_report.py gs5_fa exercise-5 REPORT_FA
python3 -m pytest exercise-5/tests -v
```
