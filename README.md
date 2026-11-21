# Operating Systems Scheduling & Synchronization — Exercises 1–7

A comprehensive seven-exercise research and software engineering suite spanning **Guaranteed Scheduling (`Ex 1–2`)**, **Hard Real-Time RM vs. EDF (`Ex 3`)**, **Mutual Exclusion & BFS Model Checking (`Ex 4`)**, **12-Variant Readers–Writers (`Ex 5`)**, **Unified Kernel Capstone (`Ex 6`)**, and **Dining Philosophers (`Ex 7`)**—all backed by reproducible Python simulators, live multithreaded Linux benchmarks, Okabe-Ito figures, automated `pytest` suites, and bilingual English/Persian DOCX & PDF monographs.

> Preserves the original root script `GuaranteedScheduling.py` at repository root while maintaining the six active exercises on the default branch `main`; earlier extended GS studies remain archived under `benchmarks/archive-studies/`.

## Quick Verification
```bash
python3 tools/vendor_core.py --check         # verify canonical core/gs_core.py parity across Ex 1–3
python3 -m pytest -v                         # run all 51 unit, invariant & artifact tests in <1s
python3 tools/check_outputs.py exercise-1 exercise-2 exercise-3 exercise-4 exercise-5 exercise-6
```

## Seven-Exercise Curriculum Overview

| Exercise | Focus & Engineering Scope | Key Verified Outcome | Deliverables |
| --- | --- | --- | --- |
| **Exercise 1** | Guaranteed Scheduling (`1/N` & Weighted GS), GPS lag, tie envelopes & live Linux `psutil` | Static `lag = 1.0q`; live Linux `[1,2,4]` ordered `100%` (`0.55s` median) | [Code](exercise-1/code), `10` PNGs, [EN PDF (42p)](exercise-1/docs/REPORT_EN.pdf), [FA PDF (42p)](exercise-1/docs/REPORT_FA.pdf) |
| **Exercise 2** | Proportional GS vs. constrained RT vs. overload regimes + independent verifier | `120` RT sets; overload `RM min_share = 0.00` vs `GS = 0.84` | [Code](exercise-2/code), `8` PNGs, [EN PDF (43p)](exercise-2/docs/REPORT_EN.pdf), [FA PDF (43p)](exercise-2/docs/REPORT_FA.pdf) |
| **Exercise 3** | Real-Time Scheduling: Rate Monotonic (RM) vs. EDF + RTA + Domino Overload + Hand Worksheet | `Set B (U=0.958 > 0.78)`: RM `1` miss vs EDF `0` misses; `2p` worksheet | [Code](exercise-3/code), `8` PNGs, [Worksheet](exercise-3/WORKSHEET_PAPER_TEMPLATE.pdf), [EN PDF (45p)](exercise-3/docs/REPORT_EN.pdf), [FA PDF (43p)](exercise-3/docs/REPORT_FA.pdf) |
| **Exercise 4** | Mutual Exclusion: Dekker `v1..v5`, Peterson (`SC` vs `TSO`), Semaphore, Mesa Monitor + BFS | Exact BFS counterexamples (`TSO 8 errs`, `Mesa if 6 errs`); `98%` vs `1%` CPU burn | [Code](exercise-4/code), `10` PNGs, [EN PDF (43p)](exercise-4/docs/REPORT_EN.pdf), [FA PDF (42p)](exercise-4/docs/REPORT_FA.pdf) |
| **Exercise 5** | Readers–Writers (`4` primitives x `3` policies + `CoarseMutex`), starvation & barging audit | `4.03x` speedup @ `95%` reads; Ticket/Deque stops Writer-Flood barging (`12` vs `0` ops) | [Code](exercise-5/code), `8` PNGs, [EN PDF (44p)](exercise-5/docs/REPORT_EN.pdf), [FA PDF (43p)](exercise-5/docs/REPORT_FA.pdf) |
| **Exercise 6** | Capstone: Mars Pathfinder Priority Inversion (PIP), Spin Deadlock & Live 5-Thread RT+RW | PIP cuts `T_High` block `9->2` ticks (`0` misses); RW `100%` hit rate vs `14.3%` Coarse | [Code](exercise-6/code), `6` PNGs, [EN PDF (42p)](exercise-6/docs/REPORT_EN.pdf), [FA PDF (41p)](exercise-6/docs/REPORT_FA.pdf), [Decks](exercise-6/docs/PRESENTATION_EN.pptx) |
| **Exercise 7** | Dining Philosophers: CPU fairness vs. resource safety, circular-wait proof, FIFO atomic-pair monitor | GS fairly allocates CPU but cannot alone solve fork deadlock; bounded model + 5-thread stress test | [Code](exercise-7/code), [README](exercise-7/README.md), worksheet, MP4 demo, [EN report](exercise-7/docs/REPORT_EN.pdf), [FA report](exercise-7/docs/REPORT_FA.pdf), bilingual 7-slide seminar |

## Repository Structure
- `GuaranteedScheduling.py`: Original root `psutil` proportional scheduler script (`8687 bytes; final slice accounting).
- `core/gs_core.py` & `tests/test_gs_core.py`: Canonical exact `Fraction` simulation core (`28` unit tests), vendored across `exercise-{1..3}/code/gs_core.py`.
- `tools/`: Shared bilingual report compiler (`report_kit.py`, `build_report.py`, `check_outputs.py`), Okabe-Ito plotting helpers (`plot_kit.py`), `vendor_core.py`, `make_decks.py`, and modular data/content loaders (`tools/content/gs{1,2}_*.py`, `ex{3..6}_*.py`).
- `exercise-1/` .. `exercise-6/`: Self-contained exercises with `code/`, `output/experiments.json`, `diagrams/` (`55` PNGs total, including 5 rubric flowcharts), `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}` (`0` page overflows, `0` missing glyphs), 10-slide bilingual capstone decks (`exercise-6`), `README.md`, and `tests/test_ex*.py`.
- `benchmarks/archive-studies/`: Archived earlier extended GS studies (`ex3_float_audit`, `ex4_theorems`, `ex5_montecarlo`, `ex6_heap_opt`, `ex7_capstone`), excluded from active test discovery via `pytest.ini`.

## Instructor-rubric deliverables and reproducibility

All seven exercises now use the same source-driven bilingual report compiler. Exercises 2–7 include an explicit process flowchart and a source-audited technical appendix generated from the actual Python implementation. The final PDF page counts are read back from the rendered PDFs: Ex1 42/42, Ex2 43/43, Ex3 45/43, Ex4 43/42, Ex5 44/43 and Ex6 42/41 pages (English/Persian). All 12 reports exceed 40 pages; the build gate checks this automatically.

- [Instructor-rubric audit and final page counts](docs/RUBRIC_AUDIT.md)
- [Guaranteed Scheduling demonstration clip](exercise-1/media/guaranteed_scheduling_demo.mp4) — generated from the exact-rational `gs_vtime` trace.
- [Exercise 3 printable paper worksheet](exercise-3/WORKSHEET_PAPER_TEMPLATE.pdf) — the template is provided for the student's own handwritten work; no handwritten submission is fabricated.
- [Exercise 6 bilingual capstone presentation and scripts](exercise-6/docs/)
- [Exercise 7 independent Dining Philosophers package](exercise-7/README.md) — its own monitor, model checker, GS CPU-share study, report, worksheet, demo video and seminar.

The workflow in `.github/workflows/verify-and-build.yml` regenerates experiment data, diagrams, reports and the video, runs pytest, checks all outputs, and enforces a minimum of 41 pages.


### Final rubric follow-up: worked paper solution and Dining Philosophers

- Exercise 3 now includes complete bilingual reference answer keys with all tick-by-tick EDF/RM traces for Sets A/B/C: [EN](exercise-3/WORKED_SOLUTION_EN.md) · [FA](exercise-3/WORKED_SOLUTION_FA.md).
- Exercise 6 now includes a tested FIFO Dining Philosophers monitor, finite-state exploration, five-thread stress test, diagram and standalone bilingual article: [EN](exercise-6/docs/ARTICLE_EN.md) · [FA](exercise-6/docs/ARTICLE_FA.md).
- The capstone presentation is extended to 11 slides with embedded bilingual speaker notes. GS is correctly described as CPU fairness, not as a fork deadlock-prevention algorithm.


## Exercise 7 — Independent Dining Philosophers assignment

The Dining Philosophers work is maintained in its own folder, exercise-7/, with its own code, experiments, charts, tests, two bilingual reports, printable worksheet, research article, presentation and MP4 demonstration. It is not merely an appendix to Exercise 6.

The design conclusion is explicit: GS determines CPU service among runnable philosophers; the FIFO monitor determines fork ownership and prevents circular wait by granting both forks atomically. The CI workflow rebuilds the Exercise 7 artifacts and enforces the same greater-than-40-page report requirement for both languages.

- [Exercise 7 README and run instructions](exercise-7/README.md)
- [Dining Philosophers implementation](exercise-7/code/dining_philosophers.py)
- [English article](exercise-7/docs/ARTICLE_EN.md) · [Persian article](exercise-7/docs/ARTICLE_FA.md)
- [Exercise 7 bilingual presentation](exercise-7/docs/)
