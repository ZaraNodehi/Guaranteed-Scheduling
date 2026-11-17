# Exercise 6 — O(log n) Lazy Heap, Fixed-Point Audit & Live Linux Sleeper Mitigation

## Four Structural Refactorings (`exercise-6/code/gs_optimized.py`)
Exercise 6 fixes every structural flaw uncovered in Exercises 1–5:
1. **`O(log N)` Lazy Versioned Min-Heap + `stay` Fast Path (Bench 1):** Slashes dispatch latency at `N = 2,000` (`112x` speedup) and `N = 4,000` (`>200x` speedup), while `O(1)` lazy sleep/wake cancellation achieves `>70x` churn speedup at `N = 2,000`.
2. **`120`-Workload Incremental Engineering Ablation (Bench 2):** Separately quantifies `V0 (gs_ratio)` -> `V1 (+V(t))` -> `V2 (+stay)` -> `V3 (+gs_capped)` (`13t` -> `4t` worst mixed burst at lowest lag).
3. **Sleeper Scaling `S = 5..160` & Cap Knee (Bench 3):** `gs_capped` keeps post-wakeup burst at **1 tick** indefinitely and proves `wakeup_cap = 1` is the exact Pareto knee.
4. **IEEE-754 Float Drift vs `10^9` & `SCALE_LCM` Fixed-Point (Bench 5):** Exposes `47,996` `float64` tie divergences on `[2, 5, 10]` across `100,000` steps vs **`0`** errors under `SCALE_FP = 10^9`, and proves `SCALE_LCM = 720,720,000` yields **`0`** errors on prime weights `[3, 7, 11]`.
5. **Dual Live Linux Validation (Bench 4 `[D]`):** Slashes mid-run spawn error `~8.6x` (`25.2%` -> `2.9%`) and eliminates `0.8s SIGSTOP` sleeper monopolies (`100%` CPU / 15-step burst -> `~46%/54%` / 2-step max).

## Deliverables
- `diagrams/`: **8 Okabe-Ito publication figures** (`fig_ex6_*.png`).
- `REPORT_EN.{md,docx,pdf}` (**42 pages**) & `REPORT_FA.{md,docx,pdf}` (**41 pages** RTL Vazirmatn).
- Standard-academic seminar package: `docs/DECK_{EN,FA}.pptx` (10 slides + full speaker notes) & `docs/SPEAKER_{EN,FA}.md`.
