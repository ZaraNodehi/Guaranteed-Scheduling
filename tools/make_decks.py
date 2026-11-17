#!/usr/bin/env python3
"""Build bilingual speaker decks (PPTX) and standalone speaker scripts for Ex 5 & 6.

Usage from the repository root::

    python3 tools/make_decks.py            # builds Ex 5 and Ex 6
    python3 tools/make_decks.py 5          # builds Ex 5 only

Every slide contains:
* non-overlapping text + scaled figure layout (aspect-ratio preserved via PIL),
* RTL-aligned Persian text with Vazirmatn font (or LTR English),
* speaker notes embedded inside the PPTX notes frame on EVERY slide,
* standalone ``SPEAKER_EN.md`` and ``SPEAKER_FA.md`` scripts in ``docs/``.
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image as PILImage
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

FONT = "Vazirmatn"
INK = RGBColor(0x16, 0x26, 0x3D)
ACCENT = RGBColor(0x2B, 0x5B, 0x84)
MUTED = RGBColor(0x3D, 0x48, 0x58)
LIGHT_BG = RGBColor(0xF5, 0xF7, 0xFA)
FOOTER_CLR = RGBColor(0x6C, 0x76, 0x84)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _data(exercise_root: str) -> dict:
    p = os.path.join(exercise_root, "output", "experiments.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _shape_text(slide, x, y, w, h, lines, lang, size, bold_all=False, color=INK):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = str(line)
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.bold = bold_all
        p.font.color.rgb = color
        p.space_after = Pt(8)
        p.alignment = PP_ALIGN.RIGHT if lang == "fa" else PP_ALIGN.LEFT
        pPr = p._p.get_or_add_pPr()
        pPr.set("rtl", "1" if lang == "fa" else "0")
        p.level = 0
    return box


def _fit_picture(slide, path: str, box_x: float, box_y: float, max_w: float, max_h: float) -> None:
    with PILImage.open(path) as im:
        iw, ih = im.size
    ratio = ih / max(iw, 1)
    w = max_w
    h = w * ratio
    if h > max_h:
        h = max_h
        w = h / max(ratio, 1e-6)
    cx = box_x + (max_w - w) / 2.0
    cy = box_y + (max_h - h) / 2.0
    slide.shapes.add_picture(path, Inches(cx), Inches(cy), width=Inches(w), height=Inches(h))


def build_one(exercise_root: str, lang: str, file_name: str, slides: list) -> str:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    diagrams = os.path.join(exercise_root, "diagrams")
    total = len(slides)

    for idx, s in enumerate(slides, start=1):
        slide = prs.slides.add_slide(blank)
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        bar_x = 13.19 if lang == "fa" else 0.0
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(bar_x), Inches(0.0),
                                     Inches(0.143), Inches(7.5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ACCENT
        bar.line.fill.background()

        title = s["title_fa"] if lang == "fa" else s["title_en"]
        body = s["body_fa"] if lang == "fa" else s["body_en"]
        notes = s["notes_fa"] if lang == "fa" else s["notes_en"]

        # Header rule
        rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(1.22),
                                      Inches(12.2), Inches(0.02))
        rule.fill.solid()
        rule.fill.fore_color.rgb = RGBColor(0xD8, 0xE0, 0xEC)
        rule.line.fill.background()

        _shape_text(slide, 0.55, 0.28, 12.2, 0.90, [title], lang, 25,
                    bold_all=True, color=INK)

        fig_rel = s.get("figure")
        fig_path = os.path.join(diagrams, fig_rel) if fig_rel else None
        has_fig = bool(fig_path and os.path.exists(fig_path))

        bullet_lines = [f"\u2022  {b}" for b in body]
        if has_fig:
            if lang == "fa":
                _shape_text(slide, 6.75, 1.45, 5.95, 5.35, bullet_lines, lang, 15.5, color=MUTED)
                _fit_picture(slide, fig_path, 0.55, 1.45, 5.95, 5.25)
            else:
                _shape_text(slide, 0.55, 1.45, 5.95, 5.35, bullet_lines, lang, 15.5, color=MUTED)
                _fit_picture(slide, fig_path, 6.75, 1.45, 5.95, 5.25)
        else:
            _shape_text(slide, 0.65, 1.50, 11.95, 5.30, bullet_lines, lang, 17.5, color=MUTED)

        # Slide footer & tag
        tag = s.get("tag", "")
        footer_text = f"{tag}  |  {idx} / {total}" if tag else f"{idx} / {total}"
        _shape_text(slide, 0.55, 6.95, 12.2, 0.35, [footer_text],
                    "en", 10.5, color=FOOTER_CLR)

        # Speaker notes on EVERY slide
        slide.notes_slide.notes_text_frame.text = str(notes)

    docs = os.path.join(exercise_root, "docs")
    os.makedirs(docs, exist_ok=True)
    path = os.path.join(docs, file_name)
    prs.save(path)
    return path


def speaker_markdown(exercise_root: str, lang: str, file_name: str, slides: list) -> str:
    docs = os.path.join(exercise_root, "docs")
    os.makedirs(docs, exist_ok=True)
    lines = ["# " + ("Speaker Script (English)" if lang == "en"
                     else "متن کامل گوینده (فارسی)"), ""]
    for i, s in enumerate(slides, start=1):
        lines.append(f"## Slide {i}. " + (s["title_en"] if lang == "en"
                                          else s["title_fa"]))
        lines.append("")
        for b in (s["body_en"] if lang == "en" else s["body_fa"]):
            lines.append(f"- {b}")
        lines.append("")
        lbl = "Speaker notes" if lang == "en" else "متن گوینده"
        lines.append(f"**{lbl}:** " + (s["notes_en"] if lang == "en" else s["notes_fa"]))
        lines.append("")
        if s.get("figure"):
            lines.append(f"*{'Figure' if lang == 'en' else 'شکل'}: `{s['figure']}`*")
            lines.append("")
        if s.get("source"):
            lines.append(f"*{'Source' if lang == 'en' else 'منبع'}: {s['source']}*")
            lines.append("")
    path = os.path.join(docs, file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def build_exercise(exercise_root: str) -> dict:
    data = _data(exercise_root)
    decks = data.get("decks", {})
    slides = decks.get("slides", [])
    if not slides:
        sys.path.insert(0, os.path.join(HERE, "content"))
        import gs_decks  # noqa: E402
        base = os.path.basename(exercise_root)
        if base.startswith("exercise-"):
            decks = gs_decks.build_decks_spec(int(base.split("-")[1]))
            slides = decks.get("slides", [])
    if not slides:
        return {"exercise": os.path.basename(exercise_root), "decks": []}
    made = []
    for name in decks.get("files", []):
        lang = "fa" if name.upper().endswith(("_FA.PPTX", "_FA.MD")) else "en"
        if name.lower().endswith(".pptx"):
            made.append(build_one(exercise_root, lang, name, slides))
        elif name.lower().endswith(".md"):
            made.append(speaker_markdown(exercise_root, lang, name, slides))
    return {
        "exercise": os.path.basename(exercise_root),
        "slides": len(slides),
        "notes_on_every_slide": all(bool(s.get("notes_en") and s.get("notes_fa")) for s in slides),
        "outputs": made,
    }


def main(argv: list) -> int:
    if os.path.isdir(os.path.join(ROOT, "exercise-5")):
        nums = [int(a) for a in argv[1:]] or [5, 6, 7]
        roots = [os.path.join(ROOT, f"exercise-{n}") for n in nums]
    else:
        roots = [os.path.dirname(HERE)]
    out = [build_exercise(r) for r in roots]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
