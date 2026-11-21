"""Reproducible Exercise 7 experiments: CPU fairness and dining-resource safety."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
EX7=HERE.parent
ROOT=EX7.parent
OUT=EX7/"output"
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/"core"))
sys.path.insert(0,str(HERE))
from gs_core import Proc, simulate_procs  # noqa: E402
from dining_philosophers import explore_fifo_model, naive_deadlock_witness, run_threaded_stress  # noqa: E402


def gs_cpu_study():
    equal=[Proc(f"P{i}",0,100,weight=1) for i in range(5)]
    weighted=[Proc(f"P{i}",0,100,weight=w) for i,w in enumerate((1,1,2,2,4))]
    eq=simulate_procs(equal,policy="gs_vtime",quantum=1,horizon=100).as_dict(keep_timeline=False)
    wt=simulate_procs(weighted,policy="gs_vtime",quantum=1,horizon=100).as_dict(keep_timeline=False)
    return {
        "equal_weight":eq,
        "weighted":wt,
        "interpretation":"GS distributes CPU among runnable philosophers; it does not allocate forks or remove a circular wait."
    }


def build_deck_spec(model, stress, cpu):
    slides=[
      {
       "tag":"Ex 7 | Problem",
       "title_en":"Exercise 7: Dining Philosophers and Guaranteed Scheduling",
       "title_fa":"تمرین ۷: مسئله فیلسوفان غذاخور و زمان‌بندی تضمینی",
       "body_en":["Five concurrent philosophers share five forks in a ring.","Each philosopher needs two adjacent forks to eat.","The study separates CPU fairness from resource-allocation correctness."],
       "body_fa":["پنج فیلسوف هم‌زمان پنج چنگال حلقه‌ای را به اشتراک می‌گذارند.","هر فیلسوف برای غذاخوردن به دو چنگال مجاور نیاز دارد.","این مطالعه عدالت پردازنده را از درستی تخصیص منابع جدا می‌کند."],
       "notes_en":"Introduce the classic Dining Philosophers problem. Explain that CPU scheduling decides which runnable thread executes, while synchronization decides whether the two required forks can be acquired safely.",
       "notes_fa":"مسئله کلاسیک فیلسوفان غذاخور را معرفی کنید. زمان‌بندی CPU نخ آماده را برای اجرا انتخاب می‌کند، اما همگام‌سازی تعیین می‌کند که دو چنگال لازم چگونه و با چه ایمنی در اختیار آن قرار گیرند.",
       "figure":"fig_ex7_table_topology.png"
      },
      {
       "tag":"Deadlock | Circular wait",
       "title_en":"The Naive Protocol: A Circular Wait",
       "title_fa":"روش ساده: تشکیل چرخه انتظار",
       "body_en":["Each philosopher takes the left fork first.","All five forks can become owned simultaneously.","Every philosopher then waits for the right fork: no transition can release the cycle."],
       "body_fa":["هر فیلسوف ابتدا چنگال سمت چپ را می‌گیرد.","ممکن است هر پنج چنگال هم‌زمان مالک داشته باشند.","همه منتظر چنگال راست می‌مانند و چرخه انتظار شکل می‌گیرد."],
       "notes_en":"Walk through the wait-for cycle P0→P1→P2→P3→P4→P0. This is a resource deadlock. Giving the philosophers more CPU time does not free a fork.",
       "notes_fa":"چرخه انتظار P0 به P1، سپس P2، P3، P4 و بازگشت به P0 را توضیح دهید. این یک بن‌بست منابع است؛ افزایش سهم CPU هیچ چنگالی را آزاد نمی‌کند.",
       "figure":"fig_ex7_wait_for_cycle.png"
      },
      {
       "tag":"GS | CPU fairness",
       "title_en":"What Guaranteed Scheduling Can and Cannot Do",
       "title_fa":"توانایی و محدودیت زمان‌بندی تضمینی",
       "body_en":["Exact virtual-time GS can distribute CPU fairly among runnable philosophers.","A philosopher blocked on a fork is not made runnable by a larger CPU share.","The scheduler cannot replace a resource protocol."],
       "body_fa":["GS با زمان مجازی دقیق می‌تواند CPU را میان فیلسوفان آماده منصفانه تقسیم کند.","فیلسوفی که پشت چنگال مسدود شده با سهم CPU بیشتر آماده اجرا نمی‌شود.","زمان‌بند جایگزین پروتکل تخصیص منابع نیست."],
       "notes_en":"Use the equal and weighted GS experiments. The scheduler is responsible for processor entitlement; the monitor is responsible for fork ownership, deadlock avoidance and admission fairness.",
       "notes_fa":"آزمایش‌های GS با وزن برابر و وزن‌دار را شرح دهید. زمان‌بند مسئول استحقاق CPU است؛ مانیتور مسئول مالکیت چنگال، جلوگیری از بن‌بست و عدالت پذیرش درخواست است.",
       "figure":"fig_ex7_gs_service_shares.png"
      },
      {
       "tag":"Solution | FIFO monitor",
       "title_en":"Solution: Atomic Pair Reservation with a FIFO Monitor",
       "title_fa":"راه‌حل: رزرو اتمی دو چنگال با مانیتور FIFO",
       "body_en":["Every hungry philosopher receives a monotonic ticket.","Only the FIFO head may proceed, and only when both forks are free.","Both forks are reserved in one critical section; no partial ownership is exposed."],
       "body_fa":["هر فیلسوف گرسنه یک بلیت افزایشی دریافت می‌کند.","فقط سر صف FIFO و در صورت آزاد بودن هر دو چنگال اجازه عبور دارد.","هر دو چنگال در یک بخش بحرانی رزرو می‌شوند و مالکیت ناقص شکل نمی‌گیرد."],
       "notes_en":"Describe the monitor condition loop. The guard checks queue-head identity and availability of both forks under one condition lock; then both owner fields change atomically.",
       "notes_fa":"حلقه انتظار مانیتور را توضیح دهید. شرط، هویت سر صف و آزاد بودن هر دو چنگال را زیر یک قفل شرطی بررسی می‌کند؛ سپس مالکیت هر دو چنگال به‌صورت اتمی تغییر می‌کند.",
       "figure":"fig_ex7_fifo_monitor.png"
      },
      {
       "tag":"Proof | Invariants",
       "title_en":"Safety, Deadlock Freedom and Conditional Liveness",
       "title_fa":"ایمنی، نبود بن‌بست و پیشرفت مشروط",
       "body_en":["One owner per fork; no neighboring philosophers eat concurrently.","No philosopher holds one fork while waiting for a second fork.","FIFO prevents repeated bypass; progress assumes meals finish and waiters are scheduled."],
       "body_fa":["هر چنگال یک مالک دارد و دو همسایه هم‌زمان غذا نمی‌خورند.","هیچ فیلسوفی یک چنگال را هنگام انتظار برای چنگال دوم نگه نمی‌دارد.","FIFO مانع سبقت مکرر است؛ پیشرفت مشروط به پایان غذا و زمان‌بندی منتظران است."],
       "notes_en":"Be precise: safety is enforced by atomic ownership, deadlock is prevented by removing hold-and-wait, and starvation resistance follows FIFO under scheduler and finite-meal assumptions.",
       "notes_fa":"دقیق باشید: ایمنی با مالکیت اتمی برقرار می‌شود، بن‌بست با حذف نگه‌داشتن و انتظار رفع می‌شود و مقاومت در برابر گرسنگی با فرض زمان‌بندی منصفانه و پایان محدود وعده‌ها از FIFO حاصل می‌شود.",
       "figure":"fig_ex7_invariants.png"
      },
      {
       "tag":"Verification | Model and threads",
       "title_en":"Independent Verification: State Exploration and Real Threads",
       "title_fa":"راستی‌آزمایی مستقل: فضای حالت و نخ‌های واقعی",
       "body_en":["Naive witness exposes the five-node circular wait.","A finite-state explorer checks reachable states and terminal completion.","Five OS threads execute four meals each; the test audits 20 completions and zero adjacent overlap."],
       "body_fa":["شاهد روش ساده چرخه انتظار پنج‌گرهی را نشان می‌دهد.","مدل‌چکر حالت‌های قابل‌دسترسی و تکمیل نهایی را بررسی می‌کند.","پنج نخ واقعی هرکدام چهار وعده اجرا می‌کنند؛ ۲۰ تکمیل و صفر هم‌پوشانی همسایه ممیزی می‌شود."],
       "notes_en":"Distinguish exhaustive exploration of a bounded abstraction from empirical stress testing of the Python monitor. Neither result should be overstated as a proof about every OS scheduler.",
       "notes_fa":"جست‌وجوی کامل یک مدل محدود را از آزمون تنش تجربی مانیتور پایتون جدا کنید. هیچ‌یک را نباید اثبات رفتار تمام زمان‌بندهای سیستم‌عامل دانست.",
       "figure":"fig_ex7_verification.png"
      },
      {
       "tag":"Conclusion",
       "title_en":"The Correct Answer: Compose Scheduling with Synchronization",
       "title_fa":"نتیجه: ترکیب زمان‌بندی و همگام‌سازی",
       "body_en":["GS provides fair CPU service to runnable philosophers.","A FIFO monitor or resource hierarchy provides safe fork acquisition.","The correct design composes and verifies both layers independently."],
       "body_fa":["GS خدمت CPU منصفانه را به فیلسوفان آماده می‌دهد.","مانیتور FIFO یا سلسله‌مراتب منابع، تصاحب ایمن چنگال را فراهم می‌کند.","طراحی صحیح هر دو لایه را ترکیب و مستقل راستی‌آزمایی می‌کند."],
       "notes_en":"Answer the instructor's question directly: the logic of a fair scheduler applies to CPU allocation, but not as a standalone deadlock solution. Dining Philosophers requires a separate synchronization policy.",
       "notes_fa":"مستقیماً به سؤال استاد پاسخ دهید: منطق زمان‌بند منصفانه برای تخصیص CPU کاربرد دارد، اما به‌تنهایی راه‌حل بن‌بست نیست. مسئله فیلسوفان غذاخور به سیاست همگام‌سازی مستقل نیاز دارد.",
       "figure":"fig_ex7_summary.png"
      }
    ]
    return {
      "files":["PRESENTATION_EN.pptx","PRESENTATION_FA.pptx","SPEAKER_SCRIPT_EN.md","SPEAKER_SCRIPT_FA.md"],
      "slides":slides
    }


def main():
    naive=naive_deadlock_witness(5)
    model=explore_fifo_model(5)
    stress=run_threaded_stress(5,4,0.0002)
    cpu=gs_cpu_study()
    payload={
      "exercise":"Exercise 7",
      "topic":"Dining Philosophers: CPU fairness versus resource safety",
      "naive_deadlock_witness":naive,
      "fifo_model":model,
      "thread_stress":stress,
      "gs_cpu_study":cpu,
      "comparison":{
        "GS_only":"CPU fairness among runnable threads; cannot break fork circular wait.",
        "FIFO_monitor":"Atomic fork-pair reservation with FIFO admission.",
        "assumptions":["Every granted meal eventually ends.","Waiting threads are eventually scheduled and notified.","The model is a fixed ring with two forks per philosopher."]
      }
    }
    payload["decks"]=build_deck_spec(model,stress,cpu)
    out=OUT/"experiments.json"
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({
      "naive_cycle":naive["wait_for_cycle"],
      "model":{k:model[k] for k in ("reachable_states","transitions","unsafe_states","deadlock_states","terminal_states","max_parallel_eaters")},
      "thread_stress":{k:stress[k] for k in ("completed_meals","completions_by_philosopher","safety_violations","passed","max_parallel_eaters")},
      "gs_equal_jain":cpu["equal_weight"]["jain_fairness"],
      "gs_weighted_jain":cpu["weighted"]["jain_fairness"],
      "output":str(out)
    },indent=2))


if __name__=="__main__":
    main()
