"""Generate all 6 publication-grade figures for Exercise 2 from experiments.json."""
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
EX2_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX2_DIR)
DATA_PATH = os.path.join(EX2_DIR, "output", "experiments.json")
DIAG_DIR = os.path.join(EX2_DIR, "diagrams")
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


def fig1_taxonomy():
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(11.5, 5.2), dpi=220)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 5.3)
    ax.axis("off")

    ax.text(5.75, 5.05, "Scheduling Algorithms Compared in Exercise 2: Metric vs Regime Domain",
            ha="center", va="top", fontsize=12.2, fontweight="bold", color=C["black"])

    pk.draw_box(ax, 1.95, 3.65, 3.25, 1.55,
                "1. Proportional Share [GS / Stride]\ngs_ratio: min(used / w_i)\ngs_vtime: min(v_i), dv = 1/w_i\nstride: pass += S / w_i\nGoal: |A_i(t) - E_i(t)| <= O(q)",
                fc="#eef5fc", ec=C["blue"], tc=C["black"], fontsize=8.1)

    pk.draw_box(ax, 5.75, 3.65, 3.25, 1.55,
                "2. Real-Time Urgency [EDF/DM/RM]\nEDF: min(abs_deadline) [Dynamic]\nDM:  min(rel_deadline) [Static]\nRM:  min(period T_i)    [Static]\nGoal: Zero missed deadlines",
                fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=8.1)

    pk.draw_box(ax, 9.55, 3.65, 3.25, 1.55,
                "3. Unweighted Baselines [RR/FIFO]\nRR(q): cyclic slice = q\nFIFO: non-preemptive arrival\nIgnores both weight w_i and D_i\nOverhead & fairness floor",
                fc="#fff5ed", ec=C["orange"], tc=C["black"], fontsize=8.1)

    pk.draw_box(ax, 1.95, 1.15, 3.25, 1.45,
                "Regime A: Static Batch [M]\nAll arrive t=0, weighted w_i\nGS & Stride track Ideal GPS\nRR & FIFO drift with weight skew",
                fc="#f4f6fa", ec=C["sky"], tc=C["black"], fontsize=8.0)

    pk.draw_box(ax, 5.75, 1.15, 3.25, 1.45,
                "Regime B: Constrained D < T [E]+[M]\nU <= 1 NOT sufficient when D < T\nEDF matches exhaustive [E] 100%\nDM > RM; GS misses urgent bursts",
                fc="#f4f6fa", ec=C["green"], tc=C["black"], fontsize=8.0)

    pk.draw_box(ax, 9.55, 1.15, 3.25, 1.45,
                "Regime C: Overload U > 1.0 [M]\nRM/DM starve T3 (0 CPU ticks)\nEDF suffers domino cascade\ngs_vtime preserves weighted shares",
                fc="#fdf2f0", ec=C["red"], tc=C["black"], fontsize=8.0)

    pk.draw_arrow(ax, 1.95, 2.74, 1.95, 2.02, "GPS bound", label_offset=(-0.82, 0.0), color=C["blue"])
    pk.draw_arrow(ax, 5.75, 2.74, 5.75, 2.02, "D < T urgency", label_offset=(-0.88, -0.22), color=C["green"])
    pk.draw_arrow(ax, 3.4, 2.74, 8.2, 2.02, "overload shield", label_offset=(-0.55, 0.24), color=C["red"])
    pk.draw_arrow(ax, 7.1, 2.74, 9.2, 2.02, "starvation risk", label_offset=(0.82, 0.08), color=C["orange"])

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex2_taxonomy.png"))


def fig2_regime_a_proportional(d):
    pk.apply_style()
    runs = d["regime_a_proportional"]["runs"]
    keys = ["gs_ratio_q1", "gs_vtime_q1", "stride_q1", "gs_ratio_q2", "rr_q1", "rr_q2", "fifo_q1"]
    labels = ["gs_ratio\n(q=1)", "gs_vtime\n(q=1)", "stride\n(q=1)", "gs_ratio\n(q=2)",
              "RR\n(q=1)", "RR\n(q=2)", "FIFO\n(q=1)"]
    lags = [runs[k]["max_abs_lag"] for k in keys]
    rmses = [runs[k]["rmse_lag"] for k in keys]
    colors = [C["blue"], C["sky"], C["green"], C["purple"], C["orange"], C["yellow"], C["red"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.6), dpi=220)
    x = np.arange(len(keys))
    w = 0.38
    b1 = ax1.bar(x - w / 2, lags, width=w, color=colors, edgecolor="#333", linewidth=0.6, label="Max |Lag|")
    ax1.bar(x + w / 2, rmses, width=w, color=colors, alpha=0.45, edgecolor="#333",
            linewidth=0.6, hatch="//", label="Lag RMSE")
    for bar, val in zip(b1, lags):
        ax1.text(bar.get_x() + bar.get_width() / 2, val + 0.18, f"{val:.2f}",
                 ha="center", va="bottom", fontsize=7.8, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.2)
    ax1.set_ylim(0, max(lags) * 1.2)
    ax1.set_ylabel("GPS Service Lag (ticks)", fontsize=9.5)
    ax1.set_title("Service Lag & RMSE (Regime A: weights [1, 2, 4, 3])", fontsize=10.2, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.3)

    pcolors = {"P1": C["blue"], "P2": C["orange"], "P3": C["green"], "P4": C["purple"]}
    show = [("gs_vtime_q1", "gs_vtime (q=1)"), ("rr_q1", "RR (q=1)"), ("fifo_q1", "FIFO (q=1)")]
    for idx, (k, _) in enumerate(show):
        y = len(show) - 1 - idx
        for name, st, en in runs[k]["gantt"]:
            if st >= 25:
                continue
            e_clip = min(en, 25)
            ax2.barh(y, e_clip - st, left=st, height=0.58, color=pcolors[name],
                     edgecolor="white", linewidth=0.8)
            if e_clip - st >= 1.5:
                ax2.text(0.5 * (st + e_clip), y, name, ha="center", va="center",
                         color="white", fontsize=7.5, fontweight="bold")
    ax2.set_yticks([2, 1, 0])
    ax2.set_yticklabels([t for _, t in show], fontsize=9)
    ax2.set_xlim(0, 25)
    ax2.set_xlabel("Time (integer ticks, first 25 ticks shown)", fontsize=9.5)
    ax2.set_title("Early Allocation Slice Order (Switches: GS=45, RR=42, FIFO=4)", fontsize=10.2, fontweight="bold")
    ax2.grid(axis="x", linestyle=":", alpha=0.5)
    leg_patches = [patches.Patch(color=pcolors[n], label=f"{n} (w={[1,2,4,3][i]})")
                   for i, n in enumerate(["P1", "P2", "P3", "P4"])]
    ax2.legend(handles=leg_patches, loc="lower right", ncol=2, fontsize=7.8, framealpha=0.92)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex2_regime_a_proportional.png"))


def fig3_constrained_gantt(d):
    pk.apply_style()
    b2 = d["regime_b_constrained_cases"]["b2_edf_vs_dm_gs"]
    H = b2["horizon"]
    pols = [("edf", "EDF (0 misses — Optimal)"),
            ("dm", "DM (2 misses)"),
            ("rm", "RM (2 misses)"),
            ("gs_vtime", "gs_vtime (4 misses)")]
    tcolors = {"T1": C["blue"], "T2": C["green"], "T3": C["orange"]}

    fig, axes = plt.subplots(4, 1, figsize=(11.5, 6.2), dpi=220, sharex=True)
    fig.suptitle("Constrained-Deadline Separation B2 (T1:6/3/4, T2:8/3/7, T3:12/1/10 | U=0.958)",
                 fontsize=11.5, fontweight="bold", y=0.98)

    jobs = b2["jobs"]
    for ax, (pk_name, title) in zip(axes, pols):
        r = b2["runs"][pk_name]
        fin = {}
        for jname, st, en in r["gantt"]:
            fin[jname] = max(fin.get(jname, 0), en)
        row_map = {"T1": 2, "T2": 1, "T3": 0}
        for jname, st, en in r["gantt"]:
            tname = jname.split("#")[0]
            y = row_map[tname]
            jmeta = next(j for j in jobs if j["name"] == jname)
            missed = fin[jname] > jmeta["deadline"]
            col = C["red"] if missed else tcolors[tname]
            ax.barh(y, en - st, left=st, height=0.58, color=col, edgecolor="white", linewidth=0.8)
            if en - st >= 1:
                ax.text(0.5 * (st + en), y, jname, ha="center", va="center",
                        color="white", fontsize=7.2, fontweight="bold")
        for j in jobs:
            y = row_map[j["task"]]
            if j["deadline"] <= H:
                ax.plot(j["deadline"], y + 0.34, marker="v", markersize=5.5,
                        color=C["red"] if fin.get(j["name"], 999) > j["deadline"] else "#333333")
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(["T3", "T2", "T1"], fontsize=8.5)
        ax.set_ylim(-0.48, 2.58)
        ax.set_title(title, loc="left", fontsize=9.5, fontweight="bold",
                     color=C["green"] if r["missed"] == 0 else C["red"])
        ax.grid(axis="x", linestyle=":", alpha=0.5)

    axes[-1].set_xlim(0, H)
    axes[-1].set_xticks(range(0, H + 1, 2))
    axes[-1].set_xlabel("Time (integer ticks; inverted triangles mark job deadlines; red = missed deadline)",
                        fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex2_constrained_gantt.png"))


def fig4_constrained_sweep(d):
    pk.apply_style()
    sw = d["regime_b_sweep_120"]
    bands = sw["bands"]
    x = np.arange(len(bands))
    blabels = [f"U in {b['band']}\n(n={b['n_sets']})" for b in bands]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.7), dpi=220)
    curves = [
        ("edf", "EDF", C["green"], "-o"),
        ("dm", "DM (Deadline Mono.)", C["blue"], "-s"),
        ("rm", "RM (Rate Mono.)", C["sky"], "--^"),
        ("gs_vtime_density", "gs_vtime (w~C/D)", C["purple"], "-D"),
        ("gs_vtime", "gs_vtime (equal w)", C["orange"], "-v"),
        ("rr", "Round Robin", C["red"], ":x"),
    ]
    for k, lbl, col, fmt in curves:
        vals = [b["success_pct"][k] for b in bands]
        ax1.plot(x, vals, fmt, color=col, linewidth=2.0, markersize=6, label=lbl)
    ax1.set_xticks(x)
    ax1.set_xticklabels(blabels, fontsize=8.3)
    ax1.set_ylim(-4, 108)
    ax1.set_ylabel("Zero-Miss Task Sets (%)", fontsize=9.5)
    ax1.set_title("Constrained-Deadline (D < T) Sweep Across 120 Task Sets [M]", fontsize=10.2, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="lower left", fontsize=8.0, framealpha=0.92)

    ex = sw["exhaustive_audit_30"]
    cats = ["Exhaustive\nTrue [E]", "EDF", "DM", "RM", "gs_vtime\n(equal w)"]
    cnts = [ex["exhaustive_feasible"], ex["edf_feasible"], ex["dm_feasible"],
            ex["rm_feasible"], ex["gs_feasible"]]
    bcols = [C["black"], C["green"], C["blue"], C["sky"], C["orange"]]
    bars = ax2.bar(np.arange(len(cats)), cnts, color=bcols, width=0.56, edgecolor="#333", linewidth=0.7)
    for bar, v in zip(bars, cnts):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.35,
                 f"{v}/{ex['n_sets']}\n({100*v/ex['n_sets']:.0f}%)",
                 ha="center", va="bottom", fontsize=8.0, fontweight="bold")
    ax2.set_xticks(np.arange(len(cats)))
    ax2.set_xticklabels(cats, fontsize=8.5)
    ax2.set_ylim(0, max(cnts) * 1.35)
    ax2.set_ylabel(f"Feasible Sets (out of {ex['n_sets']})", fontsize=9.5)
    ax2.set_title("Exact Exhaustive Feasibility Audit [E]: EDF = 100% Optimal", fontsize=10.2, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex2_constrained_sweep.png"))


def fig5_overload_domino(d):
    pk.apply_style()
    ov = d["regime_c_overload"]
    H = ov["horizon"]
    runs = ov["runs_asym"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.8), dpi=220,
                                   gridspec_kw={"width_ratios": [1.35, 1.0]})
    pols = [("rm", "RM (T3 starved = 0!)"), ("edf", "EDF (domino misses)"),
            ("gs_ratio", "gs_ratio (used/w bias)"), ("gs_vtime", "gs_vtime (4:2:1 shared)")]
    tcolors = {"T1": C["blue"], "T2": C["orange"], "T3": C["green"]}
    for idx, (pk_name, _) in enumerate(pols):
        y = len(pols) - 1 - idx
        for jname, st, en in runs[pk_name]["gantt"]:
            tname = jname.split("#")[0]
            ax1.barh(y, en - st, left=st, height=0.58, color=tcolors[tname],
                     edgecolor="white", linewidth=0.7)
            if en - st >= 1.5:
                ax1.text(0.5 * (st + en), y, tname, ha="center", va="center",
                         color="white", fontsize=7.2, fontweight="bold")
    ax1.set_yticks([3, 2, 1, 0])
    ax1.set_yticklabels([lbl for _, lbl in pols], fontsize=8.6)
    ax1.set_xlim(0, H)
    ax1.set_xticks(range(0, H + 1, 3))
    ax1.set_xlabel("Time (integer ticks, sustained overload U = 1.333)", fontsize=9.2)
    ax1.set_title("Overload Schedule (Weights [4, 2, 1])", fontsize=10.2, fontweight="bold", pad=22)
    ax1.grid(axis="x", linestyle=":", alpha=0.5)
    ax1.legend(handles=[patches.Patch(color=tcolors[k], label=f"{k} (w={w})")
                        for k, w in zip(["T1", "T2", "T3"], ov["asymmetric_weights"])],
               loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=3, fontsize=7.8, framealpha=0.95)

    pkeys = ["gs_vtime", "stride", "edf", "rr", "gs_ratio", "rm"]
    plbls = ["gs_vtime", "Stride", "EDF", "RR", "gs_ratio", "RM / DM"]
    jains = [runs[k]["jain_fairness"] for k in pkeys]
    minsrs = [runs[k]["min_task_share_ratio"] for k in pkeys]
    x = np.arange(len(pkeys))
    w = 0.37
    b1 = ax2.bar(x - w / 2, jains, width=w, color=C["blue"], edgecolor="#333", linewidth=0.6, label="Jain Fairness")
    b2 = ax2.bar(x + w / 2, minsrs, width=w, color=C["green"], edgecolor="#333", linewidth=0.6, label="Min Task Share Ratio")
    for bar, v in zip(b1, jains):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.2f}",
                 ha="center", va="bottom", fontsize=7.2)
    for bar, v in zip(b2, minsrs):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.02, f"{v:.2f}",
                 ha="center", va="bottom", fontsize=7.2)
    ax2.set_xticks(x)
    ax2.set_xticklabels(plbls, fontsize=8.2, rotation=15)
    ax2.set_ylim(0, 1.18)
    ax2.set_ylabel("Fairness / Entitlement Ratio", fontsize=9.2)
    ax2.set_title("Overload Fairness Preservation (U = 1.333)", fontsize=10.2, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=8.0)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex2_overload_domino.png"))


def fig6_tradeoff_profile(d):
    pk.apply_style()
    bands = d["regime_b_sweep_120"]["bands"]
    b_mid = [bands[1], bands[2]]
    ov_asym = d["regime_c_overload"]["runs_asym"]
    reg_a = d["regime_a_proportional"]["runs"]

    pts = [
        ("edf", "EDF\n(Deadline-optimal)", C["green"], "o", (-2.0, -0.036), None),
        ("dm", "DM", C["blue"], "s", (4.2, 0.022), None),
        ("rm", "RM", C["sky"], "^", (-4.2, 0.022), None),
        ("gs_vtime_density", "gs_vtime (w~C/D)", C["purple"], "D", (8.5, -0.026), None),
        ("gs_vtime", "gs_vtime (equal/proport.)", C["orange"], "v", (6.5, 0.026), reg_a["gs_vtime_q1"]["max_abs_lag"]),
        ("stride", "Stride", C["yellow"], "P", (5.5, -0.028), reg_a["stride_q1"]["max_abs_lag"]),
        ("rr", "Round Robin", C["red"], "X", (5.8, -0.026), reg_a["rr_q1"]["max_abs_lag"]),
    ]

    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=220)
    for key, lbl, col, marker, off, lag in pts:
        rt_rate = 0.5 * (b_mid[0]["success_pct"][key] + b_mid[1]["success_pct"][key])
        ov_key = "gs_vtime" if key == "gs_vtime_density" else key
        ov_jain = ov_asym[ov_key]["jain_fairness"]
        ax.scatter(rt_rate, ov_jain, s=140, color=col, marker=marker, edgecolors="#222", linewidth=0.9, zorder=5)
        txt = lbl if lag is None else f"{lbl}\n(Reg.A lag={lag:.2f})"
        ax.annotate(txt, (rt_rate, ov_jain),
                    xytext=(rt_rate + off[0], ov_jain + off[1]),
                    fontsize=8.3, fontweight="bold", color=col,
                    ha="center", va="center")

    ax.axhspan(0.95, 1.03, color=C["green"], alpha=0.07)
    ax.axvspan(55, 85, color=C["blue"], alpha=0.06)
    ax.text(83, 1.018, "High RT Feasibility + Fair", ha="right", va="top",
            fontsize=8.5, color=C["green"], style="italic")
    ax.text(30, 0.59, "RM / DM starve low-priority tasks under overload",
            ha="left", va="bottom", fontsize=8.3, color=C["blue"], style="italic")

    ax.set_xlim(5, 85)
    ax.set_ylim(0.56, 1.04)
    ax.set_xlabel("Constrained-Deadline (D < T) Zero-Miss Rate in U in [0.75, 0.95] (%)", fontsize=9.8)
    ax.set_ylabel("Overload Fairness Preservation (Jain Index at U = 1.333)", fontsize=9.8)
    ax.set_title("No Single Winner: Real-Time Deadline Guarantees vs Overload Proportional Fairness",
                 fontsize=10.8, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex2_tradeoff_profile.png"))


def main():
    d = load_data()
    fig1_taxonomy()
    fig2_regime_a_proportional(d)
    fig3_constrained_gantt(d)
    fig4_constrained_sweep(d)
    fig5_overload_domino(d)
    fig6_tradeoff_profile(d)
    print("Generated 6 Exercise 2 diagrams cleanly in", DIAG_DIR)


if __name__ == "__main__":
    main()
