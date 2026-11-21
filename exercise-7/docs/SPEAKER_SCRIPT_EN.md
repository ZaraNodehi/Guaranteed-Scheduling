# Speaker Script (English)

## Slide 1. Exercise 7: Dining Philosophers and Guaranteed Scheduling

- Five concurrent philosophers share five forks in a ring.
- Each philosopher needs two adjacent forks to eat.
- The study separates CPU fairness from resource-allocation correctness.

**Speaker notes:** Introduce the classic Dining Philosophers problem. Explain that CPU scheduling decides which runnable thread executes, while synchronization decides whether the two required forks can be acquired safely.

*Figure: `fig_ex7_table_topology.png`*

## Slide 2. The Naive Protocol: A Circular Wait

- Each philosopher takes the left fork first.
- All five forks can become owned simultaneously.
- Every philosopher then waits for the right fork: no transition can release the cycle.

**Speaker notes:** Walk through the wait-for cycle P0→P1→P2→P3→P4→P0. This is a resource deadlock. Giving the philosophers more CPU time does not free a fork.

*Figure: `fig_ex7_wait_for_cycle.png`*

## Slide 3. What Guaranteed Scheduling Can and Cannot Do

- Exact virtual-time GS can distribute CPU fairly among runnable philosophers.
- A philosopher blocked on a fork is not made runnable by a larger CPU share.
- The scheduler cannot replace a resource protocol.

**Speaker notes:** Use the equal and weighted GS experiments. The scheduler is responsible for processor entitlement; the monitor is responsible for fork ownership, deadlock avoidance and admission fairness.

*Figure: `fig_ex7_gs_service_shares.png`*

## Slide 4. Solution: Atomic Pair Reservation with a FIFO Monitor

- Every hungry philosopher receives a monotonic ticket.
- Only the FIFO head may proceed, and only when both forks are free.
- Both forks are reserved in one critical section; no partial ownership is exposed.

**Speaker notes:** Describe the monitor condition loop. The guard checks queue-head identity and availability of both forks under one condition lock; then both owner fields change atomically.

*Figure: `fig_ex7_fifo_monitor.png`*

## Slide 5. Safety, Deadlock Freedom and Conditional Liveness

- One owner per fork; no neighboring philosophers eat concurrently.
- No philosopher holds one fork while waiting for a second fork.
- FIFO prevents repeated bypass; progress assumes meals finish and waiters are scheduled.

**Speaker notes:** Be precise: safety is enforced by atomic ownership, deadlock is prevented by removing hold-and-wait, and starvation resistance follows FIFO under scheduler and finite-meal assumptions.

*Figure: `fig_ex7_invariants.png`*

## Slide 6. Independent Verification: State Exploration and Real Threads

- Naive witness exposes the five-node circular wait.
- A finite-state explorer checks reachable states and terminal completion.
- Five OS threads execute four meals each; the test audits 20 completions and zero adjacent overlap.

**Speaker notes:** Distinguish exhaustive exploration of a bounded abstraction from empirical stress testing of the Python monitor. Neither result should be overstated as a proof about every OS scheduler.

*Figure: `fig_ex7_verification.png`*

## Slide 7. The Correct Answer: Compose Scheduling with Synchronization

- GS provides fair CPU service to runnable philosophers.
- A FIFO monitor or resource hierarchy provides safe fork acquisition.
- The correct design composes and verifies both layers independently.

**Speaker notes:** Answer the instructor's question directly: the logic of a fair scheduler applies to CPU allocation, but not as a standalone deadlock solution. Dining Philosophers requires a separate synchronization policy.

*Figure: `fig_ex7_summary.png`*
