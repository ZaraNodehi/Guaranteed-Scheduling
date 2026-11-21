# Speaker Script (English)

## Slide 1. Operating Systems Capstone: From Guaranteed Scheduling to Fair Readers–Writers

- End-to-end synthesis of Exercises 1–6 across CPU scheduling, real-time deadlines, mutual exclusion & RW concurrency.
- Unified experimental methodology: exact discrete-tick simulators, formal BFS model checkers & live POSIX-style multithreading.
- Every number, diagram, and failure trace verified programmatically from reproducible workspace benchmarks.

**Speaker notes:** Welcome to the Operating Systems Capstone presentation. Across Exercises 1 through 6, we connected two pillars of kernel design: fair and real-time CPU scheduling on one hand, and race-free, starvation-free synchronization on the other.

*Figure: `ex6_fig6_end_to_end_architecture.png`*

## Slide 2. Exercises 1–2: Guaranteed Scheduling (GS) & Exact Rational Fairness

- Classic 1/N Guaranteed Scheduling keeps process ratios tightly around 1.000 using exact rational vtime tracking.
- Weighted GS allocates CPU strictly proportional to weights w_i while preventing sleeper starvation/credit explosions.
- Wakeup caps prevent sleeping I/O threads from stockpiling infinite deficit and starving CPU-bound peers.

**Speaker notes:** In Exercises 1 and 2, we built an exact rational-arithmetic Guaranteed Scheduling simulator. Unlike floating-point accumulators that drift over millions of ticks, exact fractions preserve perfect proportional fairness and bound sleeper wakeups.

*Figure: `ex6_fig4_hybrid_gs_rt.png`*

## Slide 3. Exercise 3: Hard Real-Time Boundaries (RM, EDF & Liu-Layland U=0.78)

- On Set B (U = 0.958 > LL(3)=0.78), RM failed 1 deadline whereas EDF and GS hit 0 misses.
- EDF achieves 100% schedulable utilization bound for independent periodic tasks while minimizing context switches.
- Under overload (Set C, U = 1.167), EDF suffers a domino miss cascade unless admission control or GS budgets intervene.

**Speaker notes:** Exercise 3 audited Rate Monotonic versus Earliest Deadline First across feasible, RM-breaking, and overloaded task sets. Above the 0.78 Liu-Layland bound, RM dropped deadlines exactly as Response Time Analysis predicted, while EDF stayed completely miss-free until U exceeded 1.0.

*Figure: `ex6_fig4_hybrid_gs_rt.png`*

## Slide 4. Exercise 4: Mutual Exclusion — Hardware Spin vs. OS Blocking & BFS Verification

- Exhaustive BFS over 10 models proved Dekker v1–v4 & TSO Peterson fail; Dekker v5 (134 states) & SC Peterson (42 states) pass.
- Mesa Monitors require 'while (cond)' rechecks: using 'if' left 6 buffer-underflow states in BFS!
- Lock-holder 10 ms sleep burned 97.8% CPU spinning on Peterson/Dekker vs. 1.0% CPU on Semaphore/Monitor.

**Speaker notes:** Exercise 4 formally model-checked ten synchronization state machines. We reproduced exact counterexample traces for Dekker bugs v2-v4, TSO store-buffer reordering in Peterson, and Mesa 'if' spurious wakeups, alongside live 98% vs 1% CPU burn benchmarks.

*Figure: `ex6_fig5_capstone_radar.png`*

## Slide 5. Exercise 5: Readers–Writers — 4.03x Speedup & Defeating Semaphore Barging

- All 12 variants (4 primitives x 3 policies) safely admitted 4 simultaneous readers with zero read/write overlap.
- At 95% reads (0.3 ms scan), RW locks outperformed CoarseMutex by up to 4.03x (9,637 vs. 2,390 ops/s).
- Under Writer-Flood, Monitor Ticket & Spin Deque protected readers (12 ops) while Semaphore suffered turnstile barging (0 ops).

**Speaker notes:** Exercise 5 built all 12 combinations of Readers-Writers across Semaphore, Monitor, Peterson, and Dekker. We uncovered a classic real-world concurrency phenomenon: unfair condition-backed semaphores allow newly arriving writers to barge ahead of awakened readers, whereas explicit FIFO tickets and deques stop barging completely.

*Figure: `ex6_fig3_rw_rt_pipeline.png`*

## Slide 6. Exercise 6 (1/3): Priority Inversion & Mars Pathfinder Rescue via PIP

- Without PIP, T_Medium preempted lock-holder T_Low, blocking T_High for 9 ticks -> 1 deadline misses!
- Enabling Priority Inheritance (PIP) boosted T_Low immediately, cutting T_High block to 2 ticks -> 0 misses.
- Matches the exact 1997 NASA Mars Pathfinder anomaly resolved in flight via VxWorks mutex priority inheritance.

**Speaker notes:** Now we integrate scheduling and locking directly in Exercise 6. In our Mars Pathfinder simulation, a medium-priority CPU task preempts the low-priority lock owner, starving the high-priority control thread until its deadline breaks. Turning on Priority Inheritance lets the lock owner finish its critical section immediately and eliminates all misses.

*Figure: `ex6_fig1_priority_inversion_timeline.png`*

## Slide 7. Exercise 6 (2/3): Why Spin-Locks Break Real-Time Preemptive Schedulers

- When T_High spins on a Peterson lock held by preempted T_Low, T_High never yields -> 54 wasted spin ticks & spin deadlock!
- Unlike OS blocking locks, busy-wait hides lock dependency from the scheduler so PIP cannot boost T_Low.
- Rule: Never hold a spinlock across preemptible RT priorities without disabling preemption or using blocking PIP mutexes.

**Speaker notes:** Even worse than classic priority inversion is placing a software spinlock inside a preemptive priority scheduler. Because T_High remains runnable while spinning, the scheduler never runs T_Low again, creating a deterministic priority-spin deadlock.

*Figure: `ex6_fig2_spin_vs_pip_comparison.png`*

## Slide 8. Exercise 6 (3/3): Live Multi-Threaded RT Control + RW Telemetry Pipeline

- 5-thread live system: Fair Monitor (100.0% RT hit) & Sem Writers-Pref (100.0%) beat CoarseMutex.
- Monitor Fair kept RT P95 latency at 0.91 ms vs. higher variance under spin-polling locks.
- Choosing the wrong RW preference directly degrades high-priority read deadline compliance under continuous writer churn.

**Speaker notes:** Finally, we coupled a live 4 ms deadline real-time control thread onto our Readers-Writers telemetry table. Fair Monitor tickets balanced high total throughput with tight tail-latency bounds for the real-time observer.

*Figure: `ex6_fig3_rw_rt_pipeline.png`*

## Slide 9. Unified Operating System Design Matrix (Exercises 1–6)

- Interactive/Batch Fairness -> Rational Guaranteed Scheduling (Ex 1–2) with wakeup cap.
- Periodic Hard Real-Time -> EDF + Priority Inheritance / Stack Resource Policy (Ex 3 + Ex 6).
- General Mutex / Producer-Consumer -> Blocking Mesa Monitor with 'while' predicates (Ex 4).
- Read-Dominated Shared State -> Fair Ticket Monitor RW or Linux RCU for 99%+ reads (Ex 5–6).

**Speaker notes:** This unified matrix summarizes six exercises into four concrete architectural prescriptions for production OS and embedded engineers.

*Figure: `ex6_fig5_capstone_radar.png`*

## Slide 10. Conclusions, Reproducibility & Artifact Inventory

- 100% reproducible codebase: exact Python simulators, formal BFS checkers, Okabe-Ito diagrams & automated pytest suites.
- Every finding—from TSO store-buffer bugs to semaphore barging and Mars Pathfinder PIP—verified end to end.
- Thank you for your attention. Questions & code walkthrough welcome.

**Speaker notes:** Thank you. All source code, JSON experiment logs, bilingual DOCX/PDF monographs, PPTX slide decks, and automated pytest verification suites are organized cleanly inside exercises 1 through 6.

*Figure: `ex6_fig6_end_to_end_architecture.png`*

## Slide 11. Dining Philosophers: CPU Fairness Is Not Resource Safety

- Equal GS CPU shares do not break the circular wait when every philosopher holds one fork and waits for the next.
- A FIFO monitor grants both adjacent forks atomically; no philosopher holds one fork while waiting for another.
- Finite-state exploration + five real worker threads audit zero adjacent eating, zero deadlock states and 20/20 completed meals.

**Speaker notes:** This slide answers the final instructor question directly. Guaranteed Scheduling allocates CPU among runnable threads, but it is not a fork-allocation protocol. The repository therefore combines GS with a FIFO monitor that reserves both forks atomically. The finite-state model checks safety and progress in the bounded model; the threaded stress test checks the implementation under real concurrency. The liveness claim assumes each meal finishes and the runtime eventually schedules waiters.

*Figure: `fig_dining_philosophers_fifo.png`*

*Source: exercise-6/code/dining_philosophers.py; exercise-6/docs/ARTICLE_EN.md; exercise-6/docs/ARTICLE_FA.md*
