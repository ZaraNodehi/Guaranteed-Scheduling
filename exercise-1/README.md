# Exercise 1 — Introduction to Guaranteed Scheduling

This exercise introduces **Guaranteed Scheduling** (Tanenbaum, Ch. 2), bridges it to the root repository script [`GuaranteedScheduling.py`](../GuaranteedScheduling.py), formalizes the `used / weight` scheduling invariant against continuous **Ideal Fluid GPS**, and validates both deterministic discrete simulations (`[M]`), exhaustive tie/starvation state-space checks (`[E]`), and 5 repeated real Linux `psutil` subprocess trials (`[M]` + `[D]`).

## Key Topics & Findings

- **Exact Integer & `Fraction` Model (`code/gs_core.py`)**: Formalizes entitled service $E_i(t)$, guaranteed ratio $used_i / w_i$, and GPS service lag $L_i(t) = A_i(t) - E_i(t)$ without floating-point drift.
- **Static Batch Equivalence (`[M]`)**: Under simultaneous arrivals ($t = 0$), `gs_ratio`, `gs_vtime`, and `stride` at $q=1$ achieve identical bounded service lag and dominate unweighted Round Robin at matched switch budgets.
- **Pareto Quantum Sweep (`[M]`)**: Sweeping $q \in \{1, 2, 4, 8, 16\}$ exposes the linear growth of max service lag versus the superlinear drop in context switches.
- **Exhaustive Tie-Breaking Envelope (`[E]`)**: All tie-breakers (`index`, `stay`, `max_weight`) lie inside the exact state-space bounds: worst-case GPS lag is invariant across tie-breakers, whereas `stay` hits the exact context-switch lower bound.
- **Dynamic Arrival Discrepancy (`[E]` + `[D]`)**: Exhaustive checks prove `GuaranteedScheduling.py`'s naive `used / weight` rule suffers bounded latecomer starvation (witness at $t_{\text{arr}} = 12$ locking out `P1` for 6 consecutive ticks), whereas `gs_vtime` and `gs_entitled` preserve starvation freedom.
- **Real Linux Subprocess Benchmark (`[M]` + `[D]`)**: Across 5 full `psutil` suspend/resume trials (`weights = [1, 2, 4]`, `q = 0.03s`, zero slices dropped), completion order matches `P3 < P2 < P1` in 5/5 runs, while normalized ratios expose real OS startup floor and 10 ms jiffy quantization effects relative to the zero-overhead discrete model.

## Structure

- `code/gs_core.py` — vendored canonical core (synced via `tools/vendor_core.py`)
- `code/run_experiments.py` — produces `output/experiments.json` dynamically (`[M]`, `[E]`, `[D]`)
- `code/make_diagrams.py` — generates all 8 high-DPI diagrams in `diagrams/`
- `docs/REPORT_EN.{pdf,docx}`, `REPORT_EN.md` — 24-page English report (dynamically generated from JSON)
- `docs/REPORT_FA.{pdf,docx}`, `REPORT_FA.md` — 24-page Persian RTL report (dynamically generated from JSON)
- `tests/test_ex1.py` — automated verification tests

## Reproducing Everything

```bash
python3 tools/vendor_core.py --check
python3 exercise-1/code/run_experiments.py
python3 exercise-1/code/make_diagrams.py
python3 tools/build_report.py gs1_en exercise-1 REPORT_EN
python3 tools/build_report.py gs1_fa exercise-1 REPORT_FA
python3 tools/check_outputs.py exercise-1
python3 -m pytest exercise-1/tests -v
```

## Demonstration clip and rubric evidence

[Play the Guaranteed Scheduling demonstration (MP4)](media/guaranteed_scheduling_demo.mp4). The clip is rendered from the exact `gs_vtime` simulator trace for a three-process weighted workload; it is a discrete scheduling demonstration, not a live-kernel performance benchmark.

The bilingual reports are rebuilt from the structured report modules. Their final PDF page counts are checked by the repository workflow, not taken from the Markdown page markers.
