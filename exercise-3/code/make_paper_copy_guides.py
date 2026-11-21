from __future__ import annotations
import json
from pathlib import Path
import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
if (HERE.parent / "output" / "experiments.json").exists():
    EX3 = HERE.parent
elif (HERE.parent / "exercise-3" / "output" / "experiments.json").exists():
    EX3 = HERE.parent / "exercise-3"
else:
    raise FileNotFoundError("Cannot locate exercise-3/output/experiments.json")
OUT = EX3 / "paper_copy_guides"
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((EX3 / "output" / "experiments.json").read_text(encoding="utf-8"))

KEY_QUEUES = {
    "set_a": {
        4: {
            "edf": ("P3#0(r=1,d=6), P2#1(r=1,d=8)", "P3#0"),
            "rm": ("P2#1(r=1,d=8), P3#0(r=1,d=6)", "P2#1"),
        },
        5: {
            "edf": ("P2#1(r=1,d=8)", "P2#1"),
            "rm": ("P3#0(r=1,d=6)", "P3#0"),
        },
    },
    "set_b": {
        6: {
            "edf": ("P3#0(r=1,d=8), P2#1(r=2,d=12)", "P3#0"),
            "rm": ("P2#1(r=2,d=12), P3#0(r=1,d=8)", "P2#1"),
        },
        7: {
            "edf": ("P2#1(r=2,d=12)", "P2#1"),
            "rm": ("P2#1(r=1,d=12), P3#0(r=1,d=8)", "P2#1"),
        },
        8: {
            "edf": ("P1#2(r=1,d=12), P2#1(r=1,d=12), P3#1(r=3,d=16)", "P1#2"),
            "rm": ("P1#2(r=1,d=12), P3#0(r=1,d=8), P3#1(r=3,d=16)", "P1#2"),
        },
        9: {
            "edf": ("P2#1(r=1,d=12), P3#1(r=3,d=16)", "P2#1"),
            "rm": ("P3#0(r=1,d=8), P3#1(r=3,d=16)", "P3#0"),
        },
        13: {
            "edf": ("P3#1(r=1,d=16), P2#2(r=2,d=18)", "P3#1"),
            "rm": ("P2#2(r=2,d=18), P3#1(r=1,d=16)", "P2#2"),
        },
        15: {
            "edf": ("P2#2(r=1,d=18)", "P2#2"),
            "rm": ("P3#1(r=1,d=16)", "P3#1"),
        },
    },
}

def arrivals_at(tasks, tick):
    result = []
    for task in tasks:
        period = task["period"]
        if tick % period == 0:
            result.append(f"{task['name']}#{tick // period}")
    return ", ".join(result) if result else "-"

PAGE_W, PAGE_H = landscape(A4)
M = 30
CONTENT_W = PAGE_W - 2 * M
NAVY = colors.HexColor("#183B56")
BLUE = colors.HexColor("#2E6F95")
PALE = colors.HexColor("#EAF1F5")
PALE2 = colors.HexColor("#F5F7F9")
INK = colors.HexColor("#17212B")
GREY = colors.HexColor("#52616B")
RED = colors.HexColor("#A52828")
GREEN = colors.HexColor("#276749")
GRID = colors.HexColor("#8796A5")

def txt(c, x, y, value, size=7, font="Helvetica", color=INK):
    c.setFont(font, size); c.setFillColor(color); c.drawString(x, y, str(value))

def right(c, x, y, value, size=7, font="Helvetica", color=INK):
    c.setFont(font, size); c.setFillColor(color); c.drawRightString(x, y, str(value))

def centered(c, x, y, value, size=7, font="Helvetica", color=INK):
    c.setFont(font, size); c.setFillColor(color); c.drawCentredString(x, y, str(value))

def header(c, copy_no, page_no, title, subtitle):
    c.setFillColor(NAVY); c.rect(0, PAGE_H - 48, PAGE_W, 48, fill=1, stroke=0)
    txt(c, M, PAGE_H - 22, "EXERCISE 3 | PAPER-COPY REFERENCE GUIDE", 12, "Helvetica-Bold", colors.white)
    right(c, PAGE_W - M, PAGE_H - 21, f"COPY {copy_no}  |  PAGE {page_no}/3", 8, "Helvetica-Bold", colors.white)
    txt(c, M, PAGE_H - 39, title, 9.5, "Helvetica-Bold", colors.white)
    y = PAGE_H - 65
    txt(c, M, y, subtitle, 7.2, "Helvetica", GREY)
    right(c, PAGE_W - M, y, "Name: ____________________   Student ID: ____________________", 7, "Helvetica", GREY)
    return y - 13

def panel(c, x, y_top, width, height, title, fill=PALE2):
    c.setFillColor(fill); c.setStrokeColor(GRID); c.setLineWidth(.6)
    c.roundRect(x, y_top - height, width, height, 5, fill=1, stroke=1)
    txt(c, x + 8, y_top - 12, title, 7.5, "Helvetica-Bold", NAVY)

def task_panel(c, y_top, set_key):
    s = DATA[set_key]
    tasks = s["tasks"]
    panel(c, M, y_top, CONTENT_W, 36,
          f"{s['label']}  |  H={s['horizon']}  |  U={s['utilization_frac']} = {s['utilization']:.4f}")
    names = [f"{t['name']}: T={t['period']}, C={t['wcet']}, D={t['deadline']}" for t in tasks]
    x = M + 9
    for i, name in enumerate(names):
        txt(c, x + i * 190, y_top - 27, name, 7, "Helvetica-Bold", INK)
    right(c, PAGE_W - M - 9, y_top - 27, f"3-task Liu-Layland bound = {s['liu_layland_bound']:.4f}", 6.7, "Helvetica", GREY)
    return y_top - 44

def gantt(c, x, y_top, width, label, timeline, start_tick=0, color=BLUE):
    txt(c, x, y_top, label, 7.2, "Helvetica-Bold", NAVY)
    y = y_top - 6
    cell_w = width / len(timeline)
    for i, job in enumerate(timeline):
        xx = x + i * cell_w
        c.setFillColor(PALE); c.setStrokeColor(GRID); c.setLineWidth(.55)
        c.rect(xx, y - 24, cell_w, 24, fill=1, stroke=1)
        centered(c, xx + cell_w / 2, y - 8, str(start_tick + i), 5.8, "Helvetica", GREY)
        centered(c, xx + cell_w / 2, y - 19, job.replace("#", "/"), 5.6,
                 "Helvetica-Bold", color if job != "IDLE" else GREY)
    return y - 32

def trace_table(c, x, y_top, width, rows, order, row_h=10.2, include_note=True, miss_tick=None):
    cols = [("t", 24), ("arrivals", 120)]
    cols += [(alg, 116) for alg in order]
    if include_note:
        cols += [("note", width - sum(v for _, v in cols))]
    else:
        cols[-1] = (cols[-1][0], width - sum(v for _, v in cols[:-1]))
    xs = []; xx = x
    for _, cell_w in cols:
        xs.append(xx); xx += cell_w
    for (key, cell_w), xx in zip(cols, xs):
        c.setFillColor(NAVY); c.setStrokeColor(GRID); c.setLineWidth(.45)
        c.rect(xx, y_top - 15, cell_w, 15, fill=1, stroke=1)
        label = {"t": "Tick", "arrivals": "New releases", "edf": "EDF chosen",
                 "rm": "RM chosen", "note": "Note"}[key]
        centered(c, xx + cell_w / 2, y_top - 10, label, 6.2, "Helvetica-Bold", colors.white)
    y = y_top - 15
    for row in rows:
        y -= row_h
        for (key, cell_w), xx in zip(cols, xs):
            c.setFillColor(colors.white if row["t"] % 2 else PALE2); c.setStrokeColor(GRID)
            c.rect(xx, y, cell_w, row_h, fill=1, stroke=1)
            if key == "t": value = str(row["t"])
            elif key == "arrivals": value = row["arrivals"] if row["arrivals"] != "-" else "-"
            elif key in ("edf", "rm"): value = row[key]
            else:
                value = "MISS P3#0" if (miss_tick is not None and row["t"] == miss_tick) else (
                    "EDF/RM differ" if row.get("different") else "")
            col = RED if (key == "note" and row["t"] == 8) else INK
            centered(c, xx + cell_w / 2, y + 3.1, value,
                     5.8 if key in ("arrivals", "note") else 6.1,
                     "Helvetica-Bold" if key in ("edf", "rm", "note") else "Helvetica", col)
    return y

def queue_rows(c, x, y_top, width, set_key, ticks):
    txt(c, x, y_top, "READY QUEUE AT THE REQUIRED CONTENTION TICKS", 7.2, "Helvetica-Bold", NAVY)
    y = y_top - 6
    cols = [("Tick", 28), ("EDF ready queue -> pick", width / 2 - 14),
            ("RM ready queue -> pick", width / 2 - 14)]
    xs = []; xx = x
    for _, cell_w in cols: xs.append(xx); xx += cell_w
    for (label, cell_w), xx in zip(cols, xs):
        c.setFillColor(PALE); c.setStrokeColor(GRID)
        c.rect(xx, y - 12, cell_w, 12, fill=1, stroke=1)
        centered(c, xx + cell_w / 2, y - 8, label, 5.8, "Helvetica-Bold", NAVY)
    y -= 12
    for tick in ticks:
        edf_q = KEY_QUEUES[set_key][tick]["edf"]
        rm_q = KEY_QUEUES[set_key][tick]["rm"]
        vals = {"Tick": str(tick),
                "EDF ready queue -> pick": f"{edf_q[0]}  => {edf_q[1]}",
                "RM ready queue -> pick": f"{rm_q[0]}  => {rm_q[1]}"}
        y -= 12
        for (label, cell_w), xx in zip(cols, xs):
            c.setFillColor(colors.white if tick % 2 else PALE2); c.setStrokeColor(GRID)
            c.rect(xx, y, cell_w, 12, fill=1, stroke=1)
            if label == "Tick":
                centered(c, xx + cell_w / 2, y + 3.4, vals[label], 6, "Helvetica-Bold", INK)
            else:
                txt(c, xx + 3, y + 3.5, vals[label], 5.5, "Helvetica", INK)
    return y

def calc_box(c, x, y_top, width, set_key):
    if set_key == "set_a":
        title = "SET A CHECK: RESPONSE-TIME ANALYSIS FOR P3 UNDER RM"
        lines = [
            "R3(0)=2;  R3(1)=2+ceil(2/3)*1+ceil(2/4)*1 = 4",
            "R3(2)=2+ceil(4/3)*1+ceil(4/4)*1 = 5;  R3(3)=2+ceil(5/3)+ceil(5/4)=6",
            "R3*=6 <= D3=6  -> RM passes the P3 response-time check.  EDF misses=0; RM misses=0."
        ]
    else:
        title = "SET B CHECK: RTA FAILURE FOR RM, AND EDF DEMAND CHECK"
        lines = [
            "R3(0)=3;  R3(1)=3+ceil(3/4)*1+ceil(3/6)*2 = 6",
            "R3(2)=3+ceil(6/4)*1+ceil(6/6)*2 = 7;  R3(3)=3+ceil(7/4)*1+ceil(7/6)*2 = 9",
            "9 > D3=8 -> RM fails.  EDF: dbf(8)=2+2+3=7 <= 8 (margin=1); EDF has 0 misses."
        ]
    height = 47
    panel(c, x, y_top, width, height, title, PALE)
    for i, line in enumerate(lines):
        txt(c, x + 8, y_top - 24 - i * 10, line, 6.4, "Helvetica", INK)
    return y_top - height - 5

def make_page1(c, copy_no, order):
    y = header(c, copy_no, 1, "SET A | H=12 | BOTH EDF AND RM FINISH WITHOUT A DEADLINE MISS",
               "Rule: EDF chooses the ready job with the earliest absolute deadline d; RM chooses the ready job with the shortest period T.")
    y = task_panel(c, y, "set_a")
    set_data = DATA["set_a"]
    for alg in order:
        y = gantt(c, M, y, CONTENT_W, f"{alg.upper()} GANTT | ticks 0-11",
                  set_data[alg]["timeline"], 0, BLUE if alg == "edf" else GREEN)
        y -= 4
    rows = []
    for tick in range(12):
        rows.append({"t": tick, "arrivals": arrivals_at(set_data["tasks"], tick),
                     "edf": set_data["edf"]["timeline"][tick], "rm": set_data["rm"]["timeline"][tick],
                     "different": set_data["edf"]["timeline"][tick] != set_data["rm"]["timeline"][tick]})
    txt(c, M, y, "TICK-BY-TICK PAPER TRACE | Copy these dispatches into the blank table.", 7.2, "Helvetica-Bold", NAVY)
    y = trace_table(c, M, y - 4, CONTENT_W, rows, order, row_h=11.5)
    y -= 8
    y = queue_rows(c, M, y, CONTENT_W, "set_a", [4, 5])
    y -= 7
    calc_box(c, M, y, CONTENT_W, "set_a")
    c.showPage()

def make_page2(c, copy_no, order):
    y = header(c, copy_no, 2, "SET B | H=24 | THE SEPARATING CASE: EDF SUCCEEDS, RM MISSES P3#0",
               "Each cell is one CPU tick. Write the full job ID shown (e.g. P3#0), not only the process name.")
    y = task_panel(c, y, "set_b")
    set_data = DATA["set_b"]
    for alg in order:
        y = gantt(c, M, y, CONTENT_W, f"{alg.upper()} | t=0..11",
                  set_data[alg]["timeline"][:12], 0, BLUE if alg == "edf" else GREEN)
        y -= 5
        y = gantt(c, M, y, CONTENT_W, f"{alg.upper()} | t=12..23",
                  set_data[alg]["timeline"][12:], 12, BLUE if alg == "edf" else GREEN)
        y -= 8
    y -= 3
    qbottom = queue_rows(c, M, y, CONTENT_W, "set_b", [6, 7, 8, 9])
    c.setFillColor(PALE2); c.setStrokeColor(GRID)
    c.roundRect(M, qbottom - 42, CONTENT_W, 34, 4, fill=1, stroke=1)
    txt(c, M + 8, qbottom - 19, "t=6: EDF chooses P3#0 (earlier deadline 8); RM chooses P2#1 (shorter period 6).", 6.2, "Helvetica", INK)
    txt(c, M + 8, qbottom - 30, "At t=8, P3#0 still has 1 unit; RM records the miss, then completes that job at t=9.", 6.2, "Helvetica", RED)
    c.setFillColor(PALE); c.setStrokeColor(GRID)
    c.roundRect(M, 26, CONTENT_W, 28, 5, fill=1, stroke=1)
    txt(c, M + 9, 43, "RESULT: EDF = 0 deadline misses.  RM = 1 miss: P3#0 at t=8 (deadline 8).", 8, "Helvetica-Bold", RED)
    txt(c, M + 9, 32, "At t=6 RM gives CPU to shorter-period P2#1; P3#0 still needs one tick and reaches its deadline at t=8.", 6.6, "Helvetica", INK)
    c.showPage()

def make_page3(c, copy_no, order):
    y = header(c, copy_no, 3, "SET B | FULL TICK TRACE AND FINAL CALCULATIONS",
               "Releases are added at the start of the tick; then the scheduler selects one ready job and consumes one unit of CPU.")
    set_data = DATA["set_b"]
    rows = []
    for tick in range(24):
        rows.append({"t": tick, "arrivals": arrivals_at(set_data["tasks"], tick),
                     "edf": set_data["edf"]["timeline"][tick], "rm": set_data["rm"]["timeline"][tick],
                     "different": set_data["edf"]["timeline"][tick] != set_data["rm"]["timeline"][tick]})
    txt(c, M, y, "COMPLETE DISPATCH RECORD | The red row marks the exact RM deadline miss.", 7.2, "Helvetica-Bold", NAVY)
    y = trace_table(c, M, y - 4, CONTENT_W, rows, order, row_h=10.0, miss_tick=8)
    y -= 12
    y = queue_rows(c, M, y, CONTENT_W, "set_b", [13, 15])
    y -= 5
    calc_box(c, M, y, CONTENT_W, "set_b")
    c.setFont("Helvetica-Oblique", 6.3); c.setFillColor(GREY)
    c.drawString(M, 19, "Tie rule in the reference trace: lower process index first (P1 < P2 < P3).  This is a reference guide, not a handwritten submission.")
    c.showPage()

def build_one(copy_no, order):
    name = f"HAND_COPY_GUIDE_STUDENT_{copy_no}.pdf"
    path = OUT / name
    c = canvas.Canvas(str(path), pagesize=landscape(A4), pageCompression=1)
    c.setTitle(f"Exercise 3 paper-copy reference - Copy {copy_no}")
    make_page1(c, copy_no, order); make_page2(c, copy_no, order); make_page3(c, copy_no, order)
    c.save()
    pngdir = OUT / f"student_{copy_no}_png"
    pngdir.mkdir(exist_ok=True)
    with fitz.open(path) as doc:
        assert len(doc) == 3, (name, len(doc))
        for i, page in enumerate(doc, 1):
            page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False).save(pngdir / f"page_{i}.png")
    return path

def main():
    p1 = build_one(1, ("edf", "rm"))
    p2 = build_one(2, ("rm", "edf"))
    print(p1); print(p2)
    print("Reference outcomes: Set A EDF=0 misses, RM=0 misses; Set B EDF=0 misses, RM misses P3#0 at t=8.")

if __name__ == "__main__":
    main()
