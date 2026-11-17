"""Generate 10 Okabe-Ito publication-grade diagrams for Exercise 4."""
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
ROOT = os.path.dirname(EX4_DIR)
DIAG_DIR = os.path.join(EX4_DIR, "diagrams")
OUT_JSON = os.path.join(EX4_DIR, "output", "experiments.json")
os.makedirs(DIAG_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "tools"))
import plot_kit as pk  # noqa: E402

PRIM_COLORS = {
    "Dekker": "#1f4e78",
    "Peterson": "#0072b2",
    "Filter": "#56b4e9",
    "Tournament": "#7570b3",
    "Semaphore": "#1b9e77",
    "Monitor": "#d95f02",
}


def _col(name: str) -> str:
    for k, v in PRIM_COLORS.items():
        if k.lower() in name.lower():
            return v
    return "#475569"


def fig1_state_space(d: dict) -> None:
    pk.apply_style()
    rows = d["dekker_evolution_fsm"] + d["all_primitives_fsm"]
    labels = [r["model"].replace(" (", "\n(") for r in rows]
    states = [r["reachable_states"] for r in rows]
    errs = [r["mutex_violations"] + r["deadlock_states"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.8), gridspec_kw={"wspace": 0.34})
    y = np.arange(len(rows))

    cols1 = ["#b91c1c" if e > 0 or "v1" in r["model"] or "v4" in r["model"] else "#1b9e77" for r, e in zip(rows, errs)]
    ax1.barh(y, states, color=cols1, edgecolor="#1e293b", alpha=0.88)
    for i, v in enumerate(states):
        ax1.text(v + 3, i, str(v), va="center", fontsize=8, fontweight="bold")
    ax1.set_yticks(y)
    ax1.set_yticklabels([r["model"] for r in rows], fontsize=7.8)
    ax1.invert_yaxis()
    ax1.set_xlim(0, max(states) * 1.18)
    ax1.set_xlabel("Reachable BFS States (Exact Interleaving Exploration)")
    ax1.set_title("State-Space Explosion Across Primitives")

    ax2.barh(y, errs, color=["#dc2626" if e > 0 else "#cbd5e1" for e in errs], edgecolor="#1e293b")
    for i, (r, e) in enumerate(zip(rows, errs)):
        tag = f"{e} errors" if e > 0 else ("Livelock/Strict" if "v1" in r["model"] or "v4" in r["model"] else "0 errors (SAFE)")
        ax2.text(e + 0.18, i, tag, va="center", fontsize=7.8, fontweight="bold",
                 color="#b91c1c" if e > 0 else ("#b45309" if "Livelock" in tag else "#047857"))
    ax2.set_yticks(y)
    ax2.set_yticklabels([])
    ax2.invert_yaxis()
    ax2.set_xlim(0, max(errs) + 4.5)
    ax2.set_xlabel("Safety / Deadlock Errors Found by Exhaustive Model Checker")
    ax2.set_title("Mutex Violations + Deadlocks (Red = Unsafe)")
    fig.suptitle("Formal Explicit-State BFS Model Checking: Dekker v1-v5, Peterson (SC vs TSO), Semaphore & Monitor", fontsize=11.5, fontweight="bold", y=1.01)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig1_state_space_audit.png"))


def fig2_busywait_vs_blocking(d: dict) -> None:
    pk.apply_style()
    rows = [r for r in d["lock_holder_sleep_audit"] if r["hold_ms"] == 10]
    names = [r["primitive"] for r in rows]
    walls = [r["wall_ms"] for r in rows]
    cpus = [r["cpu_ms"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4), gridspec_kw={"wspace": 0.25})
    x = np.arange(len(names))
    w = 0.36
    b1 = ax1.bar(x - w / 2, walls, w, label="Wall-Clock Time (ms)", color="#1f4e78", edgecolor="#0f172a")
    b2 = ax1.bar(x + w / 2, cpus, w, label="Process CPU Time Burned (ms)", color="#d95f02", edgecolor="#0f172a")
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2, h + 6, f"{h:.1f}", ha="center", fontsize=7.8, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels([n.replace(" (", "\n(") for n in names], fontsize=8)
    ax1.set_ylim(0, max(walls) * 1.18)
    ax1.set_ylabel("Milliseconds (10ms Hold Delay x 20 Ops)")
    ax1.set_title("Wall Time vs. Burned CPU Time (hold = 10 ms)")
    ax1.legend(loc="upper right", fontsize=8)

    # Panel 2: CPU-to-Wall Ratio across hold delays 2, 5, 10 ms
    for pname in ["Dekker (Busy-Wait)", "Peterson (Busy-Wait)", "Semaphore (Blocking)", "Monitor (Mesa Cond)"]:
        sub = sorted([r for r in d["lock_holder_sleep_audit"] if r["primitive"] == pname], key=lambda r: r["hold_ms"])
        ax2.plot([r["hold_ms"] for r in sub], [r["cpu_to_wall_ratio"] * 100.0 for r in sub],
                 marker="o", linewidth=2.2, color=_col(pname), label=pname)
    ax2.set_xlabel("Lock-Holder Delay / I/O Sleep per CS (ms)")
    ax2.set_ylabel("CPU-to-Wall Utilization Ratio (%)")
    ax2.set_ylim(-5, 112)
    ax2.set_title("Busy-Wait Wastes ~98% Core vs. ~1% Blocking Sleep")
    ax2.legend(loc="center right", fontsize=8)
    fig.suptitle("OS Lock-Holder Preemption / Sleep Audit: Spin-Waiting vs. Kernel Blocking", fontsize=11.5, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig2_busywait_vs_blocking_cpu.png"))


def fig3_cs_throughput(d: dict) -> None:
    pk.apply_style()
    workloads = ["Light (CS=0)", "Medium (CS=150)", "Heavy (CS=600)"]
    prims = ["Dekker (Yield)", "Peterson (Yield)", "Semaphore (Blocking)", "Monitor (Mesa Cond)"]
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    x = np.arange(len(workloads))
    w = 0.19
    for idx, p in enumerate(prims):
        vals = [next(r["throughput_ops_s"] for r in d["cs_work_sweep_n2"] if r["workload"] == wl and r["primitive"] == p) / 1000.0 for wl in workloads]
        bars = ax.bar(x + (idx - 1.5) * w, vals, w, label=p, color=_col(p), edgecolor="#0f172a", alpha=0.92)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 50, f"{v:.0f}k", ha="center", fontsize=7.2, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontsize=9.2, fontweight="bold")
    ax.set_ylabel("Throughput (k ops/sec)")
    ax.set_ylim(0, max(r["throughput_ops_s"] for r in d["cs_work_sweep_n2"]) / 1000.0 * 1.18)
    ax.set_title("2-Thread Contention Throughput Across Critical Section Workloads (Yield vs Blocking)", fontsize=11)
    ax.legend(loc="upper right", fontsize=8.3)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig3_throughput_vs_cs_work.png"))


def fig4_scaling(d: dict) -> None:
    pk.apply_style()
    prims = ["Filter Lock (N-Peterson)", "Tournament Dekker (Tree)", "Semaphore (Blocking)", "Monitor (Mesa Cond)"]
    ns = [2, 4, 8]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.5), gridspec_kw={"wspace": 0.25})
    for p in prims:
        sub = [next(r for r in d["thread_scaling"] if r["primitive"] == p and r["n_threads"] == n) for n in ns]
        ax1.plot(ns, [r["throughput_ops_s"] / 1000.0 for r in sub], marker="o", linewidth=2.2, color=_col(p), label=p)
        ax2.plot(ns, [r["wall_ms"] for r in sub], marker="s", linewidth=2.2, color=_col(p), label=p)
    ax1.set_xticks(ns)
    ax1.set_xlabel("Number of Contending OS Threads N")
    ax1.set_ylabel("Throughput (k ops/sec)")
    ax1.set_title("Throughput Scaling (N = 2, 4, 8)")
    ax1.legend(loc="upper right", fontsize=8)
    ax2.set_xticks(ns)
    ax2.set_xlabel("Number of Contending OS Threads N")
    ax2.set_ylabel("Total Wall Time (ms)")
    ax2.set_title("Latency Growth Under Multi-Thread Contention")
    ax2.legend(loc="upper left", fontsize=8)
    fig.suptitle("Multi-Thread Scalability: O(N) Filter Lock vs. O(log N) Tournament Dekker vs. Kernel Semaphore & Monitor", fontsize=11.3, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig4_multithread_scaling.png"))


def fig5_bounded_buffer(d: dict) -> None:
    pk.apply_style()
    rows = d["bounded_buffer_bench"]
    modes = [r["mode"].replace(" (", "\n(") for r in rows]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.3), gridspec_kw={"wspace": 0.25})
    x = np.arange(len(rows))
    cols = ["#1b9e77", "#d95f02", "#0072b2"]
    b1 = ax1.bar(x, [r["ops_per_s"] / 1000.0 for r in rows], width=0.52, color=cols, edgecolor="#0f172a")
    for b in b1:
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 2, f"{b.get_height():.1f}k", ha="center", fontsize=8.5, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(modes, fontsize=8.3)
    ax1.set_ylim(0, max(r["ops_per_s"] for r in rows) / 1000.0 * 1.18)
    ax1.set_ylabel("Throughput (k items/sec)")
    ax1.set_title("Throughput (1200 items, cap=8)", fontsize=10)

    b2 = ax2.bar(x, [r["cond_waits_or_spin_retries"] for r in rows], width=0.52, color=cols, edgecolor="#0f172a")
    for b in b2:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 8, f"{int(b.get_height())}", ha="center", fontsize=8.5, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(modes, fontsize=8.3)
    ax2.set_ylim(0, max(r["cond_waits_or_spin_retries"] for r in rows) * 1.18 + 20)
    ax2.set_ylabel("Condition Waits / Polling Retries")
    ax2.set_title("Condition Waits vs. Spin Retries", fontsize=10)
    fig.suptitle("Condition Synchronization Benchmark: Bounded-Buffer Producer-Consumer", fontsize=11.5, fontweight="bold", y=1.02)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig5_bounded_buffer_sync.png"))


def fig6_dekker_evolution() -> None:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(11.0, 4.8))
    ax.axis("off")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.2)
    stages = [
        ("v1: Strict Alternation\n(while turn != i)", "SAFE CS, FAILS Progress\n(16 states, 1-thread stall)", "#fef3c7", "#b45309"),
        ("v2: Check-Then-Set\n(if !flag[j]: flag[i]=1)", "FAILS Mutual Exclusion\n(25 states, 1 CS violation)", "#fee2e2", "#dc2626"),
        ("v3: Set-Then-Wait\n(flag[i]=1; while flag[j])", "FAILS Deadlock-Free\n(21 states, 1 deadlock)", "#fee2e2", "#dc2626"),
        ("v4: Symmetric Backoff\n(yield flag temporarily)", "FAILS Livelock-Free\n(45 states, 22 spin cycles)", "#ffedd5", "#ea580c"),
        ("v5: Complete Dekker\n(flag + turn tiebreak)", "ALL 3 CRITERIA SAFE\n(134 states, 0 errors)", "#d1fae5", "#047857"),
    ]
    for i, (t1, t2, fc, ec) in enumerate(stages):
        x = 0.2 + i * 2.15
        p = patches.FancyBboxPatch((x, 2.2), 1.9, 2.2, boxstyle="round,pad=0.12", fc=fc, ec=ec, lw=1.5)
        ax.add_patch(p)
        ax.text(x + 0.95, 3.85, t1, ha="center", va="center", fontsize=7.6, fontweight="bold", color="#0f172a")
        ax.text(x + 0.95, 2.75, t2, ha="center", va="center", fontsize=7.2, color="#1e293b")
        if i < len(stages) - 1:
            ax.annotate("", xy=(x + 2.13, 3.3), xytext=(x + 1.92, 3.3), arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.5))

    p_pet = patches.FancyBboxPatch((0.5, 0.35), 10.0, 1.25, boxstyle="round,pad=0.12", fc="#dbeafe", ec="#1d4ed8", lw=1.5)
    ax.add_patch(p_pet)
    ax.text(5.5, 0.97, "Peterson (1981) Unification: flag[i]=True; turn=j; while(flag[j] && turn==j)\nReduces BFS state space 3.2x (134 -> 42 states) with zero back-off branches",
            ha="center", va="center", fontsize=8.3, fontweight="bold", color="#0f172a")
    ax.set_title("Historical & Formal Verification Trajectory: Dekker v1 -> v5 -> Peterson", fontsize=11.5, fontweight="bold")
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig6_dekker_evolution_fsm.png"))


def fig7_tso_store_buffer() -> None:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(10.6, 4.6))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)

    for cx, title, st_buf, rd_val in [
        (0.4, "Core 0 (Thread 0)", "Store Buffer: [flag[0]=1]\n(NOT flushed to L1/RAM yet!)", "Reads flag[1] == 0 from RAM\n-> ENTERS CS!"),
        (5.6, "Core 1 (Thread 1)", "Store Buffer: [flag[1]=1]\n(NOT flushed to L1/RAM yet!)", "Reads flag[0] == 0 from RAM\n-> ENTERS CS TOO!"),
    ]:
        ax.add_patch(patches.FancyBboxPatch((cx, 2.7), 4.0, 1.85, boxstyle="round,pad=0.12", fc="#f8fafc", ec="#1f4e78", lw=1.4))
        ax.text(cx + 2.0, 4.28, title, ha="center", fontsize=9.5, fontweight="bold", color="#1f4e78")
        ax.add_patch(patches.FancyBboxPatch((cx + 0.2, 3.45), 3.6, 0.58, boxstyle="round,pad=0.06", fc="#fef3c7", ec="#d97706", lw=1.0))
        ax.text(cx + 2.0, 3.74, st_buf, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#92400e")
        ax.add_patch(patches.FancyBboxPatch((cx + 0.2, 2.82), 3.6, 0.48, boxstyle="round,pad=0.06", fc="#fee2e2", ec="#dc2626", lw=1.1))
        ax.text(cx + 2.0, 3.06, rd_val, ha="center", va="center", fontsize=7.5, fontweight="bold", color="#991b1b")

    ax.add_patch(patches.FancyBboxPatch((2.1, 1.35), 5.8, 0.88, boxstyle="round,pad=0.10", fc="#e2e8f0", ec="#334155", lw=1.3))
    ax.text(5.0, 1.79, "Shared Coherent Memory (Before Flush): flag[0] = 0, flag[1] = 0\nBFS TSO Model Checker Finds 8 Dual-CS Error States!", ha="center", va="center", fontsize=8.3, fontweight="bold", color="#0f172a")

    ax.add_patch(patches.FancyBboxPatch((0.6, 0.22), 8.8, 0.78, boxstyle="round,pad=0.08", fc="#d1fae5", ec="#047857", lw=1.3))
    ax.text(5.0, 0.61, "Fix: Insert Full Memory Barrier (x86 MFENCE / ARM DMB ISH / C++11 std::atomic seq_cst)\nbetween store(flag[i]) and load(flag[j])",
            ha="center", va="center", fontsize=8.0, fontweight="bold", color="#065f46")

    ax.annotate("", xy=(3.5, 2.25), xytext=(2.4, 2.7), arrowprops=dict(arrowstyle="<->", color="#dc2626", lw=1.4))
    ax.annotate("", xy=(6.5, 2.25), xytext=(7.6, 2.7), arrowprops=dict(arrowstyle="<->", color="#dc2626", lw=1.4))
    ax.set_title("Why Peterson & Dekker Break on Modern x86/ARM CPUs Without Memory Barriers", fontsize=11.3, fontweight="bold")
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig7_memory_fence_tso.png"))


def fig8_hoare_vs_mesa() -> None:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(10.8, 4.6))
    ax.axis("off")
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 5.0)

    # Left: Hoare
    ax.add_patch(patches.FancyBboxPatch((0.25, 0.35), 4.95, 4.15, boxstyle="round,pad=0.12", fc="#eff6ff", ec="#1d4ed8", lw=1.4))
    ax.text(2.72, 4.18, "Hoare Monitor (1974): Signal-and-Wait", ha="center", fontsize=9.8, fontweight="bold", color="#1e3a8a")
    hoare_steps = [
        ("1. Producer calls c.signal()", "#dbeafe"),
        ("2. Lock transfers IMMEDIATELY to Consumer\n   Producer pauses in Urgent Queue", "#bfdbfe"),
        ("3. Condition guaranteed STILL TRUE:\n   'if (not ready) wait()' is sufficient!", "#bbf7d0"),
        ("4. Consumer exits -> Urgent Producer resumes\n   (+2 extra lock handoffs per signal)", "#fef3c7"),
    ]
    for i, (txt, c) in enumerate(hoare_steps):
        ax.add_patch(patches.FancyBboxPatch((0.48, 3.2 - i * 0.85), 4.5, 0.68, boxstyle="round,pad=0.06", fc=c, ec="#334155", lw=0.9))
        ax.text(2.72, 3.54 - i * 0.85, txt, ha="center", va="center", fontsize=7.6, fontweight="bold", color="#0f172a")

    # Right: Mesa
    ax.add_patch(patches.FancyBboxPatch((5.6, 0.35), 4.95, 4.15, boxstyle="round,pad=0.12", fc="#fff7ed", ec="#c2410c", lw=1.4))
    ax.text(8.07, 4.18, "Mesa Monitor (POSIX/Java): Signal-and-Continue", ha="center", fontsize=9.1, fontweight="bold", color="#9a3412")
    mesa_steps = [
        ("1. Producer calls cond.notify()", "#ffedd5"),
        ("2. Consumer moves Wait -> Entry Queue\n   Producer CONTINUES & finishes monitor call", "#fed7aa"),
        ("3. Intruder Thread may acquire lock FIRST!\n   'if (!cond)' -> 6 BFS underflow bugs!", "#fecaca"),
        ("4. Mandatory 'while (!cond) wait()' fix:\n   Re-checks invariant safely (0 errors!)", "#bbf7d0"),
    ]
    for i, (txt, c) in enumerate(mesa_steps):
        ax.add_patch(patches.FancyBboxPatch((5.83, 3.2 - i * 0.85), 4.5, 0.68, boxstyle="round,pad=0.06", fc=c, ec="#334155", lw=0.9))
        ax.text(8.07, 3.54 - i * 0.85, txt, ha="center", va="center", fontsize=7.6, fontweight="bold", color="#0f172a")

    ax.set_title("Monitor Condition Semantics: Hoare Signal-and-Wait vs. Mesa Signal-and-Continue", fontsize=11.5, fontweight="bold")
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig8_hoare_vs_mesa_monitor.png"))


def fig9_kernel_architecture() -> None:
    pk.apply_style()
    fig, ax = plt.subplots(figsize=(10.8, 4.6))
    ax.axis("off")
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 5.0)
    cols = [
        ("Dekker (1962)", ["Pure shared memory", "2 threads (tree O(log N))", "Busy-wait spin", "No kernel syscall", "Breaks w/o fence", "Manual CS only"], "#1f4e78", "#eff6ff"),
        ("Peterson (1981)", ["Pure shared memory", "2 threads (Filter O(N))", "Busy-wait spin", "Smallest user FSM (42)", "Breaks w/o fence", "Manual CS only"], "#0072b2", "#ecfeff"),
        ("Semaphore (1965)", ["OS / Futex counter", "Arbitrary N threads", "Kernel sleep queue", "Wait/Signal decoupled", "Priority inv. risk", "Bug-prone P/V pairing"], "#1b9e77", "#ecfdf5"),
        ("Monitor (1974)", ["Language / OS Cond", "Arbitrary N threads", "Kernel sleep + condvar", "Encapsulated invariant", "Mesa needs while()", "Highest composability"], "#d95f02", "#fff7ed"),
    ]
    for i, (hdr, items, ec, fc) in enumerate(cols):
        x = 0.25 + i * 2.62
        ax.add_patch(patches.FancyBboxPatch((x, 0.3), 2.42, 4.2, boxstyle="round,pad=0.10", fc=fc, ec=ec, lw=1.6))
        ax.add_patch(patches.FancyBboxPatch((x, 3.85), 2.42, 0.65, boxstyle="round,pad=0.06", fc=ec, ec=ec, lw=1.0))
        ax.text(x + 1.21, 4.17, hdr, ha="center", va="center", fontsize=9.2, fontweight="bold", color="white")
        for j, it in enumerate(items):
            ax.text(x + 1.21, 3.35 - j * 0.52, f"- {it}", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#0f172a")
    ax.set_title("Architectural Comparison Across All Four Synchronization Paradigms", fontsize=11.5, fontweight="bold")
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig9_architecture_comparison.png"))


def fig10_decision_radar() -> None:
    pk.apply_style()
    criteria = [
        "Simplicity", "Energy Eff.\n(No Spin)", "N-Thread\nScaling", "Memory Order\nSafety",
        "Composability", "Bug Resistance", "Zero-Syscall\nFast Path"
    ]
    scores = {
        "Dekker":    [2.0, 1.0, 2.0, 1.5, 1.5, 2.0, 4.8],
        "Peterson":  [4.0, 1.0, 2.5, 1.5, 1.5, 2.5, 5.0],
        "Semaphore": [3.5, 4.8, 4.8, 5.0, 3.0, 2.5, 3.5],
        "Monitor":   [4.5, 4.8, 5.0, 5.0, 5.0, 4.6, 3.2],
    }
    x = np.arange(len(criteria))
    fig, ax = plt.subplots(figsize=(10.8, 4.6))
    w = 0.2
    for i, (pname, vals) in enumerate(scores.items()):
        ax.bar(x + (i - 1.5) * w, vals, w, label=pname, color=_col(pname), edgecolor="#0f172a", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(criteria, fontsize=8.3, fontweight="bold")
    ax.set_ylim(0, 5.7)
    ax.set_ylabel("Engineering Score (1 = Weak, 5 = Best)")
    ax.set_title("Multi-Dimensional Engineering Capability Profile (1..5 Rubric)", fontsize=11.3)
    ax.legend(loc="upper right", ncol=4, fontsize=8.5)
    pk.save_fig(fig, os.path.join(DIAG_DIR, "ex4_fig10_decision_profile.png"))


def main() -> None:
    with open(OUT_JSON, "r", encoding="utf-8") as f:
        d = json.load(f)
    fig1_state_space(d)
    fig2_busywait_vs_blocking(d)
    fig3_cs_throughput(d)
    fig4_scaling(d)
    fig5_bounded_buffer(d)
    fig6_dekker_evolution()
    fig7_tso_store_buffer()
    fig8_hoare_vs_mesa()
    fig9_kernel_architecture()
    fig10_decision_radar()
    print("Generated 10 PNG figures in", DIAG_DIR)


if __name__ == "__main__":
    main()
