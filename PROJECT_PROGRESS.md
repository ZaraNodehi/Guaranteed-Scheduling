# Project Progress Tracker — Operating Systems Scheduling & Synchronization

Branch: `main` (default branch; earlier `arena/*` variants remain available for historical comparison)
Last verified: 2026-11-21

| Stage | Scope | Tests | Bilingual Monographs (EN + FA) | Extra Deliverables | Status |
| --- | --- | --- | --- | --- | --- |
| Core Engine | `core/gs_core.py` + `tools/vendor_core.py` parity (`Ex 1–3`) | `28/28` PASS | N/A | Canonical fractional GS & RT core | Complete |
| Exercise 1 | Baseline GPS, tie envelopes, `V(t)` arrival fix, Linux `psutil` | `4/4` PASS | `42p` EN / `42p` FA DOCX+PDF (`10` PNGs) | `REPORT_{EN,FA}.md` | Complete |
| Exercise 2 | Multi-regime proportional vs RT vs overload + verifier | `3/3` PASS | `43p` EN / `43p` FA DOCX+PDF (`8` PNGs) | `REPORT_{EN,FA}.md` | Complete |
| Exercise 3 | Hard RT: RM vs EDF, Liu-Layland, RTA & Domino Overload | `3/3` PASS | `45p` EN / `43p` FA DOCX+PDF (`8` PNGs) | `WORKSHEET_PAPER_TEMPLATE.pdf` (`2p`) + `PAPER_WORKSHEET_P{1,2}.png` | Complete |
| Exercise 4 | Mutual Exclusion: Dekker v1–v5, Peterson SC/TSO, Sem, Monitor, BFS | `3/3` PASS | `43p` EN / `42p` FA DOCX+PDF (`10` PNGs) | Exhaustive BFS counterexamples & bounded buffer bench | Complete |
| Exercise 5 | Readers–Writers (`4` primitives × `3` policies), Starvation & Barging | `3/3` PASS | `44p` EN / `43p` FA DOCX+PDF (`8` PNGs) | 4.03× Read-Heavy speedup & Ticket anti-barging audit | Complete |
| Exercise 6 | Capstone: Mars Pathfinder PIP, Spin Deadlock & Live RT+RW Pipeline | Legacy suite retained | Existing bilingual DOCX+PDF reports | Capstone slides and scripts; Dining Philosophers supplement also retained | Complete |
| Exercise 7 | Independent Dining Philosophers: circular-wait proof, FIFO atomic fork monitor, GS CPU-share study | `8` dedicated tests (final CI pending) | EN/FA DOCX+PDF built by shared compiler; strict `>40p` gate | 8+ charts, rubric flowchart, worksheet, MP4 demo, bilingual article and 7-slide seminar | CI pending |

## Aggregate Verification Totals

- Exact final PDF pages: Ex1 `42/42`, Ex2 `43/43`, Ex3 `45/43`, Ex4 `43/42`, Ex5 `44/43`, Ex6 `42/41` (EN/FA). All 12 are greater than 40 pages.
- Active `pytest` suite (`pytest.ini`): **51/51 PASSED** (`28` core + `19` exercise + `4` root-scheduler regression tests; GitHub Actions run `44917446846`)
- Verified Okabe-Ito figures (`exercise-{1..6}/diagrams/*.png`): **55 PNGs** (`10+8+8+10+8+6` core figures + `5` rubric flowcharts)
- Bilingual DOCX/PDF monographs: **12 DOCX + 12 PDF** (`0` page overflows, `0` missing figures, `0` missing Vazirmatn glyphs)
- Capstone decks & speaker scripts (`exercise-6/docs/`): **2 PPTX + 2 MD** (10 slides each, speaker notes on every slide)
- Archived earlier GS studies (`benchmarks/archive-studies/`): 5 preserved studies excluded cleanly via `pytest.ini`

- Demonstration clip: `exercise-1/media/guaranteed_scheduling_demo.mp4`, generated from the exact `gs_vtime` trace.
- Rubric flowcharts: one explicit workflow diagram each for Exercises 2–6.
- The Exercise 3 handwritten worksheet remains a student-completed deliverable; no scan is fabricated.


## Exercise 7 — Independent folder

- Folder: `exercise-7/` (standalone code, tests, output data, diagrams, docs, media and README).
- Correctness model: a five-philosopher FIFO monitor grants both forks atomically; a bounded state explorer checks safety/deadlock and a five-thread stress test checks 20 meals.
- Separate GS experiment: equal and weighted CPU entitlements are measured independently from fork ownership.
- GitHub Actions now generates the Exercise 7 experiments, flowchart, charts, worksheet, video, article, seminar and bilingual >40-page reports. Final CI confirmation is pending.
