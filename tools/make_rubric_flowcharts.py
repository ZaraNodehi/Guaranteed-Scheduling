"""Generate explicit, printable flowcharts for Exercises 2–6."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
FLOWS={
"exercise-2":{
"title":"Guaranteed Scheduling vs. EDF / RM — Comparison Workflow",
"nodes":[
"1. Define a common workload and explicit assumptions",
"2. Run GS variants and EDF / RM / DM baselines",
"3. Record GPS lag, fairness, response and deadline misses",
"4. Audit constrained-deadline sets and sustained overload",
"5. Separate proportional fairness from deadline feasibility",
]},
"exercise-3":{
"title":"Paper Scheduling — EDF and RM Tick-by-Tick Procedure",
"nodes":[
"1. Define period T, execution C, deadline D and release times",
"2. Compute hyperperiod, utilization and absolute deadlines",
"3. Build the ready queue at the current tick",
"4. Dispatch: EDF = earliest deadline; RM = shortest period",
"5. Execute one tick, update remaining work and record misses",
"6. Cross-check the paper trace with RTA, dbf and independent code",
]},
"exercise-4":{
"title":"Mutual Exclusion — Formal and Empirical Verification Workflow",
"nodes":[
"1. Define actors, shared state and critical-section invariant",
"2. Select Dekker, Peterson, Semaphore or Mesa Monitor",
"3. Explore reachable states with breadth-first search",
"4. Check safety, deadlock, progress and bounded waiting",
"5. Audit SC / TSO assumptions and condition-variable semantics",
"6. Run live contention tests and report wall time and CPU use",
]},
"exercise-5":{
"title":"Readers–Writers — Policy, Safety and Fairness Evaluation",
"nodes":[
"1. Select Readers-, Writers- or Fair/FIFO preference policy",
"2. Select Semaphore, Monitor, Peterson or Dekker primitive",
"3. Create concurrent reader and writer workloads",
"4. Check exclusive writer access and concurrent-reader safety",
"5. Stress reader-flood and writer-flood starvation scenarios",
"6. Compare barging, waiting, throughput, CPU burn and BFS states",
]},
"exercise-6":{
"title":"Capstone — Integrating Scheduling and Synchronization",
"nodes":[
"1. Define the real-time tasks and scheduling policy",
"2. Add shared telemetry state and synchronization protocol",
"3. Compare no-PIP, priority inheritance and spin-lock behavior",
"4. Run the multi-thread RT + Readers–Writers pipeline",
"5. Record deadline misses, response latency and throughput",
"6. Compare findings and state the model's limits",
]},
"exercise-7":{
"title":"Exercise 7 — Dining Philosophers: CPU Fairness vs Resource Safety",
"nodes":[
"1. Define five philosophers, five forks and ring adjacency",
"2. Construct the naive left-then-right circular-wait witness",
"3. Run equal and weighted CPU-share experiments under exact GS",
"4. Queue hungry philosophers with monotonic FIFO tickets",
"5. Grant both adjacent forks atomically or grant neither",
"6. Check ownership, neighbor exclusion and no partial hold",
"7. Explore bounded states and stress five real worker threads",
"8. State liveness assumptions and compare resource hierarchy",
]},
}

def build_one(name, spec):
    out=ROOT/name/"diagrams"
    out.mkdir(parents=True,exist_ok=True)
    nodes=spec["nodes"]
    fig,ax=plt.subplots(figsize=(16,9),dpi=120)
    ax.set_xlim(0,16); ax.set_ylim(0,len(nodes)+1)
    ax.axis("off")
    ax.set_title(spec["title"],fontsize=17,pad=18,wrap=True)
    x=8
    for i,label in enumerate(nodes):
        y=len(nodes)-i
        ax.text(x,y,label,ha="center",va="center",fontsize=13,wrap=True,
                bbox={"boxstyle":"round,pad=0.55","alpha":0.15})
        if i<len(nodes)-1:
            ax.annotate("",xy=(x,y-0.58),xytext=(x,y-0.30),
                        arrowprops={"arrowstyle":"->","lw":1.6})
    ax.text(8,0.15,
            "Evidence chain: declared assumptions -> executable trace -> measured metrics -> bounded conclusions",
            ha="center",va="center",fontsize=10,wrap=True)
    fig.tight_layout()
    path=out/f"fig_{name.replace('-','')}_rubric_flowchart.png"
    fig.savefig(path,bbox_inches="tight")
    plt.close(fig)
    print(path.relative_to(ROOT))

def main():
    for name,spec in FLOWS.items():
        build_one(name,spec)

if __name__=="__main__":
    main()
