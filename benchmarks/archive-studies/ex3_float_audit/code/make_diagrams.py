"""Generate 6 crisp publication figures for Exercise 3 from experiments.json."""
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
EX3_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(EX3_DIR)
DATA_PATH = os.path.join(EX3_DIR, "output", "experiments.json")
DIAG_DIR = os.path.join(EX3_DIR, "diagrams")
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


def fig1_pipeline(d):
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(11.5, 4.9), dpi=220)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 5.0)
    ax.axis("off")

    ax.text(5.75, 4.78, "Exercise 3 Verification Architecture: Exact Fractions vs Simulation vs Float Drift",
            ha="center", va="top", fontsize=12.0, fontweight="bold", color=C["black"])

    pk.draw_box(ax, 1.95, 3.35, 3.2, 1.45,
                "1. Hand-Algebra Verifier [E]\nfractions.Fraction(p, q)\nNo shared code with gs_core\nChecks W1 (12t) & W2 (18t)",
                fc="#eef5fc", ec=C["blue"], tc=C["black"], fontsize=8.2)
    pk.draw_box(ax, 5.75, 3.35, 3.2, 1.45,
                "2. Core Simulator [M]\ngs_core.simulate_procs()\nExact Fraction ratios & V(t)\nExplicit tie-breaker param",
                fc="#eefaf5", ec=C["green"], tc=C["black"], fontsize=8.2)
    pk.draw_box(ax, 9.55, 3.35, 3.2, 1.45,
                "3. Float Accumulator [D]\nv_i += 1.0 / w_i (IEEE-754)\n1e-16 rounding flips exact ties\nDrifts 62/180 ticks on w=[3,6,9]",
                fc="#fdf2f0", ec=C["red"], tc=C["black"], fontsize=8.2)

    w1m = d["workload1_static"]["hand_vs_program_matches"]
    w2m = d["workload2_dynamic"]["hand_vs_program_matches"]
    pk.draw_box(ax, 3.85, 1.05, 6.4, 1.45,
                f"Static Match [E]=[M]: {w1m['index']}/12 (index), {w1m['stay']}/12 (stay), {w1m['max_weight']}/12 (max_w)\nDynamic Match [E]=[M]: gs_ratio={w2m['gs_ratio']}/18, gs_entitled={w2m['gs_entitled']}/18,\ngs_vtime={w2m['gs_vtime']}/18  (100% algebraic agreement)",
                fc="#f4f6fa", ec=C["sky"], tc=C["black"], fontsize=8.1)
    pk.draw_box(ax, 9.55, 1.05, 3.2, 1.3,
                "Design Rule [D]\nNever use binary float for\nexact virtual-time ties;\nuse rational Fraction / LCM!",
                fc="#fff5ed", ec=C["orange"], tc=C["black"], fontsize=8.1)

    pk.draw_arrow(ax, 3.55, 3.35, 4.15, 3.35, "==", label_offset=(0.0, 0.25), color=C["blue"])
    pk.draw_arrow(ax, 7.35, 3.35, 7.95, 3.35, "!=", label_offset=(0.0, 0.25), color=C["red"])
    pk.draw_arrow(ax, 2.3, 2.55, 3.3, 1.75, "100% tick match", label_offset=(-0.85, 0.05), color=C["blue"])
    pk.draw_arrow(ax, 5.4, 2.55, 4.4, 1.75, "exact audit", label_offset=(0.72, 0.05), color=C["green"])
    pk.draw_arrow(ax, 9.55, 2.55, 9.55, 1.75, "drift witness", label_offset=(-0.82, 0.0), color=C["red"])

    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_verification_pipeline.png"))


def fig2_static_hand_gantt(d):
    pk.apply_style()
    sim = d["workload1_static"]["sim_runs"]
    rows = [
        ("gs_ratio:index", "gs_ratio : index\n(and gs_vtime, stride)"),
        ("gs_ratio:stay", "gs_ratio : stay\n(min switches)"),
        ("gs_ratio:max_weight", "gs_ratio : max_weight\n(P3 favored on ties)"),
        ("rr:index", "RR : index\n(unweighted baseline)"),
    ]
    pcolors = {"P1": C["blue"], "P2": C["orange"], "P3": C["green"]}

    fig, ax = plt.subplots(figsize=(11.2, 4.6), dpi=220)
    for idx, (k, lbl) in enumerate(rows):
        y = len(rows) - 1 - idx
        for nm, st, en in sim[k]["gantt"]:
            ax.barh(y, en - st, left=st, height=0.56, color=pcolors[nm], edgecolor="white", linewidth=0.9)
            ax.text(0.5 * (st + en), y, f"{nm} ({en-st})" if en - st > 1 else nm,
                    ha="center", va="center", color="white", fontsize=8.0, fontweight="bold")
    # Highlight t=0 and t=6 rational reset boundaries
    for xb in (0, 6, 12):
        ax.axvline(xb, color="#334155", linestyle="--", linewidth=0.9, alpha=0.65)
    ax.text(6.0, 3.45, "Exact 1:2:3 tie reset (t=6)", ha="center", va="bottom",
            fontsize=8.2, fontweight="bold", color=C["black"])

    ax.set_yticks([3, 2, 1, 0])
    ax.set_yticklabels([lbl for _, lbl in rows], fontsize=8.8)
    ax.set_ylim(-0.5, 3.85)
    ax.set_xlim(0, 12)
    ax.set_xticks(range(0, 13))
    ax.set_xlabel("Time (integer ticks; P1(w=1, work=3), P2(w=2, work=5), P3(w=3, work=4))", fontsize=9.2)
    ax.set_title("Workload 1 Static Hand-Verified Trace (12/12 Match [E]=[M]): Effect of Tie-Breakers",
                 fontsize=10.8, fontweight="bold", pad=22)
    ax.grid(axis="x", linestyle=":", alpha=0.4)
    ax.legend(handles=[patches.Patch(color=pcolors[n], label=f"{n} (w={w})")
                       for n, w in [("P1", 1), ("P2", 2), ("P3", 3)]],
              loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=3, fontsize=8.3, framealpha=0.95)
    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_static_hand_gantt.png"))


def fig3_static_lag_fractions(d):
    pk.apply_style()
    tr = d["workload1_static"]["hand_trace_index"]
    ts = [0] + [r["t"] + 1 for r in tr]
    procs = ["P1", "P2", "P3"]
    pcolors = {"P1": C["blue"], "P2": C["orange"], "P3": C["green"]}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.0, 5.4), dpi=220, sharex=True)
    for nm in procs:
        act = [0] + [r["after"][nm]["actual"] for r in tr]
        ent = [0.0] + [r["after"][nm]["entitled_dec"] for r in tr]
        lag = [0.0] + [r["after"][nm]["lag_dec"] for r in tr]
        ax1.step(ts, act, where="post", color=pcolors[nm], linewidth=2.0, label=f"{nm} actual A(t)")
        ax1.plot(ts, ent, "--", color=pcolors[nm], linewidth=1.4, alpha=0.85, label=f"{nm} GPS E(t)")
        ax2.step(ts, lag, where="post", color=pcolors[nm], linewidth=2.0, label=f"{nm} signed lag")

    ax2.axhline(1.0, color=C["red"], linestyle=":", linewidth=1.1, label="Lag bound +1")
    ax2.axhline(-1.0, color=C["red"], linestyle=":", linewidth=1.1, label="Lag bound -1")
    ax2.axhline(0.0, color="#64748b", linewidth=0.8)
    ax1.set_ylabel("Cumulative CPU (ticks)", fontsize=9.2)
    ax1.set_title("Workload 1: Exact Cumulative Service A_i(t) vs GPS E_i(t) & Signed Lag (t = 0..12)",
                  fontsize=10.8, fontweight="bold")
    ax1.legend(loc="upper left", ncol=3, fontsize=7.8)
    ax1.grid(True, linestyle=":", alpha=0.5)

    ax2.set_ylabel("Signed Lag A_i(t) - E_i(t)", fontsize=9.2)
    ax2.set_ylim(-1.18, 1.18)
    ax2.set_xlim(0, 12)
    ax2.set_xticks(range(0, 13))
    ax2.set_xlabel("Time (integer ticks; zero-lag reset at t = 6 and completion at t = 12)", fontsize=9.2)
    ax2.legend(loc="upper right", ncol=2, fontsize=7.8)
    ax2.grid(True, linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_static_lag_fractions.png"))


def fig4_dynamic_divergence(d):
    pk.apply_style()
    sim = d["workload2_dynamic"]["sim_runs"]
    pols = [
        ("gs_ratio", "gs_ratio (used/w): P1 starved 6 ticks (t=4..10) + max lag 29/10"),
        ("gs_entitled", "gs_entitled (A_i/E_online): latecomers tracked by online entitlement (max lag 9/10)"),
        ("gs_vtime", "gs_vtime (v_i anchored to V(t)): tightest lag 7/10 across dynamic arrivals"),
    ]
    pcolors = {"P1": C["blue"], "P2": C["orange"], "P3": C["green"]}

    fig, axes = plt.subplots(3, 1, figsize=(11.4, 5.6), dpi=220, sharex=True)
    fig.suptitle("Workload 2 Dynamic Arrival Divergence: P1(arr=0,w=2), P2(arr=4,w=2), P3(arr=7,w=1)",
                 fontsize=11.4, fontweight="bold", y=0.98)
    for ax, (pk_name, title) in zip(axes, pols):
        row_map = {"P1": 2, "P2": 1, "P3": 0}
        if pk_name == "gs_ratio":
            ax.axvspan(4, 10, color="#fee2e2", alpha=0.75, zorder=0)
            ax.text(7.0, 2.0, "P1 starved 6 ticks!", ha="center", va="center",
                    fontsize=8.2, fontweight="bold", color=C["red"])
        for nm, st, en in sim[pk_name]["gantt"]:
            y = row_map[nm]
            ax.barh(y, en - st, left=st, height=0.56, color=pcolors[nm], edgecolor="white", linewidth=0.8)
            ax.text(0.5 * (st + en), y, f"{en-st}", ha="center", va="center",
                    color="white", fontsize=8.0, fontweight="bold")
        ax.axvline(4, color=C["orange"], linestyle="--", linewidth=1.0, alpha=0.75)
        ax.axvline(7, color=C["green"], linestyle="--", linewidth=1.0, alpha=0.75)
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(["P3 (arr=7)", "P2 (arr=4)", "P1 (arr=0)"], fontsize=8.5)
        ax.set_ylim(-0.48, 2.55)
        ax.set_title(title, loc="left", fontsize=9.3, fontweight="bold",
                     color=C["red"] if pk_name == "gs_ratio" else C["black"])
        ax.grid(axis="x", linestyle=":", alpha=0.45)

    axes[-1].set_xlim(0, 18)
    axes[-1].set_xticks(range(0, 19, 2))
    axes[-1].set_xlabel("Time (integer ticks; vertical lines mark P2 arrival t=4 and P3 arrival t=7)", fontsize=9.2)
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_dynamic_divergence.png"))


def fig5_dynamic_lag_curves(d):
    pk.apply_style()
    ht = d["workload2_dynamic"]["hand_traces"]
    ts = list(range(0, 19))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.5), dpi=220)
    pcolors = {"P1": C["blue"], "P2": C["orange"], "P3": C["green"]}

    worst_r = min(ht["gs_ratio"], key=lambda r: r["after"]["P1"]["lag_dec"])
    worst_t = worst_r["t"] + 1
    worst_val = worst_r["after"]["P1"]["lag_dec"]
    max_vt = max(abs(r["after"][nm]["lag_dec"]) for r in ht["gs_vtime"] for nm in ["P1", "P2", "P3"])
    for ax, pol, title in [
        (ax1, "gs_ratio", f"gs_ratio Signed Lag (Explodes to {worst_val:.2f} at t={worst_t})"),
        (ax2, "gs_vtime", f"gs_vtime Signed Lag (Strictly Bounded <= {max_vt:.2f})"),
    ]:
        rows = ht[pol]
        for nm in ["P1", "P2", "P3"]:
            vals = [0.0] + [r["after"][nm]["lag_dec"] for r in rows]
            ax.step(ts, vals, where="post", color=pcolors[nm], linewidth=2.1, label=f"{nm} lag")
        ax.axhline(0.0, color="#64748b", linewidth=0.8)
        ax.axhline(1.0, color=C["red"], linestyle=":", linewidth=1.0, alpha=0.7)
        ax.axhline(-1.0, color=C["red"], linestyle=":", linewidth=1.0, alpha=0.7)
        ax.axvline(4, color=C["orange"], linestyle="--", linewidth=0.9, alpha=0.6)
        ax.axvline(7, color=C["green"], linestyle="--", linewidth=0.9, alpha=0.6)
        ax.set_ylim(-3.2, 3.2)
        ax.set_xlim(0, 18)
        ax.set_xticks(range(0, 19, 2))
        ax.set_xlabel("Time (integer ticks)", fontsize=9.2)
        ax.set_ylabel("Signed GPS Lag A_i(t) - E_i(t)", fontsize=9.2)
        ax.set_title(title, fontsize=9.8, fontweight="bold")
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="lower right", fontsize=8.2)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_dynamic_lag_curves.png"))


def fig6_float_drift(d):
    pk.apply_style()
    dr = d["workload3_float_drift"]
    cases = dr["cases"]
    tr60 = dr["primary_first_60"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=220)
    labels = [f"w={c['weights']}\n({c['total_ticks']}t)" for c in cases]
    pcts = [c["diverged_pct"] for c in cases]
    cnts = [f"{c['diverged_ticks']}/{c['total_ticks']}\n({c['diverged_pct']:.1f}%)" for c in cases]
    colors6 = [C["red"], C["orange"], C["purple"], C["sky"], C["green"]]
    bars = ax1.bar(np.arange(len(cases)), pcts, color=colors6[:len(cases)],
                   width=0.52, edgecolor="#333", linewidth=0.7)
    for bar, txt, v in zip(bars, cnts, pcts):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 1.0, txt,
                 ha="center", va="bottom", fontsize=8.3, fontweight="bold")
    ax1.set_xticks(np.arange(len(cases)))
    ax1.set_xticklabels(labels, fontsize=8.8)
    ax1.set_ylim(0, max(pcts) * 1.28)
    ax1.set_ylabel("Diverged Dispatch Decisions (%)", fontsize=9.3)
    ax1.set_title("IEEE-754 Float vs Exact Fraction Drift [D]", fontsize=10.2, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)

    # Right: exact vs float choices on first 60 ticks of w=[3, 6, 9]
    ts = [r["t"] for r in tr60]
    ex_y = [r["exact"] for r in tr60]
    fl_y = [r["float"] for r in tr60]
    ax2.step(ts, ex_y, where="post", color=C["blue"], linewidth=2.0, label="Exact Fraction choice")
    ax2.step(ts, fl_y, where="post", color=C["red"], linestyle="--", linewidth=1.6, label="IEEE-754 float choice")
    div_ts = [r["t"] for r in tr60 if r["diverged"]]
    for dt in div_ts:
        ax2.axvspan(dt, dt + 1, color="#fee2e2", alpha=0.6, zorder=0)
    ax2.axvline(cases[0]["first_divergence_t"], color=C["red"], linestyle=":", linewidth=1.3)
    ax2.text(cases[0]["first_divergence_t"] + 1.2, 2.22,
             f"First tie flip at t={cases[0]['first_divergence_t']}",
             fontsize=8.2, fontweight="bold", color=C["red"])
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(["P1 (w=3)", "P2 (w=6)", "P3 (w=9)"], fontsize=8.8)
    ax2.set_ylim(-0.3, 2.45)
    ax2.set_xlim(0, 60)
    ax2.set_xlabel("Time (first 60 ticks of w=[3,6,9]; pink = dispatch mismatch)", fontsize=9.0)
    ax2.set_title("Tick-by-Tick Dispatch Divergence (w = [3, 6, 9])", fontsize=10.2, fontweight="bold")
    ax2.grid(axis="x", linestyle=":", alpha=0.45)
    ax2.legend(loc="lower right", fontsize=8.2)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_float_drift.png"))


def fig7_precision_comparison(d):
    pk.apply_style()
    pm = d["workload3_float_drift"]["precision_comparison"]
    fmts = [
        ("float32", "IEEE-754 float32", C["red"]),
        ("float64", "IEEE-754 float64", C["orange"]),
        ("fixed_q10", "Fixed-Point Q10 (1024/w)", C["purple"]),
        ("fixed_q20", "Fixed-Point Q20 (2^20/w)", C["sky"]),
        ("lcm_stride", "Exact Integer LCM//w (Zero Drift)", C["green"]),
    ]
    x = np.arange(len(pm))
    w = 0.155

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.7), dpi=220)
    for idx, (fk, flbl, col) in enumerate(fmts):
        vals = [c["formats"][fk]["diverged_pct"] for c in pm]
        offs = (idx - 2.0) * w
        bars = ax1.bar(x + offs, vals, width=w, color=col, edgecolor="#333", linewidth=0.55, label=flbl)
        if fk == "lcm_stride":
            for b in bars:
                ax1.text(b.get_x() + b.get_width() / 2, 1.2, "0%", ha="center", va="bottom",
                         fontsize=7.3, fontweight="bold", color=C["green"])

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"w={c['weights']}\nLCM={c['lcm']}" for c in pm], fontsize=8.4)
    ax1.set_ylabel("Diverged Dispatch Decisions (%)", fontsize=9.2)
    ax1.set_ylim(0, 62)
    ax1.set_title("Dispatch Divergence vs Exact Fraction Across 5 Formats", fontsize=10.2, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper right", fontsize=7.6, framealpha=0.95)

    # Right panel: First divergence tick (lower = breaks earlier; None = Exact Zero Drift)
    max_tot = max(c["total_ticks"] for c in pm)
    for idx, (fk, flbl, col) in enumerate(fmts):
        first_ts = []
        exact_flags = []
        for c in pm:
            ft = c["formats"][fk]["first_divergence_t"]
            if ft is None:
                first_ts.append(c["total_ticks"])
                exact_flags.append(True)
            else:
                first_ts.append(ft)
                exact_flags.append(False)
        offs = (idx - 2.0) * w
        bars = ax2.bar(x + offs, first_ts, width=w, color=col, edgecolor="#333", linewidth=0.55,
                       hatch=None if fk != "lcm_stride" else "//", label=flbl)
        for b, is_ex, val in zip(bars, exact_flags, first_ts):
            if is_ex:
                ax2.text(b.get_x() + b.get_width() / 2, val + 5, "NONE", ha="center", va="bottom",
                         fontsize=6.4, fontweight="bold", color=col, rotation=90)
            else:
                ax2.text(b.get_x() + b.get_width() / 2, val + 4, f"{val}", ha="center", va="bottom",
                         fontsize=6.5, color="#1e293b")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"w={c['weights']}\n({c['total_ticks']}t)" for c in pm], fontsize=8.4)
    ax2.set_ylabel("First Divergence Tick t (or Horizon = No Drift)", fontsize=9.0)
    ax2.set_ylim(0, max_tot * 1.18)
    ax2.set_title("Earliest Tie-Flip Tick (Lower = Fails Earlier; NONE = Exact)", fontsize=10.0, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_precision_formats.png"))


def fig8_quantum_and_w4_audit(d):
    pk.apply_style()
    w1q = d["workload1_static"]["quantum_runs"]
    w4r = d["workload4_asymmetric_audit"]["sim_runs"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.6), dpi=220)

    # Left: Workload 1 quantum sensitivity (q=1, 2, 3) index vs stay
    qs = [1, 2, 3]
    lags_idx = [w1q[f"q{q}_index"]["max_abs_lag"] for q in qs]
    lags_stay = [w1q[f"q{q}_stay"]["max_abs_lag"] for q in qs]
    sw_idx = [w1q[f"q{q}_index"]["context_switches"] for q in qs]
    sw_stay = [w1q[f"q{q}_stay"]["context_switches"] for q in qs]

    ax1.plot(qs, lags_idx, "o-", color=C["blue"], linewidth=2.1, label="Max Lag (index)")
    ax1.plot(qs, lags_stay, "s--", color=C["green"], linewidth=2.1, label="Max Lag (stay)")
    ax1b = ax1.twinx()
    ax1b.bar(np.array(qs) - 0.14, sw_idx, width=0.26, color=C["orange"], alpha=0.35, label="Switches (index)")
    ax1b.bar(np.array(qs) + 0.14, sw_stay, width=0.26, color=C["purple"], alpha=0.45, label="Switches (stay)")
    ax1.set_xticks(qs)
    ax1.set_xticklabels([f"q = {q}" for q in qs], fontsize=9.0)
    ax1.set_ylabel("Max Absolute GPS Lag (ticks)", fontsize=9.2, color=C["blue"])
    ax1b.set_ylabel("Context Switches", fontsize=9.2, color=C["purple"])
    ax1.set_ylim(0, 3.6)
    ax1b.set_ylim(0, 15.5)
    ax1.set_title("Workload 1 Quantum Scaling (q = 1, 2, 3): Lag vs Switches", fontsize=10.1, fontweight="bold")
    ax1.grid(axis="y", linestyle=":", alpha=0.45)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax1b.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", ncol=2, fontsize=7.3, framealpha=0.95)

    # Right: Workload 4 [1:3:5] 24-tick dynamic audit across q=1, 2, 3
    pols = [
        ("gs_ratio:index", "gs_ratio", C["red"]),
        ("gs_entitled:index", "gs_entitled", C["sky"]),
        ("gs_vtime:index", "gs_vtime", C["green"]),
        ("stride:index", "stride", C["orange"]),
        ("rr:index", "RR", C["purple"]),
    ]
    x = np.arange(len(qs))
    bw = 0.155
    for idx, (pk_pfx, lbl, col) in enumerate(pols):
        vals = [w4r[f"{pk_pfx}_q{q}"]["max_abs_lag"] for q in qs]
        ax2.bar(x + (idx - 2.0) * bw, vals, width=bw, color=col, edgecolor="#333", linewidth=0.55, label=lbl)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"q = {q}" for q in qs], fontsize=9.0)
    ax2.set_ylabel("Max Absolute GPS Lag (ticks)", fontsize=9.2)
    ax2.set_ylim(0, 4.4)
    ax2.set_title("Workload 4 Asymmetric [1:3:5] (24t) Lag Across Policies", fontsize=10.1, fontweight="bold")
    ax2.grid(axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper left", ncol=2, fontsize=7.6, framealpha=0.95)

    fig.tight_layout()
    pk.save_fig(fig, os.path.join(DIAG_DIR, "fig_ex3_quantum_w4_audit.png"))


def main():
    d = load_data()
    fig1_pipeline(d)
    fig2_static_hand_gantt(d)
    fig3_static_lag_fractions(d)
    fig4_dynamic_divergence(d)
    fig5_dynamic_lag_curves(d)
    fig6_float_drift(d)
    fig7_precision_comparison(d)
    fig8_quantum_and_w4_audit(d)
    print("Generated 8 Exercise 3 diagrams cleanly in", DIAG_DIR)


if __name__ == "__main__":
    main()
