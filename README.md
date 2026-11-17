# Guaranteed Scheduling — Empirical Theory, Simulation, Optimization & Live Linux OS Validation

A seven-exercise research and software engineering suite analyzing **Guaranteed Scheduling (Proportional-Share CPU Scheduling)** from first-principles exact rational proofs (`[E]`) through 240-seed Monte Carlo sweeps (`[M]`), an `O(log n)` lazy min-heap refactoring with `SCALE_LCM` exact integer clocks (`gs_optimized.py`), a Phase-2 EEVDF variable-slice prototype, and direct live Linux `psutil` validation (`[D]`).

> Preserves the original educational baseline `GuaranteedScheduling.py` cleanly at repository root while consolidating the expanded Exercises 1–7 suite on branch `arena/796ca936-guaranteed-scheduling`.

## Quick Verification & Live Demo
```bash
python3 tools/vendor_core.py --check               # confirm canonical core/gs_core.py parity across Ex 1–7
python3 -m pytest -v                               # run all 63 exact + empirical + artifact regression tests
python3 exercise-7/code/demo_all.py                # <0.5s live 7-pillar capstone terminal demo (incl. SCALE_LCM & EEVDF)
python3 tools/check_outputs.py exercise-1 exercise-2 exercise-3 exercise-4 exercise-5 exercise-6 exercise-7
```

## Seven-Exercise Suite Overview

| Exercise | Focus & Engineering Scope | Key Verified Outcome | Deliverables |
| --- | --- | --- | --- |
| **Exercise 1** | Static baseline, GPS discrepancy, tie variants & Linux OS subprocess test | Static `lag = 1.0q`; live Linux `[1,2,4]` ordered `100%` across trials (`0.55s` median) | [Code](exercise-1/code), `10` PNGs, [EN PDF (42p)](exercise-1/docs/REPORT_EN.pdf), [FA PDF (42p)](exercise-1/docs/REPORT_FA.pdf) |
| **Exercise 2** | Proportional vs constrained RT vs overload regimes + independent audit | `120` RT sets; overload `RM min_share = 0.00` vs `GS = 0.84` | [Code](exercise-2/code), `8` PNGs, [EN PDF (40p)](exercise-2/docs/REPORT_EN.pdf), [FA PDF (40p)](exercise-2/docs/REPORT_FA.pdf) |
| **Exercise 3** | Exact manual trace tables + IEEE-754 float drift audit | `100%` manual-vs-program match; float drift starts at `t = 18` | [Code](exercise-3/code), `8` PNGs, [EN PDF (41p)](exercise-3/docs/REPORT_EN.pdf), [FA PDF (41p)](exercise-3/docs/REPORT_FA.pdf) |
| **Exercise 4** | 4 formal proofs: lag bounds, `Omega(t_arr)` starvation, exhaustive RT & overload | `36/120` exceed `q` (max `1.3125q`), `V(t)` cuts gap `32 -> 1`, EDF solves `10/10` | [Code](exercise-4/code), `8` PNGs, [EN PDF (41p)](exercise-4/docs/REPORT_EN.pdf), [FA PDF (40p)](exercise-4/docs/REPORT_FA.pdf) |
| **Exercise 5** | 240-seed Monte Carlo, Zipf+burst, quantum Pareto & live OS 5-interval sweep | `gs_vtime:stay` lag `0.908` vs `ratio 3.36` (`97.9%` win); `q = 2` cuts switches `44.4%` | [Code](exercise-5/code), `8` PNGs, [EN PDF (41p)](exercise-5/docs/REPORT_EN.pdf), [FA PDF (40p)](exercise-5/docs/REPORT_FA.pdf), [Decks](exercise-5/docs/DECK_EN.pptx) |
| **Exercise 6** | `O(log n)` lazy min-heap, `SCALE_LCM`, 120-seed ablation & sleeper cap | `206.64x` speedup @ `N=4,000`; `159 -> 1` sleeper cap; `0` LCM drift; `8.6x` OS gain | [Code](exercise-6/code), `8` PNGs, [EN PDF (42p)](exercise-6/docs/REPORT_EN.pdf), [FA PDF (41p)](exercise-6/docs/REPORT_FA.pdf), [Decks](exercise-6/docs/DECK_EN.pptx) |
| **Exercise 7** | Capstone 7-regime scorecard (`R1–R7`), 40-seed EEVDF prototype, live `[1,2,4]` OS | EEVDF wins/ties `37/40` (`max=3.0 <= 4.0`); live Linux err `3.67%`; `63/63` pytest | [Code](exercise-7/code), `8` PNGs, [EN PDF (43p)](exercise-7/docs/REPORT_EN.pdf), [FA PDF (42p)](exercise-7/docs/REPORT_FA.pdf), [Decks](exercise-7/docs/DECK_EN.pptx) |

## Repository Structure
- `GuaranteedScheduling.py`: Preserved original root `psutil` proportional scheduler script (`106` lines).
- `core/gs_core.py` & `tests/test_gs_core.py`: Canonical exact integer/`Fraction` simulation core (`1,238` lines, `28` unit tests) cleanly vendored across `exercise-{1..7}/code/gs_core.py`.
- `tools/`: Shared bilingual report compiler (`report_kit.py`, `build_report.py`, `check_outputs.py`), Okabe-Ito plotting helpers (`plot_kit.py`), `vendor_core.py`, `make_decks.py`, and data-driven content modules (`tools/content/gs{1..7}_{data,en,fa}.py`, `gs_decks.py`).
- `exercise-1/` .. `exercise-7/`: Self-contained workspaces with `code/`, `output/experiments.json`, `diagrams/` (`58` PNGs total), `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}` (40–43 pages each, `0` overflows, `0` missing glyphs), 10-slide bilingual seminar decks (`exercise-{5..7}`), `README.md`, and `tests/test_ex*.py`.
- `benchmarks/archive-studies/`: Archived earlier editions of Exercises 4–7 preserved cleanly for comparison (excluded from active `pytest.ini` test discovery).
