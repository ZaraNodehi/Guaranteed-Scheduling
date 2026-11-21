"""Exercise 7 English monograph: Dining Philosophers, GS and resource safety."""
from __future__ import annotations
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__))
TOOLS=os.path.dirname(HERE)
ROOT=os.path.dirname(TOOLS)
sys.path.insert(0,TOOLS);sys.path.insert(0,HERE)
import report_kit as rk
import ex7_data as ed

def build():
    d=ed.load();m=d["fifo_model"];s=d["thread_stress"]
    eq=d["gs_cpu_study"]["equal_weight"];wt=d["gs_cpu_study"]["weighted"]
    fig=os.path.join(ROOT,"exercise-7","diagrams")
    rep=rk.Report(
      title="Exercise 7: Dining Philosophers — Guaranteed Scheduling and Deadlock-Free Resource Allocation",
      subtitle="An independent systems-engineering study of CPU fairness, circular wait, FIFO monitors, atomic fork-pair reservation, bounded state exploration and real-thread verification",
      lang="en",rtl=False,
      cover_meta=[
        ("Repository","ZaraNodehi/Guaranteed-Scheduling"),
        ("Exercise","Exercise 7 — Dining Philosophers"),
        ("Core question","Can Guaranteed Scheduling solve Dining Philosophers? How should CPU fairness be combined with resource synchronization?"),
        ("Implementation","FIFO monitor with atomic reservation of both adjacent forks"),
        ("Verification","Finite-state explorer + five real worker threads + exact-rational GS CPU-share experiment"),
      ])
    rep.page(rk.cover(rep.cover_meta));rep.page(rk.toc())
    blocks=[
      rk.ptitle("1. Executive Summary and Direct Answer to the Instructor"),
      rk.para("The Dining Philosophers problem is a concurrency-control problem in which five philosophers share five forks arranged in a ring. Each philosopher needs both adjacent forks to eat. A naive protocol can deadlock when every philosopher holds one fork and waits for the next. The final instructor question asks whether the logic of Guaranteed Scheduling can be applied to this problem, and how. The answer requires distinguishing two independent layers: CPU scheduling and resource allocation."),
      rk.para("Guaranteed Scheduling (GS) can distribute processor service fairly among philosophers that are runnable. It cannot create an available fork, revoke a fork owner safely, or remove a circular wait. Therefore GS alone is not a deadlock solution. This exercise composes the exact-rational GS scheduler with a separate FIFO monitor that grants both adjacent forks atomically."),
      rk.kv([
        ("Naive protocol",f"Five-node circular wait witness: {' → '.join('P'+str(x) for x in d['naive_deadlock_witness']['wait_for_cycle'])}"),
        ("FIFO finite-state model",f"{m['reachable_states']} reachable states; {m['unsafe_states']} unsafe states; {m['deadlock_states']} nonterminal deadlock states; {m['terminal_states']} terminal completions"),
        ("Real-thread stress",f"{s['completed_meals']} of {s['philosophers']*s['rounds_per_philosopher']} meals completed; {s['safety_violations']} adjacent-eating violations"),
        ("CPU share experiment",f"Equal-weight GS Jain index {eq['jain_fairness']:.4f}; weighted GS Jain index {wt['jain_fairness']:.4f}"),
      ]),
      rk.image("fig_ex7_table_topology.png",width_cm=14.5,caption="Five philosophers and five shared forks in the ring topology."),
      rk.ptitle("2. Problem Definition, State and Formal Safety Properties"),
      rk.para("Let N=5. Philosopher P_i is adjacent to forks F_i and F_(i+1 mod N). A philosopher alternates between thinking, hungry/waiting and eating. The resource state contains the owner of every fork, the set of eating philosophers and a queue of hungry philosophers. A correct protocol must prevent a fork from having two owners and must prevent adjacent philosophers from eating simultaneously."),
      rk.table(["Symbol","Meaning","Exercise 7 value"],[
        ["N","Number of philosophers and forks","5"],
        ["F_i","Fork between P_i and P_(i-1 mod N)","IDs 0..4"],
        ["Need(P_i)","Two forks needed for meal","{F_i,F_(i+1 mod N)}"],
        ["State","Owners, wait queue, eating set","Protected by one monitor condition"],
        ["Admission","Order in which hungry philosophers request forks","Monotonic FIFO ticket"],
      ],widths=[2.0,7.3,6.0],caption="Formal vocabulary and state variables used in the model."),
      rk.image("fig_ex7_wait_for_cycle.png",width_cm=14.5,caption="Naive left-then-right allocation can form a five-node wait-for cycle."),
      rk.ptitle("3. Why Processor Fairness Does Not Solve a Resource Deadlock"),
      rk.para("Assume every philosopher has equal CPU weight and GS rotates the processor fairly. If each philosopher has acquired its left fork and blocks waiting for the right fork, every thread is waiting on a resource. The scheduler may be perfectly fair among runnable work, yet the resource state remains unchanged. CPU entitlement does not imply resource ownership, and a wait-for cycle is not broken by dispatching the blocked participants again."),
      rk.para("This separation is central to the proof. CPU fairness is a property of the scheduler's service trace. Mutual exclusion and deadlock freedom are properties of the resource-allocation protocol. A correct system needs both; neither property implies the other."),
      rk.table(["Layer","Question","Mechanism","What it cannot guarantee alone"],[
        ["CPU scheduling","Who receives the next CPU tick?","GS virtual-time / weighted scheduling","Fork availability or deadlock freedom"],
        ["Resource allocation","Who owns the two forks?","FIFO monitor / atomic pair grant","CPU entitlement among runnable threads"],
        ["Composition","Can work progress end to end?","GS + monitor + finite critical sections","Liveness if a meal or thread never finishes"],
      ],widths=[2.4,4.1,4.8,4.2],caption="Separation of responsibilities across scheduling and synchronization."),
      rk.image("fig_ex7_gs_service_shares.png",width_cm=14.5,caption="Exact-rational GS experiment: CPU service follows equal and weighted philosopher entitlements."),
      rk.ptitle("4. Naive Protocol and Circular-Wait Proof"),
      rk.para("The naive algorithm is: each philosopher picks up the left fork, then waits for the right fork. A reachable state exists in which P_i owns F_i for every i. Since P_i's right fork F_(i+1) is owned by P_(i+1), all five philosophers wait. The wait-for graph has edges P_i → P_(i+1) and therefore contains the cycle P0→P1→P2→P3→P4→P0."),
      rk.bullets([
        "Mutual exclusion: each individual fork has at most one owner.",
        "Hold-and-wait: each philosopher holds one fork while waiting for another.",
        "No preemption: forks are not forcibly taken from an eating philosopher.",
        "Circular wait: the five ownership dependencies form a cycle.",
      ]),
      rk.para("The four Coffman conditions explain why the naive design can deadlock. The key correction in this exercise is not to adjust CPU weights; it is to remove partial ownership and circular acquisition."),
      rk.ptitle("5. Proposed Solution: FIFO Monitor with Atomic Pair Reservation"),
      rk.para("The FairDiningTable monitor protects fork ownership, a FIFO queue of (ticket, philosopher), and the set of eating philosophers with one condition lock. A hungry philosopher obtains a monotonically increasing ticket. It waits until its request is the queue head and both adjacent forks are free. At that point the monitor removes the request from the queue and changes both fork-owner fields inside one critical section. It never grants only one fork."),
      rk.bullets([
        "Request: add (ticket, philosopher) to the tail of the FIFO queue.",
        "Wait: use a condition loop that checks queue-head identity and availability of both forks.",
        "Grant: reserve both adjacent forks atomically, mark the philosopher as eating, and record the ticket.",
        "Release: clear both owners together, remove the philosopher from the eating set and notify waiters.",
      ]),
      rk.image("fig_ex7_fifo_monitor.png",width_cm=14.5,caption="The monitor grants a pair of forks atomically to the FIFO head."),
      rk.code(ed.code_slice("exercise-7/code/dining_philosophers.py",35,135),caption="Source excerpt: condition-protected FIFO monitor and atomic fork-pair reservation."),
      rk.ptitle("6. Invariants, Deadlock Freedom and Conditional Liveness"),
      rk.table(["Invariant","Statement","Enforcement / evidence"],[
        ["I1 — ownership","Each fork has at most one owner.","Single monitor lock guards owner fields."],
        ["I2 — pair ownership","An eating philosopher owns both adjacent forks.","Atomic pair assignment and runtime assertion."],
        ["I3 — neighbor safety","No adjacent philosophers eat simultaneously.","Forks are shared only by adjacent pairs."],
        ["I4 — no partial hold","A waiting philosopher owns no fork.","Wait occurs before either owner field is set."],
        ["I5 — FIFO order","Grant tickets are increasing.","Only the queue head may acquire."],
      ],widths=[2.5,6.2,6.7],caption="Safety invariants and their implementation-level checks."),
      rk.image("fig_ex7_invariants.png",width_cm=14.5,caption="Checklist of the resource-safety and FIFO invariants."),
      rk.para("Deadlock freedom follows from eliminating hold-and-wait: a philosopher either owns both forks or owns none. Since the monitor serializes both assignments, no cycle can be formed from partial fork ownership. FIFO reduces starvation by preventing later requests from bypassing an older request repeatedly. Liveness is conditional: every granted meal must eventually finish, threads must eventually receive CPU service, and waiters must eventually be notified. FIFO can also cause head-of-line waiting, sacrificing some parallelism for a simpler fairness argument."),
      rk.ptitle("7. Alternative: Global Resource Hierarchy"),
      rk.para("An alternative deadlock-prevention method is to number forks globally and require every philosopher to acquire the lower-numbered fork before the higher-numbered fork. Strictly increasing resource order prevents a circular acquisition chain. It removes circular wait without a global admission queue. However, resource ordering alone does not promise FIFO access or bounded waiting; fairness must be analyzed separately. Exercise 7 implements the ordering helper and documents the distinction."),
      rk.table(["Approach","Deadlock prevention","Fairness property","Trade-off"],[
        ["Left then right","No","None guaranteed","Circular wait is reachable."],
        ["Global fork order","Yes, by acyclic order","Not necessarily FIFO","Simple proof; waiting order can vary."],
        ["FIFO atomic monitor","Yes, no partial hold","FIFO request order","Possible head-of-line blocking."],
      ],widths=[3.2,3.2,4.0,5.0],caption="Three resource-acquisition policies and their guarantees."),
      rk.ptitle("8. Experimental Method and Independent Verification"),
      rk.para("The experiment uses two independent forms of evidence. The finite-state explorer enumerates request, grant-to-FIFO-head and finish-meal transitions for a fixed five-philosopher model. It audits every reached state for adjacent eaters, nonterminal states with no enabled transition and terminal completion. A separate stress test launches five actual Python worker threads; each performs four meals and the test records completed meals, neighbor overlap, worker exceptions, thread liveness, final owners and FIFO ticket order."),
      rk.image("fig_ex7_verification.png",width_cm=14.5,caption="Finite-state and real-thread verification evidence."),
      rk.table(["Metric","Observed value","Interpretation"],[
        ["Reachable model states",str(m["reachable_states"]),"Distinct bounded states visited."],
        ["Model transitions",str(m["transitions"]),"Request, grant and finish edges explored."],
        ["Unsafe states",str(m["unsafe_states"]),"Must be zero."],
        ["Nonterminal deadlock states",str(m["deadlock_states"]),"Must be zero."],
        ["Terminal completed states",str(m["terminal_states"]),"At least one full completion state exists."],
        ["Real meals completed",str(s["completed_meals"]),f"Target {s['philosophers']*s['rounds_per_philosopher']}."],
        ["Real safety violations",str(s["safety_violations"]),"Must be zero."],
      ],widths=[4.4,3.4,7.6],caption="Actual metrics loaded from the current experiment output."),
      rk.ptitle("9. Guaranteed Scheduling CPU-Share Experiment"),
      rk.para("The scheduler experiment is intentionally separate from the fork experiment. Five CPU-bound philosopher tasks are simulated for a 100-tick horizon under exact-rational gs_vtime. With equal weights the service counts are equal; with weights 1:1:2:2:4 the CPU service follows those weights. Jain's index is computed on service-to-entitlement ratios; it does not measure fork fairness, meal completion or deadlock freedom."),
      rk.table(["Philosopher","Equal weight","Equal CPU ticks","Weighted share weight","Weighted CPU ticks"],[
        [f"P{i}", "1", str(eq["per_proc"][f"P{i}"]["used"]), str((1,1,2,2,4)[i]), str(wt["per_proc"][f"P{i}"]["used"])] for i in range(5)
      ],widths=[2.8,3.0,3.3,3.5,3.5],caption="Exact-rational GS CPU allocation; all philosophers remain CPU-runnable in this separate experiment."),
      rk.image("fig_ex7_fairness_metrics.png",width_cm=12.5,caption="Jain proportional-fairness index for equal and weighted CPU entitlement."),
      rk.ptitle("10. Result Interpretation, Limitations and Final Answer"),
      rk.para("The results support a layered conclusion. GS fairly allocates CPU service to runnable philosophers. The FIFO monitor provides fork ownership, exclusion and a deadlock-free acquisition structure in the bounded model. The threaded test checks the implementation under actual concurrency. The model is a fixed ring and the stress test is finite; neither proves liveness under a scheduler that never runs waiters or a philosopher that never releases its forks."),
      rk.image("fig_ex7_summary.png",width_cm=14.5,caption="Exercise 7 verification summary."),
      rk.para("Direct answer to the instructor: the algorithm's fairness logic can be applied to the CPU scheduling of philosopher threads, but the Dining Philosophers problem cannot be solved by CPU scheduling alone. It must be combined with an explicit deadlock-free synchronization protocol. In this submission that protocol is a FIFO monitor granting both forks atomically; a global resource hierarchy is an alternative."),
      rk.ptitle("References and Further Reading"),
      rk.bullets([
        "E. W. Dijkstra, Hierarchical Ordering of Sequential Processes, Acta Informatica, 1971.",
        "C. A. R. Hoare, Monitors: An Operating System Structuring Concept, Communications of the ACM, 1974.",
        "C. L. Liu and J. W. Layland, Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment, Journal of the ACM, 1973.",
        "A. Silberschatz, P. B. Galvin and G. Gagne, Operating System Concepts, synchronization and deadlock chapters.",
      ]),
    ]
    rep.pack_flow(blocks,figures_dir=fig,max_fill=0.86)
    return rep
