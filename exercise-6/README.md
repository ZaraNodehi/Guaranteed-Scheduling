# Exercise 6 — Algorithmic Optimization, O(log n) Refactoring & Sleeper Mitigation

## Refactored Implementation (`code/gs_optimized.py`)
Replaces legacy `O(N)` list scanning and IEEE-754 float scoring with `OptimizedHeapScheduler`:
- **`O(log N)` lazy-deletion min-heap** with `O(1)` versioned sleep/wake state transitions and `O(1)` `stay` tie-break fast path (`113.1x` dispatch speedup at `N = 2,000`: `69.53 us -> 0.615 us`).
- **Fixed-point `10^9`-scaled virtual time** (`0` IEEE-754 rounding drift).
- **Dynamic arrival `V(t)` anchoring** + **`gs_capped` wakeup floor** (`V(t) - cap/w`, eliminating `79`-tick sleeper burst monopolies down to `1` tick!).
- **Live Linux OS validation (`[D]`):** Cuts mid-run dynamic worker CPU share deviation **4.2x** (`11.97% -> 2.82%`).

## Re-run Commands
```bash
python3 exercise-6/code/run_experiments.py
python3 exercise-6/code/make_diagrams.py
python3 tools/build_report.py gs6_en exercise-6 REPORT_EN
python3 tools/build_report.py gs6_fa exercise-6 REPORT_FA
python3 -m pytest exercise-6/tests -v
```
