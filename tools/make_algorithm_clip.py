"""Render a short MP4 from the real exact-Fraction Guaranteed Scheduling trace."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from core.gs_core import Proc, simulate_procs

ROOT=Path(__file__).resolve().parents[1]

def main():
    processes=[
        Proc("P1",arrival=0,work=12,weight=1),
        Proc("P2",arrival=0,work=18,weight=2),
        Proc("P3",arrival=2,work=10,weight=3),
    ]
    result=simulate_procs(processes,policy="gs_vtime",quantum=2,tie="stay")
    timeline=result.timeline
    horizon=len(timeline)
    out=ROOT/"exercise-1"/"media"
    out.mkdir(parents=True,exist_ok=True)
    target=out/"guaranteed_scheduling_demo.mp4"
    pnames=[p.name for p in processes]
    fig,ax=plt.subplots(figsize=(14,7),dpi=120)

    def frame(k):
        ax.clear()
        ax.set_xlim(0,max(1,horizon))
        ax.set_ylim(-0.8,1.3)
        ax.set_yticks([])
        ax.set_xlabel("Simulated CPU time (ticks)")
        ax.set_title("Guaranteed Scheduling — exact virtual-time dispatch trace")
        ax.grid(axis="x",alpha=.2)
        visible=timeline[:min(k,horizon)]
        start=0
        while start<len(visible):
            name=visible[start][1]
            end=start+1
            while end<len(visible) and visible[end][1]==name:
                end+=1
            if name is not None:
                ax.barh(0,end-start,left=start,height=.48)
                ax.text((start+end)/2,0,name,ha="center",va="center",fontsize=10)
            start=end
        ax.axvline(min(k,horizon),linewidth=1.5)
        ax.text(0,0.8,
                "Workload: P1(w=1, work=12), P2(w=2, work=18), P3(w=3, work=10; release=2)",
                ha="left",va="center",fontsize=9)
        ax.text(0,-0.55,
                "Policy: gs_vtime | quantum=2 | tie=stay | exact Fraction accounting",
                ha="left",va="center",fontsize=10)
        ax.text(horizon,-0.55,
                "Discrete simulation; not a live-kernel benchmark",
                ha="right",va="center",fontsize=9)
        return []

    animation=FuncAnimation(fig,frame,frames=range(0,horizon+1,2),interval=500,blit=False,repeat=False)
    writer=FFMpegWriter(fps=2,bitrate=1500,metadata={"title":"Guaranteed Scheduling trace"})
    animation.save(target,writer=writer,dpi=100)
    plt.close(fig)
    print(f"Saved {target.relative_to(ROOT)} ({target.stat().st_size} bytes, horizon={horizon})")

if __name__=="__main__":
    main()
