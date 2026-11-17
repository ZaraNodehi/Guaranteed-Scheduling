# Exercise 4 — Formal Correctness Proofs, SFQ vs PGPS Lag Bounds & Exhaustive Verification

## Scope & Four Formal Theorems
Exercise 4 pairs closed-form algebraic proofs with exhaustive DFS (`[E]`), a 120-workload parameter audit (`[M]`), and constructive counterexamples (`[D]`):
1. **Theorem 1 — SFQ vs PGPS Lag Bounds (`[E]`+`[M]`+`[D]`):** Refutes the naive textbook claim `|L_i(t)| <= q` for start-time `gs_vtime:index` (`36/120` exceed `q`, peaking at `21/16 q = 1.3125q` on `[1,3,5,7]`), proves the tight analytical SFQ bound `max(q, (n-1)*q*w_max/W)` matched across `4,680` DFS leaves, and demonstrates `0/120` violations under `gs_vtime:max_weight` and PGPS `wfq_finish` (`0.9375q`).
2. **Theorem 2 — Unbounded `Omega(t_arr)` Dynamic Starvation (`[E]`+`[D]`):** Proves `gs_ratio` lockouts grow linearly as `t_arr` (`gap = 32`, `lag = 16.0` at `t_arr = 32`), whereas `gs_vtime` (`v_i <- V(t)`) guarantees strict `O(1)` lag `0.50` and `gap = 1`.
3. **Theorem 3 — Exhaustive RT Feasibility & EDF Completeness (`[E]`):** Certifies `10/10` feasible sets (`verify_rt_schedule_independent = PASS`, `100%` EDF completeness) and proves `5` constrained/overload sets infeasible across all schedules.
4. **Theorem 4 — Overload Graceful Degradation (`[M]`):** Across `U in [1.08 .. 2.00]`, RM starves the low-priority task to `0` ticks (`min_sr = 0.00`), while `gs_vtime` sustains `Jain >= 0.915` (`0.932` at `U = 2.00`).

## Re-run Commands
```bash
python3 exercise-4/code/run_experiments.py
python3 exercise-4/code/make_diagrams.py
python3 tools/build_report.py gs4_en exercise-4 REPORT_EN
python3 tools/build_report.py gs4_fa exercise-4 REPORT_FA
python3 -m pytest exercise-4/tests -v
```
