# Exercise 3 — Paper Copy Guides

Two printable three-page reference guides are generated from the canonical output/experiments.json data.

- HAND_COPY_GUIDE_STUDENT_1.pdf: EDF is shown first, then RM.
- HAND_COPY_GUIDE_STUDENT_2.pdf: RM is shown first, then EDF.

Both copies cover the same required paper sets:
- Set A: H=12, P1(3,1,3), P2(4,1,4), P3(6,2,6).
- Set B: H=24, P1(4,1,4), P2(6,2,6), P3(8,3,8).

Each guide includes the Gantt tick assignments, tick-by-tick dispatch table, required ready-queue states, Set A response-time analysis, and the Set B RM miss/RTA and EDF demand-bound calculation. The second copy reverses the order of the EDF and RM columns/diagrams so each student has a separate writing layout while the exercise data and correct results remain identical.

## Important

These PDFs and PNGs are clean digital reference aids, not handwritten submissions. Each student should print or view their own guide, write the solution by hand on paper in their own handwriting, add their own name/student ID, and scan or photograph the personally completed pages into handwritten_scan/.

## Regenerate

From the repository root:

    python3 exercise-3/code/run_experiments.py
    python3 exercise-3/code/make_paper_copy_guides.py
    python3 -m pytest exercise-3/tests -v

The generator writes both PDFs plus three PNG page previews per copy into this folder.
