# Instructor-Rubric Audit — Guaranteed Scheduling

This report is generated from the files in the current build. PDF page counts below are read from the final PDF files, not inferred from Markdown section counts.

| Exercise | English PDF | Persian PDF | Main subject |
|---|---:|---:|---|
| exercise-1 | 42 pages | 42 pages | Guaranteed Scheduling introduction |
| exercise-2 | 43 pages | 43 pages | Guaranteed Scheduling vs. EDF/RM/DM comparison |
| exercise-3 | 45 pages | 43 pages | Paper EDF/RM scheduling and independent verification |
| exercise-4 | 43 pages | 42 pages | Dekker, Peterson, Semaphore and Monitor |
| exercise-5 | 44 pages | 43 pages | Readers–Writers synchronization |
| exercise-6 | 42 pages | 41 pages | Integrated operating-systems capstone and seminar |

## Checklist evidence

| Instructor criterion | Repository evidence | Status |
|---|---|---|
| Algorithm and implementation | GuaranteedScheduling.py, core/gs_core.py, exercise-specific simulators and tests | Present |
| Comparison and analysis | Exercise 2: GS variants, EDF, DM, RM, Stride and Round Robin; exact/exhaustive datasets | Present |
| Paper scheduling | Exercise 3: tick-by-tick EDF/RM traces, RTA/dbf analysis and printable A4 worksheet | Present; handwritten scan still requires the student's own work |
| Synchronization | Exercise 4: Dekker, Peterson, Semaphore, Mesa Monitor, BFS and live thread benchmarks | Present |
| Demonstration clip | exercise-1/media/guaranteed_scheduling_demo.mp4, rendered from the gs_vtime simulator trace | Present |
| Paper/seminar | Exercise 6 bilingual report, bilingual 10-slide presentation and speaker scripts | Present |
| Persian and English reports | DOCX, PDF and Markdown for all six exercises | Present |
| More than 40 PDF pages | Counts reported in the table above; all are >40 | Verified by build gate |

## Important academic note

The paper worksheet template and digital trace are supplied as study/reproducibility material. They are not represented as a student's handwritten submission. The student must complete and scan any handwritten work personally. Likewise, attending class and the instructor's grade cannot be verified from repository files.

## Automated verification

pytest, check_outputs.py, and this page-count gate run in GitHub Actions after every relevant update.
