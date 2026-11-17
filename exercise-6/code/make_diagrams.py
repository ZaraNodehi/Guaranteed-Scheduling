"""Generate 8 crisp Okabe-Ito publication figures for Exercise 6 from experiments.json."""
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
    "green": "#009e73",
    "orange": "#e69f00",
    "vermilion": "#d55e00",
    "purple": "#cc79a7",
    "black": "#0f172a",
}


def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def fig1_refactor_architecture(d):
    pk.apply_style()
    b1_2k = next(r for r in d["bench1_complexity"]["rows"] if r["n_procs"] == 2000)
    b1_4k = d["bench1_complexity"]["rows"][-1]
    b4 = d["bench4_live_os"]
    dec = d["bench5_fp_drift"]["decimal_weights_suite"]
    b3_last = d["bench3_sleeper"]["rows"][-1]
    s_max = b3_last["sleep_ticks"]
    os_gain = b4["legacy"]["max_post_spawn_deviation"] / max(1e-6, b4["optimized"]["max_post_spawn_deviation"])

    fig, ax = plt.subplots(figsize=(11.6, 5.1), dpi=220)
    ax.set_xlim(0, 11.6)
    ax.set_ylim(0, 5.1)
    ax.axis("off")

    ax.text(5.8, 4.86,
            "Exercise 6 Architectural Refactoring: Legacy GuaranteedScheduling.py -> OptimizedHeapScheduler",
            ha="center", va="top", fontsize=11.0, fontweight="bold", color=C["black"])

    pk.draw_box(
        ax, 2.55, 2.62, 4.45, 3.45,
        f"Legacy Pattern (V0 Baseline) [D]\n"
        f"- O(N) scan ({b1_2k['linear_us_per_step']:.1f} us @ 2k; {b1_4k['linear_us_per_step']:.1f} us @ 4k)\n"
        f"- IEEE-754 float ({dec['total_float_divergences_100k']:,} tie errors/100k)\n"
        f"- Latecomer starts at 0 (starves active)\n"
        f"- Uncapped wakeup ({b3_last['policies']['gs_ratio:index']['post_wakeup_burst']}t burst @ S={s_max})\n"
        f"- Fixed index tie-break + 0.10s OS poll\n"
        f"- Live OS arrival err: {b4['legacy']['max_post_spawn_deviation']*100:.2f}% | sleep burst: {b4['sleeper_uncapped']['max_sleeper_burst_steps']}st",
        fc="#fdf2f0", ec=C["vermilion"], tc=C["black"], fontsize=7.8,
    )

    pk.draw_box(
        ax, 9.05, 2.62, 4.45, 3.45,
        f"Refactored Scheduler (V4 Hardened) [M]+[D]\n"
        f"- O(log N) lazy min-heap ({b1_4k['heap_us_per_step']:.2f} us @ 4k)\n"
        f"- 10^9 & LCM fixed-point (0 errors/100k!)\n"
        f"- V(t) arrival anchor removes latecomer shock\n"
        f"- gs_capped wakeup floor (1t burst @ S={s_max})\n"
        f"- stay tie hysteresis + 0.05s OS poll\n"
        f"- Live OS arrival err: {b4['optimized']['max_post_spawn_deviation']*100:.2f}% | sleep burst: {b4['sleeper_capped']['max_sleeper_burst_steps']}st",
        fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=7.8,
    )

    pk.draw_arrow(
        ax, 4.82, 2.62, 6.78, 2.62,
        f"{b1_4k['speedup']:.0f}x faster @ 4k\n{os_gain:.1f}x OS accuracy",
        label_offset=(0.0, 0.50), color=C["blue"],
    )

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_refactor_architecture.png"))


def fig2_complexity_scaling(d):
    pk.apply_style()
    rows = d["bench1_complexity"]["rows"]
    ns = [r["n_procs"] for r in rows]
    lin = [r["linear_us_per_step"] for r in rows]
    hp = [r["heap_us_per_step"] for r in rows]
    sp = [r["speedup"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.5), dpi=220)
    ax1.plot(ns, lin, "o-", color=C["vermilion"], linewidth=2.2, label="LinearScanScheduler O(N)")
    ax1.plot(ns, hp, "s-", color=C["green"], linewidth=2.2, label="OptimizedHeapScheduler O(log N)")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xticks(ns)
    ax1.set_xticklabels([str(n) for n in ns], fontsize=8.1)
    ax1.set_xlabel("Active Process Count N (log scale)", fontsize=9.2)
    ax1.set_ylabel("Dispatch Latency (us / decision, log)", fontsize=9.2)
    ax1.set_title("Bench 1: O(N) vs O(log N) Scaling (N = 50..4,000) [M]", fontsize=9.8, fontweight="bold")
    ax1.grid(True, which="both", linestyle=":", alpha=0.45)
    ax1.legend(loc="upper left", fontsize=8.2)

    bars = ax2.bar(np.arange(len(ns)), sp, color=C["sky"], width=0.58, edgecolor="#333", linewidth=0.7)
    for bar, s in zip(bars, sp):
        ax2.text(bar.get_x() + bar.get_width() / 2, s + 4.0, f"{s:.1f}x",
                 ha="center", va="bottom", fontsize=7.9, fontweight="bold")
    ax2.set_xticks(np.arange(len(ns)))
    ax2.set_xticklabels([str(n) for n in ns], fontsize=8.4)
    ax2.set_ylim(0, max(sp) * 1.18)
    ax2.set_xlabel("Active Process Count N", fontsize=9.2)
    ax2.set_ylabel("Speedup Factor (Linear / Heap)", fontsize=9.2)
    ax2.set_title("Min-Heap Speedup Factor (2,000 steps x 5 reps)", fontsize=9.8, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_complexity_scaling.png"))


def fig3_ablation_ladder(d):
    pk.apply_style()
    st = d["bench2_ablation"]["stages"]
    n_wl = d["bench2_ablation"]["n_workloads"]
    labels = ["V0 Legacy\n(gs_ratio)", "V1 +V(t)\nAnchor", "V2 +stay\nHysteresis", "V3 +gs_capped\nSleeper Cap"]
    x = np.arange(len(st))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.5), dpi=220)
    lags = [s["mean_lag"] for s in st]
    ci95 = [s["ci95_lag"] for s in st]
    sws = [s["mean_switches"] for s in st]
    bursts = [s["max_sleeper_burst"] for s in st]
    cols = [C["vermilion"], C["orange"], C["sky"], C["green"]]

    b1 = ax1.bar(x, lags, yerr=ci95, capsize=4, color=cols, width=0.52, edgecolor="#333", linewidth=0.7)
    for bar, v, c in zip(b1, lags, ci95):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + c + 0.14, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=8.2, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.2)
    ax1.set_ylim(0, max(lags) * 1.24)
    ax1.set_ylabel(f"Mean Max GPS Lag +/- 95% CI ({n_wl} seeds)", fontsize=9.0)
    ax1.set_title(f"Bench 2 Ablation: Fairness Lag V0 -> V3 ({n_wl} seeds) [M]", fontsize=9.6, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)

    b2 = ax2.bar(x, bursts, color=cols, width=0.52, edgecolor="#333", linewidth=0.7)
    for bar, v, sw in zip(b2, bursts, sws):
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.35, f"{v}t burst\n({sw:.1f} sw)",
                 ha="center", va="bottom", fontsize=8.0, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.2)
    ax2.set_ylim(0, max(bursts) * 1.32)
    ax2.set_ylabel("Worst Post-Wakeup Sleeper Burst (ticks)", fontsize=9.0)
    ax2.set_title("Worst Sleeper Lockout & Mean Context Switches", fontsize=9.6, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_ablation_ladder.png"))


def fig4_sleeper_mitigation(d):
    pk.apply_style()
    rows = d["bench3_sleeper"]["rows"]
    ss = [r["sleep_ticks"] for r in rows]

    fig, ax = plt.subplots(figsize=(10.6, 4.5), dpi=220)
    ax.plot(ss, [r["policies"]["gs_ratio:index"]["post_wakeup_burst"] for r in rows],
            "o-", color=C["vermilion"], linewidth=2.3, label="gs_ratio:index (uncapped)")
    ax.plot(ss, [r["policies"]["gs_vtime:index"]["post_wakeup_burst"] for r in rows],
            "s--", color=C["orange"], linewidth=2.1, label="gs_vtime:index (uncapped wakeup)")
    ax.plot(ss, [r["policies"]["gs_entitled:index"]["post_wakeup_burst"] for r in rows],
            "^:", color=C["sky"], linewidth=2.0, label="gs_entitled:index")
    ax.plot(ss, [r["policies"]["gs_capped:index"]["post_wakeup_burst"] for r in rows],
            "D-", color=C["green"], linewidth=2.3, label="gs_capped:index (wakeup floor = 1)")

    s_max = ss[-1]
    ax.annotate(f"gs_capped freezes sleeper burst\nat 1 tick even after S={s_max} sleep!",
                xy=(s_max, 1), xytext=(95, 42),
                arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.4),
                fontsize=8.6, fontweight="bold", color=C["black"],
                bbox=dict(boxstyle="round,pad=0.35", fc="#eefaf5", ec=C["green"]))

    ax.set_xticks(ss)
    ax.set_xlabel("Sleeper I/O Block Duration S (ticks)", fontsize=9.4)
    ax.set_ylabel("Max Consecutive Lockout of Steady Worker (ticks)", fontsize=9.4)
    ax.set_title("Bench 3 Adversarial Sleeper Exploit: 159-Tick Monopoly vs 1-Tick Cap [E]+[M]",
                 fontsize=10.3, fontweight="bold")
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
    ax1.bar(x - w / 2, leg["post_spawn_shares"], width=w, color=C["vermilion"],
            label="Legacy (dt=0.10s, unanchored used/w)")
    ax1.bar(x + w / 2, opt["post_spawn_shares"], width=w, color=C["green"],
            label="Refactored (dt=0.05s, V(t)+stay)")
    ax1.axhline(1.0 / 3.0, color=C["black"], linestyle="--", linewidth=1.3, label="Ideal equal share (33.3%)")
    for xi, lv, ov in zip(x, leg["post_spawn_shares"], opt["post_spawn_shares"]):
        ax1.text(xi - w / 2, lv - 0.025 if lv > 0.24 else lv + 0.014,
                 f"{lv*100:.1f}%", ha="center", va="top" if lv > 0.24 else "bottom",
                 color="white" if lv > 0.24 else C["black"], fontsize=7.8, fontweight="bold")
        ax1.text(xi + w / 2, ov - 0.025, f"{ov*100:.1f}%", ha="center", va="top",
                 color="white", fontsize=7.8, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(["P1 (arr=0s)", "P2 (arr=0s)", "P3 (arr=0.6s!)"], fontsize=9.0)
    ax1.set_ylim(0, 0.62)
    ax1.set_ylabel("Post-Spawn CPU Share [0.6s .. 1.8s]", fontsize=9.1)
    ax1.set_title("Bench 4 Live Linux Mid-Run Worker Arrival [D]", fontsize=9.9, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.0)

    gain = leg["max_post_spawn_deviation"] / max(1e-6, opt["max_post_spawn_deviation"])
    bars = ax2.bar([0, 1],
                   [leg["max_post_spawn_deviation"] * 100.0, opt["max_post_spawn_deviation"] * 100.0],
                   color=[C["vermilion"], C["green"]], width=0.48, edgecolor="#333", linewidth=0.7)
    for bar, r in zip(bars, [leg, opt]):
        v = r["max_post_spawn_deviation"] * 100.0
        ax2.text(bar.get_x() + bar.get_width() / 2, v + 0.4,
                 f"{v:.2f}%\n({r['switches']} sw)", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["Legacy Controller\n(dt=0.10s, unanchored)",
                         "Refactored Controller\n(dt=0.05s, V(t)+stay)"], fontsize=8.8)
    ax2.set_ylim(0, max(leg["max_post_spawn_deviation"], opt["max_post_spawn_deviation"]) * 135.0)
    ax2.set_ylabel("Max Post-Spawn Share Error (%)", fontsize=9.1)
    ax2.set_title(f"{gain:.1f}x Lower Real-Linux Latecomer Distortion [D]", fontsize=9.9, fontweight="bold")
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
                     color=C["vermilion"] if r is r_vt else C["green"])
        ax.grid(axis="x", linestyle=":", alpha=0.45)

    ax2.set_xlim(0, 34)
    ax2.set_xticks(range(0, 35, 2))
    ax2.set_xlabel("Time (integer ticks; Sleeper sleeps t=2..12 and wakes at t=12)", fontsize=9.1)
    fig.tight_layout(rect=[0, 0, 1, 0.945])
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_timeline_sleeper.png"))


def fig7_cap_tradeoff_and_churn(d):
    pk.apply_style()
    caps = d["bench3_sleeper"]["cap_sensitivity"]
    churn = d["bench1_complexity"]["churn_rows"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.5), dpi=220)
    xc = np.arange(len(caps))
    ax1.plot(xc, [r["equal_burst_s40"] for r in caps], "o-", color=C["vermilion"], linewidth=2.2,
             label="Equal weights (S=40) burst")
    ax1.plot(xc, [r["skew_burst_s24"] for r in caps], "s--", color=C["sky"], linewidth=2.0,
             label="Skewed 2:1 (S=24) burst")
    ax1.set_xticks(xc)
    ax1.set_xticklabels([str(r["wakeup_cap"]) for r in caps], fontsize=8.4)
    ax1.set_xlabel("Wakeup Credit Cap wakeup_cap_ticks", fontsize=9.1)
    ax1.set_ylabel("Post-Wakeup Consecutive Burst (ticks)", fontsize=9.1)
    ax1.set_title("Wakeup Cap Tradeoff: Burst Suppression vs cap=0..40 [E]", fontsize=9.5, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.1)

    ax1.annotate("cap=1 optimal:\nlag=20.0 (vs 20.5 @ cap=0)",
                 xy=(1, caps[1]["equal_burst_s40"]), xytext=(2.2, 13),
                 arrowprops=dict(arrowstyle="->", color=C["green"], lw=1.3),
                 fontsize=7.9, fontweight="bold", color=C["black"],
                 bbox=dict(boxstyle="round,pad=0.3", fc="#eefaf5", ec=C["green"]))

    n_c = [r["n_procs"] for r in churn]
    lin_c = [r["linear_churn_us"] for r in churn]
    hp_c = [r["heap_churn_us"] for r in churn]
    sp_c = [r["churn_speedup"] for r in churn]
    w = 0.34
    xr = np.arange(len(n_c))
    ax2.bar(xr - w / 2, lin_c, width=w, color=C["vermilion"], label="LinearScan sleep/wake churn")
    ax2.bar(xr + w / 2, hp_c, width=w, color=C["green"], label="Lazy versioned heap (O(1) cancel)")
    ax2.set_yscale("log")
    for xi, lv, sp in zip(xr, lin_c, sp_c):
        ax2.text(xi, lv * 1.18, f"{sp:.1f}x", ha="center", va="bottom",
                 fontsize=8.2, fontweight="bold", color=C["blue"])
    ax2.set_xticks(xr)
    ax2.set_xticklabels([f"N={n}" for n in n_c], fontsize=8.6)
    ax2.set_ylim(1.0, max(lin_c) * 2.8)
    ax2.set_xlabel("Active Processes Under Sleep/Wake Churn", fontsize=9.1)
    ax2.set_ylabel("Cycle Time (us / sleep+wake cycle, log)", fontsize=9.1)
    ax2.set_title("Lazy Version Cancellation Under Heavy Churn [M]", fontsize=9.5, fontweight="bold")
    ax2.grid(axis="y", which="both", linestyle=":", alpha=0.45)
    ax2.legend(loc="upper left", fontsize=8.0)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_cap_tradeoff_and_churn.png"))


def fig8_fp_drift_and_live_sleeper(d):
    pk.apply_style()
    dec = d["bench5_fp_drift"]["decimal_weights_suite"]["checkpoints"]
    prm = d["bench5_fp_drift"]["prime_weights_suite"]["checkpoints"]
    uncap = d["bench4_live_os"]["sleeper_uncapped"]
    cap = d["bench4_live_os"]["sleeper_capped"]

    lcm_s = d["bench5_fp_drift"]["lcm_prime_suite"]["checkpoints"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.5), dpi=220)
    steps = [r["steps"] for r in dec]
    x = np.arange(len(steps))
    w = 0.21
    ax1.bar(x - 1.5 * w, [r["float_mismatch_cum"] for r in dec], width=w, color=C["vermilion"],
            label="float64 [2,5,10]")
    ax1.bar(x - 0.5 * w, [r["fp_mismatch_cum"] for r in dec], width=w, color=C["green"],
            label="10^9 FP [2,5,10] (0 err!)")
    ax1.bar(x + 0.5 * w, [r["float_mismatch_cum"] for r in prm], width=w, color=C["orange"],
            label="float64 [3,7,11]")
    ax1.bar(x + 1.5 * w, [r["fp_mismatch_cum"] for r in lcm_s], width=w, color=C["sky"],
            label="SCALE_LCM [3,7,11] (0 err!)")
    for xi, dv in zip(x, [r["float_mismatch_cum"] for r in dec]):
        ax1.text(xi - 1.5 * w, dv + max(25, dv * 0.04), f"{dv:,}", ha="center", va="bottom",
                 fontsize=7.0, fontweight="bold", rotation=30)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{s//1000}k" if s >= 1000 else str(s) for s in steps], fontsize=8.4)
    ax1.set_ylim(0, max(r["float_mismatch_cum"] for r in dec) * 1.24)
    ax1.set_xlabel("Dispatch Step Horizon", fontsize=9.1)
    ax1.set_ylabel("Cumulative Tie/Order Mismatches vs Fraction", fontsize=9.0)
    ax1.set_title("Bench 5: IEEE-754 Float Drift vs Integer Fixed-Point [E]+[M]", fontsize=9.4, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=7.9)

    xs = np.arange(2)
    ws = 0.30
    ax2.bar(xs - ws / 2, uncap["post_wake_shares"], width=ws, color=C["vermilion"],
            label=f"Uncapped OS ({uncap['max_sleeper_burst_steps']}-step monopoly)")
    ax2.bar(xs + ws / 2, cap["post_wake_shares"], width=ws, color=C["green"],
            label=f"gs_capped OS ({cap['max_sleeper_burst_steps']}-step max burst)")
    ax2.axhline(0.50, color=C["black"], linestyle="--", linewidth=1.3, label="Ideal 50% post-wake share")
    for xi, uv, cv in zip(xs, uncap["post_wake_shares"], cap["post_wake_shares"]):
        ax2.text(xi - ws / 2, uv - 0.04 if uv > 0.30 else uv + 0.02,
                 f"{uv*100:.1f}%", ha="center", va="top" if uv > 0.30 else "bottom",
                 color="white" if uv > 0.30 else C["black"], fontsize=8.3, fontweight="bold")
        ax2.text(xi + ws / 2, cv - 0.04, f"{cv*100:.1f}%", ha="center", va="top",
                 color="white", fontsize=8.3, fontweight="bold")
    ax2.set_xticks(xs)
    ax2.set_xticklabels(["Steady Worker", "Sleeper (woke @ t=1.0s)"], fontsize=8.8)
    ax2.set_ylim(0, 1.22)
    ax2.set_ylabel("Live Linux Post-Wake CPU Share [1.0s..1.8s]", fontsize=9.0)
    ax2.set_title("Bench 4 Live Linux I/O Sleeper Mitigation [D]", fontsize=9.5, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=7.9)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex6_fp_drift_and_live_sleeper.png"))


def main():
    d = load_data()
    fig1_refactor_architecture(d)
    fig2_complexity_scaling(d)
    fig3_ablation_ladder(d)
    fig4_sleeper_mitigation(d)
    fig5_os_refactor_validation(d)
    fig6_timeline_sleeper()
    fig7_cap_tradeoff_and_churn(d)
    fig8_fp_drift_and_live_sleeper(d)
    print("Generated 8 Exercise 6 diagrams cleanly in", DIAG_DIR)


if __name__ == "__main__":
    main()
