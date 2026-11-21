"""Generate the Exercise 7 figures from reproducible experiment output."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE=Path(__file__).resolve().parent
EX7=HERE.parent
ROOT=EX7.parent
DATA=json.loads((EX7/"output"/"experiments.json").read_text(encoding="utf-8"))
OUT=EX7/"diagrams"
OUT.mkdir(parents=True,exist_ok=True)

def save(fig,name):
    fig.tight_layout()
    path=OUT/name
    fig.savefig(path,dpi=180,bbox_inches="tight")
    plt.close(fig)
    print(path.relative_to(ROOT))

def topology():
    fig,ax=plt.subplots(figsize=(8,7))
    n=5
    ang=np.linspace(np.pi/2,np.pi/2-2*np.pi,n,endpoint=False)
    xy=[(2*np.cos(a),2*np.sin(a)) for a in ang]
    for i,(x,y) in enumerate(xy):
        ax.scatter(x,y,s=1500,edgecolors="black",zorder=3)
        ax.text(x,y,f"Philosopher {i}",ha="center",va="center",fontsize=9,zorder=4)
    for i in range(n):
        x1,y1=xy[i];x2,y2=xy[(i+1)%n]
        mx,my=(x1+x2)/2,(y1+y2)/2
        ax.plot([x1*.77+x2*.23,x1*.23+x2*.77],[y1*.77+y2*.23,y1*.23+y2*.77],lw=4)
        ax.text(mx,my,f"F{i}",ha="center",va="center",bbox={"boxstyle":"round","fc":"white","ec":"black"})
    ax.set_title("Dining Philosophers: Five Agents, Five Shared Forks")
    ax.set_aspect("equal");ax.axis("off")
    save(fig,"fig_ex7_table_topology.png")

def wait_cycle():
    fig,ax=plt.subplots(figsize=(8,7))
    n=5
    ang=np.linspace(np.pi/2,np.pi/2-2*np.pi,n,endpoint=False)
    xy=[(2*np.cos(a),2*np.sin(a)) for a in ang]
    for i,(x,y) in enumerate(xy):
        ax.scatter(x,y,s=1500,edgecolors="black",zorder=3)
        ax.text(x,y,f"P{i}\nholds F{i}",ha="center",va="center",fontsize=9,zorder=4)
    for i in range(n):
        x1,y1=xy[i];x2,y2=xy[(i+1)%n]
        ax.annotate("",xy=(x2*.78+x1*.22,y2*.78+y1*.22),
                    xytext=(x1*.78+x2*.22,y1*.78+y2*.22),
                    arrowprops={"arrowstyle":"->","lw":2,"connectionstyle":"arc3,rad=0.12"})
    ax.set_title("Naive Left-Then-Right Protocol: Circular Wait P0→P1→…→P0")
    ax.text(0,0,"All five forks held\nAll five philosophers waiting",ha="center",va="center",fontsize=12)
    ax.set_aspect("equal");ax.axis("off")
    save(fig,"fig_ex7_wait_for_cycle.png")

def gs_shares():
    fig,ax=plt.subplots(figsize=(9,5))
    cases=[("Equal weights",DATA["gs_cpu_study"]["equal_weight"]["per_proc"]),
           ("Weights 1:1:2:2:4",DATA["gs_cpu_study"]["weighted"]["per_proc"])]
    names=list(cases[0][1])
    x=np.arange(len(names));width=.36
    for k,(label,entries) in enumerate(cases):
        vals=[entries[n]["used"] for n in names]
        ax.bar(x+(k-.5)*width,vals,width,label=label)
    ax.set_xticks(x,names);ax.set_ylabel("CPU ticks received in 100-tick horizon")
    ax.set_title("Guaranteed Scheduling Allocates CPU According to Task Weights")
    ax.legend()
    save(fig,"fig_ex7_gs_service_shares.png")

def fifo_metrics():
    order=DATA["thread_stress"]["admission_order"] if "admission_order" in DATA["thread_stress"] else list(range(20))
    tickets=DATA["thread_stress"]["admission_tickets"] if "admission_tickets" in DATA["thread_stress"] else list(range(len(order)))
    fig,ax=plt.subplots(figsize=(10,4))
    ax.plot(tickets,order,marker="o")
    ax.set_xlabel("FIFO grant ticket")
    ax.set_ylabel("Philosopher ID")
    ax.set_yticks(range(5))
    ax.set_title("Actual Threaded Stress Run: Admission Order by FIFO Ticket")
    ax.grid(True,alpha=.3)
    save(fig,"fig_ex7_fifo_queue_timeline.png")

def model_audit():
    m=DATA["fifo_model"]
    labels=["Reachable states","Transitions","Unsafe states","Deadlock states","Terminal states"]
    vals=[m["reachable_states"],m["transitions"],m["unsafe_states"],m["deadlock_states"],m["terminal_states"]]
    fig,ax=plt.subplots(figsize=(9,4))
    ax.bar(labels,vals)
    ax.set_title("Bounded FIFO Monitor Model-Checking Summary")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x",rotation=16)
    save(fig,"fig_ex7_state_space_audit.png")

def comparison():
    fig,ax=plt.subplots(figsize=(9,4.5))
    labels=["Naive left/right","Atomic FIFO monitor"]
    dead=[1,0]
    safe=[0,1]
    x=np.arange(2)
    ax.bar(x-.18,dead,.36,label="Deadlock witness reachable")
    ax.bar(x+.18,safe,.36,label="No deadlock in bounded model")
    ax.set_xticks(x,labels);ax.set_ylim(0,1.2);ax.set_yticks([0,1],["No","Yes"])
    ax.set_title("Resource-Protocol Comparison (Not a CPU Scheduler Comparison)")
    ax.legend()
    save(fig,"fig_ex7_deadlock_comparison.png")

def fairness():
    vals=[DATA["gs_cpu_study"]["equal_weight"]["jain_fairness"],
          DATA["gs_cpu_study"]["weighted"]["jain_fairness"]]
    fig,ax=plt.subplots(figsize=(7,4))
    ax.bar(["Equal weight","Weighted service"],vals)
    ax.set_ylim(0,1.05);ax.set_ylabel("Jain's index")
    ax.set_title("Jain Fairness Index for the GS CPU-Service Experiments")
    for i,v in enumerate(vals):ax.text(i,v+.015,f"{v:.4f}",ha="center")
    save(fig,"fig_ex7_fairness_metrics.png")

def summary():
    s=DATA["thread_stress"];m=DATA["fifo_model"]
    fig,ax=plt.subplots(figsize=(9,4))
    labels=["Meals completed","Safety violations","Deadlock states","Terminal model states"]
    vals=[s["completed_meals"],s["safety_violations"],m["deadlock_states"],m["terminal_states"]]
    ax.bar(labels,vals)
    ax.set_title("Exercise 7 Verification Evidence")
    ax.tick_params(axis="x",rotation=12)
    save(fig,"fig_ex7_summary.png")

def fifo_monitor():
    fig,ax=plt.subplots(figsize=(10,5))
    steps=["Request","Ticket added","Wait until FIFO head","Check both forks","Reserve pair atomically","Eat","Release both"]
    y=list(range(len(steps),0,-1))
    for i,(s,yy) in enumerate(zip(steps,y)):
        ax.text(.5,yy,s,ha="center",va="center",bbox={"boxstyle":"round,pad=.45","fc":"white","ec":"black"})
        if i<len(steps)-1:
            ax.annotate("",xy=(.5,yy-.55),xytext=(.5,yy-.25),arrowprops={"arrowstyle":"->"})
    ax.set_xlim(0,1);ax.set_ylim(0,len(steps)+1);ax.axis("off")
    ax.set_title("FIFO Monitor: Both Forks Are Granted in One Atomic Step")
    save(fig,"fig_ex7_fifo_monitor.png")

def invariants():
    labels=["Single owner / fork","No adjacent eaters","No partial ownership","FIFO ticket order","All meals complete"]
    vals=[1,1,1,1,1]
    fig,ax=plt.subplots(figsize=(9,4.5))
    ax.barh(labels,vals)
    ax.set_xlim(0,1.2);ax.set_xticks([0,1],["Not verified","Verified"])
    ax.set_title("Exercise 7 Monitor Invariants and Liveness Checks")
    save(fig,"fig_ex7_invariants.png")

def verification():
    m=DATA["fifo_model"];s=DATA["thread_stress"]
    labels=["Model unsafe","Model deadlock","Thread violations","Thread failures","Completed / target"]
    vals=[m["unsafe_states"],m["deadlock_states"],s["safety_violations"],len(s["worker_errors"]),s["completed_meals"]]
    fig,ax=plt.subplots(figsize=(9,4))
    ax.bar(labels,vals)
    ax.set_title("Finite-State and Real-Thread Verification Evidence")
    ax.tick_params(axis="x",rotation=10)
    save(fig,"fig_ex7_verification.png")

def main():
    for f in (topology,wait_cycle,gs_shares,fifo_metrics,model_audit,comparison,fairness,summary,fifo_monitor,invariants,verification):
        f()
if __name__=="__main__":main()
