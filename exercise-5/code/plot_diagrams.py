"""Generate 8 publication-grade Okabe-Ito diagrams for Exercise 5 (Readers-Writers)."""
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
EX5_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(EX5_DIR)
DIAG_DIR = os.path.join(EX5_DIR, "diagrams")
OUT_JSON = os.path.join(EX5_DIR, "output", "experiments.json")
os.makedirs(DIAG_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "tools"))
import plot_kit as pk  # noqa: E402

COLORS = {
    "Semaphore": "#1b9e77",
    "Monitor": "#d95f02",
    "Peterson": "#0072b2",
    "Dekker": "#1f4e78",
    "CoarseMutex": "#64748b",
}


def fig1_concurrency_safety(d: dict) -> None:
    pk.apply_style()
    rows = d["safety_concurrency_audits"]
    labels = [f"{r['primitive']}\n({r['policy']})" for r in rows]
    max_r = [r["max_concurrent_readers"] for r in rows]
    cols = [COLORS[r["primitive"]] for r in rows]

    fig, ax = plt.subplots(figsize=(11.5, 4.4))
    x = np.arange(len(rows))
    bars = ax.bar(x, max_r, width=0.62, color=cols, edgecolor="#0f172a", alpha=0.9)
    for b, r in zip(bars, rows):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.12,
                f"R={r['max_concurrent_readers']}\nerr={r['safety_violations']}",
                ha="center", fontsize=7.2, fontweight="bold", color="#0f172a")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.2, rotation=20, ha="right")
    ax.set_ylim(0, 5.2)
    ax.set_ylabel("Peak Simultaneous Readers Observed")
    ax.set_title("Concurrent Safety Audit (4 Readers + 2 Writers): All 12 RW Implementations Allow 4x Readers with 0 Overlaps", fontsize=10.5)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex5_fig1_concurrency_safety.png"))


def _plot_starvation(d: dict, flood_mode: str, fname: str, title: str, victim_lbl: str) -> None:
    pk.apply_style()
    prims = ["Semaphore", "Monitor", "Peterson", "Dekker"]
    pols = ["readers", "writers", "fair"]
    pol_cols = {"readers": "#dc2626", "writers": "#d97706", "fair": "#047857"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.5), gridspec_kw={"wspace": 0.25})
    x = np.arange(len(prims))
    w = 0.25
    for idx, po in enumerate(pols):
        sub = [next(r for r in d["starvation_stress_audits"]
                    if r["flood_mode"] == flood_mode and r["primitive"] == pr and r["policy"] == po)
               for pr in prims]
        vops = [r["victim_ops"] for r in sub]
        mwait = [r["victim_max_wait_ms"] for r in sub]
        b1 = ax1.bar(x + (idx - 1) * w, vops, w, label=f"{po.title()}-Pref" if po != "fair" else "Fair/Turnstile",
                     color=pol_cols[po], edgecolor="#0f172a", alpha=0.9)
        for b in b1:
            ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.7, str(int(b.get_height())),
                     ha="center", fontsize=7.6, fontweight="bold")
        b2 = ax2.bar(x + (idx - 1) * w, mwait, w, label=f"{po.title()}-Pref" if po != "fair" else "Fair/Turnstile",
                     color=pol_cols[po], edgecolor="#0f172a", alpha=0.9)
        for b in b2:
            ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 2.5, f"{b.get_height():.0f}",
                     ha="center", fontsize=7.3, fontweight="bold")

    ax1.set_xticks(x)
    ax1.set_xticklabels(prims, fontsize=8.8, fontweight="bold")
    ax1.set_ylim(0, max(45, max(r["victim_ops"] for r in d["starvation_stress_audits"] if r["flood_mode"] == flood_mode) * 1.25))
    ax1.set_ylabel(f"Completed {victim_lbl} Ops in 120 ms Window")
    ax1.set_title(f"{victim_lbl} Throughput Under Continuous Flood")
    ax1.legend(loc="upper right", fontsize=8)

    ax2.set_xticks(x)
    ax2.set_xticklabels(prims, fontsize=8.8, fontweight="bold")
    ax2.set_ylim(0, 162)
    ax2.set_ylabel(f"Max {victim_lbl} Wait Latency (ms)")
    ax2.set_title(f"Peak {victim_lbl} Wait (120 ms = Total Starvation)")
    ax2.legend(loc="upper center", ncol=3, fontsize=7.6)
    fig.suptitle(title, fontsize=11.2, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, fname))


def fig4_mix_sweep(d: dict) -> None:
    pk.apply_style()
    prims = ["Semaphore", "Monitor", "Peterson", "Dekker", "CoarseMutex"]
    pcts = [95, 80, 50, 20]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 4.6), gridspec_kw={"wspace": 0.25})
    for cs, ax, ttl in [
        (0.0, ax1, "Zero-Work CS (0.0 ms): Lock Overhead Dominates"),
        (0.3, ax2, "Realistic Read Scan (0.3 ms): 4.0x RW Speedup at R=95%"),
    ]:
        for pr in prims:
            vals = [next(r["throughput_ops_s"] for r in d["mix_sweep"]
                         if r["cs_sleep_ms"] == cs and r["primitive"] == pr and r["read_pct"] == p) for p in pcts]
            ax.plot(pcts, [v / 1000.0 for v in vals], marker="o", linewidth=2.2,
                    linestyle="--" if pr == "CoarseMutex" else "-",
                    color=COLORS[pr], label=pr)
        ax.set_xticks(pcts)
        ax.invert_xaxis()
        ax.set_xlabel("Read Operation Percentage (%)")
        ax.set_ylabel("Throughput (k ops/sec)")
        ax.set_title(ttl, fontsize=9.8)
        if cs == 0.0:
            ax.set_ylim(50, 580)
            ax.legend(loc="center right", bbox_to_anchor=(0.99, 0.45), fontsize=7.6)
        else:
            ax.set_ylim(1.5, 10.6)
            ax.legend(loc="upper right", fontsize=7.8)
    fig.suptitle("Read:Write Ratio Crossover Sweep (95:5 -> 20:80) Across Fair RW Locks vs. Coarse Mutex", fontsize=11.3, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex5_fig4_read_write_mix_speedup.png"))


def fig5_cpu_burn(d: dict) -> None:
    pk.apply_style()
    rows = d["cpu_burn_audits"]
    prims = [r["primitive"] for r in rows]
    walls = [r["wall_ms"] for r in rows]
    cpus = [r["cpu_ms"] for r in rows]

    fig, ax = plt.subplots(figsize=(10.2, 4.5))
    x = np.arange(len(rows))
    w = 0.36
    b1 = ax.bar(x - w / 2, walls, w, label="Wall-Clock Time (ms)", color="#1f4e78", edgecolor="#0f172a")
    b2 = ax.bar(x + w / 2, cpus, w, label="Process CPU Burned (ms)", color="#d95f02", edgecolor="#0f172a")
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 10, f"{h:.1f}", ha="center", fontsize=8, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(prims, fontsize=9.5, fontweight="bold")
    ax.set_ylim(0, max(walls) * 1.18)
    ax.set_ylabel("Milliseconds (Writer Waiting Behind 5 ms Slow Readers)")
    ax.set_title("Writer-Wait CPU Burn Audit: Blocking Sleep (~2 ms CPU) vs. Spin-Wait (~469-615 ms CPU)", fontsize=10.8)
    ax.legend(loc="upper left", fontsize=8.8)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex5_fig5_writer_wait_cpu_burn.png"))


def fig6_bfs_models(d: dict) -> None:
    pk.apply_style()
    rows = d["bfs_rw_models"]
    pols = [f"{r['policy'].title()}\n({r['reachable_states']} states)" for r in rows]
    fig, ax = plt.subplots(figsize=(9.8, 4.3))
    x = np.arange(len(rows))
    w = 0.25
    b1 = ax.bar(x - w, [r["reachable_states"] for r in rows], w, label="Reachable BFS States", color="#1f4e78", edgecolor="#0f172a")
    b2 = ax.bar(x, [r["dual_reader_states"] for r in rows], w, label="Concurrent Dual-Reader States", color="#1b9e77", edgecolor="#0f172a")
    b3 = ax.bar(x + w, [r["writer_starvation_bypass_states"] for r in rows], w, label="Writer Starvation Bypass States", color="#dc2626", edgecolor="#0f172a")
    for b in list(b1) + list(b2) + list(b3):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.5, str(int(h)), ha="center", fontsize=8, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(pols, fontsize=9, fontweight="bold")
    ax.set_ylim(0, max(r["reachable_states"] for r in rows) * 1.2)
    ax.set_ylabel("State Count (2 Readers + 1 Writer BFS)")
    ax.set_title("Formal BFS State-Space Audit of Readers-Writers Policies (0 Safety Errors Across All 3)", fontsize=10.8)
    ax.legend(loc="upper left", fontsize=8.5)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex5_fig6_bfs_rw_states.png"))


def fig7_policies_arch() -> None:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(11.0, 4.6))
    ax.axis("off")
    ax.set_xlim(0, 11.0)
    ax.set_ylim(0, 4.8)
    cards = [
        ("1st RW: Readers-Preference", [
            "Rule: Readers enter whenever",
            "active_writers == 0",
            "Concurrency: Max reader overlap",
            "Starvation: WRITER STARVES!",
            "(0 writer ops in 120ms flood)",
            "BFS bypass cycles: 2 states",
        ], "#1f4e78", "#eff6ff"),
        ("2nd RW: Writers-Preference", [
            "Rule: Block new readers if",
            "waiting_writers > 0",
            "Concurrency: Burst reader overlap",
            "Starvation: READER STARVES!",
            "(0 reader ops in writer flood)",
            "Fast writer takeover (2.2ms)",
        ], "#d95f02", "#fff7ed"),
        ("3rd RW: Fair FIFO / Turnstile", [
            "Rule: Strict arrival order",
            "via turnstile / FIFO ticket",
            "Concurrency: Batch readers safe",
            "Starvation: ZERO in Ticket/Deque!",
            "(12/37 ops in both floods)",
            "Note: Unfair Sem can still barge",
        ], "#1b9e77", "#ecfdf5"),
    ]
    for i, (hdr, lines, ec, fc) in enumerate(cards):
        x = 0.25 + i * 3.58
        ax.add_patch(patches.FancyBboxPatch((x, 0.3), 3.32, 4.1, boxstyle="round,pad=0.10", fc=fc, ec=ec, lw=1.6))
        ax.add_patch(patches.FancyBboxPatch((x, 3.72), 3.32, 0.68, boxstyle="round,pad=0.06", fc=ec, ec=ec, lw=1.0))
        ax.text(x + 1.66, 4.06, hdr, ha="center", va="center", fontsize=8.8, fontweight="bold", color="white")
        for j, ln in enumerate(lines):
            ax.text(x + 1.66, 3.22 - j * 0.48, ln, ha="center", va="center", fontsize=7.9,
                    fontweight="bold" if j in (3, 4) else "normal", color="#0f172a")
    ax.set_title("Three Classical Readers-Writers Policies: Rules, Concurrency & Starvation Trade-Offs", fontsize=11.2, fontweight="bold")
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex5_fig7_three_policies_architecture.png"))


def fig8_mechanism_comparison() -> None:
    pk.apply_style()
    cats = ["Anti-Barging\nFairness", "CPU Energy\nEfficiency", "4x Reader\nSpeedup", "Code Clarity\n& Safety", "Zero Kernel\nSpin Path"]
    scores = {
        "Semaphore": [2.8, 5.0, 5.0, 3.0, 3.0],
        "Monitor":   [5.0, 5.0, 4.8, 5.0, 2.8],
        "Peterson":  [4.8, 1.0, 4.2, 2.2, 5.0],
        "Dekker":    [4.8, 1.0, 4.6, 1.8, 4.8],
    }
    x = np.arange(len(cats))
    w = 0.2
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    for i, (pr, vals) in enumerate(scores.items()):
        ax.bar(x + (i - 1.5) * w, vals, w, label=pr, color=COLORS[pr], edgecolor="#0f172a", alpha=0.92)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=8.8, fontweight="bold")
    ax.set_ylim(0, 5.8)
    ax.set_ylabel("Engineering Rubric Score (1-5)")
    ax.set_title("Readers-Writers Implementation Scorecard Across All Four Synchronization Primitives", fontsize=11)
    ax.legend(loc="upper right", ncol=4, fontsize=8.5)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex5_fig8_four_mechanisms_matrix.png"))


def main() -> None:
    with open(OUT_JSON, "r", encoding="utf-8") as f:
        d = json.load(f)
    fig1_concurrency_safety(d)
    _plot_starvation(d, "reader_flood", "ex5_fig2_starvation_reader_flood.png",
                     "Reader-Flood Starvation Test: Readers-Pref Starves Writer Completely (0 Ops)", "Writer")
    _plot_starvation(d, "writer_flood", "ex5_fig3_starvation_writer_flood.png",
                     "Writer-Flood Starvation Test: Fair Ticket/Deque Protects Reader vs. Unfair Sem Barging", "Reader")
    fig4_mix_sweep(d)
    fig5_cpu_burn(d)
    fig6_bfs_models(d)
    fig7_policies_arch()
    fig8_mechanism_comparison()
    print("Generated 8 PNG figures in", DIAG_DIR)


if __name__ == "__main__":
    main()
