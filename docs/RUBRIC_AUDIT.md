# Instructor-Rubric Audit — Guaranteed Scheduling

This report is generated from the files in the current build. PDF page counts below are read from the final PDF files, not inferred from Markdown section counts.

| Exercise | English PDF | Persian PDF | Main subject |
|---|---:|---:|---|
| exercise-1 | 42 pages | 42 pages | Guaranteed Scheduling introduction |
| exercise-2 | 43 pages | 43 pages | Guaranteed Scheduling vs. EDF/RM/DM comparison |
| exercise-3 | 45 pages | 43 pages | Paper EDF/RM scheduling and independent verification |
| exercise-4 | 43 pages | 42 pages | Dekker, Peterson, Semaphore and Monitor |
| exercise-5 | 44 pages | 43 pages | Readers–Writers synchronization |
| exercise-6 | 43 pages | 42 pages | Integrated operating-systems capstone and seminar |
| exercise-7 | 47 pages | 47 pages | Dining Philosophers: CPU fairness and deadlock-free resource allocation |

## Checklist evidence

| Instructor criterion | Repository evidence | Status |
|---|---|---|
| Algorithm and implementation | GuaranteedScheduling.py, core/gs_core.py, exercise-specific simulators and tests | Present |
| Comparison and analysis | Exercise 2: GS variants, EDF, DM, RM, Stride and Round Robin; exact/exhaustive datasets | Present |
| Paper scheduling | Exercise 3: complete tick-by-tick EDF/RM reference traces for Sets A/B/C, bilingual worked answer keys, RTA/dbf and printable A4 worksheet | Reference solution present; student must still handwrite their own submission |
| Synchronization | Exercise 4: Dekker, Peterson, Semaphore, Mesa Monitor and BFS; Exercise 7: FIFO Dining Philosophers monitor, finite-state model and real-thread stress test | Present |
| Demonstration clip | exercise-1/media/guaranteed_scheduling_demo.mp4, rendered from the gs_vtime simulator trace | Present |
| Paper/seminar | Exercise 6 integrated capstone and Exercise 7 standalone bilingual 7-slide seminar, per-slide speaker notes/scripts and research article | Present |
| Persian and English reports | DOCX, PDF and Markdown for all seven exercises | Present |
| More than 40 PDF pages | Counts reported in the table above; all are >40 | Verified by build gate |

## Important academic note

The bilingual Exercise 3 worked answer key is a reference solution generated from independent traces. Its printable worksheet is still a blank form; the student must complete and scan their own handwritten work. Exercise 7 proves the stated finite model properties, while liveness remains conditional on meals finishing and waiters eventually being scheduled. Attending class and the instructor's grade cannot be verified from repository files.

## Automated verification

pytest, check_outputs.py, and this page-count gate run in GitHub Actions after every relevant update.
