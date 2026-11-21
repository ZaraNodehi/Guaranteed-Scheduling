"""Build a printable two-page Exercise 7 worksheet."""
from pathlib import Path
import pymupdf as fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

HERE=Path(__file__).resolve().parent
EX7=HERE.parent
OUT=EX7/"WORKSHEET_DINING_PHILOSOPHERS.pdf"
PREVIEW=EX7/"diagrams"
PREVIEW.mkdir(exist_ok=True)

def page_header(c,title,subtitle):
    w,h=A4;m=16*mm
    c.setFont("Helvetica-Bold",14);c.drawString(m,h-17*mm,title)
    c.setFont("Helvetica",8.5);c.drawString(m,h-23*mm,subtitle)
    c.setStrokeColor(colors.HexColor("#475569"));c.line(m,h-27*mm,w-m,h-27*mm)
    c.setFont("Helvetica",8);c.drawString(m,h-33*mm,"Name: ________________________   Student ID: ________________   Date: ______________")
    return h-42*mm

def draw_table(c,x,y,width,rows,cols,row_h=12*mm):
    widths=[width/cols]*cols
    for r in range(rows+1):
        yy=y-r*row_h
        c.setStrokeColor(colors.HexColor("#64748b"))
        c.line(x,yy,x+width,yy)
    xx=x
    for colw in widths:
        c.line(xx,y,xx,y-rows*row_h)
        xx+=colw
    c.line(x+width,y,x+width,y-rows*row_h)

def build():
    w,h=A4;m=16*mm
    c=canvas.Canvas(str(OUT),pagesize=A4)
    # Page 1: model and deadlock witness
    y=page_header(c,"Exercise 7 Worksheet — Dining Philosophers (1/2)",
                  "Five philosophers, five forks, ring topology; each meal needs two adjacent forks.")
    cx=w/2;cy=y-53*mm;r=38*mm
    import math
    pts=[]
    for i in range(5):
        a=math.pi/2-2*math.pi*i/5
        px=cx+r*math.cos(a);py=cy+r*math.sin(a);pts.append((px,py))
    for i,(px,py) in enumerate(pts):
        c.circle(px,py,13*mm,stroke=1,fill=0)
        c.setFont("Helvetica-Bold",9);c.drawCentredString(px,py,f"P{i}")
    for i in range(5):
        x1,y1=pts[i];x2,y2=pts[(i+1)%5]
        c.setLineWidth(2.4);c.line(x1*.75+x2*.25,y1*.75+y2*.25,x1*.25+x2*.75,y1*.25+y2*.75)
        c.setFont("Helvetica-Bold",9);c.drawCentredString((x1+x2)/2,(y1+y2)/2,f"F{i}")
    c.setFont("Helvetica-Bold",10);c.drawString(m,y-106*mm,"A. Describe the naive left-then-right deadlock")
    c.setFont("Helvetica",8.5)
    questions=[
      "1. Which fork does philosopher Pi hold after taking the left fork?",
      "2. Which philosopher is Pi waiting for?",
      "3. Draw the complete wait-for cycle and explain circular wait.",
      "4. Explain why equal CPU shares under GS do not release a fork."
    ]
    yy=y-114*mm
    for q in questions:
        c.drawString(m,yy,q);yy-=8*mm
        c.setStrokeColor(colors.HexColor("#94a3b8"));c.line(m,yy,w-m,yy);yy-=5*mm
    c.showPage()
    # Page 2: monitor trace and invariants
    y=page_header(c,"Exercise 7 Worksheet — FIFO Monitor and Verification (2/2)",
                  "Complete the state table for atomic two-fork reservation and audit the invariants.")
    c.setFont("Helvetica-Bold",10);c.drawString(m,y,"B. FIFO admission trace")
    y-=9*mm
    headers=["Ticket","Philosopher","Left fork","Right fork","Grant / wait","Release event"]
    colw=(w-2*m)/len(headers)
    for i,txt in enumerate(headers):
        c.setFillColor(colors.HexColor("#e2e8f0"));c.rect(m+i*colw,y-8*mm,colw,8*mm,fill=1,stroke=1)
        c.setFillColor(colors.black);c.setFont("Helvetica-Bold",6.8);c.drawCentredString(m+(i+.5)*colw,y-5.5*mm,txt)
    draw_table(c,m,y-8*mm,w-2*m,10,6,10*mm)
    y-=121*mm
    c.setFont("Helvetica-Bold",10);c.drawString(m,y,"C. Check the monitor invariants")
    y-=8*mm
    prompts=[
      "□ At most one philosopher owns each fork.",
      "□ Neighboring philosophers never eat at the same time.",
      "□ A waiting philosopher owns no fork (no hold-and-wait).",
      "□ Both forks are granted atomically to the FIFO head.",
      "□ Every admitted meal releases both forks when it finishes."
    ]
    c.setFont("Helvetica",8.2)
    for p in prompts:
        c.drawString(m,y,p);y-=7*mm
    c.setFont("Helvetica-Bold",9);c.drawString(m,y-2*mm,"D. State your liveness assumptions:")
    c.setStrokeColor(colors.HexColor("#94a3b8"));c.rect(m,17*mm,w-2*m,28*mm,fill=0,stroke=1)
    c.showPage();c.save()
    doc=fitz.open(OUT)
    for i,page in enumerate(doc,1):
        page.get_pixmap(dpi=130).save(PREVIEW/f"ex7_worksheet_p{i}.png")
    doc.close()
    print(OUT)

if __name__=="__main__":build()
