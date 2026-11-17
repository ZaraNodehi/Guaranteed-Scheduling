# Exercise 3 — Hand-Worked Exact Fractional Verification vs Programmatic Execution

## Scope & Scientific Questions
Exercise 3 audits `core/gs_core.py` and `GuaranteedScheduling.py` via an **independent zero-shared-code exact `fractions.Fraction` verifier** across three complementary workloads:
1. **Static Simultaneous Arrival (`[E]=[M]`):** `P1(0,3,1)`, `P2(0,5,2)`, `P3(0,4,3)` (`12` ticks) verifying `12/12` exact match across `index`, `stay`, and `max_weight` tie-breakers, plus proving `all_static_equiv = True` (`gs_ratio == gs_vtime == gs_entitled == stride`).
2. **Dynamic Staggered Arrival (`[E]+[M]+[D]`):** `P1(0,8,2)`, `P2(4,6,2)`, `P3(7,4,1)` (`18` ticks) proving `18/18` independent hand-to-simulator match while exposing `gs_ratio` lockout (`max_abs_lag = 29/10`, `max_starve_gap = 6`) vs `gs_vtime` (`7/10`).
3. **IEEE-754 Float Drift Discrepancy (`[D]`):** Demonstrating that accumulating `1.0 / w_i` in binary float flips `62/180` (`34.44%`) dispatch choices on `weights = [3, 6, 9]` starting at `t = 18`.

## Key Outputs
- `code/run_experiments.py` → `output/experiments.json`
- `code/make_diagrams.py` → 6 figures in `diagrams/fig_ex3_*.png`
- `REPORT_EN.md`, `docs/REPORT_EN.{docx,pdf}` (22 pages)
- `REPORT_FA.md`, `docs/REPORT_FA.{docx,pdf}` (22 pages, Persian RTL)
- `tests/test_ex3.py` — automated verification suite

## Re-run Commands
```bash
python3 exercise-3/code/run_experiments.py
python3 exercise-3/code/make_diagrams.py
python3 tools/build_report.py gs3_en exercise-3 REPORT_EN
python3 tools/build_report.py gs3_fa exercise-3 REPORT_FA
python3 -m pytest exercise-3/tests -v
```
