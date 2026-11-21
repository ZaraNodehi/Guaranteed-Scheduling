"""Exercise 7 data accessors for reports; all numbers come from output/experiments.json."""
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DATA_PATH=ROOT/"exercise-7"/"output"/"experiments.json"

def load():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))

def cpu_rows(d,case="equal_weight"):
    per=d["gs_cpu_study"][case]["per_proc"]
    return [[name,str(v["weight"]),str(v["used"]),str(v["entitled_gps_frac"]),
             f"{v['share_ratio']:.4f}",str(v["max_starve_gap"])]
            for name,v in per.items()]

def summary_rows(d):
    m=d["fifo_model"];s=d["thread_stress"]
    return [
      ["Five philosophers",str(m["philosophers"])],
      ["Reachable states",str(m["reachable_states"])],
      ["Transitions",str(m["transitions"])],
      ["Unsafe states",str(m["unsafe_states"])],
      ["Nonterminal deadlock states",str(m["deadlock_states"])],
      ["Terminal completed states",str(m["terminal_states"])],
      ["Real-thread meals completed",str(s["completed_meals"])],
      ["Safety violations",str(s["safety_violations"])],
      ["All worker threads finished",str(not s["threads_still_alive"])],
      ["FIFO admission tickets monotone",str(s["admission_tickets_monotone"])],
    ]

def code_slice(rel_path,start,end):
    p=ROOT/rel_path
    lines=p.read_text(encoding="utf-8").splitlines()
    return [f"{i:03d}: {lines[i-1]}" for i in range(start,min(end,len(lines))+1)]
