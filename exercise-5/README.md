# Exercise 5 — Large-Scale Simulation Sweeps, Pareto Tradeoffs, Statistical Dominance & Live OS Control

## Six-Sweep Experimental Design (`[M]` + `[D]`)
Exercise 5 evaluates virtual-time scheduling (`gs_vtime`) at scale across **750 seeded rational simulations** and **5 live Linux kernel polling intervals**:
- **Sweep A (`[M]`):** 240 dynamic workloads (`80` seeds x `N in {3, 5, 8}`, `w in 1..6`, `arr in 0..14`), complete 240-seed archive, `Mean +/- 95% CI`, `p95`/`p99`, and ECDF distributions (`gs_vtime:stay` cuts mean lag **3.7x** below `gs_ratio:index`: `0.908` vs `3.362`).
- **Sweep B (`[M]`):** Quantum sweep `q in {1, 2, 3, 4, 6, 8, 12}` (`30` seeds x `7` quanta), demonstrating the Pareto knee at `q = 2` (`44.4%` switch cut) with invariant turnaround (`~39.0..39.4` ticks).
- **Sweep C (`[M]`):** Concurrency & skew scaling `N in {2, 4, 6, 8, 12, 16}` (`20` seeds/pt) comparing equal (`1:1`) vs skewed (`1:4`) weights.
- **Sweep E (`[M]`):** Heavy-tail Zipf weight skew `[1, 1, 2, 4, 8, 16]` + mid-run `t = 14..17` burst arrival shock (`60` seeds).
- **Sweep F (`[M]`):** `1,000`-resample paired Bootstrap 95% CI & Cohen's `d` dominance audit (`gs_vtime:stay` achieves `97.92%` pairwise win rate over `gs_ratio`, `d = 1.805`).
- **Sweep D (`[D]`):** Live Linux `psutil` `SIGSTOP`/`SIGCONT` scheduling across **5 intervals** (`0.01s..0.20s`, weights `[1, 2, 4]`) plus a 24-dispatch trace at `dt = 0.05s`.

## Deliverables
- `diagrams/`: **8 Okabe-Ito publication figures** (`fig_ex5_*.png`).
- `REPORT_EN.md`, `docs/REPORT_EN.{docx,pdf}` (**41 pages**) & `REPORT_FA.md`, `docs/REPORT_FA.{docx,pdf}` (**40 pages**, RTL Vazirmatn).
- Standard-academic bilingual seminar package: `docs/DECK_EN.pptx`, `docs/DECK_FA.pptx` (10 slides each + full speaker notes) & `docs/SPEAKER_{EN,FA}.md`.

## Re-run Commands
```bash
python3 exercise-5/code/run_experiments.py
python3 exercise-5/code/make_diagrams.py
python3 tools/make_decks.py 5
python3 tools/build_report.py gs5_en exercise-5 REPORT_EN
python3 tools/build_report.py gs5_fa exercise-5 REPORT_FA
python3 -m pytest exercise-5/tests -v
```
