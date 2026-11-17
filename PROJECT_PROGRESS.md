# Project Progress Tracker — Operating Systems Scheduling & Synchronization

Branch: `arena/e966e03b-guaranteed-scheduling` (branched from `main` `43bb1e2554f467ea22e1b4fbd61490454da96b2b`)
Last verified: 2026-11-17

| Stage | Scope | Tests | Bilingual Monographs (EN + FA) | Extra Deliverables | Status |
| --- | --- | --- | --- | --- | --- |
| Core Engine | `core/gs_core.py` + `tools/vendor_core.py` parity (`Ex 1–3`) | `28/28` PASS | N/A | Canonical fractional GS & RT core | Complete |
| Exercise 1 | Baseline GPS, tie envelopes, `V(t)` arrival fix, Linux `psutil` | `4/4` PASS | `42p` EN / `42p` FA DOCX+PDF (`10` PNGs) | `REPORT_{EN,FA}.md` | Complete |
| Exercise 2 | Multi-regime proportional vs RT vs overload + verifier | `3/3` PASS | `40p` EN / `40p` FA DOCX+PDF (`8` PNGs) | `REPORT_{EN,FA}.md` | Complete |
| Exercise 3 | Hard RT: RM vs EDF, Liu-Layland, RTA & Domino Overload | `3/3` PASS | `20p` EN / `18p` FA DOCX+PDF (`8` PNGs) | `WORKSHEET_PAPER_TEMPLATE.pdf` (`2p`) + `PAPER_WORKSHEET_P{1,2}.png` | Complete |
| Exercise 4 | Mutual Exclusion: Dekker v1–v5, Peterson SC/TSO, Sem, Monitor, BFS | `3/3` PASS | `41p` EN / `40p` FA DOCX+PDF (`10` PNGs) | Exhaustive BFS counterexamples & bounded buffer bench | Complete |
| Exercise 5 | Readers–Writers (`4` primitives × `3` policies), Starvation & Barging | `3/3` PASS | `17p` EN / `16p` FA DOCX+PDF (`8` PNGs) | 4.03× Read-Heavy speedup & Ticket anti-barging audit | Complete |
| Exercise 6 | Capstone: Mars Pathfinder PIP, Spin Deadlock & Live RT+RW Pipeline | `3/3` PASS | `12p` EN / `11p` FA DOCX+PDF (`6` PNGs) | 10-slide `PRESENTATION_{EN,FA}.pptx` + `SPEAKER_SCRIPT_{EN,FA}.md` | Complete |

## Aggregate Verification Totals
- Active `pytest` suite (`pytest.ini`): **47/47 PASSED** (`28` core + `19` exercise tests across `exercise-{1..6}`)
- Verified Okabe-Ito figures (`exercise-{1..6}/diagrams/*.png`): **50 PNGs** (`10+8+8+10+8+6`)
- Bilingual DOCX/PDF monographs: **12 DOCX + 12 PDF** (`0` page overflows, `0` missing figures, `0` missing Vazirmatn glyphs)
- Capstone decks & speaker scripts (`exercise-6/docs/`): **2 PPTX + 2 MD** (10 slides each, speaker notes on every slide)
- Archived earlier GS studies (`benchmarks/archive-studies/`): 5 preserved studies excluded cleanly via `pytest.ini`
