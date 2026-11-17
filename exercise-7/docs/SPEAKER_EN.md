# Speaker Script (English)

## Slide 1. Exercise 7 Capstone: From 106-Line Script to Hardened EEVDF Class

- Unified 7-exercise pipeline: formal bounds [E], 240-seed sweeps [M], O(log N) heap, live Linux [D].
- Dynamic lag dropped from 3.36 -> 0.908; sleeper burst 79 -> 1.
- Heap speedup reaches 113.1x at N=2,000 with 1.80% live OS error.

**Speaker notes:** Our seven exercises unify theory, simulation, optimization, and OS validation into one verified framework.

*Figure: `fig_ex7_research_arc.png`*

## Slide 2. Unified Six-Regime Scorecard & Production Decision Tree

- Hard feasible real-time deadlines (U <= 1.0): select EDF (100% optimal across 10/10 sets).
- Transient overload (U > 1.0): gs_vtime avoids RM starvation (0.923 vs 0.197 min share).
- General proportional sharing with dynamic/sleeper tasks: deploy gs_capped:stay heap.

**Speaker notes:** No single policy wins every regime blindly; use EDF inside U <= 1.0 and gs_capped:stay everywhere else.

*Figure: `fig_ex7_selector_decision_tree.png`*

## Slide 3. Live Linux Capstone Accuracy: 1.80% Max Error

- Weights [1, 2, 4] achieved [14.6%, 30.1%, 55.3%] vs ideal [14.3%, 28.6%, 57.1%].
- 6.6x lower real-Linux error compared to legacy unanchored dt=0.10s controller.
- Pareto frontier proves gs_capped:stay hits both low lag and zero sleeper lockout.

**Speaker notes:** Real Linux execution matches our mathematical model within 1.80% share accuracy.

*Figure: `fig_ex7_live_os_capstone.png`*

## Slide 4. Future Roadmap: Kernel EEVDF & Multi-Core SMP

- Phase 2 (EEVDF): add virtual eligibility ve_i <= V(t) + virtual deadlines vd_i = ve_i + L_i/w_i.
- Phase 3 (SMP & sched_ext): per-CPU lockless min-heaps + work stealing + BPF hook.
- Complete 7-exercise repository audited, tested (54/54 pytest), and bilingual.

**Speaker notes:** Future engineering extends our uniprocessor heap to full EEVDF virtual deadlines and multi-core Linux sched_ext.

*Figure: `fig_ex7_eevdf_smp_roadmap.png`*
