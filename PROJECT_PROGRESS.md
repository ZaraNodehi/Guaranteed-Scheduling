# Project Progress Tracker — Operating Systems Scheduling & Synchronization

Branch: `main` (default branch; earlier `arena/*` variants remain available for historical comparison)
Last verified: 2026-11-21

| Stage | Scope | Tests | Bilingual Monographs (EN + FA) | Extra Deliverables | Status |
| --- | --- | --- | --- | --- | --- |
| Core Engine | `core/gs_core.py` + `tools/vendor_core.py` parity (`Ex 1–3`) | `28/28` PASS | N/A | Canonical fractional GS & RT core | Complete |
| Exercise 1 | Baseline GPS, tie envelopes, `V(t)` arrival fix, Linux `psutil` | `4/4` PASS | `42p` EN / `42p` FA DOCX+PDF (`10` PNGs) | `REPORT_{EN,FA}.md` | Complete |
| Exercise 2 | Multi-regime proportional vs RT vs overload + verifier | `3/3` PASS | `43p` EN / `43p` FA DOCX+PDF (`8` PNGs) | `REPORT_{EN,FA}.md` | Complete |
| Exercise 3 | Hard RT: RM vs EDF, Liu-Layland, RTA & Domino Overload | `4/4` PASS | `45p` EN / `43p` FA DOCX+PDF (`8` PNGs) | `WORKSHEET_PAPER_TEMPLATE.pdf` (`2p`) + `PAPER_WORKSHEET_P{1,2}.png` | Complete |
| Exercise 4 | Mutual Exclusion: Dekker v1–v5, Peterson SC/TSO, Sem, Monitor, BFS | `3/3` PASS | `43p` EN / `42p` FA DOCX+PDF (`10` PNGs) | Exhaustive BFS counterexamples & bounded buffer bench | Complete |
| Exercise 5 | Readers–Writers (`4` primitives × `3` policies), Starvation & Barging | `3/3` PASS | `44p` EN / `43p` FA DOCX+PDF (`8` PNGs) | 4.03× Read-Heavy speedup & Ticket anti-barging audit | Complete |
| Exercise 6 | Capstone: Mars Pathfinder PIP, Spin Deadlock & Live RT+RW Pipeline | `6/6` PASS | `43p` EN / `42p` FA DOCX+PDF (`8` PNGs incl. flowchart and dining diagram) | 11-slide bilingual capstone decks and speaker scripts | Complete |
| Exercise 7 | Independent Dining Philosophers: circular-wait proof, FIFO atomic fork monitor, GS CPU-share study | `8/8` PASS | `47p` EN / `47p` FA DOCX+PDF | `14` PNGs, rubric flowchart, 2-page worksheet, MP4 demo, bilingual article and 7-slide seminar | Complete |

## Aggregate Verification Totals

- Exact final PDF pages: Ex1 `42/42`, Ex2 `43/43`, Ex3 `45/43`, Ex4 `43/42`, Ex5 `44/43`, Ex6 `43/42`, Ex7 `47/47` (EN/FA). All 14 are greater than 40 pages.
- Active `pytest` suite (`pytest.ini`): **63/63 PASSED** (`28` core + `31` exercise + `4` root-scheduler regression tests; GitHub Actions run `44925210501`)
- Verified Okabe-Ito figures (`exercise-{1..6}/diagrams/*.png`): **70 PNGs** (`10+9+9+11+9+8+14` across Exercises 1–7, including six rubric flowcharts and worksheet previews)
- Bilingual DOCX/PDF monographs: **14 DOCX + 14 PDF** (`0` page overflows, `0` missing figures, `0` missing Vazirmatn glyphs)
- Capstone decks & speaker scripts (`exercise-6/docs/`): **2 PPTX + 2 MD** (11 slides each, speaker notes on every slide)
- Archived earlier GS studies (`benchmarks/archive-studies/`): 5 preserved studies excluded cleanly via `pytest.ini`

- Demonstration clip: `exercise-1/media/guaranteed_scheduling_demo.mp4`, generated from the exact `gs_vtime` trace.
- Rubric flowcharts: one explicit workflow diagram each for Exercises 2–7.
- The Exercise 3 handwritten worksheet remains a student-completed deliverable; no scan is fabricated.


## Exercise 7 — Independent folder

- Folder: `exercise-7/` (standalone code, tests, output data, diagrams, docs, media and README).
- Correctness model: a five-philosopher FIFO monitor grants both forks atomically; a bounded state explorer checks safety/deadlock and a five-thread stress test checks 20 meals.
- Separate GS experiment: equal and weighted CPU entitlements are measured independently from fork ownership.
- GitHub Actions now generates the Exercise 7 experiments, flowchart, charts, worksheet, video, article, seminar and bilingual >40-page reports. Final CI run `44925210501` succeeded; both reports measured `47` pages, all 8 Exercise 7 tests passed, and artifact/page gates are green.
