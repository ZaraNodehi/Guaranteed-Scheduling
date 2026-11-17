#!/usr/bin/env python3
"""Generate all figures and charts for Exercise 1 from output/experiments.json."""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

HERE = os.path.dirname(os.path.abspath(__file__))
EX_ROOT = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import plot_kit as pk  # noqa: E402


def load_data() -> dict:
    p = os.path.join(EX_ROOT, "output", "experiments.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def fig_architecture(out_dir: str) -> str:
    """Diagram 1: Three-layer conceptual architecture (Ideal GPS vs gs_core vs OS script)."""
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(11.4, 4.9))
    ax.set_xlim(0, 11.4)
    ax.set_ylim(0, 4.9)
    ax.axis("off")

    ax.text(5.7, 4.60, "Guaranteed Scheduling: Three-Model Architecture",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color="#0f172a")

    # Left column: Ideal GPS
    pk.draw_box(ax, 1.75, 3.05, 2.75, 1.70,
                "1. Ideal Fluid GPS [Theory]\n\n"
                "dE_i / dt = w_i / sum_{j in A(t)} w_j\n"
                "Continuous infinitesimal slices\n"
                "Lag L_i(t) = 0 everywhere",
                fc="#eff6ff", ec="#1d4ed8", fontsize=8.3, bold=False)

    # Middle column: Integer-time simulator
    pk.draw_box(ax, 5.70, 3.05, 2.85, 1.70,
                "2. Deterministic gs_core [Sim / E]\n\n"
                "Integer time t, exact Fraction math\n"
                "Quantum q >= 1, explicit tie-break\n"
                "Measures lag |A_i(t) - E_i(t)|",
                fc="#ecfdf5", ec="#047857", fontsize=8.3, bold=False)

    # Right column: Real OS script
    pk.draw_box(ax, 9.65, 3.05, 2.75, 1.70,
                "3. GuaranteedScheduling.py [OS]\n\n"
                "psutil suspend() / resume()\n"
                "Key: min(used / weight)\n"
                "10ms cpu_times() + OS jitter",
                fc="#fff7ed", ec="#c2410c", fontsize=8.3, bold=False)

    # Bottom verification / comparison boxes
    pk.draw_box(ax, 3.70, 1.05, 3.45, 1.15,
                "Parekh-Gallager Lag Bound [E]\n"
                "Static arrivals: |A_i - E_i| <= O(q)\n"
                "Late arrivals under gs_ratio: UNBOUNDED",
                fc="#f8fafc", ec="#475569", fontsize=8.1)
    pk.draw_box(ax, 7.75, 1.05, 3.45, 1.15,
                "Empirical OS Discrepancy [D]\n"
                "Startup + suspend/resume latency\n"
                "shifts ratio P3/P1 vs discrete sim",
                fc="#fef2f2", ec="#b91c1c", fontsize=8.1)

    pk.draw_arrow(ax, 3.25, 3.05, 4.15, 3.05, "discretize", (0, 0.25))
    pk.draw_arrow(ax, 7.25, 3.05, 8.15, 3.05, "OS deploy", (0, 0.25))
    pk.draw_arrow(ax, 2.30, 2.08, 3.15, 1.72)
    pk.draw_arrow(ax, 5.20, 2.08, 4.25, 1.72)
    pk.draw_arrow(ax, 6.20, 2.08, 7.15, 1.72)
    pk.draw_arrow(ax, 9.10, 2.08, 8.30, 1.72)

    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_architecture.png"))


def fig_flowchart(out_dir: str) -> str:
    """Diagram 2: Execution & decision flowchart of Guaranteed Scheduling."""
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(10.4, 5.8))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    ax.text(5.2, 5.50, "Guaranteed Scheduling Decision & Dispatch Loop",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color="#0f172a")

    pk.draw_box(ax, 5.0, 4.80, 4.7, 0.64,
                "Start: Ready set R(t) at time t; used_i, weight_i, E_i",
                fc="#dbeafe", ec="#1e40af", fontsize=8.6, bold=True)
    pk.draw_box(ax, 5.0, 3.85, 4.2, 0.62,
                "Any runnable process (R(t) non-empty)?",
                fc="#fef9c3", ec="#a16207", fontsize=8.6, bold=True)
    pk.draw_box(ax, 8.75, 3.85, 2.1, 0.62,
                "Done / Wait\n(Idle tick)",
                fc="#f1f5f9", ec="#475569", fontsize=8.4)
    pk.draw_box(ax, 5.0, 2.82, 5.0, 0.74,
                "Compute score for each i in R(t):\n"
                "Static: used_i / w_i   |   Dynamic: A_i / E_i or vruntime_i",
                fc="#ecfdf5", ec="#047857", fontsize=8.4)
    pk.draw_box(ax, 5.0, 1.78, 5.0, 0.72,
                "Select j = argmin score_i (break ties via policy:\n"
                "index / stay / max_weight / edf); dispatch for <= q ticks",
                fc="#eff6ff", ec="#1d4ed8", fontsize=8.4)
    pk.draw_box(ax, 5.0, 0.70, 5.2, 0.74,
                "Update accounting: used_j += delta; V(t) += delta/sum(w)\n"
                "If rem_j == 0 remove j; else re-enter R(t + delta)",
                fc="#fff7ed", ec="#c2410c", fontsize=8.4)

    pk.draw_arrow(ax, 5.0, 4.46, 5.0, 4.18)
    pk.draw_arrow(ax, 7.12, 3.85, 7.68, 3.85, "No", (0, 0.22))
    pk.draw_arrow(ax, 5.0, 3.52, 5.0, 3.21, "Yes", (0.38, 0))
    pk.draw_arrow(ax, 5.0, 2.43, 5.0, 2.16)
    pk.draw_arrow(ax, 5.0, 1.40, 5.0, 1.09)

    # Loop-back arrow along the left side with clean margin
    ax.plot([2.38, 1.25, 1.25, 2.63], [0.70, 0.70, 4.80, 4.80],
            color="#334155", lw=1.4, zorder=2)
    ax.annotate("", xy=(2.63, 4.80), xytext=(2.42, 4.80),
                arrowprops=dict(arrowstyle="-|>,head_width=0.25,head_length=0.4",
                                color="#334155", lw=1.4))
    ax.text(0.68, 2.75, "Next\nquantum\nt + delta", ha="center", va="center",
            fontsize=8.2, fontweight="bold", color="#334155")

    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_flowchart.png"))


def fig_gantt_baseline(d: dict, out_dir: str) -> str:
    """Chart 3: Multi-panel Gantt comparison on baseline P1(w=1), P2(w=2), P3(w=3)."""
    pk.apply_style()
    runs = d["baseline"]["runs"]
    keys = [("gs_ratio_q1", "GS (used/w, q=1)"),
            ("gs_ratio_q2", "GS (used/w, q=2)"),
            ("rr_q2", "Round Robin (q=2)"),
            ("fifo_q1", "FIFO (non-preemptive)")]
    names = ["P1", "P2", "P3"]
    cmap = {n: pk.PALETTE[i] for i, n in enumerate(names)}
    fig, axes = plt.subplots(4, 1, figsize=(9.6, 5.8), sharex=True)

    for ax, (k, label) in zip(axes, keys):
        r = runs[k]
        gantt = r["gantt"]
        y_pos = {"P1": 2, "P2": 1, "P3": 0}
        for name, s, e in gantt:
            y = y_pos[name]
            rect = patches.FancyBboxPatch(
                (s + 0.04, y - 0.34), max(0.1, (e - s) - 0.08), 0.68,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                facecolor=cmap[name], edgecolor="white", lw=0.7
            )
            ax.add_patch(rect)
            if e - s > 1:
                ax.text((s + e) / 2, y, str(e - s), ha="center", va="center",
                        color="white", fontsize=7.5, fontweight="bold")
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(["P3", "P2", "P1"], fontsize=8.5, fontweight="bold")
        ax.set_ylim(-0.6, 2.6)
        ax.set_title(
            f"{label}  |  max_lag = {r['max_abs_lag']:.2f}, switches = {r['context_switches']}",
            fontsize=9.5, loc="left", pad=4
        )

    axes[-1].set_xlim(0, d["baseline"]["horizon"])
    axes[-1].set_xticks(list(range(0, d["baseline"]["horizon"] + 1, 1)))
    axes[-1].set_xlabel("Time (integer ticks)")
    fig.suptitle("Baseline Schedule Comparison: P1(w=1,work=4), P2(w=2,work=6), P3(w=3,work=9)",
                 fontsize=11.5, fontweight="bold", y=1.01)
    fig.tight_layout()
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_gantt_baseline.png"))


def fig_lag_trajectory(d: dict, out_dir: str) -> str:
    """Chart 4: Cumulative CPU A_i(t) vs Ideal GPS E_i(t) and signed lag L_i(t)."""
    pk.apply_style()
    traj = d["baseline"]["trajectory_gs_ratio_q1"]
    ts = [row["t"] for row in traj]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.4, 5.4), sharex=True)

    for i, name in enumerate(["P1", "P2", "P3"]):
        clr = pk.PALETTE[i]
        act = [row[f"{name}_actual"] for row in traj]
        gps = [row[f"{name}_gps"] for row in traj]
        lag = [row[f"{name}_lag"] for row in traj]
        ax1.step(ts, act, where="post", color=clr, lw=2.0, label=f"{name} actual A_i(t)")
        ax1.plot(ts, gps, color=clr, lw=1.3, ls="--", alpha=0.85, label=f"{name} GPS E_i(t)")
        ax2.step(ts, lag, where="post", color=clr, lw=1.7, label=f"{name} lag A_i - E_i")

    ax2.axhline(0.0, color="#334155", lw=1.0)
    ax2.axhline(1.0, color="#dc2626", lw=0.9, ls=":")
    ax2.axhline(-1.0, color="#dc2626", lw=0.9, ls=":")
    ax1.set_ylabel("Cumulative CPU units")
    ax1.set_title("Cumulative Service vs Ideal GPS (gs_ratio, q=1)")
    ax1.legend(ncol=3, fontsize=7.8, loc="upper left")
    ax2.set_ylabel("Signed Lag A_i(t) - E_i(t)")
    ax2.set_xlabel("Time (integer ticks)")
    ax2.set_xticks(ts)
    ax2.set_title("Signed Lag Envelope (Strictly Bounded within [-1, +1])")
    ax2.legend(ncol=3, fontsize=8.0, loc="lower right")
    fig.tight_layout()
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_lag_trajectory.png"))


def fig_quantum_sweep(d: dict, out_dir: str) -> str:
    """Chart 5: Quantum sweep trade-off (Max Lag & RMSE vs Context Switches)."""
    pk.apply_style()
    rows = d["quantum_sweep"]["rows"]
    qs = sorted({r["quantum"] for r in rows})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 4.1))

    for pol, lbl, mk, ls, lw in [
        ("gs_vtime", "GS (vtime / ratio)", "D", "-", 2.8),
        ("rr", "Round Robin", "o", "--", 1.8),
    ]:
        sub = sorted([r for r in rows if r["policy"] == pol], key=lambda x: x["quantum"])
        clr = pk.POLICY_COLORS[pol]
        ax1.plot(qs, [r["max_abs_lag"] for r in sub], marker=mk, lw=2.0, color=clr, label=f"{lbl} Max Lag")
        ax1.plot(qs, [r["rmse_lag"] for r in sub], marker="s", lw=1.4, ls=":", color=clr, alpha=0.85, label=f"{lbl} RMSE")
        ax2.plot(qs, [r["context_switches"] for r in sub], marker=mk, lw=lw, ls=ls, color=clr, label=lbl)

    ax1.set_xscale("log", base=2)
    ax1.set_xticks(qs)
    ax1.set_xticklabels([str(q) for q in qs])
    ax1.set_xlabel("Quantum q (ticks)")
    ax1.set_ylabel("Service Lag vs Ideal GPS (units)")
    ax1.set_title("Fairness Lag Growth with Quantum Size")
    ax1.legend(fontsize=7.8)

    ax2.set_xscale("log", base=2)
    ax2.set_xticks(qs)
    ax2.set_xticklabels([str(q) for q in qs])
    ax2.set_xlabel("Quantum q (ticks)")
    ax2.set_ylabel("Total Context Switches")
    ax2.set_title("Context-Switch Overhead Reduction")
    ax2.legend(fontsize=8.2)

    fig.tight_layout()
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_quantum_sweep.png"))


def fig_tie_envelope(d: dict, out_dir: str) -> str:
    """Chart 6: Exhaustive [E] tie-breaking bounds vs simulated policies."""
    pk.apply_style()
    eq = d["exhaustive_tie_check"]
    env = eq["equal_envelope"]
    sims = eq["equal_sim_by_tie"]

    ties = ["index", "stay", "max_weight"]
    sws = [sims[t]["context_switches"] for t in ties]
    lags = [sims[t]["max_abs_lag"] for t in ties]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.9))
    ax1.axhspan(env["min_context_switches"], env["max_context_switches"],
                color="#dbeafe", alpha=0.65, label=f"Exhaustive [E] range [{env['min_context_switches']}, {env['max_context_switches']}]")
    bars1 = ax1.bar(ties, sws, color=[pk.PALETTE[0], pk.PALETTE[2], pk.PALETTE[3]], width=0.5)
    for b, v in zip(bars1, sws):
        ax1.text(b.get_x() + b.get_width() / 2, v + 0.25, str(v), ha="center", va="bottom", fontweight="bold")
    ax1.set_ylim(0, env["max_context_switches"] + 3)
    ax1.set_ylabel("Context Switches")
    ax1.set_title("Context Switches within Exhaustive [E] Bounds")
    ax1.legend(fontsize=8.0, loc="lower right")

    ax2.axhline(env["worst_max_lag"], color="#b91c1c", ls="--", lw=1.6,
                label=f"Exhaustive [E] worst = {env['worst_max_lag']:.3f}")
    bars2 = ax2.bar(ties, lags, color=[pk.PALETTE[0], pk.PALETTE[2], pk.PALETTE[3]], width=0.5)
    for b, v in zip(bars2, lags):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.3f}", ha="center", va="bottom", fontweight="bold")
    ax2.set_ylim(0, 1.1)
    ax2.set_ylabel("Max Absolute GPS Lag")
    ax2.set_title("Lag Invariance Across Tie-Breakers")
    ax2.legend(fontsize=8.0, loc="lower right")

    fig.tight_layout()
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_tie_envelope.png"))


def fig_latecomer_teaser(d: dict, out_dir: str) -> str:
    """Chart 7: Latecomer starvation witness under gs_ratio vs gs_vtime (t_arr = 12)."""
    pk.apply_style()
    dr = d["dynamic_arrival_check"]["dyn_t12_gs_ratio"]
    dv = d["dynamic_arrival_check"]["dyn_t12_gs_vtime"]
    gap = dr["per_proc"]["P1"]["max_starve_gap"]

    fig, axes = plt.subplots(2, 1, figsize=(9.6, 4.2), sharex=True)
    y_pos = {"P1": 1, "P2": 0}
    cmap = {"P1": pk.PALETTE[0], "P2": pk.PALETTE[1]}

    for idx_ax, (ax, res, title_lbl, hl) in enumerate([
        (axes[0], dr, f"gs_ratio (used/weight): P1 starved {gap} consecutive ticks on P2 arrival at t=12", [(12, 12 + gap, f"P1 starved ({gap} ticks)")]),
        (axes[1], dv, f"gs_vtime (virtual-time anchored): P1 max starve gap = {dv['per_proc']['P1']['max_starve_gap']} tick", None),
    ]):
        # collapse runs
        runs = []
        for t, n in res["timeline"]:
            if n is None:
                continue
            if runs and runs[-1][0] == n and runs[-1][2] == t:
                runs[-1] = (n, runs[-1][1], t + 1)
            else:
                runs.append((n, t, t + 1))
        if hl:
            for xs, xe, lbl in hl:
                ax.axvspan(xs, xe, color="#fee2e2", alpha=0.7, zorder=0)
                ax.text((xs + xe) / 2, 1.38, lbl, ha="center", va="bottom",
                        fontsize=8.2, color="#991b1b", fontweight="bold")
        for n, s, e in runs:
            y = y_pos[n]
            rect = patches.FancyBboxPatch(
                (s + 0.05, y - 0.34), max(0.1, (e - s) - 0.1), 0.68,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                facecolor=cmap[n], edgecolor="white", lw=0.7
            )
            ax.add_patch(rect)
            if e - s >= 2:
                ax.text((s + e) / 2, y, str(e - s), ha="center", va="center",
                        color="white", fontsize=8, fontweight="bold")
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["P2 (arr=12, w=1)", "P1 (arr=0, w=2)"], fontweight="bold")
        ax.set_ylim(-0.6, 1.95)
        ax.set_title(title_lbl, fontsize=9.4, loc="left", pad=6)

    axes[1].set_xlim(0, dr["horizon"])
    axes[1].set_xticks(list(range(0, dr["horizon"] + 1, 4)))
    axes[1].set_xlabel("Time (integer ticks)")
    fig.suptitle("Dynamic Arrival Discrepancy: Naive gs_ratio vs Virtual-Time gs_vtime",
                 fontsize=11.5, fontweight="bold", y=1.01)
    fig.tight_layout()
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_latecomer_teaser.png"))


def fig_os_vs_sim(d: dict, out_dir: str) -> str:
    """Chart 8: Real OS subprocess trials (5 runs) vs discrete simulator prediction."""
    pk.apply_style()
    osb = d["os_subprocess_benchmark"]
    trials = osb["trials"]
    procs = ["P1", "P2", "P3"]
    weights = osb["weights"]
    labels = [f"{p} (w={w})" for p, w in zip(procs, weights)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 4.1))

    # Left: Normalized completion ratios (OS individual trials + median vs Sim)
    x = [0, 1, 2]
    for tidx, tr in enumerate(trials):
        p1_t = tr["runtimes_sec"]["P1"]
        vals = [tr["runtimes_sec"][p] / p1_t for p in procs]
        ax1.scatter(x, vals, color="#94a3b8", s=38, alpha=0.8, zorder=3,
                    label="OS trials (n=5)" if tidx == 0 else None)

    os_norm = [osb["os_normalized_runtime"][p] for p in procs]
    sim_norm = [osb["sim_normalized_turnaround"][p] for p in procs]
    ax1.plot(x, os_norm, marker="o", lw=2.2, color="#d95f02", label="OS Median (psutil loop)", zorder=4)
    ax1.plot(x, sim_norm, marker="s", lw=2.0, ls="--", color="#1f4e78", label="Discrete Sim (gs_core)", zorder=4)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontweight="bold")
    ax1.set_ylim(0.45, 1.12)
    ax1.set_ylabel("Turnaround Ratio (normalized to P1)")
    ax1.set_title("Normalized Turnaround: Real OS vs Discrete Sim")
    ax1.legend(fontsize=8.0, loc="lower left")

    # Right: Raw median OS runtimes with min-max error bars
    medians = [osb["per_proc_median_runtime_sec"][p] for p in procs]
    mins = [min(t["runtimes_sec"][p] for t in trials) for p in procs]
    maxs = [max(t["runtimes_sec"][p] for t in trials) for p in procs]
    err_low = [m - lo for m, lo in zip(medians, mins)]
    err_high = [hi - m for m, hi in zip(medians, maxs)]
    bars = ax2.bar(labels, medians, yerr=[err_low, err_high], capsize=5,
                   color=[pk.PALETTE[0], pk.PALETTE[1], pk.PALETTE[2]], width=0.5, zorder=3)
    for b, m, hi in zip(bars, medians, maxs):
        ax2.text(b.get_x() + b.get_width() / 2, hi + 0.015, f"{m:.3f}s",
                 ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    ax2.set_ylim(0, max(maxs) + 0.12)
    ax2.set_ylabel("Wall-clock Completion Time (sec)")
    ax2.set_title("Real OS Subprocess Runtime (Median & Min-Max, n=5)")

    fig.tight_layout()
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_os_vs_sim.png"))


def fig_pseudocode_pipeline(out_dir: str) -> str:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(12.2, 4.5), dpi=220)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    ax.text(6.1, 4.28, "Guaranteed Scheduling Algorithmic Data-Flow & Pseudocode Pipeline",
            ha="center", va="top", fontsize=11.2, fontweight="bold", color="#0f172a")

    boxes = [
        (1.40, 2.40, 2.25, 2.15, "1. Admission Hook\non arrive(P):\n  v_i = V(t)\n  push(heap, v_i)", "#eff6ff", "#1f4e78"),
        (4.53, 2.40, 2.25, 2.15, "2. Wakeup Guard\non wake(P):\n  floor = V(t) - cap/w_i\n  v_i = max(v_i, floor)", "#eefaf5", "#1b9e77"),
        (7.66, 2.40, 2.30, 2.15, "3. Dispatch Select\nif stay & v_cur <= min_v:\n  pick cur  [O(1)]\nelse: pop(heap) [O(log n)]", "#fff7ed", "#d95f02"),
        (10.80, 2.40, 2.30, 2.15, "4. Execute & Bill\nrun slice <= q ticks\nused_i += delta\nv_i += SCALE_FP // w_i\nV(t) += SCALE_FP // W", "#fdf2f8", "#7570b3"),
    ]
    for cx, cy, w, h, txt, fc, ec in boxes:
        pk.draw_box(ax, cx, cy, w, h, txt, fc=fc, ec=ec, tc="#0f172a", fontsize=7.8)

    pk.draw_arrow(ax, 2.55, 2.40, 3.38, 2.40, "", color="#0f172a")
    pk.draw_arrow(ax, 5.68, 2.40, 6.48, 2.40, "", color="#0f172a")
    pk.draw_arrow(ax, 8.83, 2.40, 9.63, 2.40, "", color="#0f172a")
    ax.plot([10.80, 10.80, 7.66], [1.30, 0.72, 0.72], color="#1f4e78", lw=1.5)
    ax.annotate("", xy=(7.66, 1.30), xytext=(7.66, 0.72),
                arrowprops=dict(arrowstyle="-|>", color="#1f4e78", lw=1.5))
    ax.text(9.23, 0.45, "Next Tick Re-Heap Push  (Exact Fixed-Point / Fraction)",
            ha="center", va="center", fontsize=8.3, fontweight="bold", color="#1f4e78")
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_pseudocode_pipeline.png"))


def fig_vtime_anchor_mechanics(d: dict, out_dir: str) -> str:
    pk.apply_style()
    traj = d["baseline"]["trajectory_gs_ratio_q1"]
    ts = [row["t"] for row in traj]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.1), dpi=220)

    # Left: cumulative CPU A_i(t) vs Ideal GPS E_i(t) for P1, P2, P3
    for p, col in [("P1", pk.PALETTE[0]), ("P2", pk.PALETTE[1]), ("P3", pk.PALETTE[2])]:
        act = [r[f"{p}_actual"] for r in traj]
        gps = [r[f"{p}_gps"] for r in traj]
        ax1.step(ts, act, where="post", lw=2.0, color=col, label=f"{p} actual A(t)")
        ax1.plot(ts, gps, ls="--", lw=1.4, color=col, alpha=0.8)
    ax1.set_xlabel("Time t (ticks)")
    ax1.set_ylabel("Cumulative CPU (ticks)")
    ax1.set_title("Cumulative Actual A(t) vs Ideal GPS Dashed Curves")
    ax1.legend(fontsize=8.0, loc="upper left")
    ax1.grid(True, linestyle=":", alpha=0.45)

    # Right: per-unit-weight progress used/w for P1, P2, P3 showing strict alternation band
    for p, w, col in [("P1", 1, pk.PALETTE[0]), ("P2", 2, pk.PALETTE[1]), ("P3", 4, pk.PALETTE[2])]:
        vt = [r[f"{p}_actual"] / w for r in traj]
        ax2.step(ts, vt, where="post", lw=1.9, color=col, label=f"{p} v_i(t) = A_i/{w}")
    ax2.set_xlabel("Time t (ticks)")
    ax2.set_ylabel("Virtual Time v_i(t) = used_i / w_i")
    ax2.set_title("Virtual Clock Equalization Across Weights [1, 2, 4]")
    ax2.legend(fontsize=8.2, loc="upper left")
    ax2.grid(True, linestyle=":", alpha=0.45)

    fig.tight_layout()
    return pk.save_fig(fig, os.path.join(out_dir, "fig_ex1_vtime_anchor_mechanics.png"))


def main() -> int:
    d = load_data()
    out_dir = os.path.join(EX_ROOT, "diagrams")
    os.makedirs(out_dir, exist_ok=True)
    made = [
        fig_architecture(out_dir),
        fig_flowchart(out_dir),
        fig_gantt_baseline(d, out_dir),
        fig_lag_trajectory(d, out_dir),
        fig_quantum_sweep(d, out_dir),
        fig_tie_envelope(d, out_dir),
        fig_latecomer_teaser(d, out_dir),
        fig_os_vs_sim(d, out_dir),
        fig_pseudocode_pipeline(out_dir),
        fig_vtime_anchor_mechanics(d, out_dir),
    ]
    for p in made:
        print("generated", os.path.relpath(p, REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
