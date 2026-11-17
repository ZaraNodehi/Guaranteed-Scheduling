"""Shared matplotlib styling and drawing primitives for all 7 exercises.

Uses a colorblind-safe Okabe-Ito inspired palette, crisp typography, clean
margins (constrained_layout / explicit bbox padding) and helper utilities for
Gantt charts, flowcharts and system architecture diagrams.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager

PALETTE = [
    "#1f4e78",  # deep navy
    "#d95f02",  # burnt orange
    "#1b9e77",  # teal green
    "#7570b3",  # slate purple
    "#e7298a",  # magenta
    "#66a61e",  # olive
    "#e6ab02",  # amber
    "#666666",  # neutral slate
]

POLICY_COLORS = {
    "gs_ratio": "#d95f02",
    "gs_entitled": "#7570b3",
    "gs_vtime": "#1f4e78",
    "gs_capped": "#1b9e77",
    "stride": "#66a61e",
    "rr": "#e6ab02",
    "fifo": "#8c6d31",
    "edf": "#0072b2",
    "rm": "#cc79a7",
    "dm": "#56b4e9",
}

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_VAZIR_REG = os.path.join(FONT_DIR, "Vazirmatn-400.ttf")
if os.path.exists(_VAZIR_REG):
    font_manager.fontManager.addfont(_VAZIR_REG)
_VAZIR_BOLD = os.path.join(FONT_DIR, "Vazirmatn-700.ttf")
if os.path.exists(_VAZIR_BOLD):
    font_manager.fontManager.addfont(_VAZIR_BOLD)


def apply_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "#fbfcfe",
        "axes.edgecolor": "#b8c4d4",
        "axes.linewidth": 0.9,
        "axes.grid": True,
        "grid.color": "#e2e8f0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "font.family": "DejaVu Sans",
        "font.size": 9.5,
        "axes.titlesize": 11.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "legend.frameon": True,
        "legend.facecolor": "white",
        "legend.edgecolor": "#cfd8e3",
        "savefig.dpi": 200,
    })


def save_fig(fig: plt.Figure, out_path: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)
    return out_path


def draw_gantt(timeline: Sequence[Sequence],
               title: str,
               out_path: str,
               proc_order: Optional[Sequence[str]] = None,
               subtitle: str = "",
               highlight_windows: Optional[Sequence[Tuple[int, int, str]]] = None) -> str:
    """Render a clean integer-tick Gantt chart from ``[(t, name_or_None), ...]``."""
    apply_style()
    names = sorted({n for _, n in timeline if n is not None})
    if proc_order:
        ordered = [p for p in proc_order if p in names] + [p for p in names if p not in proc_order]
        names = ordered
    if not names:
        names = ["IDLE"]

    # Compress runs
    runs: List[Tuple[str, int, int]] = []
    for t, n in timeline:
        if n is None:
            continue
        if runs and runs[-1][0] == n and runs[-1][2] == t:
            runs[-1] = (n, runs[-1][1], t + 1)
        else:
            runs.append((n, t, t + 1))

    horizon = len(timeline)
    h_fig = max(2.6, 0.58 * len(names) + 1.45)
    fig, ax = plt.subplots(figsize=(9.5, h_fig))

    y_pos = {name: idx for idx, name in enumerate(reversed(names))}
    color_map = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(names)}

    if highlight_windows:
        for xs, xe, lbl in highlight_windows:
            ax.axvspan(xs, xe, color="#fee2e2", alpha=0.55, zorder=0)
            ax.text((xs + xe) / 2, len(names) - 0.15, lbl, ha="center", va="bottom",
                    fontsize=8, color="#991b1b", fontweight="bold")

    for name, start, end in runs:
        y = y_pos[name]
        w = end - start
        rect = patches.FancyBboxPatch(
            (start + 0.04, y - 0.34), max(0.08, w - 0.08), 0.68,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=color_map[name], edgecolor="white", linewidth=0.8, zorder=3
        )
        ax.add_patch(rect)
        if w >= 1 and horizon <= 60:
            ax.text(start + w / 2, y, str(w) if w > 1 else "",
                    ha="center", va="center", color="white", fontsize=8, fontweight="bold", zorder=4)

    ax.set_yticks([y_pos[n] for n in names])
    ax.set_yticklabels(names, fontweight="bold")
    ax.set_ylim(-0.65, len(names) - 0.25)
    ax.set_xlim(0, max(1, horizon))
    step = 1 if horizon <= 24 else (2 if horizon <= 48 else max(4, horizon // 15))
    ax.set_xticks(list(range(0, horizon + 1, step)))
    ax.set_xlabel("Time (integer ticks)")
    ax.set_title(title + (f"\n{subtitle}" if subtitle else ""), pad=10)
    return save_fig(fig, out_path)


def draw_box(ax, cx: float, cy: float, w: float, h: float, text: str,
             fc: str = "#eef4fb", ec: str = "#1f4e78", tc: str = "#0f172a",
             fontsize: float = 9.0, bold: bool = False, rounded: bool = True) -> None:
    style = "round,pad=0.12,rounding_size=0.18" if rounded else "square,pad=0.1"
    box = patches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle=style, facecolor=fc, edgecolor=ec, linewidth=1.35, zorder=3
    )
    ax.add_patch(box)
    ax.text(cx, cy, text, ha="center", va="center", color=tc,
            fontsize=fontsize, fontweight=("bold" if bold else "normal"),
            linespacing=1.28, zorder=4)


def draw_arrow(ax, x1: float, y1: float, x2: float, y2: float,
               label: str = "", label_offset: Tuple[float, float] = (0.0, 0.0),
               color: str = "#334155") -> None:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>,head_width=0.28,head_length=0.45",
                                color=color, lw=1.35), zorder=2)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center", fontsize=8.0,
                color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85),
                zorder=5)
