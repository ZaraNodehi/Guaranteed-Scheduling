# Exercise 3 — Hand-Worked Paper Scheduling of EDF & RM with 3 Processes

Complete pen-and-paper scheduling package plus programmatic verification against `core/gs_core.py`.

## Datasets Included
1. **Set A (`H=12`, `U=11/12=0.9167`)**: `P1(3,1,3)`, `P2(4,1,4)`, `P3(6,2,6)` — crosses the 3-process Liu–Layland bound (`0.7798`), passes both EDF (`0` misses) and RM (`0` misses, `R_3*=6`), and diverges cleanly at ticks `t=4, 5`.
2. **Set B (`H=24`, `U=23/24=0.9583`)**: `P1(4,1,4)`, `P2(6,2,6)`, `P3(8,3,8)` — classic separation set where **EDF achieves `0` misses** (`dbf(L) <= L` everywhere) while **RM misses `P3#0` at `t=8`** (`R_3*=9 > D_3=8`).
3. **Set C (`2H=24`, `U=7/6=1.1667`)**: `P1(3,1,3)`, `P2(4,2,4)`, `P3(6,2,6)` — transient overload reference exposing EDF domino failure (`5` misses) vs. RM low-priority starvation (`3` misses on `P3` only).

## Key Artifacts
- **Printable Paper Worksheet**: [`WORKSHEET_PAPER_TEMPLATE.pdf`](WORKSHEET_PAPER_TEMPLATE.pdf) (2 A4 sheets with blank Gantt grids, ready-queue tables, and RTA/dbf calculation boxes).
- **Handwritten Scan Dropbox**: [`handwritten_scan/`](handwritten_scan/) (includes sheet previews `PAPER_WORKSHEET_P1.png`, `PAPER_WORKSHEET_P2.png`, and upload instructions).
- **Full Bilingual Reports**: [`REPORT_EN.md`](REPORT_EN.md), [`docs/REPORT_EN.pdf`](docs/REPORT_EN.pdf), [`REPORT_FA.md`](REPORT_FA.md), [`docs/REPORT_FA.pdf`](docs/REPORT_FA.pdf) (+ `.docx` editions).
- **Code & Data**: `code/run_experiments.py`, `code/plot_diagrams.py`, `code/make_worksheet.py`, `output/experiments.json`, and 8 Okabe-Ito diagrams in `diagrams/`.

## Reproduction
```bash
python3 exercise-3/code/run_experiments.py
python3 exercise-3/code/plot_diagrams.py
python3 exercise-3/code/make_worksheet.py
python3 tools/build_report.py ex3_en exercise-3 REPORT_EN
python3 tools/build_report.py ex3_fa exercise-3 REPORT_FA
python3 -m pytest exercise-3/tests -v
```
