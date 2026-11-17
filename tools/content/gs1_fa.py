"""Persian report content for Exercise 1: Introduction to Guaranteed Scheduling."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)

import report_kit as rk  # noqa: E402
from content import gs1_data as gd  # noqa: E402


def build() -> rk.Report:
    d = gd.load()
    osb = d["os_subprocess_benchmark"]
    env_w = d["exhaustive_tie_check"]["weighted_envelope"]
    env_e = d["exhaustive_tie_check"]["equal_envelope"]
    st_r = d["dynamic_arrival_check"]["starve_gs_ratio"]
    st_v = d["dynamic_arrival_check"]["starve_gs_vtime"]
    st_e = d["dynamic_arrival_check"]["starve_gs_entitled"]
    runs = d["baseline"]["runs"]
    qrows = d["quantum_sweep"]["rows"]
    gs_q1 = next(r for r in qrows if r["policy"] == "gs_vtime" and r["quantum"] == 1)
    gs_q16 = next(r for r in qrows if r["policy"] == "gs_vtime" and r["quantum"] == 16)
    rr_q1 = next(r for r in qrows if r["policy"] == "rr" and r["quantum"] == 1)
    dyn_r = d["dynamic_arrival_check"]["dyn_t12_gs_ratio"]
    dyn_v = d["dynamic_arrival_check"]["dyn_t12_gs_vtime"]
    dyn_gap = dyn_r["per_proc"]["P1"]["max_starve_gap"]
    dyn_v_gap = dyn_v["per_proc"]["P1"]["max_starve_gap"]
    p2_os = osb["os_normalized_runtime"]["P2"]
    p2_sim = osb["sim_normalized_turnaround"]["P2"]
    p3_os = osb["os_normalized_runtime"]["P3"]
    p3_sim = osb["sim_normalized_turnaround"]["P3"]
    all_cpu_vals = [v for tr in osb["trials"] for v in tr["cpu_used_sec"].values()]
    cpu_min, cpu_max = min(all_cpu_vals), max(all_cpu_vals)
    sw_pct = 100.0 * (env_e["max_context_switches"] - env_e["min_context_switches"]) / env_e["max_context_switches"]

    rep = rk.Report(
        title="تمرین ۱: معرفی کامل الگوریتم زمان‌بندی تضمین‌شده (Guaranteed Scheduling)",
        subtitle="مدل زمانِ صحیح و کسرِ دقیق، تحلیل تاخیر خدمت، بررسی جامع و راستی‌آزمایی سیستم‌عاملی",
        lang="fa",
        rtl=True,
        cover_meta=[
            ("مخزن", "ZaraNodehi/Guaranteed-Scheduling"),
            ("تمرین", "تمرین ۱ — مبانی الگوریتم، تعاریف صوری و نخستین اندازه‌گیری‌ها"),
            ("ابزارها", "[E] بررسی جامع فضای حالت | [M] شبیه‌ساز زمان‌صحیح و بنچمارک واقعی | [D] تحلیل ناهماهنگی‌ها"),
            ("منبع داده‌ها", "exercise-1/output/experiments.json (تولید خودکار بدون عدد دستی)"),
        ],
    )

    # Page 1: Cover
    rep.page(rk.cover(rep.cover_meta))

    # Page 2: Table of contents
    rep.page(rk.toc())

    # Page 3: Executive Overview & Research Questions
    rep.page(
        rk.ptitle("۱. چشم‌انداز اجرایی و پرسش‌های پژوهشی"),
        rk.para(
            "زمان‌بندی تضمین‌شده (Guaranteed Scheduling یا به اختصار GS) یک روش تخصیص "
            "سهم متناسب CPU است که نخستین بار توسط اندرو تاننباوم معرفی شد تا به هر "
            "فرایند هم‌روند تضمین کند در گذر زمان دقیقاً متناسب با وزنش سهم پردازنده "
            "دریافت می‌کند. برخلاف زمان‌بندهای اولویت‌ثابت که ممکن است فرایندهای کم‌اولویت "
            "را دچار گرسنگی کنند، GS در هر گام فرایندی را برمی‌گزیند که از سهم وعده‌داده‌شده "
            "خود عقب‌تر مانده است."
        ),
        rk.h1("پرسش‌های اصلی تمرین ۱"),
        rk.bullets([
            "**تعریف صوری [E]:** نسبت تضمین R_i(t) = A_i(t)/E_i(t) چه رابطه‌ای با مدل پیوسته GPS و قانون `used / weight` در فایل `GuaranteedScheduling.py` دارد؟",
            "**مبادله کوانتوم [M]:** اندازه کوانتوم q چطور مرز بهینه بین تاخیر خدمت |A_i(t) - E_i(t)| و هزینه تعویض زمینه را تعیین می‌کند؟",
            "**کران تساوی‌شکنی [E]:** آیا در تمام مسیرهای ممکن تساوی‌شکنی، تاخیر تضمینی تغییر می‌کند یا فقط شمار تعویض زمینه‌ها عوض می‌شود؟",
            "**ورود پویا [E]+[D]:** در چه شرایطی معیار `used / weight` دچار نقض عدالت شده و شاهد گرسنگی تولید می‌کند؟",
            "**راستی‌آزمایی واقعی [M]+[D]:** اجرای واقعی `GuaranteedScheduling.py` روی لینوکس با `psutil` چقدر با شبیه‌ساز دقیق مطابقت دارد؟",
        ], numbered=True),
        rk.note(
            "هیچ عددی در این گزارش با دست نوشته نشده است؛ همه مقادیر در لحظه ساخت از "
            "`exercise-1/output/experiments.json` خوانده می‌شوند و هر ادعا با برچسب‌های "
            "[E] (بررسی جامع)، [M] (اندازه‌گیری) یا [D] (ناهماهنگی) مشخص شده است.",
            caption="قرارداد علمی و مهندسی گزارش",
        ),
    )

    # Page 4: Two-Instrument Methodology
    rep.page(
        rk.ptitle("۲. روش‌شناسی دوابزاری و حسابان دقیق کسری"),
        rk.para(
            "یک اصل سخت در این پروژه جداسازی کامل ابزار بررسی درستی از ابزار اندازه‌گیری "
            "عملکرد است. اینکه یک زمان‌بند در چند اجرای محدود خطا ندهد هرگز دلیل درستی کلی نیست؛ "
            "از سوی دیگر، جستجوی جامع به تنهایی تفاوت هزینه تعویض زمینه را گزارش نمی‌کند."
        ),
        rk.kv([
            ["ابزار", "نقش، سازوکار دقیق و خروجی"],
            ["[E] بررسی‌کننده جامع", "تمام شاخه‌های تساوی‌شکنی (`exhaustive_tie_envelope`) و بازه ورودهای پویا (`find_starvation_witness`) را با حساب `Fraction` بدون خطای اعشاری پیمایش می‌کند و شاهد نقض را برمی‌گرداند."],
            ["[M] شبیه‌ساز گسسته", "شبیه‌ساز قطعی زمان‌صحیح (`simulate_procs`) که خدمت تجمعی `A_i(t)`، مرجع GPS `E_i(t)`، تاخیر، شاخص جین، تعویض زمینه و زمان چرخش را اندازه می‌گیرد."],
            ["[M] بنچمارک واقعی سیستم‌عامل", f"اجرای تکرارشونده ({osb['num_trials']} آزمایش مستقل) روی پردازش‌های واقعی لینوکس با حلقه دقیق `GuaranteedScheduling.py` (`psutil.suspend/resume`) و گزارش میانه و دامنه میان‌چارکی."],
            ["[D] تحلیل ناهماهنگی", "اختلاف‌های بین مدل پیوسته، شبیه‌ساز گسسته و هسته سیستم‌عامل (تاخیر راه‌اندازی، کوانتیزاسیون ۱۰ میلی‌ثانیه‌ای و گرسنگی تازه‌وارد) را واکاوی می‌کند."],
        ], caption="تفکیک دقیق ابزارهای راستی‌آزمایی، اندازه‌گیری و تحلیل ناهماهنگی"),
    )

    # Page 5: Three-Model Architecture Diagram
    rep.page(
        rk.ptitle("۳. معماری سه‌لایه: نظریه پیوسته، شبیه‌ساز و کد سیستم‌عامل"),
        rk.para(
            "شکل ۱ ارتباط میان سه سطح مدل‌سازی در تمرین ۱ را نشان می‌دهد: مرجع پیوسته GPS، "
            "هسته قطعی زمان‌صحیح (`gs_core.py`) و پیاده‌سازی فضای کاربر در `GuaranteedScheduling.py`."
        ),
        rk.image("fig_ex1_architecture.png", width_cm=15.4,
                 caption="معماری سه‌لایه زمان‌بندی تضمین‌شده از نظریه سیال GPS تا کنترلر فضای کاربر."),
        rk.bullets([
            "**مدل سیال GPS:** مرجع ایده‌آل که هر فرایند فعال در هر لحظه نرخ دقیق w_i / sum(w_j) و تاخیر صفر دارد.",
            "**هسته gs_core:** اجرا را به کوانتوم‌های صحیح q >= 1 گسسته می‌کند ولی ردیابی زمان مجازی را با کسرهای دقیق انجام می‌دهد.",
            "**فایل GuaranteedScheduling.py:** سهم‌دهی واقعی را با سیگنال‌های توقف/ادامه `psutil` اعمال می‌کند و ناگزیر با تاخیر سیستم‌عامل مواجه است.",
        ]),
    )

    # Page 6: Formal Mathematical Definition
    rep.page(
        rk.ptitle("۴. مدل صوری: زمان استحقاقی، نسبت تضمین و تاخیر خدمت"),
        rk.para(
            "فرض کنید n فرایند مستقل با زمان ورود صحیح a_i >= 0، کار مورد نیاز W_i > 0 "
            "و وزن صحیح w_i > 0 داریم. اگر A(t) مجموعه فرایندهای آماده در لحظه t باشد، "
            "سهم لحظه‌ای، استحقاق تجمعی در GPS، نسبت تضمین و تاخیر علامت‌دار چنین تعریف می‌شوند:"
        ),
        rk.formula(
            "phi_i(t) = w_i / sum_{j in A(t)} w_j\n"
            "E_i^GPS(t) = integral_{a_i}^{min(t, f_i)} phi_i(tau) d tau\n"
            "R_i(t) = A_i(t) / E_i(t)        L_i(t) = A_i(t) - E_i^GPS(t)",
            caption="روابط بنیادین سهم لحظه‌ای، استحقاق GPS، نسبت تضمین و تاخیر خدمت",
        ),
        rk.h1("ویژگی‌های هم‌ارزی و بقای تاخیر [E]"),
        rk.bullets([
            "**ورود هم‌زمان (a_i = 0):** تا زمانی که فرایندها فعال‌اند، E_i(t) = w_i * V(t) است و V(t) برای همه مشترک است؛ پس رتبه‌بندی بر اساس A_i(t)/E_i(t) دقیقاً هم‌رتبه با `A_i(t) / w_i` (`gs_ratio`) می‌شود.",
            "**قانون بقای تاخیر صفرجمع:** در زمان‌بند کارنگهدار بدون بیکاری اجباری، sum_i A_i(t) = sum_i E_i^GPS(t) = t و بنابراین sum_i L_i(t) = 0 در هر لحظه t برقرار است.",
            "**کران تاخیر شبه پارخ-گالگر:** در ورود هم‌زمان با q = 1، تاخیر در بار پایه از 1 واحد فراتر نمی‌رود و با افزایش q خطی رشد می‌کند.",
        ]),
    )

    # Page 7: Algorithm Pseudocode & Flowchart
    rep.page(
        rk.ptitle("۵. شبه‌کد الگوریتم و فلوچارت حلقه توزیع"),
        rk.para(
            "الگوریتم GS در ابتدای هر بازه کوانتوم امتیاز هر فرایند آماده را بازمحاسبه کرده "
            "و کمترین امتیاز را برای اجرا انتخاب می‌کند. شکل ۲ فلوچارت کامل این چرخه را نمایش می‌دهد."
        ),
        rk.image("fig_ex1_flowchart.png", width_cm=15.0,
                 caption="فلوچارت گام‌به‌گام تصمیم‌گیری و به‌روزرسانی حساب در زمان‌بندی تضمین‌شده."),
        rk.code([
            "while any process has remaining work > 0:",
            "    ready = [p for p in procs if p.arrival <= t and p.rem > 0]",
            "    if not ready: t += 1; continue",
            "    j = argmin_{i in ready} score(i)   # explicit tie policy",
            "    delta = min(quantum, j.rem)",
            "    run j for delta ticks; j.used += delta; j.rem -= delta",
            "    sys_vtime += delta / sum(p.weight for p in ready)",
            "    t += delta",
        ], caption="شبه‌کد دقیق زمان‌بندی تضمین‌شده با زمان صحیح"),
    )

    # Page 8: Code Walkthrough of GuaranteedScheduling.py
    rep.page(
        rk.ptitle("۶. کالبدشکافی کد اصلی ریپو: GuaranteedScheduling.py"),
        rk.para(
            "اسکریپت موجود در ریشه مخزن (`GuaranteedScheduling.py`) اشتراک وزن‌دار پردازنده "
            "را با `subprocess` و `psutil` در فضای کاربر پیاده‌سازی می‌کند. بررسی خط‌به‌خط حلقه "
            "اصلی، فرض‌های پنهان این پیاده‌سازی را روشن می‌سازد."
        ),
        rk.code([
            "current = min(available, key=lambda p: p[\"used\"] / p[\"weight\"])",
            "before = monitor.cpu_times()",
            "monitor.resume()",
            "try:",
            "    process.wait(timeout=quantum)",
            "    current[\"finished\"] = True",
            "except subprocess.TimeoutExpired:",
            "    monitor.suspend()",
            "    after = monitor.cpu_times()",
            "    current[\"used\"] += after.user + after.system - before.user - before.system",
        ], caption="بخش هسته‌ای انتخاب و اندازه‌گیری زمان CPU در GuaranteedScheduling.py"),
        rk.h1("فرض‌های ساختاری کشف‌شده [E] + [D]"),
        rk.bullets([
            "**فرض شروع هم‌زمان:** همه برنامه‌ها پیش از ورود به حلقه `while` آغاز می‌شوند (`arrival = 0`)، که در این حالت `used / weight` با `A_i / E_i` هم‌جهت است.",
            "**عدم ثبت برش پایانی:** اگر فرایندی پیش از انقضای `timeout` تمام شود، بدون جمع کردن بخش آخر `cpu_times()` به `finished = True` می‌رود (در ادامه کار خللی ندارد ولی جمع کل گزارش را کمی کمتر نشان می‌دهد).",
            "**دقت تیک هسته:** `cpu_times()` بر حسب تیک‌های هسته (معمولاً ۱۰ میلی‌ثانیه در لینوکس) به‌روز می‌شود که در کوانتوم‌های کوچک خطای گردکردن ایجاد می‌کند.",
        ]),
    )

    # Page 9: Baseline Workload & Policy Comparison
    rep.page(
        rk.ptitle("۷. آزمایش پایه: مقایسه سیاست‌ها روی بار وزن‌دار ایستا [M]"),
        rk.para(
            "برای ارزیابی بدون نوفه، بار کاری پایه با ورود هم‌زمان t = 0 تعریف شد: "
            "P1(weight=1, work=4)، P2(weight=2, work=6) و P3(weight=3, work=9) با مجموع ۱۹ واحد کار. "
            "جدول ۲ نتایج شبیه‌سازی تمام سیاست‌ها را مقایسه می‌کند."
        ),
        rk.table(
            ["سیاست", "q", "بیشینه تاخیر (دقیق)", "RMSE تاخیر", "تعویض زمینه", "پیش‌گیری", "میانگین TA", "شاخص جین"],
            gd.baseline_policy_rows(d),
            widths=[3.0, 0.9, 3.0, 1.8, 1.8, 1.9, 1.9, 1.7],
            caption="مقایسه معیارهای پایه بین واریانت‌های GS، راند رابین و FIFO [M]",
        ),
        rk.bullets([
            f"**هم‌ارزی دقیق در ورود هم‌زمان [M]:** سیاست‌های `gs_ratio`، `gs_vtime` و `stride` در q=1 بیشینه تاخیر یکسان `{runs['gs_ratio_q1']['max_abs_lag']:.4f}` (`{runs['gs_ratio_q1']['max_abs_lag_frac']}`) و RMSE برابر `{runs['gs_ratio_q1']['rmse_lag']:.4f}` دارند.",
            f"**برتری بر RR در کوانتوم برابر [M]:** در q=2 و تعداد تعویض یکسان ({runs['gs_ratio_q2']['context_switches']})، `gs_ratio` بیشینه تاخیر را از `{runs['rr_q2']['max_abs_lag']:.2f}` (در RR) به `{runs['gs_ratio_q2']['max_abs_lag']:.2f}` کاهش می‌دهد.",
            f"**ضعف FIFO در عدالت لحظه‌ای [M]:** FIFO کمترین تعویض زمینه ({runs['fifo_q1']['context_switches']}) را دارد اما تاخیر آن به `{runs['fifo_q1']['max_abs_lag']:.2f}` واحد اوج می‌گیرد.",
        ]),
    )

    # Page 10: Baseline Gantt Chart Comparison
    rep.page(
        rk.ptitle("۸. نمودار گانت بار پایه و تحلیل ترتیب اجرا [M]"),
        rk.para(
            "شکل ۳ زمان‌بندی ۱۹ تیکی چهار سیاست را به تصویر می‌کشد. با توجه به نسبت وزن ۱:۲:۳، "
            "الگوریتم GS در هر چرخه ۶ تیکی دقیقاً یک تیک به P1، دو تیک به P2 و سه تیک به P3 اختصاص می‌دهد."
        ),
        rk.image("fig_ex1_gantt_baseline.png", width_cm=15.4,
                 caption="نمودار گانت بار پایه برای gs_ratio (q=1 و q=2)، Round Robin و FIFO."),
        rk.bullets([
            "**چرخه تکرارشونده ۶ تیکی (`q=1`):** در بازه `[0, 6)` توالی `[P1, P2, P3, P3, P2, P3]` اجرا می‌شود و در نقاط `t = 6, 12, 18` همه نسبت‌ها دقیقاً برابر می‌شوند.",
            "**ناآگاهی RR از وزن (`q=2`):** راند رابین به وزن ۳ توجهی ندارد و باعث تاخیر تجمعی و دم طولانی برای P3 در `[14, 19)` می‌شود.",
        ]),
    )

    # Page 11: Per-Process Baseline Breakdown
    rep.page(
        rk.ptitle("۹. تحلیل تفکیکی هر فرایند و تطابق زمان اتمام با GPS [M]"),
        rk.para(
            "جدول ۳ شاخص‌های هر فرایند را برای `gs_ratio (q=1)` گزارش می‌کند. توجه کنید که "
            "از آنجا که `work / weight` برای P2 و P3 هر دو برابر ۳ و برای P1 برابر ۴ است، "
            "فرایندهای P2 و P3 باید زودتر و هم‌زمان در مدل GPS به پایان برسند."
        ),
        rk.table(
            ["فرایند", "وزن", "کار", "شروع", "پایان", "TA", "انتظار", "استحقاق GPS", "بیشینه تاخیر"],
            gd.baseline_proc_rows(d, "gs_ratio_q1"),
            widths=[1.6, 1.1, 1.2, 1.3, 1.4, 1.3, 1.5, 3.6, 2.4],
            caption="معیارهای تفکیکی فرایندها در gs_ratio (q=1) روی بار پایه [M]",
        ),
        rk.h1("تطابق دقیق نقاط پایان گسسته با مدل سیال GPS"),
        rk.para(
            f"در GPS پیوسته، هر دو فرایند P2 و P3 در لحظه `t = {d['baseline']['gps_finish_times']['P2']:.0f}.0` "
            "به اتمام می‌رسند و P1 آخرین واحد کار خود را به تنهایی تا `t = 19` کامل می‌کند. زمان‌بند "
            "گسسته GS دقیقاً همین نقاط پایان (`18` و `19`) را بازتولید کرده است."
        ),
    )

    # Page 12: Step-by-Step Trajectory Table (t = 0..9)
    rep.page(
        rk.ptitle("۱۰. ردگیری تیک‌به‌تیک خدمت تجمعی در برابر GPS (تیک ۰ تا ۹) [M]"),
        rk.para(
            "جدول ۴ مقدار دقیق خدمت واقعی A_i(t)، استحقاق سیال E_i(t) و تاخیر L_i(t) را برای "
            "ده تیک نخست نشان می‌دهد. جمع تاخیرهای علامت‌دار در هر سطر دقیقاً صفر است."
        ),
        rk.table(
            ["t", "P1: A / E (Lag)", "P2: A / E (Lag)", "P3: A / E (Lag)"],
            gd.trajectory_rows(d, 0, 10),
            widths=[1.4, 4.8, 4.8, 4.8],
            caption="ردگیری گام‌به‌گام خدمت واقعی در برابر GPS برای t = 0..9 [M]",
        ),
        rk.para(
            "در لحظه `t = 6` فرایند P1 یک واحد (GPS=1.00)، فرایند P2 دو واحد (GPS=2.00) و "
            "P3 سه واحد (GPS=3.00) گرفته‌اند و تاخیر هر سه فرایند هم‌زمان صفر شده است."
        ),
    )

    # Page 13: Trajectory (t = 10..19) + Figure 4
    rep.page(
        rk.ptitle("۱۱. پوش تاخیر علامت‌دار در کل افق اجرا [M]"),
        rk.para(
            "شکل ۴ مسیر کامل `t = 0..19` را نمایش می‌دهد و نشان می‌دهد تاخیر هر سه فرایند "
            "در کل افق درون بازه بسته `[-1, +1]` باقی می‌ماند و در مضارب ۶ به صفر بازمی‌گردد."
        ),
        rk.image("fig_ex1_lag_trajectory.png", width_cm=15.0,
                 caption="خدمت تجمعی در برابر GPS (بالا) و پوش تاخیر علامت‌دار درون [-1, +1] (پایین)."),
        rk.table(
            ["t", "P1: A / E (Lag)", "P2: A / E (Lag)", "P3: A / E (Lag)"],
            gd.trajectory_rows(d, 10, 20),
            widths=[1.4, 4.8, 4.8, 4.8],
            caption="ردگیری گام‌به‌گام خدمت واقعی در برابر GPS برای t = 10..19 [M]",
        ),
    )

    # Page 14: Quantum Sweep Table
    rep.page(
        rk.ptitle("۱۲. جاروب کوانتوم: سنجش حساسیت تاخیر و تعویض زمینه [M]"),
        rk.para(
            "برای بررسی اثر اندازه کوانتوم q در `{1, 2, 4, 8, 16}`، از یک بار کاری ۴فراینده "
            "با کار `[16, 24, 32, 24]` و وزن‌های `[1, 2, 4, 3]` (مجموع ۹۶ تیک) استفاده شد. "
            "جدول ۶ تمام ارقام اندازه‌گیری‌شده را نشان می‌دهد."
        ),
        rk.table(
            ["سیاست", "q", "بیشینه تاخیر", "RMSE", "تعویض", "پیش‌گیری", "میانگین TA", "بدترین TA", "جین"],
            gd.quantum_rows(d),
            widths=[2.1, 0.9, 1.9, 1.6, 1.7, 1.8, 1.9, 1.9, 1.7],
            caption="نتایج جاروب اندازه کوانتوم برای gs_ratio، gs_vtime و Round Robin [M]",
        ),
    )

    # Page 15: Quantum Sweep Plot
    rep.page(
        rk.ptitle("۱۳. مرز پارتو بین عدالت زمانی و سربار تعویض زمینه [M]"),
        rk.para(
            "شکل ۵ رابطه مستقیم اندازه کوانتوم با رشد تاخیر و افت شدید تعویض زمینه را آشکار می‌سازد. "
            f"با افزایش q از 1 به 16، بیشینه تاخیر `gs_vtime` از `{gs_q1['max_abs_lag']:.4f}` به "
            f"`{gs_q16['max_abs_lag']:.4f}` می‌رسد اما تعویض زمینه‌ها از {gs_q1['context_switches']} به "
            f"{gs_q16['context_switches']} سقوط می‌کند."
        ),
        rk.image("fig_ex1_quantum_sweep.png", width_cm=15.4,
                 caption="رشد خطی تاخیر خدمت (چپ) و کاهش شدید تعویض زمینه (راست) با افزایش کوانتوم."),
        rk.bullets([
            f"**برتری چشمگیر GS در کوانتوم کوچک:** در q=1 بیشینه تاخیر GS برابر `{gs_q1['max_abs_lag']:.4f}` و تاخیر RR برابر `{rr_q1['max_abs_lag']:.4f}` است؛ یعنی بیش از ۱۲ برابر عدالت دقیق‌تر با همان تعداد تعویض ({gs_q1['context_switches']}).",
            f"**هم‌گرایی در کوانتوم بزرگ:** در q=16 هر دو سیاست به تاخیر `{gs_q16['max_abs_lag']:.4f}` هم‌گرا می‌شوند زیرا برش‌های بزرگ امکان اعمال وزن را سلب می‌کنند.",
        ]),
    )

    # Page 16: Exhaustive Tie-Breaking Verification [E]
    rep.page(
        rk.ptitle("۱۴. وارسی جامع ناورداهای تساوی‌شکنی در فضای حالت [E]"),
        rk.para(
            "هنگام برابری امتیاز دو فرایند (مثل لحظه t=0 یا وزن‌های یکسان)، روش تساوی‌شکنی وارد عمل می‌شود. "
            "ابزار جامع [E] (`exhaustive_tie_envelope`) تمام مسیرهای مجاز تساوی‌شکنی را روی بار پایه "
            "وزن‌دار و نیز سه‌گانه هم‌وزن `Q1, Q2, Q3 (w=2, work=4)` بررسی کرد."
        ),
        rk.kv([
            ["شاخص وارسی جامع", "کران‌های دقیق به‌دست‌آمده [E]"],
            ["حالت‌ها / برگ‌ها (بار وزن‌دار)", f"{env_w['states']} حالت / {env_w['leaves']} برگ (truncated={env_w['truncated']})"],
            ["بازه بیشینه تاخیر (بار وزن‌دار)", f"[{env_w['best_max_lag']:.4f}, {env_w['worst_max_lag']:.4f}] (کسر {env_w['worst_max_lag_frac']})"],
            ["بازه تعویض زمینه (بار وزن‌دار)", f"[{env_w['min_context_switches']}, {env_w['max_context_switches']}]"],
            ["حالت‌ها / برگ‌ها (بار هم‌وزن)", f"{env_e['states']} حالت / {env_e['leaves']} برگ (truncated={env_e['truncated']})"],
            ["بازه بیشینه تاخیر (بار هم‌وزن)", f"[{env_e['best_max_lag']:.4f}, {env_e['worst_max_lag']:.4f}] (کسر {env_e['worst_max_lag_frac']})"],
            ["بازه تعویض زمینه (بار هم‌وزن)", f"[{env_e['min_context_switches']}, {env_e['max_context_switches']}]"],
        ], caption="کران‌های دقیق به‌دست‌آمده از پیمایش جامع همه مسیرهای تساوی‌شکنی [E]"),
    )

    # Page 17: Tie-Breaker Comparison Table & Chart
    rep.page(
        rk.ptitle("۱۵. مقایسه سیاست‌های تساوی‌شکنی درون کران‌های ثابت‌شده [E]+[M]"),
        rk.para(
            "شکل ۶ و جدول ۸ نشان می‌دهند که تساوی‌شکنی در هیچ‌یک از "
            f"{env_e['leaves']} مسیر ممکن سه‌گانه هم‌وزن، بیشینه تاخیر را تغییر نمی‌دهد "
            f"(`{env_e['worst_max_lag']:.4f}` ثابت)، اما سیاست `stay` تعویض زمینه را از "
            f"{env_e['max_context_switches']} به کران پایین دقیق {env_e['min_context_switches']} کاهش می‌دهد."
        ),
        rk.image("fig_ex1_tie_envelope.png", width_cm=15.0,
                 caption="تطابق تعویض زمینه و بیشینه تاخیر شبیه‌سازی‌شده با کران‌های وارسی جامع [E]."),
        rk.table(
            ["تساوی‌شکن", "بیشینه تاخیر", "تعویض زمینه", "پیش‌گیری", "شاخص جین"],
            gd.tie_rows(d),
            widths=[3.4, 3.0, 3.2, 3.0, 3.0],
            caption="مقایسه شبیه‌سازی تساوی‌شکن‌ها روی سه‌گانه هم‌وزن Q1, Q2, Q3 [M]",
        ),
    )

    # Page 18: Discrepancy 1 — Dynamic Arrival Starvation Witness [E] + [D]
    rep.page(
        rk.ptitle("۱۶. ناهماهنگی کلیدی [D]: شاهد گرسنگی تازه‌وارد در gs_ratio"),
        rk.para(
            "آیا قانون `min(used / weight)` در `GuaranteedScheduling.py` با ورود فرایندهای جدید در "
            "وسط اجرا همچنان ایمن است؟ با ابزار جامع `find_starvation_witness` ورودهای پویا را در "
            "بازه `t_arr in [2..20]` آزمودیم."
        ),
        rk.kv([
            ["سیاست", "نتیجه وارسی گرسنگی [E]"],
            ["gs_ratio (used / weight)", f"نقض شد={st_r['violated']} | موارد بررسی={st_r['checked_arrivals']} | بدترین وقفه P1 = {st_r['worst_p1_starve_gap']} تیک"],
            ["gs_entitled (A_i / E_i)", f"نقض شد={st_e['violated']} | موارد بررسی={st_e['checked_arrivals']} | بدترین وقفه P1 = {st_e['worst_p1_starve_gap']} تیک"],
            ["gs_vtime (لنگر زمان مجازی)", f"نقض شد={st_v['violated']} | موارد بررسی={st_v['checked_arrivals']} | بدترین وقفه P1 = {st_v['worst_p1_starve_gap']} تیک"],
        ], caption="آزمون جامع آزادی از گرسنگی هنگام ورود پویا [E]"),
        rk.note(
            "در `gs_ratio` فرایند تازه‌وارد با `used = 0` وارد صف می‌شود، در حالی که P1 قبلاً "
            "`used = t_arr` اندوخته است. بنابراین تازه‌وارد تا رسیدن نسبتش به P1 کل پردازنده را قبضه می‌کند.",
            caption="ریشه ریاضی شاهد گرسنگی [D]",
        ),
    )

    # Page 19: Latecomer Starvation Gantt & Table
    rep.page(
        rk.ptitle("۱۷. شاهد عینی نقض در لحظه ورود t = 12 [E]+[D]"),
        rk.para(
            f"شکل ۷ نمونه نقض عینی در `t_arr = 12` را نمایش می‌دهد (`P1(arr=0, work=28, w=2)`، "
            f"`P2(arr=12, work=16, w=1)`). در `gs_ratio` فرایند P1 به مدت {dyn_gap} تیک پیاپی "
            f"(`t = 12..{12 + dyn_gap}`) کاملاً متوقف می‌شود، حال آنکه `gs_vtime` با حداکثر وقفه "
            f"{dyn_v_gap} تیک فوراً سهم ۲ به ۱ را حفظ می‌کند."
        ),
        rk.image("fig_ex1_latecomer_teaser.png", width_cm=15.4,
                 caption="شاهد عینی گرسنگی P1 هنگام ورود P2 در t=12 تحت gs_ratio در برابر gs_vtime."),
        rk.table(
            ["سیاست", "بیشترین وقفه P1", "پایان P1", "پایان P2", "بیشینه تاخیر", "شاخص جین"],
            gd.dynamic_rows(d),
            widths=[3.6, 2.4, 2.2, 2.2, 2.6, 2.6],
            caption="مقایسه عددی رفتار در ورود پویا t_arr = 12 [M]",
        ),
    )

    # Page 20: Real OS Subprocess Benchmark Setup & Repeated Trials [M]
    rep.page(
        rk.ptitle("۱۸. بنچمارک واقعی لینوکس روی منطق GuaranteedScheduling.py [M]"),
        rk.para(
            "برای راستی‌آزمایی عملی بدون تکیه بر اندازه‌گیری تک‌باره، حلقه واقعی `psutil.suspend/resume` "
            f"و `cpu_times()` در {osb['num_trials']} آزمایش مستقل روی ۳ پردازش CPUمحور "
            f"(`iters = {osb['iters_per_proc']:,}`، وزن‌های `{osb['weights']}`، کوانتوم `{osb['quantum_sec']}s`) اجرا شد."
        ),
        rk.table(
            ["آزمایش", "P1 (s)", "P2 (s)", "P3 (s)", "CPU گزارش‌شده (s)", "توزیع‌ها", "ترتیب اتمام"],
            gd.os_trial_rows(d),
            widths=[1.3, 1.9, 1.9, 1.9, 3.5, 2.0, 3.1],
            caption="نتایج تک‌تک ۵ اجرای واقعی روی لینوکس (بدون حذف هیچ داده‌ای) [M]",
        ),
        rk.para(
            f"در هر {osb['num_trials']} از {osb['num_trials']} اجرا (`all_trials_ordered_p3_fastest = {osb['all_trials_ordered_p3_fastest']}`)، "
            "ترتیب اتمام دقیقاً مطابق وزن‌ها (`P3 < P2 < P1`) بود و میانه کل زمان دیواری برابر "
            f"`{osb['median_wall_sec']:.4f}s` با `{osb['total_zero_cpu_slices']}` برش بدون-CPU ثبت گردید."
        ),
    )

    # Page 21: OS Benchmark vs Discrete Simulation Discrepancy [D]
    rep.page(
        rk.ptitle("۱۹. مقایسه اجرای واقعی سیستم‌عامل با شبیه‌ساز گسسته [M]+[D]"),
        rk.para(
            "شکل ۸ و جدول ۱۲ نسبت‌های نرمال‌شده میانه زمان اتمام در لینوکس (نسبت به P1) را با "
            "شبیه‌ساز گسسته هم‌کوانتوم (`work = 6`) مقایسه می‌کنند. فرایند P2 تنها "
            f"`{abs(p2_os - p2_sim):.4f}` اختلاف دارد (`{p2_os:.4f}` در برابر `{p2_sim:.4f}`) و P3 "
            f"اختلاف کوچکی (`{p3_os:.4f}` در برابر `{p3_sim:.4f}`) نشان می‌دهد."
        ),
        rk.image("fig_ex1_os_vs_sim.png", width_cm=15.2,
                 caption="نسبت اتمام نرمال‌شده (چپ) و میانه زمان اتمام واقعی همراه بازه کمینه-بیشینه (راست)."),
        rk.table(
            ["فرایند", "میانه OS (s)", "IQR OS (s)", "نرمال OS", "TA شبیه‌ساز", "نرمال شبیه‌ساز"],
            gd.os_vs_sim_rows(d),
            widths=[2.6, 2.5, 2.4, 2.3, 2.6, 2.4],
            caption="تطبیق داده‌های میانه/IQR سیستم‌عامل با شبیه‌ساز دقیق زمان‌صحیح [M]+[D]",
        ),
    )

    # Page 22: Explaining the OS-to-Sim Discrepancy
    rep.page(
        rk.ptitle("۲۰. ریشه‌های فیزیکی ناهماهنگی سیستم‌عامل و شبیه‌ساز [D]"),
        rk.para(
            f"چرا نسبت نرمال‌شده P3 (`w=4`) در لینوکس واقعی `{p3_os:.4f}` است ولی در شبیه‌ساز "
            f"`{p3_sim:.4f}` به‌دست می‌آید؟ سه عامل واقعی سیستم‌عاملی این فاصله را توضیح می‌دهند:"
        ),
        rk.bullets([
            "**هزینه ثابت راه‌اندازی مفسر پایتون:** هر پردازش فرزند پیش از ورود به حلقه محاسباتی هزینه راه‌اندازی یکسان می‌پردازد که فاصله نسبی بین وزن بالا و پایین را اندکی کاهش می‌دهد.",
            f"**کوانتیزاسیون ۱۰ میلی‌ثانیه‌ای `cpu_times()`:** شمارنده زمان CPU در لینوکس با تیک‌های `0.01s` به‌روز می‌شود (در جدول ۱۱ مقادیر گزارش‌شده در بازه `{cpu_min:.2f}–{cpu_max:.2f}s` است) و گردشدن برش‌ها ترتیب انتخاب را اندکی جابه‌جا می‌کند.",
            "**سربار سیگنال توقف/ادامه:** فراخوانی‌های `SIGSTOP`/`SIGCONT` و `wait(timeout)` سربار زیرمیلی‌ثانیه‌ای دارند که در شبیه‌ساز بدون‌سربار دیده نمی‌شوند.",
        ], numbered=True),
        rk.note(
            "این ناهماهنگی به معنی نادرستی `GuaranteedScheduling.py` نیست؛ بلکه دقت واقعی "
            "کنترلر فضای کاربر را در مقایسه با زمان‌بند هسته به‌صورت کمی مشخص می‌کند.",
            caption="تفسیر مهندسی یافته [D]",
        ),
    )

    # Page 23: Practical Guidance & Limitations
    rep.page(
        rk.ptitle("۲۱. راهنمای انتخاب عملی و محدودیت‌های صریح تمرین ۱"),
        rk.h1("کدام نسخه را چه زمانی استفاده کنیم؟"),
        rk.table(
            ["الگوی بار کاری", "واریانت پیشنهادی", "شواهد و دلیل فنی"],
            [
                ["دسته ایستا با شروع هم‌زمان در t=0", "gs_ratio / gs_vtime", "[E]+[M]: هم‌ارز با GPS و کمترین تاخیر در کوانتوم کوچک."],
                ["ورود پویای فرایندها در میانه اجرا", "gs_vtime / gs_entitled", "[E]: حذف کامل گرسنگی تازه‌وارد اثبات‌شده در بخش ۱۶."],
                ["برابری مکرر وزن و امتیاز فرایندها", "gs_vtime:stay", f"[E]+[M]: کاهش تعویض زمینه به کران جامع ({env_e['min_context_switches']} در برابر {env_e['max_context_switches']}) بدون رشد تاخیر."],
                ["سخت‌افزار یا سیستم‌عامل با سربار تعویض بالا", "کوانتوم میانه (۲۰–۴۰ms)", "[M]: تعادل بهینه روی منحنی پارتو تاخیر-سربار."],
            ],
            widths=[4.8, 3.8, 7.2],
            caption="جدول تصمیم‌گیری مبتنی بر داده و اثبات برای پیکربندی زمان‌بندی تضمین‌شده",
        ),
        rk.h1("محدودیت‌های اعلام‌شده تمرین ۱"),
        rk.bullets([
            "**تمرکز بر بارهای CPUمحور:** چرخه‌های خواب I/O و ضرب‌الاجل‌های بیدرنگ در تمرین‌های ۲، ۴ و ۷ بررسی می‌شوند.",
            "**وابستگی مقیاس زمانی OS به میزبان:** زمان‌های ثانیه‌ای به سرعت CPU مخزن وابسته‌اند؛ از این رو استنتاج‌ها بر نسبت‌های نرمال‌شده و ترتیب اتمام در ۵ تکرار استوارند.",
        ]),
    )

    # Page 24: Summary & Bridge
    rep.page(
        rk.ptitle("۲۲. جمع‌بندی یافته‌های تاییدشده و مسیر تمرین‌های بعدی"),
        rk.para(
            "تمرین ۱ مدل صوری، هسته دقیق زمان‌صحیح، بررسی جامع ناورداها و بنچمارک واقعی لینوکس "
            "را برای الگوریتم زمان‌بندی تضمین‌شده بنیان‌گذاری کرد."
        ),
        rk.bullets([
            f"**تضمین سهم در بار ایستا [M]:** `gs_ratio (q=1)` با بیشینه تاخیر `{runs['gs_ratio_q1']['max_abs_lag']:.4f}` (`{runs['gs_ratio_q1']['max_abs_lag_frac']}`) و عدالت `{runs['gs_ratio_q1']['jain_fairness']:.4f}` کاملاً با `gs_vtime` و `stride` منطبق شد.",
            f"**کوانتیزه کردن مبادله کوانتوم [M]:** تغییر q از 1 به 16 بیشینه تاخیر را از `{gs_q1['max_abs_lag']:.4f}` به `{gs_q16['max_abs_lag']:.4f}` برد و تعویض زمینه را از {gs_q1['context_switches']} به {gs_q16['context_switches']} کاهش داد.",
            f"**ناوردایی تاخیر تحت تساوی‌شکنی [E]:** وارسی {env_e['leaves']} مسیر نشان داد تساوی‌شکنی تاخیر را تغییر نمی‌دهد (`{env_e['worst_max_lag']:.4f}`) ولی `stay` معادل {sw_pct:.1f}% تعویض زمینه را حذف می‌کند.",
            f"**کشف حفره ورود پویا [E]+[D]:** قاعده ساده `used / weight` باعث گرسنگی {st_r['worst_p1_starve_gap']} تیکی شد که با لنگر زمان مجازی (`gs_vtime`) به‌طور کامل رفع گردید.",
            f"**تایید روی سیستم‌عامل واقعی [M]:** در {osb['num_trials']}/{osb['num_trials']} اجرای لینوکس، ترتیب سرعت اتمام مطابق وزن برقرار ماند (`P3 {osb['per_proc_median_runtime_sec']['P3']}s < P2 {osb['per_proc_median_runtime_sec']['P2']}s < P1 {osb['per_proc_median_runtime_sec']['P1']}s`).",
        ]),
        rk.para(
            "در تمرین ۲ این چهارچوب را روی بارهای دوره‌ای بیدرنگ گسترش داده و زمان‌بندی تضمین‌شده "
            "را مستقیماً در برابر EDF و Rate Monotonic (RM) قرار می‌دهیم."
        ),
    )

    return rep
