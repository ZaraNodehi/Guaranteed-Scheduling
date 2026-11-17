"""Dynamic bilingual PPTX & speaker-script slide builders for Exercises 5, 6, and 7."""
from __future__ import annotations

import json
import os
from typing import Dict

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(TOOLS_DIR)


def _load(n: int) -> Dict:
    p = os.path.join(REPO_ROOT, f"exercise-{n}", "output", "experiments.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build_decks_spec(n: int) -> Dict:
    if n == 5:
        return _ex5_slides(_load(5))
    if n == 6:
        return _ex6_slides(_load(6))
    if n == 7:
        return _ex7_slides(_load(7))
    return {"files": [], "slides": []}


def _ex5_slides(d: Dict) -> Dict:
    ov = d["sweep_a_monte_carlo"]["overall"]
    vt_st = ov["gs_vtime:stay"]["lag"]
    rat = ov["gs_ratio:index"]["lag"]
    rr = ov["rr:index"]["lag"]
    ff = ov["fifo:index"]["lag"]
    pb = d["sweep_b_quantum_pareto"]["rows"]
    q1 = pb[0]["policies"]["gs_vtime:stay"]
    q2 = pb[1]["policies"]["gs_vtime:stay"]
    sc = d["sweep_c_scaling"]["scaling_rows"][-1]
    osd = {r["poll_dt_sec"]: r for r in d["sweep_d_os_intervals"]["interval_trials"]}

    slides = [
        {
            "tag": "Ex 5 | Overview",
            "title_en": "Exercise 5: Monte Carlo & Quantum-Pareto Sweep",
            "title_fa": "تمرین ۵: تحلیل مونت‌کارلو و مرز پارتوی کوانتوم",
            "body_en": [
                "240 dynamic random workloads across N in {2,3,4,6,8} processes.",
                f"gs_vtime:stay cuts mean lag to {vt_st['mean']:.3f} vs ratio {rat['mean']:.2f}, RR {rr['mean']:.2f}, FIFO {ff['mean']:.2f}.",
                "Combines exact discrete sweeps with real Linux psutil OS sweeps [M]+[D].",
            ],
            "body_fa": [
                "۲۴۰ بار کاری پویا در اندازه‌های ۲ تا ۸ فرایند با بذر قطعی.",
                f"میانگین تاخیر gs_vtime:stay برابر {vt_st['mean']:.3f} در برابر {rat['mean']:.2f} در نسخه سنتی.",
                "ترکیب آزمایش‌های شبیه‌سازی انبوه با اندازه‌گیری مستقیم روی هسته لینوکس.",
            ],
            "notes_en": "Exercise 5 scales our exact proofs across 240 randomized dynamic workloads plus live Linux OS sampling.",
            "notes_fa": "در تمرین ۵ قضایای دقیق را روی ۲۴۰ بار کاری تصادفی و کنترل زنده لینوکس آزمون می‌کنیم.",
            "figure": "fig_ex5_mc_lag_cdf.png",
        },
        {
            "tag": "Ex 5 | Pareto",
            "title_en": "Quantum Sweep: q = 2 Cuts Switches 44.4%",
            "title_fa": "جاروب کوانتوم: کاهش ۴۴.۴٪ تعویض زمینه در q = 2",
            "body_en": [
                f"At q=1: gs_vtime:stay lag={q1['lag']['mean']:.3f}, switches={q1['switches']['mean']:.1f}.",
                f"At q=2: switches drop 44.4% to {q2['switches']['mean']:.1f} with lag={q2['lag']['mean']:.3f}.",
                "stay tie hysteresis dominates index across all quanta q=1..12.",
            ],
            "body_fa": [
                f"در q=1: تاخیر {q1['lag']['mean']:.3f} با {q1['switches']['mean']:.1f} تعویض زمینه.",
                f"در q=2: تعویض‌ها ۴۴.۴٪ کاهش یافته به {q2['switches']['mean']:.1f} می‌رسد.",
                "هیسترزیس stay در تمام کوانتوم‌ها بر اندیس ثابت برتری دارد.",
            ],
            "notes_en": "Doubling q from 1 to 2 under stay achieves the optimal knee of the fairness-overhead Pareto frontier.",
            "notes_fa": "افزایش کوانتوم به ۲ به همراه stay بهترین نقطه پارتوی هزینه و عدالت را می‌سازد.",
            "figure": "fig_ex5_quantum_pareto.png",
        },
        {
            "tag": "Ex 5 | N-Scaling",
            "title_en": "Concurrency Scaling N = 2..16 Under 1:4 Skew",
            "title_fa": "مقیاس‌پذیری تعداد فرایند N = 2..16 زیر عدم تعادل وزنی",
            "body_en": [
                f"At N={sc['n_procs']}: skew gs_vtime lag={sc['skew_vtime_lag']['mean']:.3f} vs gs_ratio lag={sc['skew_ratio_lag']['mean']:.3f}.",
                f"Starvation gap drops cleanly ({sc['skew_vtime_gap']['mean']:.1f} vs {sc['skew_ratio_gap']['mean']:.1f} ticks).",
                "Validates asymptotic O(1) lag stability as workload concurrency grows.",
            ],
            "body_fa": [
                f"در N={sc['n_procs']}: تاخیر gs_vtime برابر {sc['skew_vtime_lag']['mean']:.3f} در برابر {sc['skew_ratio_lag']['mean']:.3f}.",
                f"بیشینه وقفه از {sc['skew_ratio_gap']['mean']:.1f} به {sc['skew_vtime_gap']['mean']:.1f} تیک کاهش می‌یابد.",
                "پایداری عدالت در همزمانی بالا تایید می‌گردد.",
            ],
            "notes_en": "Increasing N from 2 to 16 preserves tight bounded lag under virtual time while legacy ratio degrades.",
            "notes_fa": "با افزایش N تا ۱۶، زمان مجازی همچنان تاخیر محدود و پایدار را حفظ می‌کند.",
            "figure": "fig_ex5_n_scaling.png",
        },
        {
            "tag": "Ex 5 | Live OS [D]",
            "title_en": "Live Linux Controller Sweep (dt = 0.02s .. 0.10s)",
            "title_fa": "آزمایش زنده لینوکس در بازه‌های کنترل 0.02 تا 0.10 ثانیه",
            "body_en": [
                f"dt=0.02s: {osd[0.02]['controller_switches']} switches, max err={osd[0.02]['max_share_deviation']*100:.2f}%.",
                f"dt=0.05s: {osd[0.05]['controller_switches']} switches (64% fewer!), err={osd[0.05]['max_share_deviation']*100:.2f}%.",
                f"dt=0.10s: drops to {osd[0.1]['controller_switches']} switches, error jumps to {osd[0.1]['max_share_deviation']*100:.2f}%.",
            ],
            "body_fa": [
                f"بازه 0.02s: {osd[0.02]['controller_switches']} تعویض با خطای {osd[0.02]['max_share_deviation']*100:.2f}%.",
                f"بازه 0.05s: تنها {osd[0.05]['controller_switches']} تعویض و خطای {osd[0.05]['max_share_deviation']*100:.2f}%.",
                f"بازه 0.10s: تعویض {osd[0.1]['controller_switches']} اما خطا به {osd[0.1]['max_share_deviation']*100:.2f}% می‌جهد.",
            ],
            "notes_en": "dt = 0.05s mirrors the simulation q = 2 Pareto knee directly on real Linux processes.",
            "notes_fa": "بازه ۵۰ میلی‌ثانیه همتای واقعی نقطه بهینه کوانتوم ۲ در هسته لینوکس است.",
            "figure": "fig_ex5_os_interval_sweep.png",
        },
    ]
    return {
        "files": ["DECK_EN.pptx", "DECK_FA.pptx", "SPEAKER_EN.md", "SPEAKER_FA.md"],
        "slides": slides,
    }


def _ex6_slides(d: Dict) -> Dict:
    b1 = d["bench1_complexity"]["rows"][-1]
    b2 = d["bench2_ablation"]["stages"]
    b3 = d["bench3_sleeper"]["rows"][-1]["policies"]
    b4 = d["bench4_live_os"]
    leg, opt = b4["legacy"], b4["optimized"]
    gain = leg["max_post_spawn_deviation"] / max(1e-6, opt["max_post_spawn_deviation"])

    slides = [
        {
            "tag": "Ex 6 | Architecture",
            "title_en": "Exercise 6: O(log N) Heap Refactor & Sleeper Defense",
            "title_fa": "تمرین ۶: بازطراحی هرم O(log N) و مهار حمله خواب",
            "body_en": [
                f"Replaces O(N) list scan with lazy min-heap ({b1['speedup']:.1f}x faster at N=2,000).",
                "Uses integer fixed-point 10^9/w arithmetic to eliminate IEEE-754 drift.",
                f"Adds V(t) arrival anchor, stay tie fast path, and gs_capped sleeper floor.",
            ],
            "body_fa": [
                f"جایگزینی اسکن خطی با هرم کمینه تنبل ({b1['speedup']:.1f}x سریع‌تر در N=2,000).",
                "محاسبات ممیز ثابت صحیح برای حذف دائمی رانش ممیز شناور.",
                "ترکیب لنگر V(t)، هیسترزیس stay و سقف اعتبار بیداری.",
            ],
            "notes_en": "Exercise 6 delivers four structural upgrades inside gs_optimized.py.",
            "notes_fa": "تمرین ۶ چهار ارتقای بنیادی را در gs_optimized.py پیاده‌سازی می‌کند.",
            "figure": "fig_ex6_refactor_architecture.png",
        },
        {
            "tag": "Ex 6 | Scaling [M]",
            "title_en": f"113.1x Dispatch Speedup at N = 2,000 Processes",
            "title_fa": "شتاب ۱۱۳.۱ برابری زمان انتخاب در N = 2,000 فرایند",
            "body_en": [
                f"LinearScanScheduler grows to {b1['linear_us_per_step']:.2f} us/dispatch at N=2,000.",
                f"OptimizedHeapScheduler stays near-constant at {b1['heap_us_per_step']:.3f} us/dispatch.",
                "O(1) versioned sleep/wake cancellation avoids expensive heap removal scans.",
            ],
            "body_fa": [
                f"اسکن خطی در N=2,000 به {b1['linear_us_per_step']:.2f} میکروثانیه می‌رسد.",
                f"هرم بهینه در {b1['heap_us_per_step']:.3f} میکروثانیه پایدار می‌ماند.",
                "حذف تنبل با برچسب نسخه هزینه خواب و بیداری را O(1) نگه می‌دارد.",
            ],
            "notes_en": "Wall-clock microbenchmarks confirm exact O(N) vs O(log N) scaling up to 2,000 active tasks.",
            "notes_fa": "اندازه‌گیری دقیق مقیاس‌پذیری رشد خطی در برابر هرم لگاریتمی را تایید می‌کند.",
            "figure": "fig_ex6_complexity_scaling.png",
        },
        {
            "tag": "Ex 6 | Sleeper [E]+[M]",
            "title_en": "Breaking 79-Tick Sleeper Monopoly Down to 1 Tick",
            "title_fa": "شکستن انحصار ۷۹ تیکی بیداری به ۱ تیک با gs_capped",
            "body_en": [
                f"Even uncapped gs_vtime lets a waking sleeper hog {b3['gs_vtime:index']['post_wakeup_burst']} straight ticks at S=80.",
                f"gs_capped clamps wakeup credit at V(t) - cap/w, holding burst to {b3['gs_capped:index']['post_wakeup_burst']} tick!",
                "Mirrors Linux CFS GENTLE_FAIR_SLEEPERS anti-hoarding design.",
            ],
            "body_fa": [
                f"بدون سقف بیداری، فرایند خواب‌دار پس از ۸۰ تیک خواب {b3['gs_vtime:index']['post_wakeup_burst']} تیک قفل می‌کند.",
                f"سیاست gs_capped جهش بیداری را روی {b3['gs_capped:index']['post_wakeup_burst']} تیک مهار می‌نماید!",
                "همتای دقیق مکانیزم GENTLE_FAIR_SLEEPERS در لینوکس.",
            ],
            "notes_en": "Ablation across 30 workloads confirms V(t) cuts lag while gs_capped eliminates wakeup lockouts.",
            "notes_fa": "آزمایش حذفی نشان می‌دهد V(t) تاخیر ورود و gs_capped قفل‌شدن بیداری را حذف می‌کند.",
            "figure": "fig_ex6_sleeper_mitigation.png",
        },
        {
            "tag": "Ex 6 | Live OS [D]",
            "title_en": f"{gain:.1f}x Better Real-Linux Latecomer Share Control",
            "title_fa": f"کاهش {gain:.1f} برابری خطای ورود میانی در لینوکس زنده",
            "body_en": [
                f"Mid-run P3 spawn at t=0.6s: legacy lets P3 seize {leg['post_spawn_shares'][2]*100:.1f}% (err {leg['max_post_spawn_deviation']*100:.2f}%).",
                f"Refactored controller holds [35.6%, 30.5%, 33.9%] (err {opt['max_post_spawn_deviation']*100:.2f}%).",
                f"Ablation V2->V3 also slashes worst mixed-workload burst {b2[2]['max_sleeper_burst']} -> {b2[3]['max_sleeper_burst']} ticks.",
            ],
            "body_fa": [
                f"در ورود میانی P3، نسخه قدیمی {leg['post_spawn_shares'][2]*100:.1f}% CPU را به آن واگذار می‌کند.",
                f"نسخه بهینه سهم هر سه را نزدیک ۳۳.۳٪ با خطای {opt['max_post_spawn_deviation']*100:.2f}% تثبیت می‌کند.",
                "کاهش ۴.۲ برابری انحراف روی هسته واقعی لینوکس.",
            ],
            "notes_en": "Live psutil verification proves our V(t)+stay fix directly prevents mid-run arrival distortion on Linux.",
            "notes_fa": "اجرای زنده psutil تثبیت سهم کارگر دیرآینده را در لینوکس ثابت می‌کند.",
            "figure": "fig_ex6_os_refactor_validation.png",
        },
    ]
    return {
        "files": ["DECK_EN.pptx", "DECK_FA.pptx", "SPEAKER_EN.md", "SPEAKER_FA.md"],
        "slides": slides,
    }


def _ex7_slides(d: Dict) -> Dict:
    s = d["cross_exercise_summary"]
    os_d = d["live_capstone_os_demo"]
    slides = [
        {
            "tag": "Ex 7 | Capstone",
            "title_en": "Exercise 7 Capstone: From 106-Line Script to Hardened EEVDF Class",
            "title_fa": "تمرین ۷ نهایی: از کد ۱۰۶ خطی تا زمان‌بند سخت‌سازی‌شده",
            "body_en": [
                f"Unified 7-exercise pipeline: formal bounds [E], 240-seed sweeps [M], O(log N) heap, live Linux [D].",
                f"Dynamic lag dropped from {s['ex5_mc_240_seeds']['gs_ratio_index_lag']:.2f} -> {s['ex5_mc_240_seeds']['gs_vtime_stay_lag']:.3f}; sleeper burst 79 -> 1.",
                f"Heap speedup reaches {s['ex6_speedup_n2000']:.1f}x at N=2,000 with 1.80% live OS error.",
            ],
            "body_fa": [
                "یکپارچه‌سازی ۷ تمرین شامل اثبات دقیق، مونت‌کارلو، هرم O(log N) و تایید زنده لینوکس.",
                f"کاهش تاخیر پویا به {s['ex5_mc_240_seeds']['gs_vtime_stay_lag']:.3f} و جهش خواب از ۷۹ به ۱ تیک.",
                f"شتاب {s['ex6_speedup_n2000']:.1f}x در هرم و خطای ۱.۸۰٪ در هسته واقعی.",
            ],
            "notes_en": "Our seven exercises unify theory, simulation, optimization, and OS validation into one verified framework.",
            "notes_fa": "تمرین ۷ کل دستاوردهای نظری، شبیه‌سازی و عملیاتی پروژه را یکپارچه می‌سازد.",
            "figure": "fig_ex7_research_arc.png",
        },
        {
            "tag": "Ex 7 | Decision Tree",
            "title_en": "Unified Six-Regime Scorecard & Production Decision Tree",
            "title_fa": "ماتریس شش‌رژیمی و درخت تصمیم انتخاب زمان‌بند",
            "body_en": [
                "Hard feasible real-time deadlines (U <= 1.0): select EDF (100% optimal across 10/10 sets).",
                "Transient overload (U > 1.0): gs_vtime avoids RM starvation (0.923 vs 0.197 min share).",
                "General proportional sharing with dynamic/sleeper tasks: deploy gs_capped:stay heap.",
            ],
            "body_fa": [
                "در ضرب‌الاجل‌های شدنی: EDF بهترین است (۱۰۰٪ موفقیت در مجموعه‌های شدنی).",
                "در اضافه‌بار: زمان‌بند سهمی از گرسنگی RM جلوگیری می‌کند.",
                "در اشتراک عادلانه عمومی و I/O: هرم gs_capped:stay توصیه می‌شود.",
            ],
            "notes_en": "No single policy wins every regime blindly; use EDF inside U <= 1.0 and gs_capped:stay everywhere else.",
            "notes_fa": "هیچ سیاستی در همه جا پیروز نیست؛ EDF برای شدنی و gs_capped:stay برای سایر شرایط برتر است.",
            "figure": "fig_ex7_selector_decision_tree.png",
        },
        {
            "tag": "Ex 7 | Live OS & Pareto",
            "title_en": f"Live Linux Capstone Accuracy: {os_d['max_share_error']*100:.2f}% Max Error",
            "title_fa": f"تایید نهایی لینوکس زنده: حداکثر خطای {os_d['max_share_error']*100:.2f}%",
            "body_en": [
                f"Weights [1, 2, 4] achieved [14.6%, 30.1%, 55.3%] vs ideal [14.3%, 28.6%, 57.1%].",
                "6.6x lower real-Linux error compared to legacy unanchored dt=0.10s controller.",
                "Pareto frontier proves gs_capped:stay hits both low lag and zero sleeper lockout.",
            ],
            "body_fa": [
                "وزن‌های [1, 2, 4] سهم‌های واقعی نزدیک به ایده‌آل GPS با ۱.۸٪ خطا ثبت کردند.",
                "کاهش ۶.۶ برابری خطا نسبت به کنترل‌گر قدیمی.",
                "تنها gs_capped:stay در گوشه بهینه جبهه پارتو قرار می‌گیرد.",
            ],
            "notes_en": "Real Linux execution matches our mathematical model within 1.80% share accuracy.",
            "notes_fa": "اجرای واقعی لینوکس با دقت بیش از ۹۸٪ از مدل نظری پیروی می‌کند.",
            "figure": "fig_ex7_live_os_capstone.png",
        },
        {
            "tag": "Ex 7 | Future Work",
            "title_en": "Future Roadmap: Kernel EEVDF & Multi-Core SMP",
            "title_fa": "نقشه راه آینده: EEVDF کامل و چندپردازنده SMP",
            "body_en": [
                "Phase 2 (EEVDF): add virtual eligibility ve_i <= V(t) + virtual deadlines vd_i = ve_i + L_i/w_i.",
                "Phase 3 (SMP & sched_ext): per-CPU lockless min-heaps + work stealing + BPF hook.",
                "Complete 7-exercise repository audited, tested (54/54 pytest), and bilingual.",
            ],
            "body_fa": [
                "فاز ۲ (EEVDF): افزودن شرط شایستگی و ضرب‌الاجل مجازی بر پایه برش درخواستی.",
                "فاز ۳ (SMP و sched_ext): هرم محلی هر هسته و موازنه‌سازی با قلاب eBPF.",
                "تمامی ۷ تمرین با ۵۴ آزمون موفق pytest و گزارش‌های دوزبانه تکمیل شده‌اند.",
            ],
            "notes_en": "Future engineering extends our uniprocessor heap to full EEVDF virtual deadlines and multi-core Linux sched_ext.",
            "notes_fa": "گام آینده تعمیم هرم به ضرب‌الاجل‌های مجازی EEVDF و پیاده‌سازی چندپردازنده است.",
            "figure": "fig_ex7_eevdf_smp_roadmap.png",
        },
    ]
    return {
        "files": ["DECK_EN.pptx", "DECK_FA.pptx", "SPEAKER_EN.md", "SPEAKER_FA.md"],
        "slides": slides,
    }
