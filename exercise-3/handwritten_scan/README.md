# Exercise 3 — Handwritten Paper Scan Upload Folder (`handwritten_scan/`)

This folder is the designated dropbox for your **hand-worked pen-and-paper scheduling solution** for Exercise 3 (3-process EDF vs. RM).

## How to Use
1. Print or copy [`../WORKSHEET_PAPER_TEMPLATE.pdf`](../WORKSHEET_PAPER_TEMPLATE.pdf) (preview images `PAPER_WORKSHEET_P1.png` and `PAPER_WORKSHEET_P2.png` are included right here for reference).
2. Work through **Set A (`H=12`)** and **Set B (`H=24`)** step by step on paper:
   - Fill in each tick box (`t=0..11` for Set A, `t=0..23` for Set B) with the active job (`P1#0`, `P2#1`, `P3#0`, etc.).
   - Write the ready-queue state at key contention ticks (`t=4, 5` for Set A; `t=6, 7, 8, 9, 13, 15` for Set B).
   - Compute the Response-Time Analysis (`R_3`) fixed-point iterations and mark `MISS P3#0 @ t=8` under RM in Set B.
3. Photograph or scan your completed sheets and save them into this folder (`exercise-3/handwritten_scan/`) as e.g. `scan_page1.jpg` / `scan_page2.jpg` or `handwritten_solution.pdf`.
4. Verify your handwritten timeline against the programmatic reference (`../output/experiments.json` or `../code/run_experiments.py`).
