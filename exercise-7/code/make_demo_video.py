"""Render a short MP4 explainer for the Exercise 7 deadlock and FIFO fix."""
from pathlib import Path
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

HERE=Path(__file__).resolve().parent
EX7=HERE.parent
OUT=EX7/"media"/"dining_philosophers_demo.mp4"
OUT.parent.mkdir(parents=True,exist_ok=True)
N=5
ANGLES=[math.pi/2-2*math.pi*i/N for i in range(N)]
POINTS=[(2*math.cos(a),2*math.sin(a)) for a in ANGLES]
# Intro frames show the circular-wait witness. Later phases are valid non-adjacent grants.
PHASES=[
 ("Naive protocol: every philosopher holds the left fork",[-1,-1,-1,-1,-1],True),
 ("Deadlock: all five wait for their right-hand neighbor",[-1,-1,-1,-1,-1],True),
 ("FIFO monitor grants both forks to P0 and P2 atomically",[0,2],False),
 ("Release both pairs; FIFO head P1 and P3 receive their pairs",[1,3],False),
 ("P1 and P4 now eat without sharing a fork",[1,4],False),
 ("A meal ends; both forks are released; next FIFO request proceeds",[0,2],False),
 ("GS schedules runnable philosophers; the monitor still owns fork safety",[1,3],False),
 ("Conclusion: CPU fairness + deadlock-free resource protocol",[],False),
]
frames_per=12

fig,ax=plt.subplots(figsize=(8,7),dpi=120)
def draw(frame):
    phase=frame//frames_per
    title,eating,deadlocked=PHASES[min(phase,len(PHASES)-1)]
    ax.clear();ax.set_aspect("equal");ax.axis("off")
    ax.set_xlim(-3.2,3.2);ax.set_ylim(-3.1,3.1)
    for i,(x,y) in enumerate(POINTS):
        ax.scatter([x],[y],s=1450,edgecolors="black",zorder=3)
        state="EATING" if i in eating else ("HUNGRY" if deadlocked else "THINK / WAIT")
        ax.text(x,y,f"P{i}\n{state}",ha="center",va="center",fontsize=8,zorder=4)
    for i in range(N):
        x1,y1=POINTS[i];x2,y2=POINTS[(i+1)%N]
        ax.plot([x1*.76+x2*.24,x1*.24+x2*.76],[y1*.76+y2*.24,y1*.24+y2*.76],lw=4)
        ax.text((x1+x2)/2,(y1+y2)/2,f"F{i}",ha="center",va="center",
                bbox={"boxstyle":"round","fc":"white","ec":"black"})
    ax.text(0,0.15,"FIFO monitor" if not deadlocked else "CIRCULAR WAIT",
            ha="center",va="center",fontsize=14,weight="bold")
    ax.set_title(title,fontsize=11,pad=8)
    ax.text(0,-2.8,"Illustrative discrete protocol animation — not a live kernel benchmark",
            ha="center",fontsize=7)
    return []

ani=FuncAnimation(fig,draw,frames=frames_per*len(PHASES),interval=100,blit=False)
ani.save(str(OUT),writer=FFMpegWriter(fps=12,bitrate=1400))
plt.close(fig)
print(OUT)
