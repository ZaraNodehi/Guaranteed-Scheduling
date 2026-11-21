"""Generate a clean schematic of the FIFO Dining Philosophers monitor."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"exercise-6"/"diagrams"/"fig_dining_philosophers_fifo.png"
out.parent.mkdir(parents=True,exist_ok=True)
fig,ax=plt.subplots(figsize=(9,7),dpi=180)
ax.set_aspect("equal"); ax.axis("off")
n=5
angles=np.linspace(np.pi/2,np.pi/2-2*np.pi,n,endpoint=False)
radius=2.25
coords=[(radius*np.cos(a),radius*np.sin(a)) for a in angles]
for i,(x,y) in enumerate(coords):
    ax.scatter([x],[y],s=1800,marker="o",edgecolors="black",linewidths=1.4,zorder=3)
    ax.text(x,y,f"P{i}\nFIFO ticket {i}",ha="center",va="center",fontsize=9,zorder=4)
for i in range(n):
    x1,y1=coords[i];x2,y2=coords[(i+1)%n]
    mx,my=(x1+x2)/2,(y1+y2)/2
    ax.plot([x1*.76+x2*.24,x1*.24+x2*.76],[y1*.76+y2*.24,y1*.24+y2*.76],linewidth=5,solid_capstyle="round")
    ax.text(mx,my,f"F{i}",ha="center",va="center",fontsize=10,bbox={"boxstyle":"round,pad=.25","fc":"white","ec":"black"})
ax.text(0,0.15,"FIFO monitor\natomic pair reservation",ha="center",va="center",fontsize=13,weight="bold")
ax.text(0,-.55,"Acquire both forks or wait for both\nNo partial ownership / no hold-and-wait",ha="center",va="center",fontsize=9)
ax.set_xlim(-3.3,3.3);ax.set_ylim(-3,3.2)
fig.tight_layout()
fig.savefig(out,bbox_inches="tight")
plt.close(fig)
print(out)
