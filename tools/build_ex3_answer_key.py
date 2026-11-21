"""Generate bilingual worked EDF/RM answer keys from the independent experiment traces."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "exercise-3/output/experiments.json").read_text(encoding="utf-8"))

def task_text(tasks):
    return ", ".join(f"{t['name']}(T={t['period']}, C={t['wcet']}, D={t['deadline']})" for t in tasks)

def render_trace(trace, fa=False):
    headers = ("تیک", "ورودها", "صف آماده (باقیمانده، مهلت)", "انتخاب", "پس از اجرا", "خطا") if fa else ("Tick", "Arrivals", "Ready queue (remaining, deadline)", "Dispatch", "After execution", "Miss")
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"]*len(headers)) + "|"]
    for r in trace:
        out.append("| " + " | ".join(str(x) for x in (r["t"],r["arrivals"],r["ready_queue"],r["chosen"],r["rem_after"],r["miss_at_t"])) + " |")
    return "\n".join(out)

def build(lang):
    fa = lang == "FA"
    title = "# حل‌نامهٔ کامل تمرین ۳: ردگیری دستی EDF و RM" if fa else "# Exercise 3 Complete Worked Answer Key: EDF and RM"
    intro = (
      "این حل‌نامه پاسخ مرجع آموزشی است و از ردگیر مستقل تمرین تولید شده است. برای تحویلِ «حل روی کاغذ»، دانشجو باید همین مراحل را شخصاً روی برگه بنویسد؛ این فایل جای دست‌نویس او را نمی‌گیرد."
      if fa else
      "This is a reference answer key generated from the independent discrete-tick tracer. A student-required handwritten submission must still be written personally on the printable worksheet; this digital key is not represented as handwriting."
    )
    sections=[title,"",intro,""]
    sets=[("set_a","A", "مجموعه A" if fa else "Set A"),
          ("set_b","B", "مجموعه B" if fa else "Set B"),
          ("set_c","C", "مجموعه C" if fa else "Set C")]
    for key,letter,label in sets:
        d=DATA[key]
        sections += [f"## {label} — H={d['horizon']}, U={d['utilization_frac']} ({d['utilization']:.4f})",
                     "", (f"وظایف: {task_text(d['tasks'])}" if fa else f"Tasks: {task_text(d['tasks'])}"), ""]
        for alg,alglabel in (("edf","EDF"),("rm","RM")):
            a=d[alg]
            sections += [f"### {alglabel}: {a['missed_count']} " + ("شکست مهلت" if fa else "deadline misses"), "",
                         render_trace(a["trace_rows"],fa),""]
            misses=a.get("misses",[])
            if misses:
                sections.append(("نقطهٔ شکست: " if fa else "Miss witness: ") + "; ".join(f"t={m['tick']} {m['job']} D={m['deadline']}" for m in misses))
                sections.append("")
        if key=="set_a":
            sections += [
              "### تحلیل اختلاف در t=4 و t=5" if fa else "### Why the schedules diverge at t=4 and t=5",
              ("EDF در t=4 کار P3#0 با مهلت 6 را بر P2#1 با مهلت 8 مقدم می‌کند؛ RM به دلیل دورهٔ کوتاه‌تر P2، ابتدا P2#1 را اجرا می‌کند. هر دو پیش از مهلت P3#0 تمام می‌شوند."
               if fa else
               "At t=4, EDF chooses P3#0 (absolute deadline 6) ahead of P2#1 (deadline 8). RM instead chooses P2#1 because its period is shorter. Both finish P3#0 before its deadline."),
              ""
            ]
        if key=="set_b":
            sections += [
              "### اثبات شکست RM در P3#0" if fa else "### Exact RM miss proof for P3#0",
              ("در بازهٔ [6,8)، P3#0 فقط یک واحد کار باقی‌مانده و مهلت 8 دارد. EDF آن را در [6,7) تمام می‌کند. RM به علت اولویت ثابت P2 با دورهٔ 6، P2#1 را در [6,8) اجرا می‌کند؛ در t=8، P3#0 هنوز یک واحد کار دارد و مهلتش از دست رفته است."
               if fa else
               "At [6,8), P3#0 has one unit left and deadline 8. EDF completes it in [6,7). RM gives both ticks to the newly released P2#1 because period 6 outranks period 8. At t=8, P3#0 still has one unit remaining and misses its deadline."),
              "",
              ("تحلیل RTA برای P3: R⁽⁰⁾=3، R⁽¹⁾=6، R⁽²⁾=7، R⁽³⁾=9؛ چون 9>8، RM قابل زمان‌بندی نیست."
               if fa else
               "RTA for P3: R(0)=3, R(1)=6, R(2)=7, R(3)=9. Since 9>8, RM is not schedulable for Set B."),
              ""
            ]
        if key=="set_c":
            sections += [
              "### تفسیر بار بیش از ظرفیت" if fa else "### Overload interpretation",
              ("U=7/6>1 است؛ تقاضای کل در افق 24 تیک از ظرفیت پردازنده بیشتر است. در دادهٔ آزمایش، EDF پنج مهلت و RM سه مهلت را از دست می‌دهد؛ بنابراین هیچ سیاست تک‌پردازنده‌ای نمی‌تواند همهٔ کارها را در این بار تضمین کند."
               if fa else
               "U=7/6>1, so demand over the 24-tick horizon exceeds processor capacity. The reference trace records five EDF misses and three RM misses. No uniprocessor policy can guarantee all jobs under this overload."),
              ""
            ]
    sections += [
      "## خلاصهٔ پاسخ" if fa else "## Answer summary",
      "",
      "| مجموعه | U | EDF miss | RM miss |" if not fa else "| مجموعه | U | خطای EDF | خطای RM |",
      "|---|---:|---:|---:|",
    ]
    for key,_,_ in sets:
        d=DATA[key]
        sections.append(f"| {key[-1].upper()} | {d['utilization']:.4f} | {d['edf']['missed_count']} | {d['rm']['missed_count']} |")
    sections += ["", ("روش: آزادسازی در ابتدای تیک، ممیزی مهلت، انتخاب EDF یا RM و سپس مصرف یک تیک CPU. در تساوی EDF، شاخص پردازه کوچک‌تر انتخاب می‌شود."
                   if fa else
                   "Method: release jobs at the start of each tick, audit expired deadlines, dispatch by EDF or fixed RM priority, then consume one CPU tick. EDF ties are broken by lower task index."),""]
    return "\n".join(sections)

for lang in ("EN","FA"):
    out=ROOT/f"exercise-3/WORKED_SOLUTION_{lang}.md"
    out.write_text(build(lang),encoding="utf-8")
    print(out)
