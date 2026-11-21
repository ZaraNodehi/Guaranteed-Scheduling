# Exercise 7 — Dining Philosophers: Guaranteed Scheduling and Deadlock-Free Resource Allocation

**Independent exercise folder:** exercise-7/

This exercise answers the final instructor-rubric question: can the logic of Guaranteed Scheduling be used for Dining Philosophers, and how? The answer is layered: GS distributes CPU service among runnable philosophers; a separate resource protocol must guarantee fork ownership, avoid circular wait and provide fair admission.

## Learning objectives
1. Distinguish processor fairness from shared-resource safety.
2. Construct and explain the naive five-philosopher circular-wait deadlock.
3. Implement a FIFO monitor that reserves both adjacent forks atomically.
4. State and test mutual-exclusion, ownership, no-partial-hold and FIFO invariants.
5. Explore a finite state model and stress the actual monitor with concurrent threads.
6. Run exact-rational GS CPU-share experiments with equal and weighted philosopher tasks.
7. State the limits and assumptions behind deadlock freedom and liveness.

## Design answer
**GS alone does not solve Dining Philosophers.** A thread can be fairly scheduled and still be blocked by a fork cycle. The implementation composes the existing exact-rational gs_vtime CPU scheduler with FairDiningTable, a monitor that:
- issues monotonic FIFO tickets;
- lets only the queue head proceed when both adjacent forks are free;
- reserves both forks in one monitor critical section;
- never exposes partial fork ownership; and
- releases both forks together after a meal.

The global resource-hierarchy alternative is also documented: acquire the lower-numbered fork before the higher-numbered fork. It prevents a circular acquisition order but does not itself promise FIFO waiting.

## Reproducible evidence
- output/experiments.json: naive deadlock witness, finite-state metrics, live-thread result and exact-rational GS CPU service.
- diagrams/: eight analysis charts, the rubric flowchart and worksheet previews.
- WORKSHEET_DINING_PHILOSOPHERS.pdf: printable study worksheet with the wait-for graph and FIFO state table.
- media/dining_philosophers_demo.mp4: short explanatory animation of the circular wait and FIFO fix. It is an educational protocol animation, not a live-kernel benchmark.
- docs/REPORT_EN.pdf and docs/REPORT_FA.pdf: source-audited monographs; the CI page gate requires more than 40 pages for both.
- docs/ARTICLE_{EN,FA}.{md,docx,pdf}: standalone bilingual research article.
- docs/PRESENTATION_{EN,FA}.pptx and SPEAKER_SCRIPT_{EN,FA}.md: seven-slide bilingual seminar with speaker notes on every slide.

## Quick start
Run these commands from the repository root:

    python3 exercise-7/code/run_experiments.py
    python3 exercise-7/code/plot_diagrams.py
    python3 exercise-7/code/make_worksheet.py
    python3 exercise-7/code/make_demo_video.py
    python3 tools/make_rubric_flowcharts.py
    python3 tools/make_decks.py 7
    python3 tools/build_ex7_articles.py
    python3 tools/build_report.py ex7_en exercise-7 REPORT_EN
    python3 tools/build_report.py ex7_fa exercise-7 REPORT_FA
    python3 -m pytest exercise-7/tests -v
    python3 tools/check_outputs.py exercise-7

## What is proven and what is conditional
The finite-state explorer exhaustively checks its stated five-philosopher abstraction for adjacent-eater safety, nonterminal deadlocks and terminal completion. The real-thread stress test checks one finite concurrent execution. Liveness assumes each granted meal finishes, waiting threads are eventually scheduled, and notifications are eventually processed. Neither a finite test nor FIFO can guarantee progress if a thread holds both forks forever or the runtime never schedules a waiter.

## Instructor rubric mapping
| Criterion | Exercise 7 evidence |
|---|---|
| Algorithm / implementation | code/dining_philosophers.py and exact-rational GS CPU experiment |
| Flowchart | diagrams/fig_exercise7_rubric_flowchart.png |
| Comparative analysis | naive left/right, global resource order and FIFO atomic monitor |
| Executable code | independent experiment driver, finite-state explorer and tests |
| Demonstration clip | media/dining_philosophers_demo.mp4 |
| English / Persian files | bilingual reports, research article and seminar |
| More than 40 pages | enforced on both final PDF reports by tools/rubric_page_gate.py |
| Explanation | this README and the bilingual monographs answer why GS alone is insufficient |

The report and article are generated from this independent exercise folder; the exercise does not rely on the Exercise 6 implementation at runtime.
