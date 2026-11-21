# Guaranteed Scheduling and Dining Philosophers: Why CPU Fairness Is Not Enough

## Abstract
Guaranteed Scheduling (GS) distributes processor service among runnable tasks according to an entitlement model. The Dining Philosophers problem concerns the safe acquisition of shared resources. These questions interact but have different correctness conditions. This article explains why equal or weighted CPU shares cannot break a circular wait over forks, and presents a layered design combining exact-rational GS with a FIFO monitor. The monitor grants both adjacent forks atomically, so no philosopher holds one fork while waiting for another. The implementation is checked by a bounded state-space explorer and a five-thread stress test. A global resource hierarchy is also discussed, together with the assumptions required for liveness.

**Keywords:** Guaranteed Scheduling, Dining Philosophers, virtual time, mutual exclusion, deadlock, monitor, FIFO fairness, resource hierarchy.

## 1. Introduction
The Dining Philosophers problem is a compact model of resource contention. Philosophers alternate between thinking and eating. A single fork lies between each neighboring pair, and a philosopher needs both adjacent forks to eat. The ring structure makes it possible for every philosopher to hold one fork while waiting for the other. This state is a deadlock: no participant can make progress and no fork is released.

Guaranteed Scheduling addresses a different resource: processor time. It aims to provide a task with a predictable share of CPU service based on its weight or entitlement. Exact virtual-time accounting helps the scheduler compare service histories without floating-point drift. Yet CPU time and fork ownership are not interchangeable. A thread may receive a fair share of CPU over time and still be unable to make progress because a required resource is unavailable.

The question “Can Guaranteed Scheduling solve Dining Philosophers?” therefore needs a precise answer. GS can contribute to fair CPU allocation among runnable philosophers. It does not, by itself, guarantee that forks are allocated safely or that circular wait is impossible. The system must compose a scheduler with a resource protocol.

## 2. Model and correctness properties
Let there be N philosophers P0…P(N−1) and N forks F0…F(N−1) arranged in a ring. Philosopher Pi needs forks Fi and F(i+1 mod N). Each philosopher cycles through thinking, hungry/waiting, and eating.

Three distinct properties matter:
1. **CPU fairness:** when philosophers are runnable, the scheduler distributes processor service according to its policy.
2. **Resource safety:** each fork has at most one owner and two neighboring philosophers never eat simultaneously.
3. **Resource liveness:** the protocol avoids deadlock and, under explicit assumptions, prevents starvation.

CPU fairness is a property of the scheduling trace. Resource safety and liveness are properties of the lock/resource-allocation protocol. A successful implementation must not infer one from another.

## 3. Why a fair CPU scheduler cannot break circular wait
In the naive left-then-right protocol, each philosopher first takes the fork on the left and then waits for the fork on the right. A reachable state exists in which Pi owns Fi for all i. Philosopher Pi waits for F(i+1), which is owned by P(i+1). The wait-for graph is P0 → P1 → P2 → P3 → P4 → P0. Every fork is owned, every philosopher is waiting, and no participant can release a fork because release occurs after eating.

Now suppose all philosophers have equal weights under GS. The scheduler can rotate CPU service perfectly among runnable threads. It still cannot make a held fork free, revoke the fork owner safely, or remove the dependency cycle. Blocked philosophers are not eligible for ordinary CPU service until the resource becomes available. Increasing their CPU entitlement does not change the resource state.

This is why “fair scheduling” and “fair resource allocation” must be treated separately. Scheduling fairness can reduce unfair CPU waiting after a thread becomes runnable. It cannot by itself guarantee access to a shared lock or resource.

## 4. Layered design: GS plus a FIFO monitor
The implementation in exercise-7/code/dining_philosophers.py uses a monitor that protects fork ownership, the eating set, and a FIFO queue of (ticket, philosopher) requests. A philosopher receives a monotonically increasing ticket when it becomes hungry.

The monitor grants a request only when it is at the head of the FIFO queue and both adjacent forks are free. It then assigns both fork owners in one condition-protected critical section. It never gives one fork and leaves the philosopher waiting for the second.

This removes hold-and-wait: a waiting philosopher owns no fork. Because all fork ownership changes are serialized by one monitor and partial allocation is never exposed, circular wait cannot be formed from the monitor's fork grants. FIFO admission also prevents later arrivals from repeatedly overtaking an older request.

An alternative is a global resource hierarchy: number the forks and require every philosopher to acquire the lower-numbered fork before the higher-numbered fork. A strict global order prevents a cycle in resource acquisition. Resource ordering is effective for deadlock prevention, but it does not itself guarantee FIFO service or bounded waiting. The monitor is used here because it makes request order explicit.

## 5. Invariants and proof sketch
The FIFO monitor is designed to maintain these invariants:
- **Unique ownership:** each fork has at most one owner.
- **Pair ownership:** if philosopher Pi is eating, both Fi and F(i+1 mod N) are owned by Pi.
- **Neighbor exclusion:** no two adjacent philosophers eat simultaneously.
- **No partial hold:** a philosopher waiting for admission owns no fork.
- **Monotonic admission:** tickets are granted in increasing order.

Deadlock freedom follows from the absence of hold-and-wait in the resource protocol: a philosopher either has both forks or neither. A circular chain of partial fork ownership is therefore impossible. FIFO helps with starvation resistance, but the liveness claim is conditional. Each meal must eventually finish; a thread must eventually receive CPU time; and a waiting condition must eventually be notified and re-evaluated. No synchronization algorithm can promise progress if a thread holding both forks stops forever.

## 6. Verification strategy
The repository includes two complementary forms of verification.

### 6.1 Bounded state-space exploration
The model checker explores a fixed ring of five philosophers. A state records the FIFO waiting queue, the eating bitmask, and the completed bitmask. The transitions are request, grant to the FIFO head, and finish meal. Every reachable state is checked for adjacent eaters. Nonterminal states with no enabled successor are recorded as deadlocks. Terminal states show that all philosophers can complete their bounded meal.

This is exhaustive for the stated finite abstraction. It is not an unbounded proof for arbitrary philosopher counts, arbitrary resource graphs, or unfair runtime scheduling.

### 6.2 Real-thread stress test
A separate test creates five Python worker threads. Each philosopher performs four meals. The test records completion counts, overlap violations, worker errors, live threads, final fork owners, and FIFO ticket order. The target is 20 completed meals, zero adjacent-eating violations, no outstanding fork owners, and no remaining waiting requests.

The state-space model removes timing noise and explores all states in its bounded model. The threaded test exercises the actual monitor under concurrent execution, but it is empirical and finite. The two methods complement each other.

## 7. Separating the CPU-share experiment from fork allocation
Exercise 7 also runs five CPU-bound philosopher tasks through the repository's exact-rational gs_vtime simulator. In the equal-weight experiment each philosopher has weight 1. In the weighted experiment the weights are 1:1:2:2:4. The measured service follows the entitlement weights over a 100-tick horizon.

This experiment is deliberately separate from the fork monitor. Jain's fairness index in this study is computed from CPU service relative to CPU entitlement. It is not a measure of fair fork access, starvation-free meals, or deadlock freedom. Keeping these metrics separate prevents a common conceptual error: treating a high CPU fairness score as evidence that a resource protocol is correct.

## 8. Limitations and engineering implications
FIFO admission can cause head-of-line waiting. A philosopher at the queue head may wait for its two forks even when a later non-neighbor request could proceed. This can reduce concurrency, although it simplifies the fairness argument. A more advanced allocator may allow compatible later requests to proceed while bounding bypass; that policy would need its own proof and tests.

The model assumes a fixed ring and two forks per meal. Real systems may have nested locks, dynamic resource sets, cancellation, timeouts, process failure, and priority inversion. Priority inheritance can address some priority-inversion scenarios when a high-priority thread blocks behind a low-priority lock holder. It does not replace deadlock prevention.

## 9. Conclusion
Guaranteed Scheduling and Dining Philosophers address different layers of concurrency. GS can distribute CPU service fairly among runnable philosopher threads. A monitor or resource allocator must still ensure exclusive fork ownership and prevent circular wait. The solution in this repository combines exact-rational CPU scheduling with a FIFO monitor that atomically reserves both forks, then checks the bounded model and the real-thread implementation independently.

The direct answer is: **the logic of Guaranteed Scheduling applies to CPU allocation among runnable philosophers, but GS alone does not solve Dining Philosophers. A deadlock-free resource protocol—such as the FIFO atomic-pair monitor or a global resource hierarchy—must be composed with it.**

## References
1. E. W. Dijkstra, “Hierarchical Ordering of Sequential Processes,” Acta Informatica, vol. 1, pp. 115–138, 1971.
2. C. A. R. Hoare, “Monitors: An Operating System Structuring Concept,” Communications of the ACM, vol. 17, no. 10, pp. 549–557, 1974.
3. C. L. Liu and J. W. Layland, “Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment,” Journal of the ACM, vol. 20, no. 1, pp. 46–61, 1973.
4. A. Silberschatz, P. B. Galvin, and G. Gagne, Operating System Concepts, synchronization and deadlock chapters.
