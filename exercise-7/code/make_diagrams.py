"""Generate 6 crisp capstone synthesis figures for Exercise 7 from experiments.json."""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EX7_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX7_DIR)
DATA_PATH = os.path.join(EX7_DIR, "output", "experiments.json")
DIAG_DIR = os.path.join(EX7_DIR, "diagrams")
os.makedirs(DIAG_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import plot_kit as pk  # noqa: E402

C = {
    "blue": "#1f4e78",
    "sky": "#0072b2",
    "green": "#1b9e77",
    "orange": "#d95f02",
    "purple": "#7570b3",
    "yellow": "#e6ab02",
    "red": "#b91c1c",
    "black": "#0f172a",
}


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def fig1_research_arc(d):
    pk.apply_style()
    s = d["cross_exercise_summary"]
    fig, ax = plt.subplots(figsize=(12.6, 5.2), dpi=220)
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    ax.text(6.3, 4.95, "Capstone Trajectory: Seven-Exercise Evolution of Guaranteed Scheduling",
            ha="center", va="top", fontsize=11.4, fontweight="bold", color=C["black"])

    boxes = [
        (1.45, 3.65, 2.45, 1.32, f"Ex 1: Baseline & OS\nLag=1.0q; Linux ordered\n({s['ex1_os_median_wall_sec']:.2f}s median) [D]", "#eff6ff", C["blue"]),
        (4.65, 3.65, 2.45, 1.32, f"Ex 2: Regimes\n120 RT sets; Overload RM\nshare=0.0 vs GS=0.84", "#eefaf5", C["green"]),
        (7.85, 3.65, 2.45, 1.32, f"Ex 3: Hand & Drift\n100% hand match; float\ndrift onset t={s['ex3_float_drift_tick']}", "#fff7ed", C["orange"]),
        (11.05, 3.65, 2.45, 1.32, f"Ex 4: Formal Bounds\nDynamic gap={s['ex4_dynamic_ratio_gap']} vs 1\nEDF 100% ({s['ex4_rt_feasible_count']}/10)", "#fdf2f8", C["purple"]),
        (2.40, 1.25, 3.15, 1.38, f"Ex 5: 240-Seed Monte Carlo\ngs_vtime:stay lag={s['ex5_mc_240_seeds']['gs_vtime_stay_lag']:.3f}\nvs ratio={s['ex5_mc_240_seeds']['gs_ratio_index_lag']:.2f}, RR={s['ex5_mc_240_seeds']['rr_index_lag']:.2f}", "#eff6ff", C["sky"]),
        (6.30, 1.25, 3.15, 1.38, f"Ex 6: O(log N) & Sleeper Cap\n{s['ex6_speedup_n2000']:.1f}x @ N=2000; burst\n{s['ex6_sleeper_80_burst']['gs_vtime']}t->{s['ex6_sleeper_80_burst']['gs_capped']}t; {s['ex6_live_os_dev_ratio']:.1f}x OS", "#eefaf5", C["green"]),
        (10.20, 1.25, 3.15, 1.38, f"Ex 7: Capstone Synthesis\n6-Regime Matrix + Demo\nLive Linux Err={d['live_capstone_os_demo']['max_share_error']*100:.2f}%", "#fefce8", C["black"]),
    ]
    for cx, cy, w, h, txt, fc, ec in boxes:
        pk.draw_box(ax, cx, cy, w, h, txt, fc=fc, ec=ec, tc=C["black"], fontsize=7.8)

    pk.draw_arrow(ax, 2.70, 3.65, 3.40, 3.65, "", color=C["black"])
    pk.draw_arrow(ax, 5.90, 3.65, 6.60, 3.65, "", color=C["black"])
    pk.draw_arrow(ax, 9.10, 3.65, 9.80, 3.65, "", color=C["black"])
    # Orthogonal routed connector from Ex 4 bottom down to Ex 5 top
    ax.plot([11.05, 11.05, 2.40], [2.96, 2.48, 2.48], color=C["sky"], lw=1.6, zorder=2)
    ax.annotate("", xy=(2.40, 1.98), xytext=(2.40, 2.48),
                arrowprops=dict(arrowstyle="-|>", color=C["sky"], lw=1.6), zorder=2)
    pk.draw_arrow(ax, 4.00, 1.25, 4.70, 1.25, "", color=C["black"])
    pk.draw_arrow(ax, 7.90, 1.25, 8.60, 1.25, "", color=C["black"])

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex7_research_arc.png"))


def fig2_six_regime_heatmap(d):
    pk.apply_style()
    m = d["six_regime_matrix"]
    pols = ["gs_vtime:stay", "gs_ratio:index", "rr:index", "fifo:index"]
    plabels = ["gs_vtime:stay\n(Hardened GS)", "gs_ratio:index\n(Legacy GS)", "rr:index\n(Round-Robin)", "fifo:index\n(FCFS Batch)"]
    reg_labels = ["R1 Static\n(1 / Lag)", "R2 Dynamic\n(1 / Lag)", "R4 RT Feas\n(1 - Misses)", "R5 Overload\n(Min Share)"]

    mat = np.zeros((len(pols), len(reg_labels)))
    raw = [["" for _ in reg_labels] for _ in pols]
    for i, p in enumerate(pols):
        l1 = m["R1_Static_Weighted"][p]["max_abs_lag"]
        l2 = m["R2_Dynamic_Latecomers"][p]["max_abs_lag"]
        m4 = m["R4_RT_Feasible_U090"][p]["deadline_misses"]
        s5 = m["R5_RT_Overload_U110"][p]["min_share_ratio"]

        mat[i, 0] = max(0.05, min(1.0, 1.5 / max(1.0, l1)))
        mat[i, 1] = max(0.05, min(1.0, 1.5 / max(1.0, l2)))
        mat[i, 2] = max(0.05, 1.0 - min(1.0, m4 / 8.0))
        mat[i, 3] = s5

        raw[i][0] = f"lag={l1:.2f}"
        raw[i][1] = f"lag={l2:.2f}"
        raw[i][2] = f"miss={m4}"
        raw[i][3] = f"minS={s5:.2f}"

    fig, ax = plt.subplots(figsize=(10.4, 4.4), dpi=220)
    im = ax.imshow(mat, cmap="YlGn", vmin=0.0, vmax=1.0, aspect="auto")
    ax.grid(False)
    for i in range(len(pols)):
        for j in range(len(reg_labels)):
            tc = "white" if mat[i, j] > 0.62 else C["black"]
            ax.text(j, i, raw[i][j], ha="center", va="center", color=tc, fontsize=9.2, fontweight="bold")
    ax.set_xticks(range(len(reg_labels)))
    ax.set_xticklabels(reg_labels, fontsize=9.0, fontweight="bold")
    ax.set_yticks(range(len(plabels)))
    ax.set_yticklabels(plabels, fontsize=8.8, fontweight="bold")
    ax.set_xticks(np.arange(-0.5, len(reg_labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(plabels), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2.0)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("Capstone Multi-Regime Scorecard (Darker Green = Better Performance) [M]", fontsize=10.5, fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.03)
    cbar.set_label("Normalized Regime Score", fontsize=8.8)
    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex7_six_regime_heatmap.png"))


def fig3_live_os_capstone(d):
    pk.apply_style()
    os_d = d["live_capstone_os_demo"]
    x = np.arange(3)
    w = 0.30

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.3), dpi=220)
    ax1.bar(x - w / 2, os_d["ideal_shares"], width=w, color=C["blue"], label="Ideal GPS [1/7, 2/7, 4/7]")
    ax1.bar(x + w / 2, os_d["observed_shares"], width=w, color=C["green"], label="Live Linux Observed (dt=0.05s)")
    for xi, iv, ov in zip(x, os_d["ideal_shares"], os_d["observed_shares"]):
        ax1.text(xi - w / 2, iv + 0.015, f"{iv*100:.1f}%", ha="center", va="bottom", fontsize=8.0, fontweight="bold")
        ax1.text(xi + w / 2, ov + 0.015, f"{ov*100:.1f}%", ha="center", va="bottom", fontsize=8.0, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(["P1 (w=1)", "P2 (w=2)", "P3 (w=4)"], fontsize=9.2)
    ax1.set_ylim(0, 0.68)
    ax1.set_ylabel("Measured CPU Share", fontsize=9.2)
    ax1.set_title(f"Live Linux Capstone Verification (Max Err={os_d['max_share_error']*100:.2f}%) [D]", fontsize=9.8, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.2)

    # Right panel: live OS accuracy evolution Ex1/Ex5/Ex6/Ex7
    ex_labels = ["Ex6 Legacy OS\n(dt=0.10s, unanchored)", "Ex6 Refactored\n(dt=0.05s, V(t)+stay)", "Ex7 Capstone\n(dt=0.05s, [1,2,4])"]
    errs = [11.97, 2.82, os_d["max_share_error"] * 100.0]
    bars = ax2.bar([0, 1, 2], errs, color=[C["red"], C["sky"], C["green"]], width=0.48, edgecolor="#333", linewidth=0.7)
    for b, e in zip(bars, errs):
        ax2.text(b.get_x() + b.get_width() / 2, e + 0.35, f"{e:.2f}%", ha="center", va="bottom", fontsize=8.8, fontweight="bold")
    ax2.set_xticks([0, 1, 2])
    ax2.set_xticklabels(ex_labels, fontsize=8.5)
    ax2.set_ylim(0, 14.5)
    ax2.set_ylabel("Max Share Deviation (%)", fontsize=9.2)
    ax2.set_title("Real-Linux OS Error Across Project Stages [D]", fontsize=9.8, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex7_live_os_capstone.png"))


def fig4_selector_decision_tree():
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(11.8, 5.2), dpi=220)
    ax.set_xlim(0, 11.8)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    ax.text(5.9, 4.98, "Capstone Production Scheduler Selection Decision Tree (From Formal Theorems & OS Benchmarks)",
            ha="center", va="top", fontsize=10.8, fontweight="bold", color=C["black"])

    pk.draw_box(ax, 5.9, 4.25, 4.6, 0.72, "Workload Requirement Audit:\nHard Deadlines vs Weighted Proportional Sharing?",
                fc="#eff6ff", ec=C["blue"], tc=C["black"], fontsize=8.3)

    pk.draw_box(ax, 2.75, 2.85, 3.8, 0.80, "Hard Real-Time Deadlines?\nCheck U <= 1.0 & Response Time",
                fc="#fdf2f8", ec=C["purple"], tc=C["black"], fontsize=8.2)
    pk.draw_box(ax, 9.05, 2.85, 3.8, 0.80, "Proportional CPU / Fair Share?\nUse V(t) Virtual Time + Fixed-Point",
                fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=8.2)

    pk.draw_box(ax, 1.45, 1.15, 2.5, 1.15, "Feasible (U <= 1.0):\nSelect EDF!\n100% exact optimal\n(Ex 4 Theorem 3)",
                fc="#dbeafe", ec=C["sky"], tc=C["black"], fontsize=7.9)
    pk.draw_box(ax, 4.25, 1.15, 2.5, 1.15, "Transient Overload:\nSelect gs_vtime / Hybrid\nGraceful share >= 0.84\n(vs RM 0.00 starve!)",
                fc="#fff7ed", ec=C["orange"], tc=C["black"], fontsize=7.9)
    pk.draw_box(ax, 7.60, 1.15, 2.6, 1.15, "Static/Batch Only:\ngs_vtime:stay / WFQ\nlag <= 1.0q (0.94q)\nMinimal switches",
                fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=7.9)
    pk.draw_box(ax, 10.45, 1.15, 2.5, 1.15, "Dynamic + I/O Sleep:\ngs_capped:stay Heap\n113x @ N=2000; 1t cap\n(Linux EEVDF class)",
                fc="#dcfce7", ec=C["green"], tc=C["black"], fontsize=7.9)

    pk.draw_arrow(ax, 4.6, 3.88, 3.1, 3.28, "Deadlines", label_offset=(-0.45, 0.1), color=C["purple"])
    pk.draw_arrow(ax, 7.2, 3.88, 8.7, 3.28, "Fairness", label_offset=(0.45, 0.1), color=C["green"])
    pk.draw_arrow(ax, 2.1, 2.42, 1.55, 1.75, "U <= 1", label_offset=(-0.35, 0.05), color=C["sky"])
    pk.draw_arrow(ax, 3.4, 2.42, 4.10, 1.75, "U > 1", label_offset=(0.35, 0.05), color=C["orange"])
    pk.draw_arrow(ax, 8.4, 2.42, 7.75, 1.75, "CPU-bound", label_offset=(-0.45, 0.05), color=C["green"])
    pk.draw_arrow(ax, 9.7, 2.42, 10.3, 1.75, "Mixed I/O", label_offset=(0.45, 0.05), color=C["green"])

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex7_selector_decision_tree.png"))


def fig5_latency_fairness_frontier(d):
    pk.apply_style()
    m = d["six_regime_matrix"]
    r2 = m["R2_Dynamic_Latecomers"]
    r3 = m["R3_Heavy_Sleeper_40"]
    pols = [
        ("gs_capped:stay", "gs_capped:stay (Hardened)", C["green"], "D"),
        ("gs_vtime:stay", "gs_vtime:stay (Uncapped)", C["sky"], "s"),
        ("gs_entitled:index", "gs_entitled:index", C["purple"], "^"),
        ("gs_ratio:index", "gs_ratio:index (Legacy)", C["red"], "o"),
        ("rr:index", "rr:index (Round-Robin)", C["orange"], "P"),
        ("fifo:index", "fifo:index (FCFS)", C["black"], "X"),
    ]
    fig, ax = plt.subplots(figsize=(10.8, 4.6), dpi=220)
    offsets = {
        "gs_capped:stay": (0.6, 3.2),
        "gs_vtime:stay": (0.6, 1.2),
        "gs_entitled:index": (0.6, -1.6),
        "gs_ratio:index": (0.6, 1.2),
        "rr:index": (0.6, 1.2),
        "fifo:index": (-4.5, -3.5),
    }
    xs, ys = [], []
    for key, label, col, mk in pols:
        x = r2[key]["max_abs_lag"]
        y = r3[key]["max_starve_gap"]
        xs.append(x)
        ys.append(y)
        ax.scatter([x], [y], s=110, color=col, marker=mk, zorder=4, label=label)
        dx, dy = offsets[key]
        ax.annotate(label.split(" ")[0], (x, y), xytext=(x + dx, y + dy),
                    fontsize=8.2, fontweight="bold", color=col)

    ax.axvspan(-0.5, 2.6, ymin=0, ymax=0.22, color="#dcfce7", alpha=0.5, zorder=1)
    ax.text(0.1, 8.8, "Target Pareto Corner:\nLow Lag & Zero Sleeper Lockout",
            ha="left", va="bottom", fontsize=8.0, fontweight="bold", color=C["green"])
    ax.set_xlabel("Dynamic Latecomer Max GPS Lag (ticks, R2)", fontsize=9.3)
    ax.set_ylabel("Heavy Sleeper Max Starvation Gap (ticks, R3 S=40)", fontsize=9.3)
    ax.set_title("Capstone Fairness vs Anti-Sleeper Pareto Frontier Across R2 & R3 [M]", fontsize=10.3, fontweight="bold")
    ax.set_xlim(-0.5, max(xs) * 1.12)
    ax.set_ylim(-3.5, max(ys) * 1.18)
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="center right", fontsize=8.0)
    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex7_latency_fairness_frontier.png"))


def fig6_eevdf_smp_roadmap():
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(12.4, 4.6), dpi=220)
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    ax.text(6.2, 4.38, "Future Work Roadmap: Bridging Ex 6 User-Space Heap to Kernel EEVDF & Multi-Core SMP",
            ha="center", va="top", fontsize=10.8, fontweight="bold", color=C["black"])

    stages = [
        (1.75, 2.25, 2.85, 2.35, "Delivered in Ex 6 (SMP=1)\n- Lazy O(log N) min-heap\n- Integer fixed-point 10^9/w\n- V(t) arrival anchor\n- gs_capped wakeup floor\n- stay hysteresis & dt=0.05s", "#eefaf5", C["green"]),
        (6.20, 2.25, 2.85, 2.35, "Phase 2: Full EEVDF Semantics\n- Eligibility check ve_i <= V(t)\n- Virtual deadline vd_i = ve_i + L_i/w_i\n- Variable request slices L_i\n- Augmented RB-tree min-vd\n- Lag bound <= max(L_i) strictly", "#eff6ff", C["sky"]),
        (10.65, 2.25, 2.85, 2.35, "Phase 3: Multi-Core SMP & Kernel\n- Per-CPU lockless runqueues\n- Work-stealing load balancer\n- Cross-core V(t) migration sync\n- cgroups v2 cpu.weight hook\n- eBPF / sched_ext prototype", "#fff7ed", C["orange"]),
    ]
    for cx, cy, w, h, txt, fc, ec in stages:
        pk.draw_box(ax, cx, cy, w, h, txt, fc=fc, ec=ec, tc=C["black"], fontsize=7.9)

    pk.draw_arrow(ax, 3.22, 2.25, 4.72, 2.25, "Virtual Deadlines", label_offset=(0.0, 0.36), color=C["sky"])
    pk.draw_arrow(ax, 7.67, 2.25, 9.17, 2.25, "SMP Scaling", label_offset=(0.0, 0.36), color=C["orange"])
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex7_eevdf_smp_roadmap.png"))


def main():
    d = load_data()
    fig1_research_arc(d)
    fig2_six_regime_heatmap(d)
    fig3_live_os_capstone(d)
    fig4_selector_decision_tree()
    fig5_latency_fairness_frontier(d)
    fig6_eevdf_smp_roadmap()
    print("Generated 6 Exercise 7 diagrams cleanly in", DIAG_DIR)


if __name__ == "__main__":
    main()
