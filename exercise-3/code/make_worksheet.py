"""Build the printable 2-page blank paper worksheet for Exercise 3 (Set A & Set B)."""
from __future__ import annotations

import os
import fitz  # PyMuPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
EX3_DIR = os.path.dirname(HERE)
PDF_OUT = os.path.join(EX3_DIR, "WORKSHEET_PAPER_TEMPLATE.pdf")
SCAN_DIR = os.path.join(EX3_DIR, "handwritten_scan")
os.makedirs(SCAN_DIR, exist_ok=True)


def _draw_blank_gantt(c: canvas.Canvas, x0: float, y_top: float, w: float, H: int,
                      tasks: list, alg_title: str) -> float:
    row_h = 8.5 * mm
    lbl_w = 24 * mm
    grid_w = w - lbl_w
    cell_w = grid_w / H

    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(colors.HexColor("#1f4e78"))
    c.drawString(x0, y_top, alg_title)
    y = y_top - 4 * mm

    # Tick numbers along top
    c.setFont("Helvetica", 7.2)
    c.setFillColor(colors.HexColor("#334155"))
    for t in range(H + 1):
        cx = x0 + lbl_w + t * cell_w
        c.drawCentredString(cx, y + 1 * mm, str(t))

    for r_idx, (name, period, wcet) in enumerate(tasks):
        ry = y - (r_idx + 1) * row_h
        # Label cell
        c.setFillColor(colors.HexColor("#f8fafc"))
        c.setStrokeColor(colors.HexColor("#94a3b8"))
        c.setLineWidth(0.7)
        c.rect(x0, ry, lbl_w, row_h, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x0 + 2 * mm, ry + 3 * mm, f"{name} (T={period}, C={wcet})")

        # Blank cells
        c.setFillColor(colors.white)
        for t in range(H):
            cx = x0 + lbl_w + t * cell_w
            c.rect(cx, ry, cell_w, row_h, fill=1, stroke=1)
            # Release tick marker along bottom edge
            if t % period == 0:
                c.setStrokeColor(colors.HexColor("#1f4e78"))
                c.setLineWidth(1.4)
                c.line(cx, ry, cx, ry + 2.5 * mm)
                c.setStrokeColor(colors.HexColor("#94a3b8"))
                c.setLineWidth(0.7)

    # Bottom axis note
    y_bot = y - len(tasks) * row_h
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(x0 + lbl_w, y_bot - 3.5 * mm, "Mark each executed tick with job ID (e.g., P1#0, P3#0) and circle any deadline miss.")
    return y_bot - 8 * mm


def _draw_trace_table(c: canvas.Canvas, x0: float, y_top: float, w: float, rows: int, title: str) -> float:
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#1f4e78"))
    c.drawString(x0, y_top, title)
    y = y_top - 4 * mm
    cols = [("Tick t", 0.08), ("New Arrivals", 0.17), ("Ready Queue + (rem, d)", 0.36), ("Chosen Job", 0.16), ("Miss / Note", 0.23)]
    hdr_h = 6 * mm
    row_h = 5.4 * mm

    cx = x0
    c.setFillColor(colors.HexColor("#e2e8f0"))
    c.setStrokeColor(colors.HexColor("#64748b"))
    c.setLineWidth(0.7)
    for hdr, frac in cols:
        cw = w * frac
        c.rect(cx, y - hdr_h, cw, hdr_h, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 7.3)
        c.drawString(cx + 1.5 * mm, y - hdr_h + 2 * mm, hdr)
        c.setFillColor(colors.HexColor("#e2e8f0"))
        cx += cw

    for r in range(rows):
        ry = y - hdr_h - (r + 1) * row_h
        cx = x0
        c.setFillColor(colors.white)
        for c_i, (_, frac) in enumerate(cols):
            cw = w * frac
            c.rect(cx, ry, cw, row_h, fill=1, stroke=1)
            if c_i == 0:
                c.setFillColor(colors.HexColor("#475569"))
                c.setFont("Helvetica", 7.2)
                c.drawCentredString(cx + cw / 2, ry + 1.7 * mm, str(r))
                c.setFillColor(colors.white)
            cx += cw
    return y - hdr_h - rows * row_h - 6 * mm


def _header(c: canvas.Canvas, page_w: float, page_h: float, title: str, subtitle: str) -> float:
    margin = 16 * mm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(margin, page_h - 16 * mm, title)
    c.setFont("Helvetica", 8.8)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(margin, page_h - 21.5 * mm, subtitle)
    c.setStrokeColor(colors.HexColor("#1f4e78"))
    c.setLineWidth(1.2)
    c.line(margin, page_h - 24 * mm, page_w - margin, page_h - 24 * mm)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(margin, page_h - 29 * mm, "Name / Student ID: ______________________________   Date: ______________   (Scan & save to exercise-3/handwritten_scan/)")
    return page_h - 36 * mm


def build_pdf() -> None:
    pw, ph = A4
    margin = 16 * mm
    usable_w = pw - 2 * margin
    c = canvas.Canvas(PDF_OUT, pagesize=A4)

    # Page 1: Set A (H=12)
    y = _header(c, pw, ph,
                "Exercise 3 Paper Worksheet (Page 1/2): Set A (Harmonic Feasible, H=12)",
                "3 Processes: P1(T=3, C=1, D=3)  |  P2(T=4, C=1, D=4)  |  P3(T=6, C=2, D=6)  |  U = 1/3 + 1/4 + 2/6 = 11/12 = 0.917")
    tasks_a = [("P1", 3, 1), ("P2", 4, 1), ("P3", 6, 2)]
    y = _draw_blank_gantt(c, margin, y, usable_w, 12, tasks_a, "1A. EDF Hand-Drawn Gantt Chart (min absolute deadline d = release + D_i; tie: P1 < P2 < P3)")
    y = _draw_blank_gantt(c, margin, y, usable_w, 12, tasks_a, "1B. RM Hand-Drawn Gantt Chart (static priority: min period T_i => P1 > P2 > P3)")
    y = _draw_trace_table(c, margin, y, usable_w, 12, "1C. Tick-by-Tick Ready Queue Trace (compare EDF vs RM, highlight t=4 and t=5):")

    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(colors.HexColor("#1f4e78"))
    c.drawString(margin, y, "1D. Hand Calculation Box (RTA for P3 & Divergence Explanation):")
    c.setStrokeColor(colors.HexColor("#94a3b8"))
    c.rect(margin, 14 * mm, usable_w, y - 16 * mm, fill=0, stroke=1)
    c.setFont("Helvetica", 7.8)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(margin + 3 * mm, y - 6 * mm, "R_3^(0) = ____   R_3^(1) = ______________________   R_3^(2) = ______________________   Converges to R_3* = ____ <= D_3=6?")
    c.showPage()

    # Page 2: Set B (H=24)
    y = _header(c, pw, ph,
                "Exercise 3 Paper Worksheet (Page 2/2): Set B (EDF vs RM Separator, H=24)",
                "3 Processes: P1(T=4, C=1, D=4)  |  P2(T=6, C=2, D=6)  |  P3(T=8, C=3, D=8)  |  U = 1/4 + 2/6 + 3/8 = 23/24 = 0.958")
    tasks_b = [("P1", 4, 1), ("P2", 6, 2), ("P3", 8, 3)]
    y = _draw_blank_gantt(c, margin, y, usable_w, 24, tasks_b, "2A. EDF Hand-Drawn Gantt Chart (H=24 ticks — verify 0 misses)")
    y = _draw_blank_gantt(c, margin, y, usable_w, 24, tasks_b, "2B. RM Hand-Drawn Gantt Chart (H=24 ticks — identify exact miss tick of P3#0)")
    y = _draw_trace_table(c, margin, y, usable_w, 10, "2C. Critical Window Trace t=0..9 (where RM causes P3#0 to miss at t=8):")

    c.setFont("Helvetica-Bold", 8.8)
    c.setFillColor(colors.HexColor("#1f4e78"))
    c.drawString(margin, y, "2D. Hand Calculation Box (RTA Failure Proof for P3 vs Baruah dbf(8) <= 8 Check):")
    c.setStrokeColor(colors.HexColor("#94a3b8"))
    c.rect(margin, 14 * mm, usable_w, y - 16 * mm, fill=0, stroke=1)
    c.setFont("Helvetica", 7.8)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(margin + 3 * mm, y - 6 * mm, "RM RTA for P3: R_3^(0)=3, R_3^(1)=_______, R_3^(2)=_______, R_3^(3)=_______ (> D_3=8 => MISS!)")
    c.drawString(margin + 3 * mm, y - 12 * mm, "EDF Demand Bound at L=8: dbf(8) = __________________________ <= 8?   Context switches (EDF vs RM): ______ vs ______")
    c.showPage()
    c.save()

    # Export preview PNGs to handwritten_scan/ so user sees exact printable sheets
    doc = fitz.open(PDF_OUT)
    for idx, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(SCAN_DIR, f"PAPER_WORKSHEET_P{idx}.png"))
    doc.close()
    print("Built", PDF_OUT, "and PNG previews in", SCAN_DIR)


if __name__ == "__main__":
    build_pdf()
