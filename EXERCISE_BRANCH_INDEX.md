# Exercise Directory & Deliverable Index

All seven active curriculum exercises and the rubric-complete deliverables are maintained on the default branch `main`. Earlier `arena/*` variants and historical studies remain available for comparison:

| Exercise | Folder | Code & Experiments | Reports, Figures & Media | Unit Tests |
| --- | --- | --- | --- | --- |
| Baseline & Core | `core/`, `tests/` | `core/gs_core.py` | — | `tests/test_gs_core.py` (`28` tests) |
| Exercise 1 | `exercise-1/` | `code/{gs_core,run_experiments,make_diagrams}.py` | `10` PNGs, `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}` (`42p`/`42p`) | `exercise-1/tests/test_ex1.py` (`4` tests) |
| Exercise 2 | `exercise-2/` | `code/{gs_core,run_experiments,make_diagrams}.py` | `9` PNGs, `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}` (`43p`/`43p`) | `exercise-2/tests/test_ex2.py` (`3` tests) |
| Exercise 3 | `exercise-3/` | `code/{gs_core,run_experiments,plot_diagrams,make_worksheet,make_paper_copy_guides}.py` | `9` PNGs, `WORKSHEET_PAPER_TEMPLATE.pdf` (`2p`), two 3-page hand-copy guides (`paper_copy_guides/`), `handwritten_scan/`, `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}` (`45p`/`43p`) | `exercise-3/tests/test_ex3.py` (`4` tests) |
| Exercise 4 | `exercise-4/` | `code/{sync_primitives,run_experiments,plot_diagrams}.py` | `11` PNGs, `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}` (`43p`/`42p`) | `exercise-4/tests/test_ex4.py` (`3` tests) |
| Exercise 5 | `exercise-5/` | `code/{rw_locks,run_experiments,plot_diagrams}.py` | `9` PNGs, `REPORT_{EN,FA}.md`, `docs/REPORT_{EN,FA}.{docx,pdf}` (`44p`/`43p`) | `exercise-5/tests/test_ex5.py` (`3` tests) |
| Exercise 6 | `exercise-6/` | `code/{integrated_kernel,run_experiments,plot_diagrams,make_dining_diagram}.py` | `8` PNGs, reports (`43p`/`42p`), 11-slide bilingual capstone decks and scripts | `exercise-6/tests/test_ex6.py` (`6` tests) |
| Exercise 7 | `exercise-7/` | `code/{dining_philosophers,run_experiments,plot_diagrams,make_worksheet,make_demo_video}.py` | Independent FIFO monitor, GS CPU-share study, `14` PNGs, worksheet, MP4 demo, reports (`47p`/`47p`), bilingual article and 7-slide seminar | `exercise-7/tests/test_ex7.py` (`8/8` PASS) |
| Archived Studies | `benchmarks/archive-studies/` | `ex3_float_audit`, `ex4_theorems`, `ex5_montecarlo`, `ex6_heap_opt`, `ex7_capstone` | Preserved pre-pivot GS studies | Excluded via `pytest.ini` |


All report page numbers above are the exact counts read from the final PDF files by the build gate. Six exercise-specific rubric flowcharts (Exercises 2–7), the Exercise 1 GS demonstration and the Exercise 7 Dining Philosophers demonstration are generated in the same workflow. The full repository now has 70 PNG assets and 14 bilingual report pairs (DOCX/PDF), all exceeding 40 PDF pages.


Exercise 7 is an independent submission folder and is not stored only as a supplement to Exercise 6. Its final counts are verified: English/Persian reports are 47/47 pages, all eight dedicated tests pass, and the full CI run 44925210501 succeeded.
