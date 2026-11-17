"""Generate 8 publication-grade figures for Exercise 3 (3-process EDF vs RM paper scheduling)."""
from __future__ import annotations

import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EX3_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(EX3_DIR)
DIAG_DIR = os.path.join(EX3_DIR, "diagrams")
OUT_JSON = os.path.join(EX3_DIR, "output", "experiments.json")
os.makedirs(DIAG_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "tools"))
import plot_kit as pk  # noqa: E402

TASK_COLORS = {
    "P1": "#1f4e78",  # deep navy
    "P2": "#1b9e77",  # teal green
    "P3": "#d95f02",  # burnt orange
    "IDLE": "#e2e8f0",
}


def _draw_two_panel_gantt(s: dict, out_name: str, fig_title: str) -> None:
    pk.apply_style()
    H = s["horizon"]
    tasks = [t["name"] for t in s["tasks"]]
    fig, axes = plt.subplots(2, 1, figsize=(11.2, 5.4), sharex=True, gridspec_kw={"hspace": 0.32})

    for ax, alg_key, alg_label in [
        (axes[0], "edf", "EDF (Dynamic Priority: min absolute deadline d_i)"),
        (axes[1], "rm", "RM (Static Priority: min period T_i => P1 > P2 > P3)"),
    ]:
        alg_d = s[alg_key]
        tl = alg_d["timeline"]
        diffs = {d["t"] for d in s["edf_vs_rm_diff_ticks"]}
        miss_ticks = {m["tick"]: m["job"] for m in alg_d["misses"]}

        # Draw each task row
        for row_idx, tname in enumerate(reversed(tasks)):
            y = row_idx * 1.0 + 0.15
            for t in range(H):
                lbl = tl[t]
                owner = lbl.split("#")[0] if lbl != "IDLE" else "IDLE"
                if owner == tname:
                    edge = "#b91c1c" if t in diffs else "#1e293b"
                    lw = 1.6 if t in diffs else 0.7
                    rect = patches.Rectangle(
                        (t, y), 1.0, 0.7,
                        facecolor=TASK_COLORS[tname], edgecolor=edge, linewidth=lw, alpha=0.92,
                    )
                    ax.add_patch(rect)
                    jid = lbl.split("#")[1]
                    ax.text(t + 0.5, y + 0.35, f"#{jid}", ha="center", va="center",
                            color="white", fontsize=7.5 if H <= 14 else 6.8, fontweight="bold")
                else:
                    # light guide box
                    ax.add_patch(patches.Rectangle(
                        (t, y), 1.0, 0.7, facecolor="none", edgecolor="#e2e8f0", linewidth=0.5
                    ))

            # Release & deadline arrows along bottom of each lane
            spec = next(x for x in s["tasks"] if x["name"] == tname)
            for rel in range(0, H + 1, spec["period"]):
                if rel <= H:
                    ax.plot(rel, y - 0.04, marker="^", markersize=4.5, color=TASK_COLORS[tname], clip_on=False)

        # Annotate deadline misses (non-overlapping coordinates)
        for idx_m, (mt, mjob) in enumerate(sorted(miss_ticks.items())):
            tname = mjob.split("#")[0]
            row_idx = list(reversed(tasks)).index(tname)
            y = row_idx * 1.0 + 0.5
            ax.axvline(mt, color="#dc2626", linestyle="--", linewidth=1.6, zorder=6)
            if len(miss_ticks) >= 4:
                # Spread cleanly in whitespace for Set C EDF (t=12, 16, 18, 20, 21)
                x_text = [7.4, 12.3, 12.3, 16.5, 19.6][idx_m % 5]
                y_text = [2.75, 2.75, 1.85, 2.75, 1.15][idx_m % 5]
            else:
                # Set B (t=8) and Set C RM (t=6, 12, 18): always step right in free space
                x_text = mt + 0.5 if mt <= H - 5.2 else mt - 4.3
                y_text = 2.75 if (idx_m % 2 == 0 or len(miss_ticks) == 1) else 2.25
            ax.annotate(
                f"MISS {mjob} @ t={mt}",
                xy=(mt, y), xytext=(x_text, y_text),
                fontsize=7.4, fontweight="bold", color="#b91c1c",
                bbox=dict(boxstyle="round,pad=0.18", fc="#fee2e2", ec="#dc2626", lw=0.9),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.1),
                zorder=7,
            )

        # Mark idle ticks
        for t in range(H):
            if tl[t] == "IDLE":
                ax.add_patch(patches.Rectangle((t, 0.08), 1.0, 2.84, facecolor="#f1f5f9", edgecolor="#94a3b8",
                                               hatch="//", linewidth=0.5, alpha=0.6, zorder=1))
                ax.text(t + 0.5, 1.5, "IDLE", ha="center", va="center", rotation=90,
                        fontsize=7.2, color="#475569", fontweight="bold")

        ax.set_xlim(0, H)
        ax.set_ylim(-0.1, len(tasks) + 0.05)
        ax.set_yticks([0.5, 1.5, 2.5])
        ax.set_yticklabels([f"{t} (T={next(x['period'] for x in s['tasks'] if x['name']==t)}, C={next(x['wcet'] for x in s['tasks'] if x['name']==t)})" for t in reversed(tasks)])
        ax.set_xticks(range(0, H + 1))
        ax.set_title(f"{alg_label}  |  Misses={alg_d['missed_count']}  Switches={alg_d['switches']}  Preemptions={alg_d['preemptions']}",
                     fontsize=10, loc="left", pad=6)
        ax.grid(True, axis="x", color="#cbd5e1", linestyle=":", linewidth=0.7)

    axes[1].set_xlabel(f"Discrete Time Tick t (0 to H={H}; red borders = ticks where EDF and RM diverge)")
    fig.suptitle(fig_title, fontsize=12, fontweight="bold", y=0.99)
    pk.save_fig(fig, os.path.join(DIAG_DIR, out_name))


def fig3_rta_fixed_point(data: dict) -> None:
    pk.apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.4), gridspec_kw={"wspace": 0.25})
    for ax, skey, title in [
        (axes[0], "set_a", "Set A (U=11/12=0.917): RM Fixed-Point Converges"),
        (axes[1], "set_b", "Set B (U=23/24=0.958): P3 Misses D_3=8 at R_3=9"),
    ]:
        s = data[skey]
        for rec in s["rta_rm"]:
            iters = rec["iterations"]
            xs = list(range(len(iters)))
            c = TASK_COLORS[rec["name"]]
            ax.plot(xs, iters, marker="o", linewidth=2.1, markersize=6, color=c,
                    label=f"{rec['name']} (D={rec['deadline']}, R*={rec['worst_R_i']}, {'PASS' if rec['rta_feasible'] else 'FAIL'})")
            ax.axhline(rec["deadline"], color=c, linestyle="--", linewidth=1.1, alpha=0.65)
            ax.text(3.05, rec["deadline"] + 0.16, f"D({rec['name']})={rec['deadline']}",
                    ha="right", fontsize=7.8, color=c, fontweight="bold")
            for k, val in zip(xs, iters):
                ax.text(k, val + 0.2, str(val), ha="center", fontsize=8, color=c, fontweight="bold")
        ax.set_title(title, fontsize=9.8)
        ax.set_xlabel("RTA Fixed-Point Iteration k")
        ax.set_ylabel("Worst-Case Response Time Estimate R_i^(k) [ticks]")
        ax.set_xticks(range(4))
        ax.set_ylim(0, 10.5)
        ax.legend(loc="upper left", fontsize=8)
    fig.suptitle("Exact Rate-Monotonic Response-Time Analysis (RTA): Paper Fixed-Point Iterations", fontsize=11.5, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex3_fig3_rta_fixed_point.png"))


def fig4_dbf_curve(data: dict) -> None:
    pk.apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5), gridspec_kw={"wspace": 0.24})
    for ax, skey, title in [
        (axes[0], "set_a", "Set A (H=12): dbf(L) <= L Everywhere"),
        (axes[1], "set_b", "Set B (H=24): dbf(L) <= L Proves EDF Feasibility"),
    ]:
        s = data[skey]
        Ls = [r["L"] for r in s["dbf_edf"]]
        dbfs = [r["dbf"] for r in s["dbf_edf"]]
        ax.step(Ls, dbfs, where="post", color="#0072b2", linewidth=2.2, label="EDF Demand Bound dbf(L)")
        ax.plot([0, max(Ls)], [0, max(Ls)], color="#1b9e77", linestyle="--", linewidth=1.8, label="CPU Supply Line S(L)=L")
        ax.fill_between(Ls, dbfs, Ls, step="post", color="#1b9e77", alpha=0.12, label="Slack L - dbf(L) >= 0")
        ax.set_title(title, fontsize=9.8)
        ax.set_xlabel("Interval Length L [ticks]")
        ax.set_ylabel("Cumulative Demand dbf(L) [ticks]")
        ax.legend(loc="upper left", fontsize=8)
    fig.suptitle("Baruah Exact Processor Demand Bound Function dbf(L) vs Linear Capacity Supply", fontsize=11.5, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex3_fig4_dbf_curve.png"))


def fig5_overload_domino(data: dict) -> None:
    s = data["set_c"]
    _draw_two_panel_gantt(
        s,
        "ex3_fig5_overload_domino_setC.png",
        "Set C Overload Audit (2H=24, U=7/6=1.167): EDF Domino Effect vs RM Strict P3 Starvation",
    )


def fig6_utilization_regions(data: dict) -> None:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    ll3 = 3 * (2 ** (1 / 3) - 1)  # 0.77976
    ax.axvspan(0, ll3, color="#d1fae5", alpha=0.65, label=f"Zone 1: U <= LL(3)={ll3:.3f} (Both RM & EDF guaranteed)")
    ax.axvspan(ll3, 1.0, color="#fef3c7", alpha=0.70, label="Zone 2: 0.780 < U <= 1.000 (EDF always passes; RM needs RTA)")
    ax.axvspan(1.0, 1.25, color="#fee2e2", alpha=0.70, label="Zone 3: U > 1.000 (Overload: both miss deadlines)")

    pts = [
        ("Set A\n(U=11/12=0.917)\nEDF:0, RM:0", data["set_a"]["utilization"], 0.65, "#1b9e77", "o"),
        ("Set B\n(U=23/24=0.958)\nEDF:0, RM:1 miss", data["set_b"]["utilization"], 0.38, "#0072b2", "D"),
        ("Set C\n(U=7/6=1.167)\nEDF:5, RM:3 misses", data["set_c"]["utilization"], 0.55, "#b91c1c", "X"),
    ]
    for lbl, x, y, col, mk in pts:
        ax.scatter([x], [y], s=140, color=col, marker=mk, edgecolor="#0f172a", linewidth=1.1, zorder=5)
        ax.annotate(lbl, xy=(x, y), xytext=(x - 0.06, y + 0.14),
                    fontsize=8.3, fontweight="bold", color="#0f172a",
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=col, lw=1.1),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.1))

    ax.axvline(ll3, color="#047857", linestyle="--", linewidth=1.8)
    ax.axvline(1.0, color="#b45309", linestyle="-", linewidth=2.0)
    ax.set_xlim(0.45, 1.25)
    ax.set_ylim(0.05, 0.98)
    ax.set_yticks([])
    ax.set_xlabel("Total CPU Utilization U = sum(C_i / T_i)")
    ax.set_title("Schedulability Decision Regions for n=3 Periodic Processes (Liu-Layland vs Exact RTA/EDF)", fontsize=11)
    ax.legend(loc="lower left", fontsize=8.2)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex3_fig6_utilization_regions.png"))


def fig7_paper_decision_tree(data: dict) -> None:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)

    def box(x, y, w, h, text, fc, ec="#1e293b", fsz=8.2):
        p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.14", fc=fc, ec=ec, lw=1.3)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fsz, fontweight="bold", color="#0f172a")

    def arrow(x1, y1, x2, y2, lbl=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.4))
        if lbl:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.14, lbl, ha="center", va="center", fontsize=7.8,
                    bbox=dict(fc="white", ec="none", pad=0.8), color="#1e293b", fontweight="bold")

    box(3.3, 4.9, 3.4, 0.8, "Step 1: At tick t, add jobs where\nt mod T_i == 0; set d = t + D_i", "#e0f2fe", "#0369a1")
    box(3.3, 3.55, 3.4, 0.8, "Step 2: Check Misses & Ready Set\nAny active job with t >= d and rem > 0?", "#fef3c7", "#b45309")
    arrow(5.0, 4.9, 5.0, 4.35)

    box(0.4, 2.0, 3.3, 0.95, "EDF Rule (Dynamic)\nPick job with smallest d\nTie-break: P1 < P2 < P3", "#dbeafe", "#1d4ed8")
    box(6.3, 2.0, 3.3, 0.95, "RM Rule (Static)\nPick job with smallest T_i\n(Always P1 > P2 > P3)", "#fce7f3", "#be185d")
    arrow(4.1, 3.55, 2.1, 2.95, "Ready != empty")
    arrow(5.9, 3.55, 7.9, 2.95, "Ready != empty")

    box(0.25, 0.45, 4.45, 0.98, "Set A Divergence (t=4): P3#0 (d=6) beats P2#1 (d=8)\nunder EDF; RM preempts P3#0 since T_2=4 < T_3=6", "#ecfdf5", "#047857", fsz=7.7)
    box(5.3, 0.45, 4.45, 0.98, "Set B Failure (t=6..8): RM gives t=6,7 to P2#1 (T=6)\nleaving P3#0 short by 1 tick -> MISS @ t=8!", "#fee2e2", "#b91c1c", fsz=7.7)
    arrow(2.0, 2.0, 2.45, 1.4)
    arrow(8.0, 2.0, 7.55, 1.4)

    ax.set_title("Hand-Worked Paper Scheduling Flowchart: Tick-by-Tick Ready-Queue Protocol", fontsize=11.5, fontweight="bold")
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex3_fig7_paper_decision_tree.png"))


def fig8_gs_vtime_bridge(data: dict) -> None:
    pk.apply_style()
    s = data["set_b"]
    H = s["horizon"]
    tasks = ["P1", "P2", "P3"]
    algs = [
        ("EDF (0 misses)", s["edf"]["timeline"]),
        ("RM (1 miss @ t=8)", s["rm"]["timeline"]),
        ("GS_vtime (0 misses)", s["gs_vtime_ref"]["timeline"]),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(11.2, 5.4), sharex=True, gridspec_kw={"hspace": 0.34})
    for ax, (title, tl) in zip(axes, algs):
        for t in range(H):
            lbl = tl[t]
            owner = lbl.split("#")[0] if lbl != "IDLE" else "IDLE"
            y = 2 - tasks.index(owner) if owner in tasks else 0
            if owner in tasks:
                ax.add_patch(patches.Rectangle((t, y + 0.12), 1.0, 0.76,
                                               facecolor=TASK_COLORS[owner], edgecolor="#1e293b", lw=0.6))
                ax.text(t + 0.5, y + 0.5, lbl.split("#")[1], ha="center", va="center",
                        color="white", fontsize=6.8, fontweight="bold")
            else:
                ax.add_patch(patches.Rectangle((t, 0.1), 1.0, 2.8, facecolor="#f1f5f9", hatch="//", edgecolor="#94a3b8", lw=0.5))
        ax.set_xlim(0, H)
        ax.set_ylim(0, 3)
        ax.set_yticks([0.5, 1.5, 2.5])
        ax.set_yticklabels(["P3", "P2", "P1"])
        ax.set_xticks(range(0, H + 1))
        ax.set_title(title, loc="left", fontsize=9.8, pad=4)
    axes[-1].set_xlabel("Tick t in Set B (H=24, U=23/24=0.9583): GS_vtime preserves deadline feasibility without knowing deadlines")
    fig.suptitle("Bridge to Guaranteed Scheduling (Ex 1-2): EDF vs RM vs GS_vtime on Set B (H=24)", fontsize=11.5, fontweight="bold", y=0.99)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex3_fig8_gs_vtime_bridge.png"))


def main() -> None:
    with open(OUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    _draw_two_panel_gantt(
        data["set_a"],
        "ex3_fig1_paper_gantt_setA.png",
        "Set A Hand-Worked Schedule (H=12, U=11/12=0.917): EDF vs RM (Both 0 Misses, Diverge at t=4..5)",
    )
    _draw_two_panel_gantt(
        data["set_b"],
        "ex3_fig2_paper_gantt_setB.png",
        "Set B Hand-Worked Schedule (H=24, U=23/24=0.958): EDF (0 Misses) vs RM (P3#0 Misses at t=8)",
    )
    fig3_rta_fixed_point(data)
    fig4_dbf_curve(data)
    fig5_overload_domino(data)
    fig6_utilization_regions(data)
    fig7_paper_decision_tree(data)
    fig8_gs_vtime_bridge(data)
    print("Generated 8 PNG figures in", DIAG_DIR)


if __name__ == "__main__":
    main()
