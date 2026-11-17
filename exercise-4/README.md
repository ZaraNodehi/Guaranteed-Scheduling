# Exercise 4 — Formal Correctness Proofs, SFQ vs PGPS vs EEVDF Bounds & Exhaustive Audits

## Scope & Five Formal Theorems
Exercise 4 pairs closed-form algebraic proofs with exhaustive zero-truncation DFS (`[E]`), a 120-workload parameter census (`[M]`), and constructive counterexamples (`[D]`):
1. **Theorem 1 — SFQ vs PGPS vs EEVDF Lag Bounds (`[E]`+`[M]`+`[D]`):** Refutes the naive textbook claim `|L_i(t)| <= q` for start-time `gs_vtime:index` (`36/120` exceed `q`, peaking at `21/16 q = 1.3125q` on `[1,3,5,7]`), proves Goyal's tight analytical SFQ bound `max(q, (n-1)*q*w_max/W)` across `4,680` DFS leaves, shows `0/120` violations under `gs_vtime:max_weight` and PGPS `wfq_finish` (`0.9375q`), and establishes **EEVDF optimality (`0/120`, peak `0.7500q = 3/4 q`)** explaining Linux 6.6+ adoption.
2. **Theorem 2 — Unbounded `Omega(t_arr)` Dynamic Starvation (`[E]`+`[D]`):** Proves `gs_ratio` lockouts grow linearly as `t_arr` (`gap = 32`, `lag = 16.0` at `t_arr = 32`, full 24-tick witness at `t_arr = 8`), whereas `gs_vtime` (`v_i <- V(t)`) and `EEVDF` guarantee strict `O(1)` lag `0.50` and `gap = 1`.
3. **Theorem 3 — Exhaustive RT Feasibility, Baruah `dbf(L)` & EDF Completeness (`[E]`):** Certifies `10/10` feasible sets (`verify_rt_schedule_independent = PASS`, `100%` EDF completeness, work-conserving == `allow_idle` across all `15/15` sets) and separates `I01..I05` via `dbf(L)/L > 1` (including `U < 1.0` sets `I01, I02`).
4. **Theorem 4 — Overload Graceful Degradation (`[M]`):** Across `U in [1.08 .. 2.00]`, RM starves the low-priority task to `0` ticks (`min_sr = 0.00`), while `gs_vtime` sustains `Jain >= 0.915` (`0.932` equal-weight and `0.974..1.000` weighted `[3,2,1]` at `U = 2.00`).

## Deliverables
- `output/experiments.json`: Full 120-case census (`q1_40_cases`, `q2_40_cases`, `q3_40_cases`), DFS tie envelopes, 32-tick `[1,3,5,7]` and 20-tick `[1,2,3,4]` witnesses, `t_arr=8` dynamic witness, 15 RT sets + `F05`/`F07` traces, and equal/weighted overload sweeps.
- `diagrams/`: **8 Okabe-Ito publication figures** (`fig_ex4_*.png`).
- `REPORT_EN.md`, `docs/REPORT_EN.{docx,pdf}` (**41 pages**, 0 overflow/missing glyphs) and `REPORT_FA.md`, `docs/REPORT_FA.{docx,pdf}` (**40 pages**, RTL Vazirmatn, 0 overflow/missing glyphs).

## Re-run Commands
```bash
python3 exercise-4/code/run_experiments.py
python3 exercise-4/code/make_diagrams.py
python3 tools/build_report.py gs4_en exercise-4 REPORT_EN
python3 tools/build_report.py gs4_fa exercise-4 REPORT_FA
python3 -m pytest exercise-4/tests -v
```
