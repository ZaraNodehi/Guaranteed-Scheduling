# Speaker Script (English)

## Slide 1. Exercise 6: O(log N) Heap Refactor & Sleeper Defense

- Replaces O(N) list scan with lazy min-heap (113.1x faster at N=2,000).
- Uses integer fixed-point 10^9/w arithmetic to eliminate IEEE-754 drift.
- Adds V(t) arrival anchor, stay tie fast path, and gs_capped sleeper floor.

**Speaker notes:** Exercise 6 delivers four structural upgrades inside gs_optimized.py.

*Figure: `fig_ex6_refactor_architecture.png`*

## Slide 2. 113.1x Dispatch Speedup at N = 2,000 Processes

- LinearScanScheduler grows to 69.53 us/dispatch at N=2,000.
- OptimizedHeapScheduler stays near-constant at 0.615 us/dispatch.
- O(1) versioned sleep/wake cancellation avoids expensive heap removal scans.

**Speaker notes:** Wall-clock microbenchmarks confirm exact O(N) vs O(log N) scaling up to 2,000 active tasks.

*Figure: `fig_ex6_complexity_scaling.png`*

## Slide 3. Breaking 79-Tick Sleeper Monopoly Down to 1 Tick

- Even uncapped gs_vtime lets a waking sleeper hog 79 straight ticks at S=80.
- gs_capped clamps wakeup credit at V(t) - cap/w, holding burst to 1 tick!
- Mirrors Linux CFS GENTLE_FAIR_SLEEPERS anti-hoarding design.

**Speaker notes:** Ablation across 30 workloads confirms V(t) cuts lag while gs_capped eliminates wakeup lockouts.

*Figure: `fig_ex6_sleeper_mitigation.png`*

## Slide 4. 4.2x Better Real-Linux Latecomer Share Control

- Mid-run P3 spawn at t=0.6s: legacy lets P3 seize 45.3% (err 11.97%).
- Refactored controller holds [35.6%, 30.5%, 33.9%] (err 2.82%).
- Ablation V2->V3 also slashes worst mixed-workload burst 13 -> 4 ticks.

**Speaker notes:** Live psutil verification proves our V(t)+stay fix directly prevents mid-run arrival distortion on Linux.

*Figure: `fig_ex6_os_refactor_validation.png`*
