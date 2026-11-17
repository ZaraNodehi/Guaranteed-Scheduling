"""Generate 6 crisp publication figures for Exercise 4 from experiments.json."""
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
EX4_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX4_DIR)
DATA_PATH = os.path.join(EX4_DIR, "output", "experiments.json")
DIAG_DIR = os.path.join(EX4_DIR, "diagrams")
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


def fig1_proof_map(d):
    pk.apply_style()
    t1 = d["theorem1_lag_bounds"]
    t2 = d["theorem2_starvation_scaling"]
    t3 = d["theorem3_exhaustive_rt"]
    t4 = d["theorem4_overload"]

    fig, ax = plt.subplots(figsize=(11.6, 5.2), dpi=220)
    ax.set_xlim(0, 11.6)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    ax.text(5.8, 4.96, "Exercise 4 Formal Correctness Architecture: Theorems, Exhaustive Proofs & Counterexamples",
            ha="center", va="top", fontsize=11.6, fontweight="bold", color=C["black"])

    pk.draw_box(ax, 2.6, 3.45, 4.75, 1.55,
                f"Theorem 1 [E]+[M]+[D]: SFQ vs PGPS Lag Bounds\n120 static sets: start-time gs:index exceeds q in {t1['violations_above_q']['gs_vtime:index']}/120 cases\nTight SFQ bound = max(q, (n-1)*q*w_max/W) = 21/16 on [1,3,5,7]\ngs_vtime:max_weight & WFQ finish achieve 0/120 violations (<=0.9375q)",
                fc="#eef5fc", ec=C["blue"], tc=C["black"], fontsize=7.8)

    pk.draw_box(ax, 9.0, 3.45, 4.75, 1.55,
                f"Theorem 2 [E]+[D]: Dynamic Starvation Scaling\ngs_ratio suffers Omega(t_arr) lag = t_arr/2 (gap = {t2['scaling_rows'][-1]['gs_ratio_gap']} at t=32)\ngs_vtime (v_i <- V(t)) proves O(1) constant lag = {t2['scaling_rows'][-1]['gs_vtime_lag']} (gap={t2['scaling_rows'][-1]['gs_vtime_gap']})\ngs_entitled bounds gap = {t2['scaling_rows'][-1]['gs_entitled_gap']} across all arrival delays",
                fc="#fdf2f0", ec=C["red"], tc=C["black"], fontsize=7.8)

    pk.draw_box(ax, 2.6, 1.2, 4.75, 1.55,
                f"Theorem 3 [E]: Exhaustive RT State-Space Feasibility\n{t3['n_sets']} constrained & overload sets: {t3['feasible_count']} feasible, {t3['infeasible_count']} infeasible\n100% ({t3['independent_verified_count']}/{t3['feasible_count']}) passed independent verifier; EDF 100% matches exact DFS\nContrasts work-conserving vs allow_idle=True search trees",
                fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=7.8)

    u20 = t4["sweep"][-1]["policies"]
    pk.draw_box(ax, 9.0, 1.2, 4.75, 1.55,
                f"Theorem 4 [M]: Overload Fairness Lower Bound\nAcross U = 1.08 .. 2.00: RM starves Low task (min_sr = {u20['rm']['min_sr']:.2f})\ngs_vtime sustains Jain = {u20['gs_vtime_eq']['jain']:.3f}, min_sr = {u20['gs_vtime_eq']['min_sr']:.3f} at U=2.00\nGraceful proportional degradation beats fixed-priority collapse",
                fc="#fff5ed", ec=C["orange"], tc=C["black"], fontsize=7.8)

    pk.draw_arrow(ax, 4.98, 3.45, 6.62, 3.45, "static->dyn", label_offset=(0.0, 0.28), color=C["black"])
    pk.draw_arrow(ax, 2.6, 2.65, 2.6, 2.00, "DFS proof", label_offset=(-0.72, 0.0), color=C["blue"])
    pk.draw_arrow(ax, 9.0, 2.65, 9.0, 2.00, "U>1 bound", label_offset=(0.72, 0.0), color=C["orange"])
    pk.draw_arrow(ax, 4.98, 1.2, 6.62, 1.2, "U<=1 -> U>1", label_offset=(0.0, 0.28), color=C["green"])

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_proof_map.png"))


def fig2_lag_bound_audit(d):
    pk.apply_style()
    t1 = d["theorem1_lag_bounds"]
    pols = ["eevdf", "wfq_finish", "gs_vtime:max_weight", "gs_vtime:index", "stride:index", "rr:index", "fifo:index"]
    labels = ["EEVDF\n(elig+vd)", "WFQ\n(finish)", "gs_vtime\n(max_w)", "gs_vtime\n(index)", "Stride\n(index)", "RR\n(unwtd)", "FIFO\n(batch)"]
    colors = ["#0f766e", C["green"], C["sky"], C["orange"], C["purple"], C["yellow"], C["red"]]

    viols = [t1["violations_above_q"][p] for p in pols]
    ratios = [t1["max_lag_over_q"][p] for p in pols]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.5), dpi=220)
    x = np.arange(len(pols))
    b1 = ax1.bar(x, viols, color=colors, width=0.58, edgecolor="#333", linewidth=0.7)
    for bar, v in zip(b1, viols):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 2.0, f"{v}/120",
                 ha="center", va="bottom", fontsize=8.3, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.3)
    ax1.set_ylim(0, 118)
    ax1.set_ylabel("Workloads Exceeding |L_i(t)| <= q", fontsize=9.2)
    ax1.set_title("Naive Bound Violations Across 120 Static Cases [E]+[D]", fontsize=10.0, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)

    b2 = ax2.bar(x, ratios, color=colors, width=0.58, edgecolor="#333", linewidth=0.7)
    ax2.axhline(1.0, color=C["black"], linestyle="--", linewidth=1.2, label="Naive q bound (1.0x)")
    for bar, v in zip(b2, ratios):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.5, f"{v:.2f}x",
                 ha="center", va="bottom", fontsize=8.2, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.3)
    ax2.set_ylim(0, max(ratios) * 1.15)
    ax2.set_ylabel("Worst Normalized Lag max |L_i(t)| / q", fontsize=9.2)
    ax2.set_title("Worst-Case Normalized Lag Ratio (q in {1, 2, 3})", fontsize=10.0, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8.3)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_lag_bound_audit.png"))


def fig3_starvation_scaling(d):
    pk.apply_style()
    rows = d["theorem2_starvation_scaling"]["scaling_rows"]
    ts = [r["t_arrival"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    ax1.plot(ts, [r["gs_ratio_lag"] for r in rows], "o-", color=C["red"], linewidth=2.2, label="gs_ratio max lag (= t_arr / 2)")
    ax1.plot(ts, [r["gs_entitled_lag"] for r in rows], "s--", color=C["orange"], linewidth=2.0, label="gs_entitled max lag (0.5)")
    ax1.plot(ts, [r["gs_vtime_lag"] for r in rows], "^-", color=C["green"], linewidth=2.0, label="gs_vtime max lag (0.5)")
    ax1.set_xlabel("Latecomer Arrival Time t_arr (ticks)", fontsize=9.2)
    ax1.set_ylabel("Max Absolute GPS Lag (ticks)", fontsize=9.2)
    ax1.set_title("Theorem 2: Omega(t_arr) Lag Explosion vs O(1) Bound", fontsize=10.0, fontweight="bold")
    ax1.set_xticks(ts)
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.3)

    ax2.plot(ts, [r["gs_ratio_gap"] for r in rows], "o-", color=C["red"], linewidth=2.2, label="gs_ratio P1 starve gap (= t_arr)")
    ax2.plot(ts, [r["gs_entitled_gap"] for r in rows], "s--", color=C["orange"], linewidth=2.0, label="gs_entitled max gap (= 2)")
    ax2.plot(ts, [r["gs_vtime_gap"] for r in rows], "^-", color=C["green"], linewidth=2.0, label="gs_vtime max gap (= 1)")
    ax2.set_xlabel("Latecomer Arrival Time t_arr (ticks)", fontsize=9.2)
    ax2.set_ylabel("Max Consecutive Lockout Gap (ticks)", fontsize=9.2)
    ax2.set_title("Longest Consecutive Lockout Duration vs Arrival Delay", fontsize=10.0, fontweight="bold")
    ax2.set_xticks(ts)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8.3)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_starvation_scaling.png"))


def fig4_rt_exhaustive_map(d):
    pk.apply_style()
    sets = d["theorem3_exhaustive_rt"]["sets"]
    names = [s["name"].replace("_", "\n", 1) for s in sets]
    x = np.arange(len(sets))
    st_wc = [s["states_wc"] for s in sets]
    st_id = [s["states_idle"] for s in sets]
    feas = [s["exhaustive_wc_feasible"] for s in sets]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12.2, 5.8), dpi=220, sharex=True)
    w = 0.36
    ax1.bar(x - w / 2, st_wc, width=w, color=C["blue"], label="Work-conserving DFS states (allow_idle=False)")
    ax1.bar(x + w / 2, st_id, width=w, color=C["orange"], alpha=0.85, label="Deliberate-idle DFS states (allow_idle=True)")
    ax1.set_yscale("log")
    ax1.set_ylabel("DFS States Explored (log scale)", fontsize=9.2)
    ax1.set_title("Theorem 3: Exhaustive State-Space Complexity & EDF/DM/GS Misses Across 15 RT Sets [E]",
                  fontsize=10.5, fontweight="bold")
    ax1.legend(loc="upper left", fontsize=8.3)
    ax1.grid(axis="y", linestyle=":", alpha=0.5)

    ax2.plot(x, [s["edf_missed"] for s in sets], "o-", color=C["green"], linewidth=2.0, label="EDF misses")
    ax2.plot(x, [s["dm_missed"] for s in sets], "s--", color=C["sky"], linewidth=1.8, label="DM misses")
    ax2.plot(x, [s["gs_vtime_missed"] for s in sets], "^:", color=C["red"], linewidth=2.0, label="gs_vtime misses")
    for idx_s, ok in enumerate(feas):
        if not ok:
            ax2.axvspan(idx_s - 0.45, idx_s + 0.45, color="#fee2e2", alpha=0.55, zorder=0)
    ax2.text(12.0, max(s["gs_vtime_missed"] for s in sets) * 0.88,
             "Shaded = Exhaustively Infeasible [E]",
             ha="center", va="center", fontsize=8.4, fontweight="bold", color=C["red"])
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, fontsize=7.3, rotation=22, ha="right")
    ax2.set_ylabel("Deadline Misses in Hyperperiod", fontsize=9.2)
    ax2.set_xlabel("Constrained & Overload Real-Time Task Sets (F01..F10 Feasible, I01..I05 Infeasible)", fontsize=9.2)
    ax2.legend(loc="upper left", fontsize=8.3)
    ax2.grid(True, linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_rt_exhaustive_map.png"))


def fig5_overload_graceful(d):
    pk.apply_style()
    sw = d["theorem4_overload"]["sweep"]
    us = [r["utilization"] for r in sw]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    styles = [
        ("gs_vtime_eq", "gs_vtime (equal w)", C["green"], "o-"),
        ("gs_ratio_eq", "gs_ratio (equal w)", C["orange"], "s--"),
        ("edf", "EDF", C["sky"], "^-."),
        ("rm", "Rate Monotonic (RM)", C["red"], "D:"),
    ]
    for k, lbl, col, mk in styles:
        ax1.plot(us, [r["policies"][k]["jain"] for r in sw], mk, color=col, linewidth=2.1, label=lbl)
        ax2.plot(us, [r["policies"][k]["min_sr"] for r in sw], mk, color=col, linewidth=2.1, label=lbl)

    ax1.set_xlabel("Total RT Utilization U = sum(C_i / T_i)", fontsize=9.2)
    ax1.set_ylabel("Jain Fairness Index", fontsize=9.2)
    ax1.set_ylim(0.35, 1.05)
    ax1.set_title("Theorem 4: Overload Jain Fairness Degradation (H=24)", fontsize=10.0, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="lower left", fontsize=8.2)

    ax2.set_xlabel("Total RT Utilization U = sum(C_i / T_i)", fontsize=9.2)
    ax2.set_ylabel("Minimum Task Service Ratio", fontsize=9.2)
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title("Starvation Resistance: RM Collapses to 0.00 vs Proportional GS", fontsize=10.0, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="lower left", fontsize=8.2)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_overload_graceful.png"))


def fig6_envelope_tightness(d):
    pk.apply_style()
    envs = d["theorem1_lag_bounds"]["exhaustive_tie_envelopes"]
    labels = [f"{e['case']}\n({e['leaves']} leaves)" for e in envs]
    x = np.arange(len(envs))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    best_l = [e["best_max_lag"] for e in envs]
    worst_l = [e["worst_max_lag"] for e in envs]
    theo_b = [e["sfq_theoretical_bound"] for e in envs]

    ax1.bar(x - 0.16, best_l, width=0.30, color=C["green"], label="Best tie-branch max lag")
    ax1.bar(x + 0.16, worst_l, width=0.30, color=C["orange"], label="Worst tie-branch max lag")
    ax1.plot(x, theo_b, "D--", color=C["red"], linewidth=1.8, markersize=7,
             label="SFQ bound max(1, (n-1)*w_max/W)")
    ax1.axhline(1.0, color="#64748b", linestyle=":", linewidth=1.1, label="q = 1 reference")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.1)
    ax1.set_ylim(0, 1.55)
    ax1.set_ylabel("Max Absolute Lag (ticks)", fontsize=9.2)
    ax1.set_title("Exhaustive DFS Tie Envelope vs Exact SFQ Bound [E]", fontsize=9.9, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=7.8)

    min_sw = [e["min_switches"] for e in envs]
    max_sw = [e["max_switches"] for e in envs]
    ax2.bar(x - 0.16, min_sw, width=0.30, color=C["sky"], label="Min context switches (stay)")
    ax2.bar(x + 0.16, max_sw, width=0.30, color=C["purple"], label="Max context switches (adversarial tie)")
    for xi, mn, mx in zip(x, min_sw, max_sw):
        ax2.text(xi - 0.16, mn + 0.4, str(mn), ha="center", va="bottom", fontsize=7.8)
        ax2.text(xi + 0.16, mx + 0.4, str(mx), ha="center", va="bottom", fontsize=7.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.1)
    ax2.set_ylim(0, max(max_sw) * 1.18)
    ax2.set_ylabel("Total Context Switches", fontsize=9.2)
    ax2.set_title("Exact Context-Switch Range Across All Tie Paths [E]", fontsize=9.9, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8.0)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_envelope_tightness.png"))


def fig7_witness_1357(d):
    pk.apply_style()
    w = d["theorem1_lag_bounds"]["witness_1357"]
    idx_tr = w["gs_vtime_index"]
    mw_tr = w["gs_vtime_max_weight"]
    wfq_tr = w["wfq_finish"]

    ts = list(range(1, len(idx_tr) + 1))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.5), dpi=220)

    ax1.step(ts, [r["max_abs_lag"] for r in idx_tr], where="post", color=C["red"], linewidth=2.1,
             label="gs_vtime:index (peaks 21/16 = 1.3125)")
    ax1.step(ts, [r["max_abs_lag"] for r in mw_tr], where="post", color=C["blue"], linewidth=1.9, linestyle="--",
             label="gs_vtime:max_weight (<= 15/16 = 0.9375)")
    ax1.step(ts, [r["max_abs_lag"] for r in wfq_tr], where="post", color=C["green"], linewidth=2.0, linestyle=":",
             label="WFQ/PGPS finish (<= 15/16 = 0.9375)")
    ax1.axhline(1.0, color=C["black"], linestyle="--", linewidth=1.1, label="q = 1 naive bound")
    ax1.axhline(21 / 16, color=C["red"], linestyle=":", linewidth=1.0, alpha=0.8, label="Exact SFQ bound 21/16")
    ax1.set_xlim(1, 32)
    ax1.set_ylim(0, 1.48)
    ax1.set_xticks(range(0, 33, 4))
    ax1.set_xlabel("Time (ticks across w=[1, 3, 5, 7], W=16)", fontsize=9.1)
    ax1.set_ylabel("Instantaneous Max |L_i(t)| (ticks)", fontsize=9.1)
    ax1.set_title("Counterexample Witness [1,3,5,7]: SFQ Index vs WFQ Finish", fontsize=9.9, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.45)
    ax1.legend(loc="upper right", fontsize=7.4, framealpha=0.95)

    pws = d["theorem1_lag_bounds"]["per_weight_summary"]
    x = np.arange(len(pws))
    ax2.plot(x, [p["max_lag_over_q"]["gs_vtime:index"] for p in pws], "o-", color=C["red"], linewidth=2.0,
             label="Observed gs_vtime:index max |L|/q")
    ax2.plot(x, [p["sfq_bound"] for p in pws], "D--", color=C["orange"], linewidth=1.7,
             label="Theoretical SFQ max(1, (n-1)*w_max/W)")
    ax2.plot(x, [p["max_lag_over_q"]["wfq_finish"] for p in pws], "s-", color=C["green"], linewidth=2.0,
             label="WFQ finish & max_weight (always < 1.0)")
    ax2.axhline(1.0, color=C["black"], linestyle=":", linewidth=1.0)
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(p["weights"]) for p in pws], fontsize=7.2, rotation=24, ha="right")
    ax2.set_ylabel("Max Normalized Lag |L_i(t)| / q", fontsize=9.1)
    ax2.set_ylim(0.55, 1.45)
    ax2.set_title("120-Workload Tightness: Observed Lag Matches SFQ Theory", fontsize=9.9, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.45)
    ax2.legend(loc="upper left", fontsize=7.5, framealpha=0.95)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_witness_1357.png"))


def fig8_dbf_and_weighted_overload(d):
    pk.apply_style()
    sets = d["theorem3_exhaustive_rt"]["sets"]
    sw = d["theorem4_overload"]["sweep"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.6), dpi=220)
    us_rt = [s["utilization"] for s in sets]
    dbfs = [s["max_dbf_over_L"] for s in sets]
    feas_x = [u for u, s in zip(us_rt, sets) if s["exhaustive_wc_feasible"]]
    feas_y = [r for r, s in zip(dbfs, sets) if s["exhaustive_wc_feasible"]]
    inf_x = [u for u, s in zip(us_rt, sets) if not s["exhaustive_wc_feasible"]]
    inf_y = [r for r, s in zip(dbfs, sets) if not s["exhaustive_wc_feasible"]]

    ax1.scatter(feas_x, feas_y, c=C["green"], s=75, marker="o", edgecolors="#111", label="DFS Feasible (F01..F10)", zorder=4)
    ax1.scatter(inf_x, inf_y, c=C["red"], s=85, marker="X", edgecolors="#111", label="DFS Infeasible (I01..I05)", zorder=4)
    for s in sets:
        if not s["exhaustive_wc_feasible"] or s["utilization"] > 0.9:
            tag = s["name"].split("_")[0]
            offs = (5, 4)
            if tag == "I01":
                offs = (-22, 6)
            elif tag == "I04":
                offs = (7, -3)
            elif tag == "F03":
                offs = (-24, -10)
            elif tag == "F05":
                offs = (7, -6)
            ax1.annotate(tag, (s["utilization"], s["max_dbf_over_L"]),
                         textcoords="offset points", xytext=offs, fontsize=7.4, color=C["black"])
    ax1.axhline(1.0, color=C["red"], linestyle="--", linewidth=1.2, label="Baruah dbf(L)/L = 1.0 boundary")
    ax1.axvline(1.0, color=C["blue"], linestyle=":", linewidth=1.1, label="U = 1.0 boundary")
    ax1.set_xlabel("Processor Utilization U = sum(C_i / T_i)", fontsize=9.1)
    ax1.set_ylabel("Peak Demand Ratio max_L dbf(L) / L", fontsize=9.1)
    ax1.set_xlim(0.60, 1.25)
    ax1.set_ylim(0.75, 1.55)
    ax1.set_title("Baruah dbf(L)/L <= 1 Exactly Separates Feasible vs Infeasible [E]", fontsize=9.6, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.45)
    ax1.legend(loc="upper left", fontsize=7.5, framealpha=0.95)

    us_ov = [r["utilization"] for r in sw]
    ax2.plot(us_ov, [r["weighted_gs_vtime"]["jain"] for r in sw], "o-", color=C["green"], linewidth=2.2,
             label="Weighted gs_vtime (w=[3,2,1]) Jain")
    ax2.plot(us_ov, [r["weighted_gs_vtime"]["min_sr"] for r in sw], "s--", color=C["sky"], linewidth=2.0,
             label="Weighted gs_vtime Min Share Ratio")
    ax2.plot(us_ov, [r["weighted_rm"]["jain"] for r in sw], "D:", color=C["red"], linewidth=2.1,
             label="Weighted RM (w=[3,2,1]) Jain")
    ax2.plot(us_ov, [r["weighted_rm"]["min_sr"] for r in sw], "^-.", color=C["orange"], linewidth=2.0,
             label="Weighted RM Min Share (Low=0.00!)")
    ax2.set_xlabel("Total Overload Utilization U", fontsize=9.1)
    ax2.set_ylabel("Weighted Fairness / Min Share Ratio", fontsize=9.1)
    ax2.set_ylim(-0.08, 1.08)
    ax2.set_title("Theorem 4 Extension: Weighted [3:2:1] Overload Resilience", fontsize=9.8, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.45)
    ax2.legend(loc=(0.04, 0.16), fontsize=7.5, framealpha=0.95)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex4_dbf_and_weighted_overload.png"))


def main():
    d = load_data()
    fig1_proof_map(d)
    fig2_lag_bound_audit(d)
    fig3_starvation_scaling(d)
    fig4_rt_exhaustive_map(d)
    fig5_overload_graceful(d)
    fig6_envelope_tightness(d)
    fig7_witness_1357(d)
    fig8_dbf_and_weighted_overload(d)
    print("Generated 8 Exercise 4 diagrams cleanly in", DIAG_DIR)


if __name__ == "__main__":
    main()
