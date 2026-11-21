# CPU Fairness Is Not Resource Safety: Guaranteed Scheduling and Dining Philosophers

## Abstract
Guaranteed Scheduling (GS) asks how a processor should distribute service among runnable tasks so each receives its contractual share over time. Dining Philosophers asks how concurrent agents acquire shared resources without conflicting ownership, deadlock, or starvation. These questions interact, but are not interchangeable. This article distinguishes CPU fairness from resource safety, connects exact virtual-time scheduling to monitor-based resource arbitration, and specifies a FIFO monitor that atomically grants both forks. A finite-state exploration and a real-thread stress test provide complementary evidence. The central result is qualified: GS can make runnable philosophers receive fair CPU service, but only a correct resource protocol can make fork allocation safe and live.

**Keywords:** Guaranteed Scheduling, virtual time, Dining Philosophers, mutual exclusion, deadlock, FIFO monitor, starvation.

## 1. Two different fairness problems
A CPU scheduler selects one runnable task at a time. In a weighted fair model, task i has weight w_i and target share w_i/sum(w). Exact virtual-time accounting tracks received service relative to entitlement without floating-point drift. A wake-up policy must also prevent a sleeping task from accumulating unlimited credit and monopolizing the processor when it returns.

Dining Philosophers has N philosophers and N forks, one between each neighboring pair. Philosopher i needs forks i and (i+1) mod N. If everyone takes the left fork and waits for the right, all forks can be held while every philosopher waits for a neighbor. The wait-for graph contains a cycle. More CPU time cannot break that cycle: the obstacle is resource ownership, not processor entitlement.

Three properties must be separated:
- **CPU fairness:** runnable tasks receive processor service according to their weights or declared policy.
- **Resource safety:** neighboring philosophers never eat simultaneously while sharing a fork.
- **Resource liveness:** the protocol avoids deadlock and, under stated assumptions, prevents starvation.

## 2. Why GS alone is insufficient
Suppose all philosophers receive equal CPU weight under GS and the scheduler rotates them perfectly. If each owns its left fork and blocks on its right fork, the state does not change. Fair CPU allocation cannot create a free fork, revoke ownership safely, or remove circular wait.

Nor can a CPU scheduler decide whether a new request may bypass an older hungry neighbor. That is an admission policy belonging in a monitor, semaphore protocol, or resource allocator.

The correct architecture is layered: (1) GS selects a runnable thread; (2) a monitor serializes fork requests; (3) both required forks are granted atomically or neither is granted; (4) FIFO admission prevents repeated bypass of older requests; and (5) both forks are released when the meal ends. The scheduler and monitor solve complementary problems.

## 3. FIFO monitor with atomic pair reservation
The reference implementation is exercise-6/code/dining_philosophers.py. It protects fork owners, a FIFO queue of (ticket, philosopher), and the set of eating philosophers with one condition lock. Each request receives a monotonically increasing ticket and waits until it is both queue head and both adjacent forks are free. The monitor then reserves both forks in one critical section.

This removes hold-and-wait: a philosopher never owns one fork while waiting for the other. It also prevents circular wait because partial allocation is never exposed. FIFO admission prevents newer requests from repeatedly overtaking the oldest. Liveness still assumes every admitted meal eventually ends, threads continue to be scheduled, and condition waiters are eventually awakened. A finite test cannot prove fairness under an unfair or permanently stalled runtime.

An alternative is a global resource hierarchy: every philosopher acquires the lower-numbered fork before the higher-numbered fork. A strict total order prevents a circular acquisition chain. The monitor is used here because it also makes FIFO admission explicit and auditable.

## 4. Invariants and verification
The implementation maintains five invariants: (1) each fork has at most one owner; (2) an eating philosopher owns both adjacent forks; (3) no adjacent philosophers eat simultaneously; (4) a waiting philosopher owns no fork; and (5) grant tickets are increasing.

Two independent checks are included. A finite-state explorer enumerates request, grant, and finish transitions for five philosophers and checks every reachable state for adjacent eaters and nonterminal deadlocks. A real-thread stress test runs five workers through repeated meals and audits overlap, completion counts, remaining owners, and ticket order.

The finite model is deterministic and independent of OS thread timing. The threaded test exercises the actual monitor under concurrency, but is empirical evidence rather than a proof for every possible runtime schedule. Together they provide stronger coverage.

## 5. What to measure
Report completed meals per philosopher; maximum simultaneous eaters (at most floor(N/2)); safety violations (zero); final fork owners and waiting queue (empty); FIFO ticket order; maximum queue length; and per-philosopher waiting time. CPU wait time and fork wait time are distinct quantities and must not be conflated.

## 6. Limitations
FIFO admission can cause head-of-line waiting: an older request may wait for a pair while a later nonconflicting request could proceed. This can reduce parallelism, although it simplifies starvation reasoning. A more advanced allocator can grant compatible requests while bounding bypass, but needs its own proof and tests.

Real systems also have dynamic resource sets, nested locks, cancellation, timeouts, and failures. Priority inheritance or priority-ceiling protocols may be needed when a high-priority task blocks behind a low-priority lock holder. Those mechanisms address priority inversion; they do not replace deadlock prevention.

## 7. Conclusion
Guaranteed Scheduling and Dining Philosophers address different concurrency layers. GS can distribute CPU time fairly among runnable philosophers. A monitor or resource allocator must still guarantee exclusive fork ownership and progress. The repository combines exact CPU entitlement at the scheduler layer, atomic fork-pair reservation at the monitor layer, and FIFO admission to reduce starvation. The exact answer to the instructor's question is: **the scheduling algorithm helps ensure fair processor access, but does not by itself solve Dining Philosophers; it must be combined with a deadlock-free synchronization protocol.**

## References
1. E. W. Dijkstra, “Hierarchical Ordering of Sequential Processes,” Acta Informatica, vol. 1, pp. 115–138, 1971.
2. C. A. R. Hoare, “Monitors: An Operating System Structuring Concept,” Communications of the ACM, vol. 17, no. 10, pp. 549–557, 1974.
3. C. L. Liu and J. W. Layland, “Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment,” Journal of the ACM, vol. 20, no. 1, pp. 46–61, 1973.
4. L. Sha, R. Rajkumar, and J. P. Lehoczky, “Priority Inheritance Protocols: An Approach to Real-Time Synchronization,” IEEE Transactions on Computers, vol. 39, no. 9, 1990.
