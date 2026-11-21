# Exercise 3 Complete Worked Answer Key: EDF and RM

This is a reference answer key generated from the independent discrete-tick tracer. A student-required handwritten submission must still be written personally on the printable worksheet; this digital key is not represented as handwriting.

## Set A — H=12, U=11/12 (0.9167)

Tasks: P1(T=3, C=1, D=3), P2(T=4, C=1, D=4), P3(T=6, C=2, D=6)

### EDF: 0 deadline misses

| Tick | Arrivals | Ready queue (remaining, deadline) | Dispatch | After execution | Miss |
|---|---|---|---|---|---|
| 0 | P1#0, P2#0, P3#0 | P1#0(r=1,d=3), P2#0(r=1,d=4), P3#0(r=2,d=6) | P1#0 | P1#0:DONE | - |
| 1 | - | P2#0(r=1,d=4), P3#0(r=2,d=6) | P2#0 | P2#0:DONE | - |
| 2 | - | P3#0(r=2,d=6) | P3#0 | P3#0:1 | - |
| 3 | P1#1 | P1#1(r=1,d=6), P3#0(r=1,d=6) | P1#1 | P1#1:DONE | - |
| 4 | P2#1 | P3#0(r=1,d=6), P2#1(r=1,d=8) | P3#0 | P3#0:DONE | - |
| 5 | - | P2#1(r=1,d=8) | P2#1 | P2#1:DONE | - |
| 6 | P1#2, P3#1 | P1#2(r=1,d=9), P3#1(r=2,d=12) | P1#2 | P1#2:DONE | - |
| 7 | - | P3#1(r=2,d=12) | P3#1 | P3#1:1 | - |
| 8 | P2#2 | P2#2(r=1,d=12), P3#1(r=1,d=12) | P2#2 | P2#2:DONE | - |
| 9 | P1#3 | P1#3(r=1,d=12), P3#1(r=1,d=12) | P1#3 | P1#3:DONE | - |
| 10 | - | P3#1(r=1,d=12) | P3#1 | P3#1:DONE | - |
| 11 | - | EMPTY | IDLE | - | - |

### RM: 0 deadline misses

| Tick | Arrivals | Ready queue (remaining, deadline) | Dispatch | After execution | Miss |
|---|---|---|---|---|---|
| 0 | P1#0, P2#0, P3#0 | P1#0(r=1,d=3), P2#0(r=1,d=4), P3#0(r=2,d=6) | P1#0 | P1#0:DONE | - |
| 1 | - | P2#0(r=1,d=4), P3#0(r=2,d=6) | P2#0 | P2#0:DONE | - |
| 2 | - | P3#0(r=2,d=6) | P3#0 | P3#0:1 | - |
| 3 | P1#1 | P1#1(r=1,d=6), P3#0(r=1,d=6) | P1#1 | P1#1:DONE | - |
| 4 | P2#1 | P2#1(r=1,d=8), P3#0(r=1,d=6) | P2#1 | P2#1:DONE | - |
| 5 | - | P3#0(r=1,d=6) | P3#0 | P3#0:DONE | - |
| 6 | P1#2, P3#1 | P1#2(r=1,d=9), P3#1(r=2,d=12) | P1#2 | P1#2:DONE | - |
| 7 | - | P3#1(r=2,d=12) | P3#1 | P3#1:1 | - |
| 8 | P2#2 | P2#2(r=1,d=12), P3#1(r=1,d=12) | P2#2 | P2#2:DONE | - |
| 9 | P1#3 | P1#3(r=1,d=12), P3#1(r=1,d=12) | P1#3 | P1#3:DONE | - |
| 10 | - | P3#1(r=1,d=12) | P3#1 | P3#1:DONE | - |
| 11 | - | EMPTY | IDLE | - | - |

### Why the schedules diverge at t=4 and t=5
At t=4, EDF chooses P3#0 (absolute deadline 6) ahead of P2#1 (deadline 8). RM instead chooses P2#1 because its period is shorter. Both finish P3#0 before its deadline.

## Set B — H=24, U=23/24 (0.9583)

Tasks: P1(T=4, C=1, D=4), P2(T=6, C=2, D=6), P3(T=8, C=3, D=8)

### EDF: 0 deadline misses

| Tick | Arrivals | Ready queue (remaining, deadline) | Dispatch | After execution | Miss |
|---|---|---|---|---|---|
| 0 | P1#0, P2#0, P3#0 | P1#0(r=1,d=4), P2#0(r=2,d=6), P3#0(r=3,d=8) | P1#0 | P1#0:DONE | - |
| 1 | - | P2#0(r=2,d=6), P3#0(r=3,d=8) | P2#0 | P2#0:1 | - |
| 2 | - | P2#0(r=1,d=6), P3#0(r=3,d=8) | P2#0 | P2#0:DONE | - |
| 3 | - | P3#0(r=3,d=8) | P3#0 | P3#0:2 | - |
| 4 | P1#1 | P1#1(r=1,d=8), P3#0(r=2,d=8) | P1#1 | P1#1:DONE | - |
| 5 | - | P3#0(r=2,d=8) | P3#0 | P3#0:1 | - |
| 6 | P2#1 | P3#0(r=1,d=8), P2#1(r=2,d=12) | P3#0 | P3#0:DONE | - |
| 7 | - | P2#1(r=2,d=12) | P2#1 | P2#1:1 | - |
| 8 | P1#2, P3#1 | P1#2(r=1,d=12), P2#1(r=1,d=12), P3#1(r=3,d=16) | P1#2 | P1#2:DONE | - |
| 9 | - | P2#1(r=1,d=12), P3#1(r=3,d=16) | P2#1 | P2#1:DONE | - |
| 10 | - | P3#1(r=3,d=16) | P3#1 | P3#1:2 | - |
| 11 | - | P3#1(r=2,d=16) | P3#1 | P3#1:1 | - |
| 12 | P1#3, P2#2 | P1#3(r=1,d=16), P3#1(r=1,d=16), P2#2(r=2,d=18) | P1#3 | P1#3:DONE | - |
| 13 | - | P3#1(r=1,d=16), P2#2(r=2,d=18) | P3#1 | P3#1:DONE | - |
| 14 | - | P2#2(r=2,d=18) | P2#2 | P2#2:1 | - |
| 15 | - | P2#2(r=1,d=18) | P2#2 | P2#2:DONE | - |
| 16 | P1#4, P3#2 | P1#4(r=1,d=20), P3#2(r=3,d=24) | P1#4 | P1#4:DONE | - |
| 17 | - | P3#2(r=3,d=24) | P3#2 | P3#2:2 | - |
| 18 | P2#3 | P2#3(r=2,d=24), P3#2(r=2,d=24) | P2#3 | P2#3:1 | - |
| 19 | - | P2#3(r=1,d=24), P3#2(r=2,d=24) | P2#3 | P2#3:DONE | - |
| 20 | P1#5 | P1#5(r=1,d=24), P3#2(r=2,d=24) | P1#5 | P1#5:DONE | - |
| 21 | - | P3#2(r=2,d=24) | P3#2 | P3#2:1 | - |
| 22 | - | P3#2(r=1,d=24) | P3#2 | P3#2:DONE | - |
| 23 | - | EMPTY | IDLE | - | - |

### RM: 1 deadline misses

| Tick | Arrivals | Ready queue (remaining, deadline) | Dispatch | After execution | Miss |
|---|---|---|---|---|---|
| 0 | P1#0, P2#0, P3#0 | P1#0(r=1,d=4), P2#0(r=2,d=6), P3#0(r=3,d=8) | P1#0 | P1#0:DONE | - |
| 1 | - | P2#0(r=2,d=6), P3#0(r=3,d=8) | P2#0 | P2#0:1 | - |
| 2 | - | P2#0(r=1,d=6), P3#0(r=3,d=8) | P2#0 | P2#0:DONE | - |
| 3 | - | P3#0(r=3,d=8) | P3#0 | P3#0:2 | - |
| 4 | P1#1 | P1#1(r=1,d=8), P3#0(r=2,d=8) | P1#1 | P1#1:DONE | - |
| 5 | - | P3#0(r=2,d=8) | P3#0 | P3#0:1 | - |
| 6 | P2#1 | P2#1(r=2,d=12), P3#0(r=1,d=8) | P2#1 | P2#1:1 | - |
| 7 | - | P2#1(r=1,d=12), P3#0(r=1,d=8) | P2#1 | P2#1:DONE | - |
| 8 | P1#2, P3#1 | P1#2(r=1,d=12), P3#0(r=1,d=8), P3#1(r=3,d=16) | P1#2 | P1#2:DONE | P3#0 |
| 9 | - | P3#0(r=1,d=8), P3#1(r=3,d=16) | P3#0 | P3#0:DONE | - |
| 10 | - | P3#1(r=3,d=16) | P3#1 | P3#1:2 | - |
| 11 | - | P3#1(r=2,d=16) | P3#1 | P3#1:1 | - |
| 12 | P1#3, P2#2 | P1#3(r=1,d=16), P2#2(r=2,d=18), P3#1(r=1,d=16) | P1#3 | P1#3:DONE | - |
| 13 | - | P2#2(r=2,d=18), P3#1(r=1,d=16) | P2#2 | P2#2:1 | - |
| 14 | - | P2#2(r=1,d=18), P3#1(r=1,d=16) | P2#2 | P2#2:DONE | - |
| 15 | - | P3#1(r=1,d=16) | P3#1 | P3#1:DONE | - |
| 16 | P1#4, P3#2 | P1#4(r=1,d=20), P3#2(r=3,d=24) | P1#4 | P1#4:DONE | - |
| 17 | - | P3#2(r=3,d=24) | P3#2 | P3#2:2 | - |
| 18 | P2#3 | P2#3(r=2,d=24), P3#2(r=2,d=24) | P2#3 | P2#3:1 | - |
| 19 | - | P2#3(r=1,d=24), P3#2(r=2,d=24) | P2#3 | P2#3:DONE | - |
| 20 | P1#5 | P1#5(r=1,d=24), P3#2(r=2,d=24) | P1#5 | P1#5:DONE | - |
| 21 | - | P3#2(r=2,d=24) | P3#2 | P3#2:1 | - |
| 22 | - | P3#2(r=1,d=24) | P3#2 | P3#2:DONE | - |
| 23 | - | EMPTY | IDLE | - | - |

Miss witness: t=8 P3#0 D=8

### Exact RM miss proof for P3#0
At [6,8), P3#0 has one unit left and deadline 8. EDF completes it in [6,7). RM gives both ticks to the newly released P2#1 because period 6 outranks period 8. At t=8, P3#0 still has one unit remaining and misses its deadline.

RTA for P3: R(0)=3, R(1)=6, R(2)=7, R(3)=9. Since 9>8, RM is not schedulable for Set B.

## Set C — H=24, U=7/6 (1.1667)

Tasks: P1(T=3, C=1, D=3), P2(T=4, C=2, D=4), P3(T=6, C=2, D=6)

### EDF: 5 deadline misses

| Tick | Arrivals | Ready queue (remaining, deadline) | Dispatch | After execution | Miss |
|---|---|---|---|---|---|
| 0 | P1#0, P2#0, P3#0 | P1#0(r=1,d=3), P2#0(r=2,d=4), P3#0(r=2,d=6) | P1#0 | P1#0:DONE | - |
| 1 | - | P2#0(r=2,d=4), P3#0(r=2,d=6) | P2#0 | P2#0:1 | - |
| 2 | - | P2#0(r=1,d=4), P3#0(r=2,d=6) | P2#0 | P2#0:DONE | - |
| 3 | P1#1 | P1#1(r=1,d=6), P3#0(r=2,d=6) | P1#1 | P1#1:DONE | - |
| 4 | P2#1 | P3#0(r=2,d=6), P2#1(r=2,d=8) | P3#0 | P3#0:1 | - |
| 5 | - | P3#0(r=1,d=6), P2#1(r=2,d=8) | P3#0 | P3#0:DONE | - |
| 6 | P1#2, P3#1 | P2#1(r=2,d=8), P1#2(r=1,d=9), P3#1(r=2,d=12) | P2#1 | P2#1:1 | - |
| 7 | - | P2#1(r=1,d=8), P1#2(r=1,d=9), P3#1(r=2,d=12) | P2#1 | P2#1:DONE | - |
| 8 | P2#2 | P1#2(r=1,d=9), P2#2(r=2,d=12), P3#1(r=2,d=12) | P1#2 | P1#2:DONE | - |
| 9 | P1#3 | P1#3(r=1,d=12), P2#2(r=2,d=12), P3#1(r=2,d=12) | P1#3 | P1#3:DONE | - |
| 10 | - | P2#2(r=2,d=12), P3#1(r=2,d=12) | P2#2 | P2#2:1 | - |
| 11 | - | P2#2(r=1,d=12), P3#1(r=2,d=12) | P2#2 | P2#2:DONE | - |
| 12 | P1#4, P2#3, P3#2 | P3#1(r=2,d=12), P1#4(r=1,d=15), P2#3(r=2,d=16), P3#2(r=2,d=18) | P3#1 | P3#1:1 | P3#1 |
| 13 | - | P3#1(r=1,d=12), P1#4(r=1,d=15), P2#3(r=2,d=16), P3#2(r=2,d=18) | P3#1 | P3#1:DONE | - |
| 14 | - | P1#4(r=1,d=15), P2#3(r=2,d=16), P3#2(r=2,d=18) | P1#4 | P1#4:DONE | - |
| 15 | P1#5 | P2#3(r=2,d=16), P1#5(r=1,d=18), P3#2(r=2,d=18) | P2#3 | P2#3:1 | - |
| 16 | P2#4 | P2#3(r=1,d=16), P1#5(r=1,d=18), P3#2(r=2,d=18), P2#4(r=2,d=20) | P2#3 | P2#3:DONE | P2#3 |
| 17 | - | P1#5(r=1,d=18), P3#2(r=2,d=18), P2#4(r=2,d=20) | P1#5 | P1#5:DONE | - |
| 18 | P1#6, P3#3 | P3#2(r=2,d=18), P2#4(r=2,d=20), P1#6(r=1,d=21), P3#3(r=2,d=24) | P3#2 | P3#2:1 | P3#2 |
| 19 | - | P3#2(r=1,d=18), P2#4(r=2,d=20), P1#6(r=1,d=21), P3#3(r=2,d=24) | P3#2 | P3#2:DONE | - |
| 20 | P2#5 | P2#4(r=2,d=20), P1#6(r=1,d=21), P2#5(r=2,d=24), P3#3(r=2,d=24) | P2#4 | P2#4:1 | P2#4 |
| 21 | P1#7 | P2#4(r=1,d=20), P1#6(r=1,d=21), P1#7(r=1,d=24), P2#5(r=2,d=24), P3#3(r=2,d=24) | P2#4 | P2#4:DONE | P1#6 |
| 22 | - | P1#6(r=1,d=21), P1#7(r=1,d=24), P2#5(r=2,d=24), P3#3(r=2,d=24) | P1#6 | P1#6:DONE | - |
| 23 | - | P1#7(r=1,d=24), P2#5(r=2,d=24), P3#3(r=2,d=24) | P1#7 | P1#7:DONE | - |

Miss witness: t=12 P3#1 D=12; t=16 P2#3 D=16; t=18 P3#2 D=18; t=20 P2#4 D=20; t=21 P1#6 D=21

### RM: 3 deadline misses

| Tick | Arrivals | Ready queue (remaining, deadline) | Dispatch | After execution | Miss |
|---|---|---|---|---|---|
| 0 | P1#0, P2#0, P3#0 | P1#0(r=1,d=3), P2#0(r=2,d=4), P3#0(r=2,d=6) | P1#0 | P1#0:DONE | - |
| 1 | - | P2#0(r=2,d=4), P3#0(r=2,d=6) | P2#0 | P2#0:1 | - |
| 2 | - | P2#0(r=1,d=4), P3#0(r=2,d=6) | P2#0 | P2#0:DONE | - |
| 3 | P1#1 | P1#1(r=1,d=6), P3#0(r=2,d=6) | P1#1 | P1#1:DONE | - |
| 4 | P2#1 | P2#1(r=2,d=8), P3#0(r=2,d=6) | P2#1 | P2#1:1 | - |
| 5 | - | P2#1(r=1,d=8), P3#0(r=2,d=6) | P2#1 | P2#1:DONE | - |
| 6 | P1#2, P3#1 | P1#2(r=1,d=9), P3#0(r=2,d=6), P3#1(r=2,d=12) | P1#2 | P1#2:DONE | P3#0 |
| 7 | - | P3#0(r=2,d=6), P3#1(r=2,d=12) | P3#0 | P3#0:1 | - |
| 8 | P2#2 | P2#2(r=2,d=12), P3#0(r=1,d=6), P3#1(r=2,d=12) | P2#2 | P2#2:1 | - |
| 9 | P1#3 | P1#3(r=1,d=12), P2#2(r=1,d=12), P3#0(r=1,d=6), P3#1(r=2,d=12) | P1#3 | P1#3:DONE | - |
| 10 | - | P2#2(r=1,d=12), P3#0(r=1,d=6), P3#1(r=2,d=12) | P2#2 | P2#2:DONE | - |
| 11 | - | P3#0(r=1,d=6), P3#1(r=2,d=12) | P3#0 | P3#0:DONE | - |
| 12 | P1#4, P2#3, P3#2 | P1#4(r=1,d=15), P2#3(r=2,d=16), P3#1(r=2,d=12), P3#2(r=2,d=18) | P1#4 | P1#4:DONE | P3#1 |
| 13 | - | P2#3(r=2,d=16), P3#1(r=2,d=12), P3#2(r=2,d=18) | P2#3 | P2#3:1 | - |
| 14 | - | P2#3(r=1,d=16), P3#1(r=2,d=12), P3#2(r=2,d=18) | P2#3 | P2#3:DONE | - |
| 15 | P1#5 | P1#5(r=1,d=18), P3#1(r=2,d=12), P3#2(r=2,d=18) | P1#5 | P1#5:DONE | - |
| 16 | P2#4 | P2#4(r=2,d=20), P3#1(r=2,d=12), P3#2(r=2,d=18) | P2#4 | P2#4:1 | - |
| 17 | - | P2#4(r=1,d=20), P3#1(r=2,d=12), P3#2(r=2,d=18) | P2#4 | P2#4:DONE | - |
| 18 | P1#6, P3#3 | P1#6(r=1,d=21), P3#1(r=2,d=12), P3#2(r=2,d=18), P3#3(r=2,d=24) | P1#6 | P1#6:DONE | P3#2 |
| 19 | - | P3#1(r=2,d=12), P3#2(r=2,d=18), P3#3(r=2,d=24) | P3#1 | P3#1:1 | - |
| 20 | P2#5 | P2#5(r=2,d=24), P3#1(r=1,d=12), P3#2(r=2,d=18), P3#3(r=2,d=24) | P2#5 | P2#5:1 | - |
| 21 | P1#7 | P1#7(r=1,d=24), P2#5(r=1,d=24), P3#1(r=1,d=12), P3#2(r=2,d=18), P3#3(r=2,d=24) | P1#7 | P1#7:DONE | - |
| 22 | - | P2#5(r=1,d=24), P3#1(r=1,d=12), P3#2(r=2,d=18), P3#3(r=2,d=24) | P2#5 | P2#5:DONE | - |
| 23 | - | P3#1(r=1,d=12), P3#2(r=2,d=18), P3#3(r=2,d=24) | P3#1 | P3#1:DONE | - |

Miss witness: t=6 P3#0 D=6; t=12 P3#1 D=12; t=18 P3#2 D=18

### Overload interpretation
U=7/6>1, so demand over the 24-tick horizon exceeds processor capacity. The reference trace records five EDF misses and three RM misses. No uniprocessor policy can guarantee all jobs under this overload.

## Answer summary

| مجموعه | U | EDF miss | RM miss |
|---|---:|---:|---:|
| A | 0.9167 | 0 | 0 |
| B | 0.9583 | 0 | 1 |
| C | 1.1667 | 5 | 3 |

Method: release jobs at the start of each tick, audit expired deadlines, dispatch by EDF or fixed RM priority, then consume one CPU tick. EDF ties are broken by lower task index.
