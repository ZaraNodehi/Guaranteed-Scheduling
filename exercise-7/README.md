# Exercise 7 — Capstone Synthesis, Live Audit & EEVDF/SMP Roadmap

## Highlights
- **Cross-Exercise Synthesis (`output/experiments.json`):** Consolidates verified metrics across Exercises 1–6 (`1.0q` static baseline, `120` RT sets, `t = 18` float drift onset, `32 -> 1` dynamic gap fix, `240`-seed Monte Carlo, `113.1x` heap speedup, `79 -> 1` sleeper burst protection).
- **Unified 6-Regime Matrix:** Benchmarks `gs_capped:stay`, `gs_vtime:stay`, `gs_entitled`, `gs_ratio`, `stride`, `edf`, `rm`, `rr`, and `fifo` across static, dynamic arrival, sleeper attack, feasible RT, RT overload, and `N = 2,000` scaling.
- **Live Linux `[1, 2, 4]` Verification (`[D]`):** Achieves **`1.80%`** max share deviation vs ideal GPS `[14.3%, 28.6%, 57.1%]`.
- **Fast Live Demo (`code/demo_all.py`):** Demonstrates all 5 pillars cleanly in `< 0.5s`.

## Re-run Commands
```bash
python3 exercise-7/code/demo_all.py
python3 exercise-7/code/run_experiments.py
python3 exercise-7/code/make_diagrams.py
python3 tools/build_report.py gs7_en exercise-7 REPORT_EN
python3 tools/build_report.py gs7_fa exercise-7 REPORT_FA
python3 -m pytest exercise-7/tests -v
```
