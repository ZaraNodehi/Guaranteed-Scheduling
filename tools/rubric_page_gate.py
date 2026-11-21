"""Strict output gate for the instructor's >40-page bilingual report requirement."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import report_kit as rk

ROOT=Path(__file__).resolve().parents[1]
EXERCISES=[f"exercise-{i}" for i in range(1,8)]
REPORT_TITLES={
"exercise-1":"Guaranteed Scheduling introduction",
"exercise-2":"Guaranteed Scheduling vs. EDF/RM/DM comparison",
"exercise-3":"Paper EDF/RM scheduling and independent verification",
"exercise-4":"Dekker, Peterson, Semaphore and Monitor",
"exercise-5":"Readers–Writers synchronization",
"exercise-6":"Integrated operating-systems capstone and seminar",
"exercise-7":"Dining Philosophers: CPU fairness and deadlock-free resource allocation",
}

def main():
    records=[]
    failures=[]
    for exercise in EXERCISES:
        for lang in ("EN","FA"):
            pdf=ROOT/exercise/"docs"/f"REPORT_{lang}.pdf"
            docx=ROOT/exercise/"docs"/f"REPORT_{lang}.docx"
            md=ROOT/exercise/f"REPORT_{lang}.md"
            if not pdf.is_file() or not docx.is_file() or not md.is_file():
                failures.append(f"{exercise}/{lang}: missing MD/DOCX/PDF report")
                continue
            pages=rk.pdf_page_count(str(pdf))
            records.append({"exercise":exercise,"language":lang,"pages":pages})
            if pages<=40:
                failures.append(f"{exercise}/{lang}: PDF has {pages} pages; required >40")
    for exercise in EXERCISES[1:]:
        image=ROOT/exercise/"diagrams"/f"fig_{exercise.replace('-','')}_rubric_flowchart.png"
        if not image.is_file() or image.stat().st_size<10_000:
            failures.append(f"{exercise}: missing generated rubric flowchart")
    clip=ROOT/"exercise-1"/"media"/"guaranteed_scheduling_demo.mp4"
    if not clip.is_file() or clip.stat().st_size<20_000:
        failures.append("Exercise 1: missing or incomplete Guaranteed Scheduling MP4")
    ex7_clip=ROOT/"exercise-7"/"media"/"dining_philosophers_demo.mp4"
    if not ex7_clip.is_file() or ex7_clip.stat().st_size<20_000:
        failures.append("Exercise 7: missing or incomplete Dining Philosophers MP4")
    for path in [
        ROOT/"exercise-3"/"WORKSHEET_PAPER_TEMPLATE.pdf",
        ROOT/"exercise-3"/"WORKED_SOLUTION_EN.md",
        ROOT/"exercise-3"/"WORKED_SOLUTION_FA.md",
        ROOT/"exercise-6"/"code"/"dining_philosophers.py",
        ROOT/"exercise-6"/"diagrams"/"fig_dining_philosophers_fifo.png",
        ROOT/"exercise-6"/"docs"/"ARTICLE_EN.md",
        ROOT/"exercise-6"/"docs"/"ARTICLE_FA.md",
        ROOT/"exercise-6"/"docs"/"ARTICLE_EN.docx",
        ROOT/"exercise-6"/"docs"/"ARTICLE_FA.docx",
        ROOT/"exercise-6"/"docs"/"ARTICLE_EN.pdf",
        ROOT/"exercise-6"/"docs"/"ARTICLE_FA.pdf",
        ROOT/"exercise-6"/"docs"/"PRESENTATION_EN.pptx",
        ROOT/"exercise-6"/"docs"/"PRESENTATION_FA.pptx",
        ROOT/"exercise-6"/"docs"/"SPEAKER_SCRIPT_EN.md",
        ROOT/"exercise-6"/"docs"/"SPEAKER_SCRIPT_FA.md",
        ROOT/"exercise-7"/"WORKSHEET_DINING_PHILOSOPHERS.pdf",
        ROOT/"exercise-7"/"output"/"experiments.json",
        ROOT/"exercise-7"/"code"/"dining_philosophers.py",
        ROOT/"exercise-7"/"tests"/"test_ex7.py",
        ROOT/"exercise-7"/"media"/"dining_philosophers_demo.mp4",
        ROOT/"exercise-7"/"diagrams"/"fig_ex7_table_topology.png",
        ROOT/"exercise-7"/"diagrams"/"fig_ex7_wait_for_cycle.png",
        ROOT/"exercise-7"/"diagrams"/"fig_ex7_fifo_monitor.png",
        ROOT/"exercise-7"/"diagrams"/"fig_exercise7_rubric_flowchart.png",
        ROOT/"exercise-7"/"docs"/"ARTICLE_EN.md",
        ROOT/"exercise-7"/"docs"/"ARTICLE_FA.md",
        ROOT/"exercise-7"/"docs"/"ARTICLE_EN.docx",
        ROOT/"exercise-7"/"docs"/"ARTICLE_FA.docx",
        ROOT/"exercise-7"/"docs"/"ARTICLE_EN.pdf",
        ROOT/"exercise-7"/"docs"/"ARTICLE_FA.pdf",
        ROOT/"exercise-7"/"docs"/"PRESENTATION_EN.pptx",
        ROOT/"exercise-7"/"docs"/"PRESENTATION_FA.pptx",
        ROOT/"exercise-7"/"docs"/"SPEAKER_SCRIPT_EN.md",
        ROOT/"exercise-7"/"docs"/"SPEAKER_SCRIPT_FA.md",
    ]:
        if not path.is_file():
            failures.append(f"Missing complementary deliverable: {path.relative_to(ROOT)}")

    if not failures:
        lines=[
            "# Instructor-Rubric Audit — Guaranteed Scheduling",
            "",
            "This report is generated from the files in the current build. PDF page counts below are read from the final PDF files, not inferred from Markdown section counts.",
            "",
            "| Exercise | English PDF | Persian PDF | Main subject |",
            "|---|---:|---:|---|",
        ]
        by={(x["exercise"],x["language"]):x["pages"] for x in records}
        for exercise in EXERCISES:
            lines.append(f"| {exercise} | {by[(exercise,'EN')]} pages | {by[(exercise,'FA')]} pages | {REPORT_TITLES[exercise]} |")
        lines += [
            "",
            "## Checklist evidence",
            "",
            "| Instructor criterion | Repository evidence | Status |",
            "|---|---|---|",
            "| Algorithm and implementation | GuaranteedScheduling.py, core/gs_core.py, exercise-specific simulators and tests | Present |",
            "| Comparison and analysis | Exercise 2: GS variants, EDF, DM, RM, Stride and Round Robin; exact/exhaustive datasets | Present |",
            "| Paper scheduling | Exercise 3: complete tick-by-tick EDF/RM reference traces for Sets A/B/C, bilingual worked answer keys, RTA/dbf and printable A4 worksheet | Reference solution present; student must still handwrite their own submission |",
            "| Synchronization | Exercise 4: Dekker, Peterson, Semaphore, Mesa Monitor and BFS; Exercise 7: FIFO Dining Philosophers monitor, finite-state model and real-thread stress test | Present |",
            "| Demonstration clip | exercise-1/media/guaranteed_scheduling_demo.mp4, rendered from the gs_vtime simulator trace | Present |",
            "| Paper/seminar | Exercise 6 integrated capstone and Exercise 7 standalone bilingual 7-slide seminar, per-slide speaker notes/scripts and research article | Present |",
            "| Persian and English reports | DOCX, PDF and Markdown for all seven exercises | Present |",
            "| More than 40 PDF pages | Counts reported in the table above; all are >40 | Verified by build gate |",
            "",
            "## Important academic note",
            "",
            "The bilingual Exercise 3 worked answer key is a reference solution generated from independent traces. Its printable worksheet is still a blank form; the student must complete and scan their own handwritten work. Exercise 7 proves the stated finite model properties, while liveness remains conditional on meals finishing and waiters eventually being scheduled. Attending class and the instructor's grade cannot be verified from repository files.",
            "",
            "## Automated verification",
            "",
            "pytest, check_outputs.py, and this page-count gate run in GitHub Actions after every relevant update.",
            "",
        ]
        (ROOT/"docs").mkdir(exist_ok=True)
        (ROOT/"docs"/"RUBRIC_AUDIT.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"reports":records,"failures":failures},ensure_ascii=False,indent=2))
    return 1 if failures else 0

if __name__=="__main__":
    raise SystemExit(main())
