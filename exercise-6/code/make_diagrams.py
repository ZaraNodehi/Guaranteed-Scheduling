"""Generate 6 crisp publication figures for Exercise 6 from experiments.json."""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EX6_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX6_DIR)
DATA_PATH = os.path.join(EX6_DIR, "output", "experiments.json")
DIAG_DIR = os.path.join(EX6_DIR, "diagrams")
os.makedirs(DIAG_DIR, exist_ok=True)

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import plot_kit as pk  # noqa: E402
from gs_core import Proc, gantt_rows, simulate_procs  # noqa: E402

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


def fig1_refactor_architecture(d):
    pk.apply_style()
    b1_last = d["bench1_complexity"]["rows"][-1]
    b4 = d["bench4_live_os"]
    fig, ax = plt.subplots(figsize=(11.6, 5.0), dpi=220)
    ax.set_xlim(0, 11.6)
    ax.set_ylim(0, 5.0)
    ax.axis("off")

    ax.text(5.8, 4.78, "Exercise 6 Architectural Refactoring: Legacy GuaranteedScheduling.py -> OptimizedHeapScheduler",
            ha="center", va="top", fontsize=11.0, fontweight="bold", color=C["black"])

    pk.draw_box(ax, 2.55, 2.65, 4.4, 3.25,
                f"Legacy Pattern (V0 Baseline) [D]\n- O(N) linear scan ({b1_last['linear_us_per_step']:.1f} us @ N=2000)\n- IEEE-754 float used / weight\n- Latecomer starts at 0 (starves active)\n- Uncapped wakeup credit (79t burst @ S=80)\n- Fixed index tie-break + 0.10s OS poll\n- Live OS post-spawn dev: {b4['legacy']['max_post_spawn_deviation']*100:.2f}%",
                fc="#fdf2f0", ec=C["red"], tc=C["black"], fontsize=8.0)

    pk.draw_box(ax, 9.05, 2.65, 4.4, 3.25,
                f"Refactored Scheduler (V4 Optimized) [M]+[D]\n- O(log N) lazy min-heap ({b1_last['heap_us_per_step']:.2f} us @ N=2000)\n- Integer fixed-point 10^9/w (0 drift!)\n- V(t) arrival anchor eliminates shock\n- gs_capped wakeup floor (1t burst @ S=80)\n- stay tie hysteresis + 0.05s OS poll\n- Live OS post-spawn dev: {b4['optimized']['max_post_spawn_deviation']*100:.2f}%",
                fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=8.0)

    pk.draw_arrow(ax, 4.78, 2.65, 6.82, 2.65,
                  f"{b1_last['speedup']:.0f}x faster\n4.2x OS accuracy",
                  label_offset=(0.0, 0.48), color=C["blue"])

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_refactor_architecture.png"))


def fig2_complexity_scaling(d):
    pk.apply_style()
    rows = d["bench1_complexity"]["rows"]
    ns = [r["n_procs"] for r in rows]
    lin = [r["linear_us_per_step"] for r in rows]
    hp = [r["heap_us_per_step"] for r in rows]
    sp = [r["speedup"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    ax1.plot(ns, lin, "o-", color=C["red"], linewidth=2.2, label="LinearScanScheduler O(N)")
    ax1.plot(ns, hp, "s-", color=C["green"], linewidth=2.2, label="OptimizedHeapScheduler O(log N)")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xticks(ns)
    ax1.set_xticklabels([str(n) for n in ns])
    ax1.set_xlabel("Active Process Count N (log scale)", fontsize=9.2)
    ax1.set_ylabel("Dispatch Latency (us / decision, log)", fontsize=9.2)
    ax1.set_title("Bench 1: O(N) vs O(log N) Wall-Clock Dispatch Scaling [M]", fontsize=9.8, fontweight="bold")
    ax1.grid(True, which="both", linestyle=":", alpha=0.45)
    ax1.legend(loc="upper left", fontsize=8.2)

    bars = ax2.bar(np.arange(len(ns)), sp, color=C["sky"], width=0.55, edgecolor="#333", linewidth=0.7)
    for bar, s in zip(bars, sp):
        ax2.text(bar.get_x() + bar.get_width() / 2, s + 2.5, f"{s:.1f}x",
                 ha="center", va="bottom", fontsize=8.3, fontweight="bold")
    ax2.set_xticks(np.arange(len(ns)))
    ax2.set_xticklabels([str(n) for n in ns], fontsize=8.8)
    ax2.set_ylim(0, max(sp) * 1.18)
    ax2.set_xlabel("Active Process Count N", fontsize=9.2)
    ax2.set_ylabel("Speedup Factor (Linear / Heap)", fontsize=9.2)
    ax2.set_title("Min-Heap Dispatch Speedup Factor (2,000 steps x 5 reps)", fontsize=9.8, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_complexity_scaling.png"))


def fig3_ablation_ladder(d):
    pk.apply_style()
    st = d["bench2_ablation"]["stages"]
    labels = ["V0 Legacy\n(gs_ratio)", "V1 +V(t)\nAnchor", "V2 +stay\nHysteresis", "V3 +gs_capped\nSleeper Cap"]
    x = np.arange(len(st))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    lags = [s["mean_lag"] for s in st]
    sws = [s["mean_switches"] for s in st]
    bursts = [s["max_sleeper_burst"] for s in st]

    b1 = ax1.bar(x, lags, color=[C["red"], C["orange"], C["sky"], C["green"]],
                 width=0.52, edgecolor="#333", linewidth=0.7)
    for bar, v in zip(b1, lags):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 0.12, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=8.3, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.3)
    ax1.set_ylim(0, max(lags) * 1.2)
    ax1.set_ylabel("Mean Max GPS Lag (ticks, 30 seeds)", fontsize=9.1)
    ax1.set_title("Bench 2 Ablation: Fairness Lag V0 -> V3 [M]", fontsize=9.9, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)

    b2 = ax2.bar(x, bursts, color=[C["red"], C["orange"], C["sky"], C["green"]],
                 width=0.52, edgecolor="#333", linewidth=0.7)
    for bar, v, sw in zip(b2, bursts, sws):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.35, f"{v}t burst\n({sw:.1f} sw)",
                 ha="center", va="bottom", fontsize=8.0, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.3)
    ax2.set_ylim(0, max(bursts) * 1.30)
    ax2.set_ylabel("Worst Post-Wakeup Sleeper Burst (ticks)", fontsize=9.1)
    ax2.set_title("Sleeper Burst Suppression & Context Switches (V0 -> V3)", fontsize=9.9, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_ablation_ladder.png"))


def fig4_sleeper_mitigation(d):
    pk.apply_style()
    rows = d["bench3_sleeper"]["rows"]
    ss = [r["sleep_ticks"] for r in rows]

    fig, ax = plt.subplots(figsize=(10.6, 4.5), dpi=220)
    ax.plot(ss, [r["policies"]["gs_ratio:index"]["post_wakeup_burst"] for r in rows],
            "o-", color=C["red"], linewidth=2.3, label="gs_ratio:index (uncapped)")
    ax.plot(ss, [r["policies"]["gs_vtime:index"]["post_wakeup_burst"] for r in rows],
            "s--", color=C["orange"], linewidth=2.1, label="gs_vtime:index (uncapped wakeup)")
    ax.plot(ss, [r["policies"]["gs_entitled:index"]["post_wakeup_burst"] for r in rows],
            "^:", color=C["sky"], linewidth=2.0, label="gs_entitled:index")
    ax.plot(ss, [r["policies"]["gs_capped:index"]["post_wakeup_burst"] for r in rows],
            "D-", color=C["green"], linewidth=2.3, label="gs_capped:index (wakeup floor = 1)")

    ax.annotate("gs_capped freezes sleeper burst\nat 1 tick even after S=80 sleep!",
                xy=(80, 1), xytext=(45, 24),
                arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.4),
                fontsize=8.6, fontweight="bold", color=C["black"],
                bbox=dict(boxstyle="round,pad=0.35", fc="#eefaf5", ec=C["green"]))

    ax.set_xticks(ss)
    ax.set_xlabel("Sleeper I/O Block Duration S (ticks)", fontsize=9.4)
    ax.set_ylabel("Max Consecutive Lockout of Steady Worker (ticks)", fontsize=9.4)
    ax.set_title("Bench 3 Adversarial Sleeper Exploit: 79-Tick Monopoly vs 1-Tick Cap [E]+[M]",
                 fontsize=10.5, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper left", fontsize=8.4)
    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_sleeper_mitigation.png"))


def fig5_os_refactor_validation(d):
    pk.apply_style()
    leg = d["bench4_live_os"]["legacy"]
    opt = d["bench4_live_os"]["optimized"]
    x = np.arange(3)
    w = 0.28

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    ax1.bar(x - w / 2, leg["post_spawn_shares"], width=w, color=C["red"], label="Legacy (dt=0.10s, used/w)")
    ax1.bar(x + w / 2, opt["post_spawn_shares"], width=w, color=C["green"], label="Refactored (dt=0.05s, V(t)+stay)")
    ax1.axhline(1.0 / 3.0, color=C["black"], linestyle="--", linewidth=1.3, label="Ideal equal share (33.3%)")
    for xi, lv, ov in zip(x, leg["post_spawn_shares"], opt["post_spawn_shares"]):
        ax1.text(xi - w / 2, lv - 0.032, f"{lv*100:.1f}%", ha="center", va="top",
                 color="white", fontsize=7.9, fontweight="bold")
        ax1.text(xi + w / 2, ov - 0.032, f"{ov*100:.1f}%", ha="center", va="top",
                 color="white", fontsize=7.9, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(["P1 (arr=0s)", "P2 (arr=0s)", "P3 (arr=0.6s!)"], fontsize=9.0)
    ax1.set_ylim(0, 0.56)
    ax1.set_ylabel("Post-Spawn CPU Share [0.6s .. 1.8s]", fontsize=9.1)
    ax1.set_title("Bench 4 Live Linux Mid-Run Worker Arrival [D]", fontsize=9.9, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.0)

    bars = ax2.bar([0, 1],
                   [leg["max_post_spawn_deviation"] * 100.0, opt["max_post_spawn_deviation"] * 100.0],
                   color=[C["red"], C["green"]], width=0.48, edgecolor="#333", linewidth=0.7)
    for bar, r in zip(bars, [leg, opt]):
        v = r["max_post_spawn_deviation"] * 100.0
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.4,
                 f"{v:.2f}%\n({r['switches']} sw)", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["Legacy Controller\n(dt=0.10s, unanchored)", "Refactored Controller\n(dt=0.05s, V(t)+stay)"], fontsize=8.8)
    ax2.set_ylim(0, max(leg["max_post_spawn_deviation"], opt["max_post_spawn_deviation"]) * 135.0)
    ax2.set_ylabel("Max Post-Spawn Share Error (%)", fontsize=9.1)
    ax2.set_title("4.2x Lower Real-Linux Latecomer Distortion [D]", fontsize=9.9, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_os_refactor_validation.png"))


def fig6_timeline_sleeper():
    pk.apply_style()
    ps = [Proc("Steady", 0, 22, 1), Proc("Sleeper", 0, 12, 1, sleep_at=((1, 10),))]
    r_vt = simulate_procs(ps, "gs_vtime:index", 1)
    r_cp = simulate_procs(ps, "gs_capped:index", 1)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.2, 4.4), dpi=220, sharex=True)
    fig.suptitle("Sleeper Wakeup Contrast (Sleeper blocks t=2..12, wakes at t=12): Monopoly vs 1-Tick Cap",
                 fontsize=10.6, fontweight="bold", y=0.98)
    pcols = {"Steady": C["blue"], "Sleeper": C["orange"]}
    for ax, r, title in [
        (ax1, r_vt, "gs_vtime (uncapped): Sleeper captures 10 straight ticks (t=12..22), freezing Steady!"),
        (ax2, r_cp, "gs_capped (V(t) - 1 floor): Alternates cleanly 1:1 immediately after wakeup at t=12"),
    ]:
        ymap = {"Steady": 1, "Sleeper": 0}
        if r is r_vt:
            ax.axvspan(12, 22, color="#fee2e2", alpha=0.7, zorder=0)
        for nm, st, en in gantt_rows(r.timeline):
            y = ymap[nm]
            ax.barh(y, en - st, left=st, height=0.56, color=pcols[nm], edgecolor="white", linewidth=0.8)
            ax.text(0.5 * (st + en), y, f"{en-st}", ha="center", va="center", color="white",
                    fontsize=7.8, fontweight="bold")
        ax.axvline(12, color=C["black"], linestyle="--", linewidth=1.1)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Sleeper", "Steady"], fontsize=8.8)
        ax.set_ylim(-0.45, 1.55)
        ax.set_title(title, loc="left", fontsize=9.1, fontweight="bold",
                     color=C["red"] if r is r_vt else C["green"])
        ax.grid(axis="x", linestyle=":", alpha=0.45)

    ax2.set_xlim(0, 34)
    ax2.set_xticks(range(0, 35, 2))
    ax2.set_xlabel("Time (integer ticks; Sleeper sleeps t=2..12 and wakes at t=12)", fontsize=9.1)
    fig.tight_layout(rect=[0, 0, 1, 0.945])
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_timeline_sleeper.png"))


def main():
    d = load_data()
    fig1_refactor_architecture(d)
    fig2_complexity_scaling(d)
    fig3_ablation_ladder(d)
    fig4_sleeper_mitigation(d)
    fig5_os_refactor_validation(d)
    fig6_timeline_sleeper()
    print("Generated 6 Exercise 6 diagrams cleanly in", DIAG_DIR)


if __name__ == "__main__":
    main()
