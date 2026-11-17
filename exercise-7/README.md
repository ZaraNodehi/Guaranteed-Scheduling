# Exercise 7 — Capstone Synthesis, 7-Regime Selector, EEVDF Prototype & Live Linux OS Validation

## Overview

Exercise 7 is the unifying technical capstone of the **Guaranteed Scheduling** research program (`Exercises 1–7`). It consolidates exact theoretical bounds, 240-seed Monte Carlo statistics, `O(log N)` lazy heap engineering, `SCALE_LCM` fixed-point zero-drift arithmetic, a 7-regime policy evaluation matrix (`R1–R7`), a **Phase-2 EEVDF variable-slice prototype** benchmarked across 40 randomized heterogeneous-slice workloads (`L_i in {1, 2, 4}`), and a live Linux `[1, 2, 4]` weighted process control validation.

## Key Capstone Findings

| Dimension | Legacy Baseline (`V0`) | Hardened / Capstone | Improvement | Source Tag |
| :--- | :---: | :---: | :---: | :---: |
| **MC 240-Seed Mean Lag (Ex 5)** | `3.3616` ticks | `0.9078` ticks | `3.70x` lower | `[M]` |
| **Dynamic Arrival Gap (Ex 4)** | `32` ticks | `1` tick | `32.00x` lower | `[E]` |
| **Sleeper Lockout @ S=160 (Ex 6)** | `159` ticks | `1` tick | `159.00x` lower | `[E]` |
| **Prime-Weight Float Drift / 100k** | `47,996` shifts (`float64`) | `0` shifts (`SCALE_LCM`) | Exact integer | `[E]` |
| **Dispatch Speedup @ N=4,000** | Linear `O(N)` scan | `206.64x` lazy heap | `206.64x` faster | `[M]` |
| **Phase-2 EEVDF Prototype (40 Seeds)** | `5.4545` max (`gs_var`) | `3.0000` max (`<= 4.0` bound) | Wins/ties `37/40` | `[E]+[M]` |
| **Live Linux OS Error (`[1, 2, 4]`)** | `25.23%` (Ex 6 legacy) | `3.67%` (Ex 7 capstone) | `6.87x` lower | `[D]` |

## Directory Structure

- `code/gs_core.py` — Canonical exact `Fraction` simulation core (byte-identical to `core/gs_core.py`).
- `code/run_experiments.py` — Dynamic cross-exercise consolidator, 7-regime evaluator (`R1–R7`), 40-seed EEVDF variable-slice benchmark, live `[1, 2, 4]` Linux controller, and Ex 1–6 disk auditor.
- `code/make_diagrams.py` — Generates 8 Okabe-Ito colorblind-safe analytical figures dynamically from `output/experiments.json`.
- `code/demo_all.py` — Fast (`< 0.5s`) 7-demo interactive terminal suite covering static GPS, latecomers, sleeper cap, EDF vs overload, `O(log N)` heap speedup, `SCALE_LCM` drift elimination, and Phase-2 EEVDF.
- `output/experiments.json` — Complete machine-readable dataset backing every table, figure, and monograph claim.
- `diagrams/fig_ex7_*.png` — 8 high-DPI synthesis, heatmap, Pareto, decision tree, OS verification, EEVDF trace, and SMP roadmap figures.
- `docs/REPORT_EN.{pdf,docx}` & `REPORT_EN.md` — 40+-page English capstone monograph.
- `docs/REPORT_FA.{pdf,docx}` & `REPORT_FA.md` — 40+-page Persian RTL monograph (`Vazirmatn`).
- `docs/DECK_{EN,FA}.pptx` & `SPEAKER_{EN,FA}.md` — 10-slide bilingual seminar presentation deck and narration script.
- `tests/test_ex7.py` — Automated pytest suite verifying cross-exercise bounds, 7 regimes, EEVDF Stoica limit, core parity, and monograph contracts.

## Reproduction

```bash
python3 exercise-7/code/run_experiments.py
python3 exercise-7/code/make_diagrams.py
python3 exercise-7/code/demo_all.py
python3 tools/make_decks.py 7
python3 tools/build_report.py gs7_en exercise-7 REPORT_EN
python3 tools/build_report.py gs7_fa exercise-7 REPORT_FA
python3 -m pytest exercise-7/tests -v
```
