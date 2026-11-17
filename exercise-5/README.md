# Exercise 5 — Readers–Writers Across Semaphore, Monitor, Peterson & Dekker

Comprehensive comparative implementation and empirical verification of all three classical Readers–Writers policies (**Readers-Preference**, **Writers-Preference**, and **Fair FIFO/Turnstile**) across **Semaphore**, **Mesa Monitor**, **Peterson FilterLock**, and **Tournament Dekker** (+ `CoarseMutex` serial baseline).

## Key Findings
- **Concurrent Read Safety (`4 Readers + 2 Writers`)**: All 12 RW variants achieved `maxR = 4` simultaneous readers (`CoarseMutex = 1`) with `0` overlap errors.
- **Starvation & Barging Discovery**:
  - Under `Reader-Flood (120 ms)`, `Readers-Pref` starved writers completely (`0` ops across all 4 primitives), while `Writers-Pref` and `Fair` delivered `35–39` bounded writer ops (`~2.2 ms` max wait).
  - Under `Writer-Flood (120 ms)`, **Monitor Ticket (`12` ops)** and **Peterson/Dekker Deque (`12` ops)** completely eliminated starvation, exposing turnstile **barging** in unfair `Semaphore` (`0` ops).
- **Read-Heavy Crossover (`0.3 ms` Read Scan at `95%` Reads)**: Fair RW locks delivered **3.6×–4.03× speedup** (`8,659–9,637 ops/s`) over `CoarseMutex` (`2,390 ops/s`).
- **Writer-Wait CPU Burn**: Waiting writers burned `~2.0 ms` CPU on blocking Semaphore/Monitor vs. `396–615 ms` on spinning Peterson/Dekker (`~200–300×` more CPU).

## Reproduction
```bash
python3 exercise-5/code/run_experiments.py
python3 exercise-5/code/plot_diagrams.py
python3 tools/build_report.py ex5_en exercise-5 REPORT_EN
python3 tools/build_report.py ex5_fa exercise-5 REPORT_FA
python3 -m pytest exercise-5/tests -v
```
