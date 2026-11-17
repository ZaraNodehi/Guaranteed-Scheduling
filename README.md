# Guaranteed Scheduling — Empirical Theory, Simulation, Optimization & Live Linux OS Validation

A seven-exercise research and software engineering suite analyzing **Guaranteed Scheduling (Proportional-Share CPU Scheduling)** from first-principles exact rational proofs (`[E]`) through 240-seed Monte Carlo sweeps (`[M]`), an `O(log n)` lazy min-heap refactoring (`gs_optimized.py`), and direct live Linux `psutil` validation (`[D]`).

> Preserves the original educational baseline `GuaranteedScheduling.py` cleanly at repository root while organizing Exercises 1–7 on branch `arena/7c38f201-guaranteed-scheduling`.

## Quick Verification & Live Demo
```bash
python3 tools/vendor_core.py --check               # confirm canonical core/gs_core.py parity across Ex 1-7
python3 -m pytest tests exercise-*/tests -v        # run 54 exact + empirical regression tests
python3 exercise-7/code/demo_all.py                # <0.5s live 5-pillar capstone terminal demo
python3 tools/check_outputs.py exercise-1 exercise-2 exercise-3 exercise-4 exercise-5 exercise-6 exercise-7
```

## Seven-Exercise Suite Overview

| Exercise | Focus & Engineering Scope | Key Verified Outcome | Deliverables |
| --- | --- | --- | --- |
| **Exercise 1** | Static baseline, GPS discrepancy, tie variants & Linux OS subprocess test | Static `lag = 1.0q`; live Linux `[1,2,4]` ordered `100%` across trials (`0.55s` median) | [Code](exercise-1/code), [EN PDF](exercise-1/docs/REPORT_EN.pdf), [FA PDF](exercise-1/docs/REPORT_FA.pdf) |
| **Exercise 2** | Proportional vs constrained RT vs overload regimes + independent audit | `120` RT sets; overload `RM min_share = 0.00` vs `GS = 0.84` | [Code](exercise-2/code), [EN PDF](exercise-2/docs/REPORT_EN.pdf), [FA PDF](exercise-2/docs/REPORT_FA.pdf) |
| **Exercise 3** | Exact manual trace tables + IEEE-754 float drift audit | `100%` manual-vs-program match; float drift starts at `t = 18` | [Code](exercise-3/code), [EN PDF](exercise-3/docs/REPORT_EN.pdf), [FA PDF](exercise-3/docs/REPORT_FA.pdf) |
| **Exercise 4** | Formal proofs: lag bounds, `Omega(t_arr)` starvation, exhaustive RT & overload | `36/120` exceed `q` (max `1.3125q`), `V(t)` cuts gap `32 -> 1`, EDF solves `10/10` | [Code](exercise-4/code), [EN PDF](exercise-4/docs/REPORT_EN.pdf), [FA PDF](exercise-4/docs/REPORT_FA.pdf) |
| **Exercise 5** | 240-seed Monte Carlo, quantum Pareto & live OS interval sweep | `gs_vtime:stay` lag `0.908` vs `ratio 3.36`; `q = 2` cuts switches `44.4%` | [Code](exercise-5/code), [EN PDF](exercise-5/docs/REPORT_EN.pdf), [FA PDF](exercise-5/docs/REPORT_FA.pdf), [Decks](exercise-5/docs/DECK_EN.pptx) |
| **Exercise 6** | `O(log n)` lazy min-heap refactor, ablation & sleeper credit cap | `113.1x` speedup @ `N = 2,000`; `79 -> 1` tick sleeper cap; `4.2x` OS fix | [Code](exercise-6/code), [EN PDF](exercise-6/docs/REPORT_EN.pdf), [FA PDF](exercise-6/docs/REPORT_FA.pdf), [Decks](exercise-6/docs/DECK_EN.pptx) |
| **Exercise 7** | Capstone 6-regime matrix, live `[1,2,4]` Linux audit (`1.80%`), EEVDF/SMP roadmap | Synthesizes Ex 1–6; `54/54` pytest pass; zero-overflow bilingual suite | [Code](exercise-7/code), [EN PDF](exercise-7/docs/REPORT_EN.pdf), [FA PDF](exercise-7/docs/REPORT_FA.pdf), [Decks](exercise-7/docs/DECK_EN.pptx) |

## Repository Structure
- `GuaranteedScheduling.py`: Preserved original root `psutil` proportional scheduler script (`106` lines).
- `core/gs_core.py` & `tests/test_gs_core.py`: Canonical exact integer/`Fraction` simulation core (`28` unit tests) cleanly vendored across `exercise-{1..7}/code/gs_core.py`.
- `tools/`: Shared bilingual report compiler (`report_kit.py`, `build_report.py`, `check_outputs.py`), Okabe-Ito plotting helpers (`plot_kit.py`), `vendor_core.py`, `make_decks.py`, and modular data-driven content scripts (`tools/content/gs{1..7}_{data,en,fa}.py`, `gs_decks.py`).
- `exercise-1/` .. `exercise-7/`: Self-contained workspaces containing `code/`, `output/experiments.json`, `diagrams/` (`44` PNGs total), `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}`, bilingual PPTX/Markdown speaker decks (`exercise-{5..7}`), `README.md`, and `tests/test_ex*.py`.
