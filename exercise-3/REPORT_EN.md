# Exercise 3: Exact Fractional Hand Verification vs Programmatic Execution

**Step-by-Step Rational Arithmetic Audits, Tie-Breaker Branching, Static vs Dynamic Divergence, and IEEE-754 Float Drift**

- **Repository:** ZaraNodehi/Guaranteed-Scheduling
- **Scope:** Exercise 3 — Hand-Worked Exact Verification & Algebraic Audits
- **Instruments:** Independent Fraction Algebra [E] | Core Sim [M] | Float Drift Audit [D]
- **Data Source:** exercise-3/output/experiments.json (zero hardcoded numbers)

## Table of contents

- 1. Executive Overview & Verification Objectives (p. 3)
- 2. Three-Instrument Verification Pipeline [E]+[M]+[D] (p. 4)
- 3. Exact Fractional Update Laws (p. 5)
- 4. Workload 1: Full 12-Tick Hand Trace (Tie = index) [E]=[M] (p. 6)
- 5. Workload 1: Static Equivalence & Tie-Breaker Sensitivity [M]+[E] (p. 7)
- 6. Exact Fractional Branching Under stay & max_weight [E] (p. 8)
- 7. Visualizing Exact Tie Resets & Tie-Breaker Divergence [M] (p. 9)
- 8. Signed GPS Lag Envelope Verification on Workload 1 [E]+[M] (p. 10)
- 9. Workload 2: Static vs Dynamic Arrival Divergence [E]+[M]+[D] (p. 11)
- 10. Hand Verification of gs_ratio Starvation Trace (t = 0..17) [E]=[M] (p. 12)
- 11. Hand Verification of gs_entitled (A_i / E_online) [E]=[M] (p. 13)
- 12. Hand Verification of gs_vtime (Virtual-Time Anchor V(t)) [E]=[M] (p. 14)
- 13. Visualizing Static vs Dynamic Dispatch Divergence [M]+[D] (p. 15)
- 14. Lag Trajectory Comparison: Explosion vs Tight Bound [E]+[M] (p. 16)
- 15. Instrument Discrepancy [D]: IEEE-754 Float vs Exact Fraction (p. 17)
- 16. Visualizing Cascading Dispatch Drift From 1e-16 Error [D] (p. 18)
- 17. Engineering Drift-Free Virtual Time (Exact & Fixed-Point) (p. 19)
- 18. Reproducible Step-by-Step Hand-Checking Protocol (p. 20)
- 19. Practical Recommendations & Explicit Limitations (p. 21)
- 20. Summary of Verified Findings & Exercise 4 Preview (p. 22)


<!-- page 1 -->


<!-- page 2 -->


<!-- page 3 -->


## 1. Executive Overview & Verification Objectives

Whenever a systems simulator uses floating-point approximations or unverified tie rules, subtle discrepancies can silently alter dispatch sequences. Exercise 3 constructs a complete **zero-shared-code hand-algebra audit** using exact Python `fractions.Fraction` arithmetic and checks it tick-by-tick against `gs_core.py` across both simultaneous and dynamic arrival workloads.

- **Exact Static Correspondence (`[E]`=`[M]`):** Verify all 12 ticks of weighted batch `P1(0,3,1), P2(0,5,2), P3(0,4,3)` across `index`, `stay`, and `max_weight` tie-breakers.
- **Static Variant Equivalence (`[M]`):** Confirm whether `gs_ratio`, `gs_vtime`, `gs_entitled`, and `stride` generate identical schedules when arrivals occur together at `t = 0`.
- **Dynamic Arrival Divergence (`[E]`+`[M]`+`[D]`):** Trace 18 ticks of staggered arrivals (`t = 0, 4, 7`) by hand to expose why `gs_ratio` starves existing work while `gs_entitled` and `gs_vtime` remain bounded.
- **IEEE-754 Float Drift Discrepancy (`[D]`):** Quantify exactly how floating-point `1.0 / w` accumulation silently breaks exact virtual-time ties on ordinary integer weights.


<!-- page 4 -->


## 2. Three-Instrument Verification Pipeline [E]+[M]+[D]

Figure 1 summarizes the cross-validation loop tying independent rational hand algebra `[E]`, the vendored core simulator `[M]`, and an IEEE-754 binary float accumulator `[D]`.

![Figure 1: Cross-verification pipeline between exact rational hand traces, gs_core, and float drift.](diagrams/fig_ex3_verification_pipeline.png)

*Figure 1. Cross-verification pipeline between exact rational hand traces, gs_core, and float drift.*

| Verification Check | Verified Outcome |
|---|---|
| Workload 1 Static Match (index / stay / max_w) | 12/12 \| 12/12 \| 12/12 |
| Static Equivalence (gs_ratio==gs_vtime==entitled==stride) | True |
| Workload 2 Dynamic Match (ratio / entitled / vtime) | 18/18 \| 18/18 \| 18/18 |
| Primary Float Drift Case (w=[3,6,9]) | 62/180 ticks (34.44%) |

*Table 1. Summary of exact algebraic agreements and discrepancies [E]+[D]*


<!-- page 5 -->


## 3. Exact Fractional Update Laws


### Static Ratio & Virtual-Time Equivalence

```text
W = sum_{j=1}^n w_j = 1 + 2 + 3 = 6
E_i(t) = t * (w_i / W)  while all 3 processes remain active (t <= 8)
gs_ratio score:    used_i / w_i
gs_vtime score:    v_i = sum_{slices of i} (1 / w_i) = used_i / w_i (for arr = 0!)
Signed Lag:        L_i(t) = A_i(t) - E_i(t) in [-1, +1] for q = 1
```
*Exact rational invariants explaining static identity between gs_ratio and gs_vtime*

Because `P1`, `P2`, and `P3` arrive together at `t = 0`, global virtual time `V(t)` starts at `0` for all three processes. Consequently, `gs_vtime`'s virtual clock `v_i` equals `used_i / w_i` identically — until a late arrival occurs in Workload 2.


<!-- page 6 -->


## 4. Workload 1: Full 12-Tick Hand Trace (Tie = index) [E]=[M]

Workload 1 consists of `P1(arr=0, work=3, w=1)`, `P2(arr=0, work=5, w=2)`, and `P3(arr=0, work=4, w=3)` (`total_work = 12`). Table 2 records every single tick `t = 0..11` computed independently by hand-algebra Fractions and matched 12/12 against `gs_core`.

| t | Ratios Before (used/w) | Tied Min | Chosen | vs Sim | Lags After [P1, P2, P3] |
|---|---|---|---|---|---|
| 0 | P1:0, P2:0, P3:0 | P1/P2/P3 | P1 | MATCH | P1:5/6, P2:-1/3, P3:-1/2 |
| 1 | P1:1, P2:0, P3:0 | P2/P3 | P2 | MATCH | P1:2/3, P2:1/3, P3:-1 |
| 2 | P1:1, P2:1/2, P3:0 | P3 | P3 | MATCH | P1:1/2, P2:0, P3:-1/2 |
| 3 | P1:1, P2:1/2, P3:1/3 | P3 | P3 | MATCH | P1:1/3, P2:-1/3, P3:0 |
| 4 | P1:1, P2:1/2, P3:2/3 | P2 | P2 | MATCH | P1:1/6, P2:1/3, P3:-1/2 |
| 5 | P1:1, P2:1, P3:2/3 | P3 | P3 | MATCH | P1:0, P2:0, P3:0 |
| 6 | P1:1, P2:1, P3:1 | P1/P2/P3 | P1 | MATCH | P1:5/6, P2:-1/3, P3:-1/2 |
| 7 | P1:2, P2:1, P3:1 | P2/P3 | P2 | MATCH | P1:2/3, P2:1/3, P3:-1 |
| 8 | P1:2, P2:3/2, P3:1 | P3 | P3 | MATCH | P1:1/3, P2:-1/3, P3:0 |
| 9 | P1:2, P2:3/2 | P2 | P2 | MATCH | P1:0, P2:0, P3:0 |
| 10 | P1:2, P2:2 | P1/P2 | P1 | MATCH | P1:2/3, P2:-2/3, P3:0 |
| 11 | P2:2 | P2 | P2 | MATCH | P1:0, P2:0, P3:0 |

*Table 2. Complete 12-tick exact fractional ledger for Workload 1 under gs_ratio:index [E]=[M]*


<!-- page 7 -->


## 5. Workload 1: Static Equivalence & Tie-Breaker Sensitivity [M]+[E]

Table 3 verifies `all_static_equiv = True`: `gs_ratio`, `gs_vtime`, `gs_entitled`, and `stride` share identical lag (`1`), RMSE (`0.4547`), and switch count (`11`).

| Policy : Tie | Max Lag (frac) | RMSE | Switches | Preempts | Mean TA | Jain |
|---|---|---|---|---|---|---|
| gs_ratio:index | 1.0000 (1) | 0.4547 | 11 | 8 | 10.67 | 1.0000 |
| gs_vtime:index | 1.0000 (1) | 0.4547 | 11 | 8 | 10.67 | 1.0000 |
| gs_entitled:index | 1.0000 (1) | 0.4547 | 11 | 8 | 10.67 | 1.0000 |
| stride:index | 1.0000 (1) | 0.4547 | 11 | 8 | 10.67 | 1.0000 |
| gs_ratio:stay | 1.0000 (1) | 0.3889 | 8 | 5 | 10.00 | 1.0000 |
| gs_ratio:max_weight | 0.5000 (1/2) | 0.2778 | 10 | 7 | 10.00 | 1.0000 |
| rr:index | 2.0000 (2) | 0.9146 | 12 | 9 | 10.00 | 1.0000 |

*Table 3. Workload 1 metrics across static GS variants, tie-breakers, and Round Robin [M]*

| Exhaustive Tie Envelope [E] Metric | Value |
|---|---|
| Total states / terminal leaves | 304 states / 72 leaves (truncated=False) |
| Exact Lag Range [best, worst] | [0.5000, 1.0000] (frac 1) |
| Context Switch Range [min, max] | [8, 12] |

*Table 4. Workload 1 exhaustive tie-breaking bounds across all valid choices [E]*


<!-- page 8 -->


## 6. Exact Fractional Branching Under stay & max_weight [E]

At `t = 0` all three ratios equal `0`, and at `t = 6` (`used = [1, 2, 3]`) all three ratios reset to exact equality `1/1` (`1:2:3` full cycle!). Table 5 shows `stay` cutting context switches from `11` to `8` (`min_context_switches = 8`).

| t | Ratios Before | Tied Min | Chosen (stay) | vs Sim | Lags After |
|---|---|---|---|---|---|
| 0 | P1:0, P2:0, P3:0 | P1/P2/P3 | P1 | MATCH | P1:5/6, P2:-1/3, P3:-1/2 |
| 1 | P1:1, P2:0, P3:0 | P2/P3 | P2 | MATCH | P1:2/3, P2:1/3, P3:-1 |
| 2 | P1:1, P2:1/2, P3:0 | P3 | P3 | MATCH | P1:1/2, P2:0, P3:-1/2 |
| 3 | P1:1, P2:1/2, P3:1/3 | P3 | P3 | MATCH | P1:1/3, P2:-1/3, P3:0 |
| 4 | P1:1, P2:1/2, P3:2/3 | P2 | P2 | MATCH | P1:1/6, P2:1/3, P3:-1/2 |
| 5 | P1:1, P2:1, P3:2/3 | P3 | P3 | MATCH | P1:0, P2:0, P3:0 |
| 6 | P1:1, P2:1, P3:1 | P1/P2/P3 | P3 | MATCH | P1:-1/6, P2:-1/3, P3:1/2 |
| 7 | P1:1, P2:1 | P1/P2 | P1 | MATCH | P1:2/3, P2:-2/3, P3:0 |
| 8 | P1:2, P2:1 | P2 | P2 | MATCH | P1:1/3, P2:-1/3, P3:0 |
| 9 | P1:2, P2:3/2 | P2 | P2 | MATCH | P1:0, P2:0, P3:0 |
| 10 | P1:2, P2:2 | P1/P2 | P2 | MATCH | P1:-1/3, P2:1/3, P3:0 |
| 11 | P1:2 | P1 | P1 | MATCH | P1:0, P2:0, P3:0 |

*Table 5. Full 12-tick exact hand verification for gs_ratio:stay (12/12 match) [E]=[M]*


<!-- page 9 -->


## 7. Visualizing Exact Tie Resets & Tie-Breaker Divergence [M]

Figure 2 contrasts the four 12-tick execution timelines side by side, highlighting the exact `t = 6` rational reset boundary where all three processes simultaneously return to score `1`.

![Figure 2: Workload 1 timelines showing exact 1:2:3 tie reset at t=6 and stay switch savings.](diagrams/fig_ex3_static_hand_gantt.png)

*Figure 2. Workload 1 timelines showing exact 1:2:3 tie reset at t=6 and stay switch savings.*

- **At `t = 0` (`0 == 0 == 0`):** `index` picks `P1`, whereas `max_weight` picks `P3 (w=3)`.
- **At `t = 6` (`1 == 1 == 1`):** `index` preempts `P3` for `P1`, whereas `stay` keeps `P3` running and finishes `P3` cleanly at `t = 7` before switching to `P1`!
- **Why `RR` differs from GS:** Unweighted `RR` ignores the `1:2:3` ratio and wastes early ticks on `P1`, finishing `P1` at `t = 7` instead of `P3` at `t = 9`.


<!-- page 10 -->


## 8. Signed GPS Lag Envelope Verification on Workload 1 [E]+[M]

Figure 3 verifies the Parekh–Gallager single-quantum lag bound `L_i(t) in [-1, +1]` across all 12 ticks of Workload 1. Note how every lag returns cleanly to `0` at the `t = 6` rational cycle boundary, and `P3` drops out cleanly after completing at `t = 9`.

![Figure 3: Cumulative actual vs Ideal GPS service (top) and strictly bounded signed lag in [-1, +1] (bottom).](diagrams/fig_ex3_static_lag_fractions.png)

*Figure 3. Cumulative actual vs Ideal GPS service (top) and strictly bounded signed lag in [-1, +1] (bottom).*

> **GPS Weight Re-Normalization on Completion.** As verified in Table 2, once `P3` completes its fourth and final tick at `t = 9`, only `P1` (`w = 1`) and `P2` (`w = 2`) remain active; ideal GPS immediately re-normalizes their service rates to exact `1/3` and `2/3` proportions over `t = 9..12`.


<!-- page 11 -->


## 9. Workload 2: Static vs Dynamic Arrival Divergence [E]+[M]+[D]

Workload 2 breaks the simultaneous-arrival assumption (`t = 0`): `P1(arr=0, work=8, w=2)`, `P2(arr=4, work=6, w=2)`, and `P3(arr=7, work=4, w=1)` (`total_work = 18`). Table 6 summarizes how three GS variants that were identical on Workload 1 split sharply here.

| Policy | Max Lag (frac) | RMSE | Max Starve Gap | Switches | Mean TA | Jain |
|---|---|---|---|---|---|---|
| gs_ratio | 2.9000 (29/10) | 1.0135 | 6 | 12 | 13.00 | 1.0000 |
| gs_entitled | 0.9000 (9/10) | 0.2575 | 5 | 11 | 12.00 | 1.0000 |
| gs_vtime | 0.7000 (7/10) | 0.2182 | 4 | 12 | 11.67 | 1.0000 |
| stride | 0.7000 (7/10) | 0.2182 | 4 | 12 | 11.67 | 1.0000 |
| rr | 1.1667 (7/6) | 0.3995 | 2 | 15 | 12.67 | 1.0000 |

*Table 6. Workload 2 dynamic arrival metrics comparing GS variants, Stride, and RR [M]*

- **`gs_ratio` (`GuaranteedScheduling.py`) collapses:** Max lag balloons to `2.9000` (`29/10`) and `P1` is locked out for `6` straight ticks (`t = 4..10`).
- **`gs_entitled` recovers online fairness:** Tracking cumulative entitled service from arrival cuts max lag over 3x to `0.9000` (`9/10`).
- **`gs_vtime` achieves optimal dynamic tracking:** Anchoring newcomers to `V(t)` produces the tightest lag (`0.7000`, `7/10`) and best RMSE (`0.2182`).


<!-- page 12 -->


## 10. Hand Verification of gs_ratio Starvation Trace (t = 0..17) [E]=[M]

Table 7 walks through all 18 execution ticks of `gs_ratio` by hand. At `t = 4`, `P1` has ratio `4/2 = 2`, while newly arrived `P2` has ratio `0/2 = 0` — forcing `P1` to sit idle while `P2` takes `t=4..7`, and then `P3` arrives at `t=7` with `0/1 = 0`, prolonging `P1`'s lockout through `t = 10`.

| t | Scores Before | Chosen | P1 A/E (Lag) | P2 A/E (Lag) | P3 A/E (Lag) |
|---|---|---|---|---|---|
| 0 | P1:0 | P1 (OK) | 1/1 (0) | 0/0 (0) | 0/0 (0) |
| 1 | P1:1/2 | P1 (OK) | 2/2 (0) | 0/0 (0) | 0/0 (0) |
| 2 | P1:1 | P1 (OK) | 3/3 (0) | 0/0 (0) | 0/0 (0) |
| 3 | P1:3/2 | P1 (OK) | 4/4 (0) | 0/0 (0) | 0/0 (0) |
| 4 | P1:2, P2:0 | P2 (OK) | 4/9/2 (-1/2) | 1/1/2 (1/2) | 0/0 (0) |
| 5 | P1:2, P2:1/2 | P2 (OK) | 4/5 (-1) | 2/1 (1) | 0/0 (0) |
| 6 | P1:2, P2:1 | P2 (OK) | 4/11/2 (-3/2) | 3/3/2 (3/2) | 0/0 (0) |
| 7 | P1:2, P2:3/2, P3:0 | P3 (OK) | 4/59/10 (-19/10) | 3/19/10 (11/10) | 1/1/5 (4/5) |
| 8 | P1:2, P2:3/2, P3:1 | P3 (OK) | 4/63/10 (-23/10) | 3/23/10 (7/10) | 2/2/5 (8/5) |
| 9 | P1:2, P2:3/2, P3:2 | P2 (OK) | 4/67/10 (-27/10) | 4/27/10 (13/10) | 2/3/5 (7/5) |
| 10 | P1:2, P2:2, P3:2 | P1 (OK) | 5/71/10 (-21/10) | 4/31/10 (9/10) | 2/4/5 (6/5) |
| 11 | P1:5/2, P2:2, P3:2 | P2 (OK) | 5/15/2 (-5/2) | 5/7/2 (3/2) | 2/1 (1) |
| 12 | P1:5/2, P2:5/2, P3:2 | P3 (OK) | 5/79/10 (-29/10) | 5/39/10 (11/10) | 3/6/5 (9/5) |
| 13 | P1:5/2, P2:5/2, P3:3 | P1 (OK) | 6/8 (-2) | 5/9/2 (1/2) | 3/3/2 (3/2) |
| 14 | P1:3, P2:5/2, P3:3 | P2 (OK) | 6/8 (-2) | 6/31/6 (5/6) | 3/11/6 (7/6) |
| 15 | P1:3, P3:3 | P1 (OK) | 7/8 (-1) | 6/35/6 (1/6) | 3/13/6 (5/6) |
| 16 | P1:7/2, P3:3 | P3 (OK) | 7/8 (-1) | 6/6 (0) | 4/3 (1) |
| 17 | P1:7/2 | P1 (OK) | 8/8 (0) | 6/6 (0) | 4/4 (0) |

*Table 7. Full 18-tick exact hand verification of gs_ratio on Workload 2 (18/18 match) [E]=[M]*


<!-- page 13 -->


## 11. Hand Verification of gs_entitled (A_i / E_online) [E]=[M]

Under `gs_entitled`, newly arrived `P2` at `t=4` shares only the online GPS entitlement accrued *since* its arrival (`E_online` starts at `0`, so after 1 tick of `P2` at `t=4..5`, `P2` reaches ratio `1 / (1/2) = 2` while `P1` only has `4 / (9/2) = 8/9 < 2`), returning the CPU to `P1` immediately at `t = 5` (Table 8).

| t | Scores Before | Chosen | P1 A/E (Lag) | P2 A/E (Lag) | P3 A/E (Lag) |
|---|---|---|---|---|---|
| 0 | P1:0 | P1 (OK) | 1/1 (0) | 0/0 (0) | 0/0 (0) |
| 1 | P1:1 | P1 (OK) | 2/2 (0) | 0/0 (0) | 0/0 (0) |
| 2 | P1:1 | P1 (OK) | 3/3 (0) | 0/0 (0) | 0/0 (0) |
| 3 | P1:1 | P1 (OK) | 4/4 (0) | 0/0 (0) | 0/0 (0) |
| 4 | P1:1, P2:0 | P2 (OK) | 4/9/2 (-1/2) | 1/1/2 (1/2) | 0/0 (0) |
| 5 | P1:8/9, P2:2 | P1 (OK) | 5/5 (0) | 1/1 (0) | 0/0 (0) |
| 6 | P1:1, P2:1 | P1 (OK) | 6/11/2 (1/2) | 1/3/2 (-1/2) | 0/0 (0) |
| 7 | P1:12/11, P2:2/3, P3:0 | P3 (OK) | 6/59/10 (1/10) | 1/19/10 (-9/10) | 1/1/5 (4/5) |
| 8 | P1:60/59, P2:10/19, P3:5 | P2 (OK) | 6/63/10 (-3/10) | 2/23/10 (-3/10) | 1/2/5 (3/5) |
| 9 | P1:20/21, P2:20/23, P3:5/2 | P2 (OK) | 6/67/10 (-7/10) | 3/27/10 (3/10) | 1/3/5 (2/5) |
| 10 | P1:60/67, P2:10/9, P3:5/3 | P1 (OK) | 7/71/10 (-1/10) | 3/31/10 (-1/10) | 1/4/5 (1/5) |
| 11 | P1:70/71, P2:30/31, P3:5/4 | P2 (OK) | 7/15/2 (-1/2) | 4/7/2 (1/2) | 1/1 (0) |
| 12 | P1:14/15, P2:8/7, P3:1 | P1 (OK) | 8/79/10 (1/10) | 4/39/10 (1/10) | 1/6/5 (-1/5) |
| 13 | P2:40/39, P3:5/6 | P3 (OK) | 8/8 (0) | 4/9/2 (-1/2) | 2/3/2 (1/2) |
| 14 | P2:120/137, P3:30/23 | P2 (OK) | 8/8 (0) | 5/31/6 (-1/6) | 2/11/6 (1/6) |
| 15 | P2:150/157, P3:15/14 | P2 (OK) | 8/8 (0) | 6/35/6 (1/6) | 2/13/6 (-1/6) |
| 16 | P3:10/11 | P3 (OK) | 8/8 (0) | 6/6 (0) | 3/3 (0) |
| 17 | P3:15/16 | P3 (OK) | 8/8 (0) | 6/6 (0) | 4/4 (0) |

*Table 8. Full 18-tick exact hand verification of gs_entitled on Workload 2 (18/18 match) [E]=[M]*


<!-- page 14 -->


## 12. Hand Verification of gs_vtime (Virtual-Time Anchor V(t)) [E]=[M]

Under `gs_vtime`, when `P2` enters at `t = 4`, `v_P2` is initialized to system virtual time `V(4) = 4 * (1/2) = 2`, matching `v_P1 = 2` exactly! Because `index` tie-breaking resolves `P1` ahead of `P2` at `t = 4`, `P1` runs `t = 4..5` (`v_P1 = 5/2`), then `P2` runs `t = 5..6` (`v_P2 = 5/2`), maintaining exact 1:1 sharing without any transient shock (Table 9).

| t | Scores Before | Chosen | P1 A/E (Lag) | P2 A/E (Lag) | P3 A/E (Lag) |
|---|---|---|---|---|---|
| 0 | P1:0 | P1 (OK) | 1/1 (0) | 0/0 (0) | 0/0 (0) |
| 1 | P1:1/2 | P1 (OK) | 2/2 (0) | 0/0 (0) | 0/0 (0) |
| 2 | P1:1 | P1 (OK) | 3/3 (0) | 0/0 (0) | 0/0 (0) |
| 3 | P1:3/2 | P1 (OK) | 4/4 (0) | 0/0 (0) | 0/0 (0) |
| 4 | P1:2, P2:2 | P1 (OK) | 5/9/2 (1/2) | 0/1/2 (-1/2) | 0/0 (0) |
| 5 | P1:5/2, P2:2 | P2 (OK) | 5/5 (0) | 1/1 (0) | 0/0 (0) |
| 6 | P1:5/2, P2:5/2 | P1 (OK) | 6/11/2 (1/2) | 1/3/2 (-1/2) | 0/0 (0) |
| 7 | P1:3, P2:5/2, P3:11/4 | P2 (OK) | 6/59/10 (1/10) | 2/19/10 (1/10) | 0/1/5 (-1/5) |
| 8 | P1:3, P2:3, P3:11/4 | P3 (OK) | 6/63/10 (-3/10) | 2/23/10 (-3/10) | 1/2/5 (3/5) |
| 9 | P1:3, P2:3, P3:15/4 | P1 (OK) | 7/67/10 (3/10) | 2/27/10 (-7/10) | 1/3/5 (2/5) |
| 10 | P1:7/2, P2:3, P3:15/4 | P2 (OK) | 7/71/10 (-1/10) | 3/31/10 (-1/10) | 1/4/5 (1/5) |
| 11 | P1:7/2, P2:7/2, P3:15/4 | P1 (OK) | 8/15/2 (1/2) | 3/7/2 (-1/2) | 1/1 (0) |
| 12 | P2:7/2, P3:15/4 | P2 (OK) | 8/79/10 (1/10) | 4/39/10 (1/10) | 1/6/5 (-1/5) |
| 13 | P2:4, P3:15/4 | P3 (OK) | 8/8 (0) | 4/9/2 (-1/2) | 2/3/2 (1/2) |
| 14 | P2:4, P3:19/4 | P2 (OK) | 8/8 (0) | 5/31/6 (-1/6) | 2/11/6 (1/6) |
| 15 | P2:9/2, P3:19/4 | P2 (OK) | 8/8 (0) | 6/35/6 (1/6) | 2/13/6 (-1/6) |
| 16 | P3:19/4 | P3 (OK) | 8/8 (0) | 6/6 (0) | 3/3 (0) |
| 17 | P3:23/4 | P3 (OK) | 8/8 (0) | 6/6 (0) | 4/4 (0) |

*Table 9. Full 18-tick exact hand verification of gs_vtime on Workload 2 (18/18 match) [E]=[M]*


<!-- page 15 -->


## 13. Visualizing Static vs Dynamic Dispatch Divergence [M]+[D]

Figure 4 places all three dynamic-arrival schedules on a common 18-tick timeline, marking arrival shocks at `t = 4` (`P2`) and `t = 7` (`P3`) and highlighting the 6-tick lockout of `P1` under naive `gs_ratio`.

![Figure 4: Dynamic arrival Gantt comparison showing P1 lockout under gs_ratio vs immediate sharing under gs_entitled and gs_vtime.](diagrams/fig_ex3_dynamic_divergence.png)

*Figure 4. Dynamic arrival Gantt comparison showing P1 lockout under gs_ratio vs immediate sharing under gs_entitled and gs_vtime.*

> **Turnaround Impact of Unanchored Credit.** Notice that `gs_vtime` finishes `P1` at `t = 12` (`P1` turnaround = `12`), whereas `gs_ratio` stretches `P1`'s completion all the way to `t = 18` (`50%` turnaround penalty on the longest-running job!).


<!-- page 16 -->


## 14. Lag Trajectory Comparison: Explosion vs Tight Bound [E]+[M]

Figure 5 plots the exact rational signed lag trajectories `L_i(t) = A_i(t) - E_i(t)` from Tables 7 and 9. Under `gs_ratio`, `P1`'s lag plunges continuously across `t = 4..13` to `-29/10 = -2.90`, whereas `gs_vtime` keeps every process strictly within `[-7/10, +7/10]`.

![Figure 5: Signed GPS lag comparison across Workload 2: gs_ratio (-2.90 peak lag) vs gs_vtime (<= 0.70).](diagrams/fig_ex3_dynamic_lag_curves.png)

*Figure 5. Signed GPS lag comparison across Workload 2: gs_ratio (-2.90 peak lag) vs gs_vtime (<= 0.70).*

- **Exact Peak Witness:** At `t = 13` (end of tick `t=12..13`), `P1` has `A = 5`, `GPS = 79/10` (`L = -29/10`), while `P3` runs ahead by `+18/10` (`+1.80`).
- **Why `gs_vtime` never breaches 1.0:** Re-anchoring at `V(t)` enforces global monotonic progress so new entrants neither inherit debt nor free-ride.


<!-- page 17 -->


## 15. Instrument Discrepancy [D]: IEEE-754 Float vs Exact Fraction

Why does `core/gs_core.py` rely on Python's exact `fractions.Fraction` instead of standard IEEE-754 64-bit `float`? To test whether floating-point representation error is merely academic or changes real schedules, we compared `v_i += Fraction(1, w_i)` against `v_i += 1.0 / w_i` across three integer weight triples (Table 10).

| Weights | Horizon (ticks) | Diverged Ticks (%) | First Flip | Exact vs Float Choice |
|---|---|---|---|---|
| [3, 6, 9] | 180 | 62 (34.44%) | t = 18 | P1 vs P2 |
| [3, 7, 10] | 200 | 24 (12.00%) | t = 20 | P1 vs P2 |
| [6, 10, 15] | 310 | 57 (18.39%) | t = 13 | P2 vs P3 |

*Table 10. Schedule divergence caused solely by IEEE-754 binary float rounding vs exact Fractions [D]*

> **Root Mechanism of Silent Tie Inversion [D].** On `weights = [3, 6, 9]` (`work = [30, 60, 90]`), first divergence hits at tick `t = 18`: exact Fractions tie (`['4/3', '1', '1']`) and select `P1` by index, whereas IEEE-754 floats (`['1', '1.1666666666666665', '1.0000000000000002']`) invert the comparison by `1e-16` and pick `P2`!


<!-- page 18 -->


## 16. Visualizing Cascading Dispatch Drift From 1e-16 Error [D]

Figure 6 exposes the magnitude of binary rounding drift: on weights `[3, 6, 9]`, over `34.4%` (`62/180`) of all dispatch ticks flip silently relative to the exact algebraic schedule!

![Figure 6: Percentage of diverged ticks across weight sets (left) and first 60-tick trace for w=[3,6,9] (right).](diagrams/fig_ex3_float_drift.png)

*Figure 6. Percentage of diverged ticks across weight sets (left) and first 60-tick trace for w=[3,6,9] (right).*

- **Why (3, 6, 9) drifts more than (3, 7, 10):** Shared common factors (`3:6:9 = 1:2:3`) trigger exact rational ties far more frequently — and every exact tie is vulnerable to a `1 ULP` rounding asymmetry!
- **Connection to GuaranteedScheduling.py:** Using `used / weight` in Python `float` combined with `0.01s` OS jiffies means real user-space controllers cannot rely on deterministic exact tie-breaking without integer/fixed-point arithmetic (`ns` or `Fraction`).


<!-- page 19 -->


## 17. Engineering Drift-Free Virtual Time (Exact & Fixed-Point)

How do production kernels avoid both rational overflow and binary floating-point drift without invoking Python `Fraction` objects on every context switch?

1. **Option 1 — Exact `Fraction` (Verification & Simulation `[E]`/`[M]`):** Zero drift, handles arbitrary rational ratios cleanly, ideal for formal checking and discrete simulators (`gs_core.py`).
2. **Option 2 — Pre-computed `LCM` Integer Multipliers (`Stride Scheduling`):** Set `stride_i = L / w_i` where `L = lcm(w_1..w_n)` (or `2^20 / w_i`). All virtual-time increments become exact integer additions with zero float error (`O(1)` latency)!
3. **Option 3 — Fixed-Point Scaled Shifts (`Linux CFS / EEVDF`):** Maintain `vruntime` in integer nanoseconds scaled via `inv_weight` precomputed shift-and-multiply tables (`NICE_0_LOAD`), eliminating FPU usage in kernel space.


<!-- page 20 -->


## 18. Reproducible Step-by-Step Hand-Checking Protocol

To audit any custom workload manually or verify an exam trace against `gs_core.py`, follow this five-step exact rational protocol:

```text
1. Compute total active weight W(t) = sum_{i in A(t)} w_i on each interval.
2. Integrate Fluid GPS E_i(t) piecewise as exact Fractions E_i(t) += w_i / W(t).
3. Record score_i(t) before tick t (used/w_i, used/E_on, or v_i anchored at V(t)).
4. Identify tied minimum candidates explicitly and apply tie rule (index/stay/max_w).
5. Assert |A_i(t) - E_i(t)| <= 1 for static q=1 and compare 100% of ticks to gs_core.
```
*Canonical 5-step hand verification checklist verified across Workloads 1 and 2*


<!-- page 21 -->


## 19. Practical Recommendations & Explicit Limitations

| Scenario / Hazard | Correct Engineering Choice | Evidence from Exercise 3 |
|---|---|---|
| Static arrival batch (`t = 0`) | Any exact GS variant (`gs_ratio`/`vtime`/`stride`) | [E]: 100% identical trace (`all_static_equiv=True`). |
| Dynamic / staggered arrivals | `gs_vtime` (`v_i <- V(t)`) or `gs_entitled` | [E]+[M]: Lag 7/10 vs gs_ratio 29/10. |
| Tied equal-weight or periodic resets | Explicit `stay` tie-breaker | [E]: Cuts switches (8 vs 11) cleanly. |
| Avoiding tie instability in code | `Fraction` or integer `LCM/w_i` stride | [D]: Eliminates 62/180 float-drift flips. |

*Table 11. Exercise 3 engineering recommendations grounded in exact algebraic proofs*


### Explicit Limitations

- Hand-worked traces assume unit-time preemption (`q = 1`) and deterministic non-sleeping CPU bursts (sleeping I/O processes are examined in Exercise 7).
- IEEE-754 drift depends on exact binary representations of `1/w_i`; power-of-two weights (`w = 1, 2, 4, 8`) avoid float drift cleanly, whereas non-powers-of-two (`3, 6, 9`) expose it immediately.


<!-- page 22 -->


## 20. Summary of Verified Findings & Exercise 4 Preview

- **100% Static Hand Verification (`[E]`=`[M]`):** All `12` ticks of Workload 1 match identically across `index`, `stay`, and `max_weight` tie-breakers, confirming `all_static_equiv = True`.
- **100% Dynamic Hand Verification (`[E]`=`[M]`):** All `18` ticks of Workload 2 match independently across `gs_ratio`, `gs_entitled`, and `gs_vtime`.
- **Quantified Dynamic Divergence (`[D]`):** Unanchored `gs_ratio` inflates max lag to `2.9000` (`29/10`) and locks out `P1` for `6` ticks, vs `0.7000` (`7/10`) for `gs_vtime`.
- **IEEE-754 Drift Exposure (`[D]`):** Naive floating-point `1.0 / w_i` accumulation flips `62/180` (`34.44%`) of dispatch choices on `w = [3, 6, 9]` starting at `t = 18`.
- **Next — Exercise 4:** Formal mathematical correctness proofs, Parekh–Gallager lag theorems, exhaustive state-space real-time feasibility, and overload fairness invariants.
