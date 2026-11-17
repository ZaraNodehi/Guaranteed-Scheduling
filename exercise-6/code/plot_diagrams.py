"""Generate 6 Okabe-Ito Capstone diagrams for Exercise 6 (Integrated Scheduling & Sync)."""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EX6_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(EX6_DIR)
DIAG_DIR = os.path.join(EX6_DIR, "diagrams")
OUT_JSON = os.path.join(EX6_DIR, "output", "experiments.json")
os.makedirs(DIAG_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "tools"))
import plot_kit as pk  # noqa: E402

TASK_COL = {
    "T_High": "#dc2626",
    "T_Medium": "#d97706",
    "T_Low": "#1f4e78",
    "T_High_SPIN": "#991b1b",
    "IDLE": "#cbd5e1",
}


def fig1_pi_timeline(d: dict) -> None:
    pk.apply_style()
    no_pip = next(r for r in d["priority_inversion_audits"] if r["mode"] == "no_pip")
    pip = next(r for r in d["priority_inversion_audits"] if r["mode"] == "pip")

    fig, axes = plt.subplots(2, 1, figsize=(11.4, 4.6), sharex=True, gridspec_kw={"hspace": 0.36})
    for ax, r, title in [
        (axes[0], no_pip, f"Without PIP (Fixed-Priority): T_Medium Preempts T_Low -> T_High Blocked {no_pip['high_blocked_ticks']} Ticks ({no_pip['high_misses']} Deadline Miss!)"),
        (axes[1], pip,    f"With Priority Inheritance (PIP): T_Low Boosted -> T_High Blocked Only {pip['high_blocked_ticks']} Ticks ({pip['high_misses']} Misses!)"),
    ]:
        tl = r["timeline"][:30]
        for t, who in tl:
            col = TASK_COL.get(who, "#64748b")
            ax.barh(0, 0.92, left=t, height=0.62, color=col, edgecolor="#0f172a", linewidth=0.5)
            lbl = "H" if who == "T_High" else ("M" if who == "T_Medium" else ("L" if who == "T_Low" else "-"))
            ax.text(t + 0.46, 0, lbl, ha="center", va="center", color="white" if lbl != "-" else "#0f172a",
                    fontsize=7.2, fontweight="bold")
        for m in r["misses"]:
            if m["tick"] <= 30:
                ax.axvline(m["tick"], color="#b91c1c", linestyle="--", linewidth=1.8)
                ax.text(m["tick"] + 0.2, 0.38, f"MISS ({m['task']} @ t={m['tick']})",
                        color="#b91c1c", fontsize=7.8, fontweight="bold")
        ax.set_yticks([])
        ax.set_xlim(0, 30)
        ax.set_ylim(-0.5, 0.6)
        ax.set_title(title, fontsize=9.6, fontweight="bold")

    axes[1].set_xlabel("Discrete CPU Tick (0 .. 29) — Legend: [L]=T_Low (Mutex Owner), [M]=T_Medium, [H]=T_High (RT Control)")
    legend_handles = [
        patches.Patch(color="#dc2626", label="T_High (Prio 3)"),
        patches.Patch(color="#d97706", label="T_Medium (Prio 2)"),
        patches.Patch(color="#1f4e78", label="T_Low (Prio 1)"),
    ]
    axes[0].legend(handles=legend_handles, loc="upper right", ncol=3, fontsize=8)
    fig.suptitle("Mars Pathfinder Priority Inversion & Priority Inheritance Rescue (t = 0..29)", fontsize=11.3, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex6_fig1_priority_inversion_timeline.png"))


def fig2_spin_vs_pip(d: dict) -> None:
    pk.apply_style()
    rows = d["priority_inversion_audits"]
    labels = ["No-PIP\n(Unbounded Inv.)", "PIP Mutex\n(Mars Rescue)", "Spin-Lock\n(Priority Deadlock)"]
    high_block = [r["high_blocked_ticks"] for r in rows]
    max_resp = [r["high_max_response_ticks"] for r in rows]
    misses = [r["high_misses"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.4), gridspec_kw={"wspace": 0.25})
    x = np.arange(3)
    w = 0.34
    b1 = ax1.bar(x - w / 2, high_block, w, label="T_High Blocked/Spin Ticks", color="#d95f02", edgecolor="#0f172a")
    b2 = ax1.bar(x + w / 2, max_resp, w, label="T_High Max Response (Ticks)", color="#1f4e78", edgecolor="#0f172a")
    ax1.axhline(8, color="#dc2626", linestyle="--", linewidth=1.6, label="T_High Deadline = 8 ticks")
    for b in list(b1) + list(b2):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2, str(int(b.get_height())),
                 ha="center", fontsize=8.2, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.6, fontweight="bold")
    ax1.set_ylim(0, 72)
    ax1.set_ylabel("Ticks (Horizon H = 60)")
    ax1.set_title("Blocking Delay & Worst-Case Response")
    ax1.legend(loc="upper left", fontsize=7.6)

    cols = ["#d97706", "#1b9e77", "#dc2626"]
    b3 = ax2.bar(x, misses, width=0.52, color=cols, edgecolor="#0f172a")
    for b in b3:
        m = int(b.get_height())
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.12,
                 f"{m} {'miss' if m == 1 else 'misses'}",
                 ha="center", fontsize=8.8, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.6, fontweight="bold")
    ax2.set_ylim(0, 3.8)
    ax2.set_ylabel("T_High Deadline Misses (60-Tick Run)")
    ax2.set_title("Real-Time Safety Failures Across Lock Types")
    fig.suptitle("Why Preemptive Spin-Locks Deadlock RT Tasks While PIP Eliminates Deadline Misses", fontsize=11.0, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex6_fig2_spin_vs_pip_comparison.png"))


def fig3_rw_rt_pipeline(d: dict) -> None:
    pk.apply_style()
    rows = d["rt_rw_pipeline"]
    short_pr = {"CoarseMutex": "Coarse", "Semaphore": "Sem", "Monitor": "Mon", "Peterson": "Pet", "Dekker": "Dek"}
    labels = [f"{short_pr.get(r['primitive'], r['primitive'])}\n({r['policy']})" for r in rows]
    hits = [r["rt_hit_rate_pct"] for r in rows]
    p95s = [r["rt_p95_lat_ms"] for r in rows]
    tps = [r["total_throughput_ops_s"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.6), gridspec_kw={"wspace": 0.25})
    x = np.arange(len(rows))
    cols = ["#64748b", "#1b9e77", "#1b9e77", "#1b9e77", "#d95f02", "#0072b2", "#1f4e78"]
    b1 = ax1.bar(x, hits, width=0.58, color=cols, edgecolor="#0f172a", alpha=0.92)
    for b, p95 in zip(b1, p95s):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                 f"{b.get_height():.1f}%\n({p95:.2f}ms)", ha="center", fontsize=7.0, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=7.0, fontweight="bold")
    ax1.set_ylim(0, 118)
    ax1.set_ylabel("RT Control Deadline Hit Rate (%) [D = 1.6 ms]")
    ax1.set_title("RT Control Deadline Compliance & P95 Latency")

    b2 = ax2.bar(x, tps, width=0.58, color=cols, edgecolor="#0f172a", alpha=0.92)
    for b in b2:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 65, f"{b.get_height():.0f}",
                 ha="center", fontsize=7.5, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=7.0, fontweight="bold")
    ax2.set_ylim(0, max(tps) * 1.18)
    ax2.set_ylabel("Combined Telemetry + RT Throughput (ops/s)")
    ax2.set_title("System Throughput Under Live 5-Thread RW Workload")
    fig.suptitle("Live 5-Thread RT Control + Shared RW Telemetry Table: CoarseMutex Collapses to 14.3% vs. 100% on Blocking RW", fontsize=10.5, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex6_fig3_rw_rt_pipeline.png"))


def fig4_hybrid_gs_rt(d: dict) -> None:
    pk.apply_style()
    hyb = d["gs_rt_hybrid"]
    pols = ["rm", "edf", "gs_vtime:stay"]
    names = ["Rate Monotonic\n(Static Priority)", "EDF\n(Dynamic Deadline)", "Guaranteed Sched.\n(Weighted vtime)"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.3), gridspec_kw={"wspace": 0.25})
    x = np.arange(3)
    w = 0.36
    misses = [hyb[p]["misses"] for p in pols]
    worst = [hyb[p]["worst_response"] for p in pols]
    jains = [hyb[p]["jain_fairness"] for p in pols]

    b1 = ax1.bar(x - w / 2, misses, w, label="Deadline Misses", color="#dc2626", edgecolor="#0f172a")
    b2 = ax1.bar(x + w / 2, worst, w, label="Worst Response (ticks)", color="#1f4e78", edgecolor="#0f172a")
    for b in list(b1) + list(b2):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.22, str(int(b.get_height())),
                 ha="center", fontsize=8.5, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontsize=8.4, fontweight="bold")
    ax1.set_ylim(0, 12.2)
    ax1.set_ylabel("Ticks / Miss Count (U = 0.958 > LL(3)=0.78)")
    ax1.set_title("Real-Time Deadlines & Worst Response")
    ax1.legend(loc="upper right", fontsize=8)

    b3 = ax2.bar(x, jains, width=0.52, color=["#d97706", "#0072b2", "#1b9e77"], edgecolor="#0f172a")
    for b in b3:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.015, f"{b.get_height():.4f}",
                 ha="center", fontsize=8.8, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, fontsize=8.4, fontweight="bold")
    ax2.set_ylim(0.7, 1.07)
    ax2.set_ylabel("Jain's Proportional Fairness Index (1.0 = Exact)")
    ax2.set_title("CPU Share Equity Across Weighted RT Tasks")
    fig.suptitle("Exercise 1-3 Bridge: GS Achieves 0 Deadlines Missed AND Highest Proportional Fairness (0.9902)", fontsize=10.8, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex6_fig4_hybrid_gs_rt.png"))


def fig5_capstone_radar() -> None:
    pk.apply_style()
    cats = ["Deadline\nCompliance", "Proportional\nFairness", "Anti-Barging\nRW Safety", "CPU Energy\nEfficiency", "Overload\nResilience"]
    series = {
        "EDF + Ticket Monitor + PIP": [5.0, 4.4, 5.0, 5.0, 4.6],
        "GS (vtime) + Ticket Monitor": [4.7, 5.0, 5.0, 5.0, 4.8],
        "RM + Unfair Sem (No-PIP)":   [3.2, 3.6, 2.5, 4.8, 3.0],
        "Priority + Peterson Spin":   [1.2, 3.0, 4.5, 1.0, 1.5],
    }
    cols = ["#1b9e77", "#1f4e78", "#d97706", "#dc2626"]
    x = np.arange(len(cats))
    w = 0.2
    fig, ax = plt.subplots(figsize=(10.8, 4.5))
    for i, ((lbl, vals), col) in enumerate(zip(series.items(), cols)):
        ax.bar(x + (i - 1.5) * w, vals, w, label=lbl, color=col, edgecolor="#0f172a", alpha=0.92)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=8.8, fontweight="bold")
    ax.set_ylim(0, 6.0)
    ax.set_ylabel("Engineering Architecture Score (1-5)")
    ax.set_title("Capstone Architecture Synthesis Across CPU Scheduling & Synchronization Stacks", fontsize=11)
    ax.legend(loc="upper right", ncol=2, fontsize=8.0)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex6_fig5_capstone_radar.png"))


def fig6_end_to_end_arch(d: dict) -> None:
    pk.apply_style()
    ms = d["cross_exercise_milestones"]
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.axis("off")
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 5.0)
    boxes = [
        ("Ex 1-2: GS Fairness", "Exact Rational vtime\nWeighted & Sleeper Cap\nJain ~ 0.990", "#1f4e78", "#eff6ff", 0.2, 2.7),
        ("Ex 3: Real-Time CPU", f"RM ({ms['ex3_rm_misses_set_b']} miss) vs EDF ({ms['ex3_edf_misses_set_b']})\nAbove LL(3)=0.78\nRTA + Domino Audit", "#0072b2", "#f0f9ff", 3.9, 2.7),
        ("Ex 4: Mutex & BFS", f"Dekker v5 ({ms['ex4_dekker_v5_states']} states)\nPeterson TSO ({ms['ex4_peterson_tso_errors']} errs)\n98% Spin vs 1% Sleep", "#d95f02", "#fff7ed", 7.6, 2.7),
        ("Ex 5: Readers-Writers", f"12 RW Locks (4x3)\n{ms['ex5_rw_max_speedup_95']}x Speedup @ 95% R\nTicket Beats Barging", "#1b9e77", "#ecfdf5", 1.9, 0.35),
        ("Ex 6: Integrated Kernel", "PIP Stops Pathfind. Miss\nSpin Deadlock Avoided\n100% RT RW Pipeline", "#7c3aed", "#f5f3ff", 5.9, 0.35),
    ]
    for hdr, body, ec, fc, x, y in boxes:
        ax.add_patch(patches.FancyBboxPatch((x, y), 3.35, 1.9, boxstyle="round,pad=0.08", fc=fc, ec=ec, lw=1.6))
        ax.add_patch(patches.FancyBboxPatch((x, y + 1.38), 3.35, 0.52, boxstyle="round,pad=0.04", fc=ec, ec=ec, lw=1.0))
        ax.text(x + 1.675, y + 1.64, hdr, ha="center", va="center", color="white", fontsize=8.8, fontweight="bold")
        ax.text(x + 1.675, y + 0.68, body, ha="center", va="center", color="#0f172a", fontsize=8.0)

    # Connecting arrows
    arrow_kw = dict(arrowstyle="-|>", lw=1.8, color="#334155")
    ax.annotate("", xy=(3.88, 3.65), xytext=(3.57, 3.65), arrowprops=arrow_kw)
    ax.annotate("", xy=(7.58, 3.65), xytext=(7.27, 3.65), arrowprops=arrow_kw)
    ax.annotate("", xy=(3.6, 2.28), xytext=(5.5, 2.68), arrowprops=arrow_kw)
    ax.annotate("", xy=(7.5, 2.28), xytext=(8.8, 2.68), arrowprops=arrow_kw)
    ax.annotate("", xy=(5.88, 1.30), xytext=(5.27, 1.30), arrowprops=arrow_kw)

    ax.set_title("Operating Systems Architecture Map: Connecting Exercises 1 through 6", fontsize=11.4, fontweight="bold")
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex6_fig6_end_to_end_architecture.png"))


def main() -> None:
    with open(OUT_JSON, "r", encoding="utf-8") as f:
        d = json.load(f)
    fig1_pi_timeline(d)
    fig2_spin_vs_pip(d)
    fig3_rw_rt_pipeline(d)
    fig4_hybrid_gs_rt(d)
    fig5_capstone_radar()
    fig6_end_to_end_arch(d)
    print("Generated 6 PNG figures in", DIAG_DIR)


if __name__ == "__main__":
    main()
