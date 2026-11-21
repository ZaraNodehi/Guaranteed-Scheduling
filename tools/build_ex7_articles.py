"""Render the standalone bilingual capstone research article to DOCX and PDF."""
from __future__ import annotations
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem
import arabic_reshaper
from bidi.algorithm import get_display
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/"exercise-7"/"docs"
FONT="/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"
if not Path(FONT).exists():
    FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("ArticleArabic",FONT))

def rtl(text):
    return get_display(arabic_reshaper.reshape(text))

def add_rtl(paragraph):
    paragraph.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    pPr=paragraph._p.get_or_add_pPr()
    bidi=OxmlElement("w:bidi"); pPr.append(bidi)
    for run in paragraph.runs:
        rPr=run._r.get_or_add_rPr()
        rtl_el=OxmlElement("w:rtl"); rPr.append(rtl_el)
        rFonts=rPr.rFonts
        if rFonts is not None:
            rFonts.set(qn("w:cs"),"Noto Sans Arabic")

def build(lang):
    md=DOCS/f"ARTICLE_{lang}.md"
    lines=md.read_text(encoding="utf-8").splitlines()
    fa=lang=="FA"
    doc=Document()
    sec=doc.sections[0]
    sec.top_margin=Inches(.72);sec.bottom_margin=Inches(.72)
    normal=doc.styles["Normal"];normal.font.name="Noto Sans Arabic" if fa else "Aptos";normal.font.size=Pt(10.5)
    story=[]
    bullets=[]
    for line in lines:
        s=line.strip()
        if not s:
            continue
        if s.startswith("# "):
            title=s[2:]
            doc.add_heading(title,0)
            story.append(("h1",title))
        elif s.startswith("## "):
            if bullets:
                doc.add_paragraph(" • ".join(bullets),style="List Bullet");bullets=[]
            heading=s[3:]
            doc.add_heading(heading,1)
            story.append(("h2",heading))
        elif s.startswith("### "):
            heading=s[4:]
            doc.add_heading(heading,2);story.append(("h2",heading))
        elif s.startswith("- "):
            item=s[2:]
            p=doc.add_paragraph(item,style="List Bullet")
            story.append(("bullet",item))
        elif re.match(r"^\d+\. ",s):
            item=re.sub(r"^\d+\. ","",s)
            doc.add_paragraph(item,style="List Number")
            story.append(("p",item))
        else:
            text=re.sub(r"\*\*(.*?)\*\*",r"\1",s)
            p=doc.add_paragraph(text)
            if fa:add_rtl(p)
            story.append(("p",text))
    docx=DOCS/f"ARTICLE_{lang}.docx"
    doc.save(docx)

    styles=getSampleStyleSheet()
    body=ParagraphStyle("ArticleBody",parent=styles["BodyText"],fontName="ArticleArabic" if fa else "Helvetica",fontSize=9.2,leading=14,alignment=TA_RIGHT if fa else TA_LEFT,spaceAfter=7)
    h1=ParagraphStyle("ArticleH1",parent=styles["Title"],fontName="ArticleArabic" if fa else "Helvetica-Bold",fontSize=18,leading=23,alignment=TA_RIGHT if fa else TA_LEFT,textColor=colors.HexColor("#17365D"),spaceAfter=15)
    h2=ParagraphStyle("ArticleH2",parent=styles["Heading2"],fontName="ArticleArabic" if fa else "Helvetica-Bold",fontSize=13,leading=17,alignment=TA_RIGHT if fa else TA_LEFT,textColor=colors.HexColor("#1F4E78"),spaceBefore=10,spaceAfter=7)
    flow=[]
    for typ,text in story:
        content=rtl(text) if fa else text
        safe=escape(content)
        if typ=="h1":flow.append(Paragraph(safe,h1))
        elif typ=="h2":flow.append(Paragraph(safe,h2))
        elif typ=="bullet":flow.append(Paragraph(("• " if not fa else "• ")+safe,body))
        else:flow.append(Paragraph(safe,body))
        flow.append(Spacer(1,2))
    pdf=DOCS/f"ARTICLE_{lang}.pdf"
    SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=17*mm,bottomMargin=17*mm,title=f"Guaranteed Scheduling and Dining Philosophers ({lang})").build(flow)
    print({"language":lang,"docx":str(docx),"pdf":str(pdf),"paragraphs":len(story)})

if __name__=="__main__":
    for language in ("EN","FA"):build(language)
