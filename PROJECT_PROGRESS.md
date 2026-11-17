# Project Progress Tracker — Guaranteed Scheduling

Branch: `arena/796ca936-guaranteed-scheduling` (branched from `main` `f02ea49e25b7e394199efddde7282c03a78c4d24`)
Last verified: 2026-11-17

| Stage | Scope | Tests | Bilingual Monographs (EN + FA) | Seminar Decks | Status |
| --- | --- | --- | --- | --- | --- |
| Core Engine | `core/gs_core.py` + vendoring sync (`tools/vendor_core.py`) | `28/28` PASS | N/A | N/A | Complete |
| Exercise 1 | Baseline GPS, tie envelopes, `V(t)` arrival fix, OS subprocess benchmark | `4/4` PASS | `42p` EN / `42p` FA DOCX+PDF (`10` PNGs) | N/A | Complete |
| Exercise 2 | Multi-regime proportional vs RT vs overload + independent verifier | `3/3` PASS | `40p` EN / `40p` FA DOCX+PDF (`8` PNGs) | N/A | Complete |
| Exercise 3 | Exact hand-trace equivalence & IEEE-754 float drift | `6/6` PASS | `41p` EN / `41p` FA DOCX+PDF (`8` PNGs) | N/A | Complete |
| Exercise 4 | 4 formal theorems (SFQ/WFQ, `Omega(t_arr)`, exhaustive RT, overload) | `6/6` PASS | `41p` EN / `40p` FA DOCX+PDF (`8` PNGs) | N/A | Complete |
| Exercise 5 | 240-seed MC, Zipf+burst, quantum Pareto (`q=1..12`), `N=2..16`, 5-rate OS | `5/5` PASS | `41p` EN / `40p` FA DOCX+PDF (`8` PNGs) | 10-slide `DECK_{EN,FA}.pptx` + `SPEAKER_{EN,FA}.md` | Complete |
| Exercise 6 | `O(log n)` lazy heap (`206.64x @ 4k`), `SCALE_LCM`, 120-seed ablation, `159->1` sleeper, live OS | `6/6` PASS | `42p` EN / `41p` FA DOCX+PDF (`8` PNGs) | 10-slide `DECK_{EN,FA}.pptx` + `SPEAKER_{EN,FA}.md` | Complete |
| Exercise 7 | Cross-ex synthesis, 7-regime (`R1..R7`), 40-seed EEVDF (`37/40`), live `[1,2,4]` OS, audit | `5/5` PASS | `43p` EN / `42p` FA DOCX+PDF (`8` PNGs) | 10-slide `DECK_{EN,FA}.pptx` + `SPEAKER_{EN,FA}.md` | Complete |

## Aggregate Verification Totals
- Total active pytest suite (`pytest.ini`): **63/63 PASSED** across `tests/` and `exercise-{1..7}/tests/`
- Total verified Okabe-Ito diagrams (`exercise-{1..7}/diagrams/*.png`): **58 PNGs** (Ex1: `10`, Ex2–7: `8` each)
- Total verified bilingual DOCX/PDF monographs: **14 DOCX + 14 PDF** (`40–43` pages each, `0` page overflows, `0` missing figures, `0` missing font glyphs)
- Total bilingual 10-slide PPTX decks + speaker scripts: **6 PPTX + 6 MD** (Ex5–Ex7, speaker notes on every slide)
