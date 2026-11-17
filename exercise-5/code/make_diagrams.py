"""Generate 8 crisp publication figures for Exercise 5 from experiments.json."""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EX5_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX5_DIR)
DATA_PATH = os.path.join(EX5_DIR, "output", "experiments.json")
DIAG_DIR = os.path.join(EX5_DIR, "diagrams")
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


def fig1_design_matrix(d):
    pk.apply_style()
    ov = d["sweep_a_monte_carlo"]["overall"]
    tr = d["sweep_d_os_intervals"]["interval_trials"]
    swe = d["sweep_e_zipf_burst"]["summary"]
    swf = d["sweep_f_bootstrap"]["comparisons"]
    vs_rat = next(c for c in swf if c["competitor"] == "gs_ratio:index")

    fig, ax = plt.subplots(figsize=(12.2, 5.4), dpi=220)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.4)
    ax.axis("off")

    ax.text(6.1, 5.18, "Exercise 5 Six-Sweep Factorial Design: Monte Carlo, Pareto, Zipf-Burst, Bootstrap & Live OS",
            ha="center", va="top", fontsize=11.0, fontweight="bold", color=C["black"])

    pk.draw_box(ax, 2.05, 3.65, 3.65, 1.55,
                f"Sweep A [M]: 240 Dynamic Seeds\n80 seeds x N in {{3,5,8}}, w in 1..6\ngs_vtime:stay {ov['gs_vtime:stay']['lag']['mean']:.3f} vs ratio {ov['gs_ratio:index']['lag']['mean']:.3f}\nProduces 60-seed archive + ECDFs",
                fc="#eef5fc", ec=C["blue"], tc=C["black"], fontsize=7.6)

    pk.draw_box(ax, 6.10, 3.65, 3.65, 1.55,
                "Sweep B [M]: Quantum Pareto\nq in {1,2,3,4,6,8,12} x 30 seeds\nLag vs switches tradeoff frontier\nIdentifies q=2 (stay) optimal knee",
                fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=7.6)

    pk.draw_box(ax, 10.15, 3.65, 3.65, 1.55,
                "Sweep C [M]: N-Scaling (2..16)\nEqual (1:1) vs Skew (1:4) x 20 seeds\nTests O(1) stability vs gs_ratio\nMaps starvation gap escalation",
                fc="#fff5ed", ec=C["orange"], tc=C["black"], fontsize=7.6)

    pk.draw_box(ax, 2.05, 1.25, 3.65, 1.55,
                f"Sweep F [M]: 1000x Bootstrap Audit\nPaired resamples over 240 seeds\nstay beats ratio {vs_rat['win_rate_pct']:.1f}% ({vs_rat['stay_wins']}/240)\nCohen's d = {vs_rat['cohens_d']:.2f} (huge effect)",
                fc="#f5f3ff", ec=C["purple"], tc=C["black"], fontsize=7.6)

    pk.draw_box(ax, 6.10, 1.25, 3.65, 1.55,
                f"Sweep E [M]: Zipf + Burst Shock\n60 seeds, w=[1,1,2,4,8,16] + t=15 burst\nmax_weight {swe['gs_vtime:max_weight']['lag']['mean']:.3f} / stay {swe['gs_vtime:stay']['lag']['mean']:.3f}\nvs gs_ratio {swe['gs_ratio:index']['lag']['mean']:.3f}, RR {swe['rr:index']['lag']['mean']:.3f}",
                fc="#fefce8", ec=C["yellow"], tc=C["black"], fontsize=7.6)

    pk.draw_box(ax, 10.15, 1.25, 3.65, 1.55,
                f"Sweep D [D]: 5-Interval Live OS\npsutil workers w=[1,2,4] (0.01s..0.20s)\nError drops {tr[-1]['max_share_deviation']*100:.2f}% -> {tr[0]['max_share_deviation']*100:.2f}%\nLogs 24-step dt=0.05s trace",
                fc="#fdf2f0", ec=C["red"], tc=C["black"], fontsize=7.6)

    pk.draw_arrow(ax, 3.90, 3.65, 4.25, 3.65, "", color=C["blue"])
    pk.draw_arrow(ax, 7.95, 3.65, 8.30, 3.65, "", color=C["green"])
    pk.draw_arrow(ax, 2.05, 2.85, 2.05, 2.05, "240 pairs", label_offset=(-0.72, 0.0), color=C["purple"])
    pk.draw_arrow(ax, 3.90, 1.25, 4.25, 1.25, "", color=C["purple"])
    pk.draw_arrow(ax, 7.95, 1.25, 8.30, 1.25, "", color=C["yellow"])
    pk.draw_arrow(ax, 10.15, 2.85, 10.15, 2.05, "OS parity", label_offset=(0.75, 0.0), color=C["red"])

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_design_matrix.png"))


def fig2_mc_lag_ci(d):
    pk.apply_style()
    ov = d["sweep_a_monte_carlo"]["overall"]
    byn = d["sweep_a_monte_carlo"]["by_n"]
    pols = ["gs_vtime:stay", "gs_vtime:index", "stride:index", "gs_entitled:index", "gs_ratio:index", "rr:index", "fifo:index"]
    lbls = ["gs_vtime\n(stay)", "gs_vtime\n(index)", "stride\n(index)", "gs_entitled\n(index)", "gs_ratio\n(index)", "RR\n(index)", "FIFO\n(batch)"]
    cols = [C["green"], C["sky"], C["purple"], C["blue"], C["orange"], C["yellow"], C["red"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.6), dpi=220)
    x = np.arange(len(pols))
    means = [ov[p]["lag"]["mean"] for p in pols]
    cis = [ov[p]["lag"]["ci95"] for p in pols]
    p99s = [ov[p]["lag"]["p99"] for p in pols]

    b = ax1.bar(x, means, yerr=cis, capsize=4, color=cols, width=0.58, edgecolor="#333", linewidth=0.7)
    ax1.scatter(x, p99s, marker="^", s=55, color=C["black"], zorder=5, label="99th percentile (p99)")
    for xi, m, p9 in zip(x, means, p99s):
        ax1.text(xi, p9 + 0.35, f"p99={p9:.1f}", ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(lbls, fontsize=7.9)
    ax1.set_ylim(0, max(p99s) * 1.14)
    ax1.set_ylabel("Max Absolute GPS Lag (Mean +/- 95% CI & p99)", fontsize=9.0)
    ax1.set_title("Sweep A (240 Dynamic Seeds): Lag Distribution [M]", fontsize=10.0, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.2)

    ns = [3, 5, 8]
    for p, lbl, col, mk in [
        ("gs_vtime:stay", "gs_vtime:stay", C["green"], "o-"),
        ("gs_entitled:index", "gs_entitled:index", C["blue"], "s--"),
        ("gs_ratio:index", "gs_ratio:index", C["orange"], "^-."),
        ("rr:index", "rr:index", C["red"], "D:"),
    ]:
        ys = [byn[str(n)][p]["lag"]["mean"] for n in ns]
        errs = [byn[str(n)][p]["lag"]["ci95"] for n in ns]
        ax2.errorbar(ns, ys, yerr=errs, fmt=mk, capsize=4, color=col, linewidth=2.1, label=lbl)
    ax2.set_xticks(ns)
    ax2.set_xlabel("Process Count N (80 seeds per N)", fontsize=9.2)
    ax2.set_ylabel("Mean Max Lag (ticks +/- 95% CI)", fontsize=9.0)
    ax2.set_title("Lag Separation by Concurrency N in {3, 5, 8}", fontsize=10.0, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8.2)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_mc_lag_ci.png"))


def fig3_quantum_pareto(d):
    pk.apply_style()
    rows = d["sweep_b_quantum_pareto"]["rows"]
    qs = [r["quantum"] for r in rows]

    fig, ax = plt.subplots(figsize=(10.8, 4.9), dpi=220)
    styles = [
        ("gs_vtime:stay", "gs_vtime : stay (Pareto-optimal)", C["green"], "o-"),
        ("gs_vtime:index", "gs_vtime : index", C["sky"], "s--"),
        ("gs_ratio:index", "gs_ratio : index (dominated)", C["orange"], "^-."),
        ("rr:index", "RR : index (dominated)", C["red"], "D:"),
    ]
    for pol, lbl, col, mk in styles:
        xs = [r["policies"][pol]["switches"]["mean"] for r in rows]
        ys = [r["policies"][pol]["lag"]["mean"] for r in rows]
        ax.plot(xs, ys, mk, color=col, linewidth=2.1, markersize=6, label=lbl)
        if pol in ("gs_vtime:stay", "rr:index"):
            for xi, yi, q in zip(xs, ys, qs):
                dx, dy = (0.7, 0.22) if pol == "rr:index" else (-0.2, -0.45)
                if q in (1, 2, 3, 6, 12):
                    ax.text(xi + dx, yi + dy, f"q={q}", fontsize=7.8, fontweight="bold", color=col)

    # Highlight knee at q=2..3 on gs_vtime:stay cleanly below gs_ratio curve
    kx = rows[1]["policies"]["gs_vtime:stay"]["switches"]["mean"]
    ky = rows[1]["policies"]["gs_vtime:stay"]["lag"]["mean"]
    ax.annotate("Recommended knee (q=2, stay):\ncuts switches ~45% vs q=1!",
                xy=(kx, ky), xytext=(kx + 6.0, ky + 0.55),
                arrowprops=dict(arrowstyle="->", color=C["black"], lw=1.2),
                fontsize=8.3, fontweight="bold", color=C["black"],
                bbox=dict(boxstyle="round,pad=0.35", fc="#eefaf5", ec=C["green"]))

    ax.set_xlabel("Mean Context Switches (lower = less scheduling overhead)", fontsize=9.4)
    ax.set_ylabel("Mean Max Absolute GPS Lag (lower = tighter fairness)", fontsize=9.4)
    ax.set_title("Sweep B Pareto Frontier: Fairness Lag vs Context-Switch Overhead (q = 1..12, 30 seeds) [M]",
                 fontsize=10.4, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", fontsize=8.3)
    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_quantum_pareto.png"))


def fig4_quantum_ta_rmse(d):
    pk.apply_style()
    rows = d["sweep_b_quantum_pareto"]["rows"]
    qs = [r["quantum"] for r in rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    styles = [
        ("gs_vtime:stay", "gs_vtime:stay", C["green"], "o-"),
        ("gs_vtime:index", "gs_vtime:index", C["sky"], "s--"),
        ("gs_ratio:index", "gs_ratio:index", C["orange"], "^-."),
        ("rr:index", "rr:index", C["red"], "D:"),
    ]
    for pol, lbl, col, mk in styles:
        ax1.plot(qs, [r["policies"][pol]["rmse"]["mean"] for r in rows], mk, color=col, linewidth=2.0, label=lbl)
        ax2.plot(qs, [r["policies"][pol]["turnaround"]["mean"] for r in rows], mk, color=col, linewidth=2.0, label=lbl)

    ax1.set_xticks(qs)
    ax1.set_xlabel("Time Quantum q (ticks)", fontsize=9.2)
    ax1.set_ylabel("Mean RMSE Lag (ticks)", fontsize=9.2)
    ax1.set_title("RMSE Lag Sensitivity to Quantum q (q = 1..12)", fontsize=10.0, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="lower right", fontsize=8.2)

    ax2.set_xticks(qs)
    ax2.set_xlabel("Time Quantum q (ticks)", fontsize=9.2)
    ax2.set_ylabel("Mean Turnaround Time (ticks)", fontsize=9.2)
    ax2.set_title("Mean Turnaround Stability Across Quanta [M]", fontsize=10.0, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="lower right", fontsize=8.2)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_quantum_ta_rmse.png"))


def fig5_n_scaling(d):
    pk.apply_style()
    rows = d["sweep_c_scaling"]["scaling_rows"]
    ns = [r["n_procs"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    ax1.errorbar(ns, [r["eq_vtime_lag"]["mean"] for r in rows],
                 yerr=[r["eq_vtime_lag"]["ci95"] for r in rows], fmt="o-", capsize=4, color=C["green"], linewidth=2.1, label="gs_vtime (equal w=1)")
    ax1.errorbar(ns, [r["skew_vtime_lag"]["mean"] for r in rows],
                 yerr=[r["skew_vtime_lag"]["ci95"] for r in rows], fmt="s--", capsize=4, color=C["sky"], linewidth=2.0, label="gs_vtime (skew 1:4)")
    ax1.errorbar(ns, [r["eq_ratio_lag"]["mean"] for r in rows],
                 yerr=[r["eq_ratio_lag"]["ci95"] for r in rows], fmt="^:", color=C["orange"], capsize=4, linewidth=2.0, label="gs_ratio (equal w=1)")
    ax1.errorbar(ns, [r["skew_ratio_lag"]["mean"] for r in rows],
                 yerr=[r["skew_ratio_lag"]["ci95"] for r in rows], fmt="D-", color=C["red"], capsize=4, linewidth=2.1, label="gs_ratio (skew 1:4)")
    ax1.set_xticks(ns)
    ax1.set_ylim(0, 4.35)
    ax1.set_xlabel("Process Count N", fontsize=9.2)
    ax1.set_ylabel("Mean Max Absolute Lag (+/- 95% CI)", fontsize=9.2)
    ax1.set_title("Sweep C: Process-Count & Weight-Skew Scaling [M]", fontsize=10.0, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.0)

    ax2.plot(ns, [r["skew_ratio_gap"]["mean"] for r in rows], "D-", color=C["red"], linewidth=2.1, label="gs_ratio max starve gap (skew 1:4)")
    ax2.plot(ns, [r["skew_vtime_gap"]["mean"] for r in rows], "s--", color=C["sky"], linewidth=2.1, label="gs_vtime max starve gap (skew 1:4)")
    ax2.set_xticks(ns)
    ax2.set_xlabel("Process Count N", fontsize=9.2)
    ax2.set_ylabel("Mean Longest Starvation Gap (ticks)", fontsize=9.2)
    ax2.set_title("Starvation Gap Scaling Under 1:4 Skew (20 seeds/pt)", fontsize=10.0, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8.2)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_n_scaling.png"))


def fig6_os_interval_pareto(d):
    pk.apply_style()
    tr = d["sweep_d_os_intervals"]["interval_trials"]
    dts = [f"{r['poll_dt_sec']:.2f}s" for r in tr]
    x = np.arange(3)
    targets = tr[0]["target_shares"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.6), dpi=220)
    w = 0.13
    ax1.bar(x - 2.5 * w, targets, width=w, color=C["black"], label="Target (1:2:4)")
    cols = [C["green"], C["sky"], C["blue"], C["orange"], C["red"]]
    for idx_t, (r, col) in enumerate(zip(tr, cols)):
        ax1.bar(x + (idx_t - 1.5) * w, r["actual_shares"], width=w, color=col,
                label=f"dt={r['poll_dt_sec']:.2f}s ({r['controller_switches']}sw)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(["P1 (w=1)", "P2 (w=2)", "P3 (w=4)"], fontsize=9.0)
    ax1.set_ylim(0, 0.72)
    ax1.set_ylabel("Measured OS CPU Share", fontsize=9.2)
    ax1.set_title("Sweep D Live Linux psutil CPU Shares (5 Poll Intervals) [D]", fontsize=9.8, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=7.4, ncol=2)

    sws = [r["controller_switches"] for r in tr]
    devs = [r["max_share_deviation"] * 100.0 for r in tr]
    ax2.plot(sws, devs, "o-", color=C["red"], linewidth=2.2, markersize=7)
    offsets = {
        "0.20s": (-16, -64),
        "0.10s": (14, 18),
        "0.05s": (22, 16),
        "0.02s": (16, 18),
        "0.01s": (-78, 36),
    }
    for sw, dv, lbl in zip(sws, devs, dts):
        ox, oy = offsets.get(lbl, (8, 8))
        ax2.annotate(
            f"dt={lbl} ({dv:.2f}%, {sw}sw)",
            xy=(sw, dv), xytext=(ox, oy), textcoords="offset points",
            fontsize=7.6, fontweight="bold", color=C["black"],
            arrowprops=dict(arrowstyle="-", color="#64748b", lw=0.8),
        )
    ax2.set_xlabel("Controller Preemption Switches (in 1.2s run)", fontsize=9.2)
    ax2.set_ylabel("Max OS CPU Share Error (%)", fontsize=9.2)
    ax2.set_xlim(-2, max(sws) * 1.18)
    ax2.set_ylim(-0.3, max(devs) * 1.35)
    ax2.set_title("Real-OS Fairness Error vs Switch Overhead Pareto [D]", fontsize=9.8, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_os_interval_pareto.png"))


def fig7_empirical_cdf(d):
    pk.apply_style()
    el = d["sweep_a_monte_carlo"]["ecdf_lags"]
    eg = d["sweep_a_monte_carlo"]["ecdf_gaps"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.5), dpi=220)
    styles = [
        ("gs_vtime:stay", "gs_vtime:stay", C["green"], "-"),
        ("gs_vtime:index", "gs_vtime:index", C["sky"], "--"),
        ("gs_entitled:index", "gs_entitled:index", C["blue"], "-."),
        ("gs_ratio:index", "gs_ratio:index", C["orange"], "-"),
        ("rr:index", "RR:index", C["red"], ":"),
    ]
    for pol, lbl, col, ls in styles:
        xs = np.array(el[pol])
        ys = np.arange(1, len(xs) + 1) / len(xs) * 100.0
        ax1.step(xs, ys, where="post", color=col, linestyle=ls, linewidth=2.1, label=lbl)
    ax1.axhline(95.0, color="#64748b", linestyle="--", linewidth=1.0)
    ax1.text(10.8, 96.0, "p95", fontsize=8.0, fontweight="bold", color="#475569")
    ax1.set_xlim(0, 12.5)
    ax1.set_ylim(0, 103)
    ax1.set_xlabel("Max Absolute GPS Lag (ticks, truncated at 12.5)", fontsize=9.0)
    ax1.set_ylabel("Empirical CDF Across 240 Runs (%)", fontsize=9.0)
    ax1.set_title("Empirical CDF of Max GPS Lag (240 Dynamic Seeds) [M]", fontsize=9.8, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="lower right", fontsize=8.0)

    for pol, lbl, col, ls in [
        ("gs_vtime:stay", "gs_vtime:stay", C["green"], "-"),
        ("gs_entitled:index", "gs_entitled:index", C["blue"], "-."),
        ("gs_ratio:index", "gs_ratio:index", C["orange"], "-"),
        ("rr:index", "RR:index", C["red"], ":"),
    ]:
        xs = np.array(eg[pol])
        ys = np.arange(1, len(xs) + 1) / len(xs) * 100.0
        ax2.step(xs, ys, where="post", color=col, linestyle=ls, linewidth=2.1, label=lbl)
    ax2.axhline(95.0, color="#64748b", linestyle="--", linewidth=1.0)
    ax2.text(21.0, 96.0, "p95", fontsize=8.0, fontweight="bold", color="#475569")
    ax2.set_xlim(0, 25)
    ax2.set_ylim(0, 103)
    ax2.set_xlabel("Longest Unbroken Starvation Gap (ticks)", fontsize=9.0)
    ax2.set_ylabel("Empirical CDF Across 240 Runs (%)", fontsize=9.0)
    ax2.set_title("Empirical CDF of Longest Starvation Gap (240 Seeds) [M]", fontsize=9.8, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="lower right", fontsize=8.0)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_empirical_cdf.png"))


def fig8_burst_and_bootstrap(d):
    pk.apply_style()
    swe = d["sweep_e_zipf_burst"]["summary"]
    pols = ["gs_vtime:max_weight", "gs_vtime:stay", "gs_vtime:index", "stride:index", "gs_entitled:index", "gs_ratio:index", "rr:index"]
    lbls = ["max_w", "stay", "index", "stride", "entitled", "gs_ratio", "RR"]
    cols = [C["green"], C["sky"], C["blue"], C["purple"], C["yellow"], C["orange"], C["red"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.6), dpi=220)
    x = np.arange(len(pols))
    means = [swe[p]["lag"]["mean"] for p in pols]
    cis = [swe[p]["lag"]["ci95"] for p in pols]
    p99s = [swe[p]["lag"]["p99"] for p in pols]
    ax1.bar(x, means, yerr=cis, capsize=4, color=cols, width=0.58, edgecolor="#333", linewidth=0.7)
    ax1.scatter(x, p99s, marker="^", s=50, color=C["black"], zorder=5, label="p99 tail lag")
    for xi, m, p9 in zip(x, means, p99s):
        ax1.text(xi, p9 + 0.35, f"{m:.2f}\n(p99={p9:.1f})", ha="center", va="bottom", fontsize=7.0, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(lbls, fontsize=8.1)
    ax1.set_ylim(0, max(p99s) * 1.18)
    ax1.set_ylabel("Max GPS Lag under Zipf + Burst (Mean +/- CI & p99)", fontsize=8.7)
    ax1.set_title("Sweep E (60 Zipf [1..16] + t=15 Burst Seeds) [M]", fontsize=9.8, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.0)

    comps = d["sweep_f_bootstrap"]["comparisons"]
    y = np.arange(len(comps))
    clbls = [c["competitor"] for c in comps]
    wins = [c["win_rate_pct"] for c in comps]
    diffs = [c["mean_lag_reduction"] for c in comps]
    bcols = [C["green"] if w >= 90 else (C["sky"] if w >= 60 else C["purple"]) for w in wins]
    ax2.barh(y, wins, color=bcols, height=0.58, edgecolor="#333", linewidth=0.7)
    for yi, w_pct, df in zip(y, wins, diffs):
        inside = w_pct >= 88.0
        xpos = w_pct - 1.5 if inside else w_pct + 1.5
        ax2.text(xpos, yi, f"{w_pct:.1f}% win (dLag={df:+.2f})",
                 va="center", ha="right" if inside else "left",
                 fontsize=7.6, fontweight="bold", color="#fff" if inside else C["black"])
    ax2.set_yticks(y)
    ax2.set_yticklabels(clbls, fontsize=8.4)
    ax2.set_xlim(0, 114)
    ax2.set_xlabel("gs_vtime:stay Pairwise Win Rate Across 240 Paired Runs (%)", fontsize=8.7)
    ax2.set_title("Sweep F Paired Bootstrap Dominance (1,000 Resamples) [M]", fontsize=9.8, fontweight="bold")
    ax2.grid(axis="x", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex5_burst_and_bootstrap.png"))


def main():
    d = load_data()
    fig1_design_matrix(d)
    fig2_mc_lag_ci(d)
    fig3_quantum_pareto(d)
    fig4_quantum_ta_rmse(d)
    fig5_n_scaling(d)
    fig6_os_interval_pareto(d)
    fig7_empirical_cdf(d)
    fig8_burst_and_bootstrap(d)
    print("Generated 8 Exercise 5 diagrams cleanly in", DIAG_DIR)


if __name__ == "__main__":
    main()
