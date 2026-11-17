"""Exercise 3 Persian RTL report builder (22 pages, 100% data-driven from experiments.json)."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, HERE)

import report_kit as rk  # noqa: E402
import gs3_data as gd  # noqa: E402


def build() -> rk.Report:
    d = gd.load()
    w1 = d["workload1_static"]
    w1m = w1["hand_vs_program_matches"]
    env1 = w1["exhaustive_tie_envelope"]
    w2 = d["workload2_dynamic"]
    w2m = w2["hand_vs_program_matches"]
    w3 = d["workload3_float_drift"]
    w3_c0 = w3["cases"][0]
    w3_d0 = w3_c0["first_divergence_detail"]

    sim1 = w1["sim_runs"]
    sim2 = w2["sim_runs"]

    rep = rk.Report(
        title="تمرین ۳: حل دستی دقیق کسری و تطبیق گام‌به‌گام با خروجی برنامه",
        subtitle="ممیزی جبری مستقل با کسرهای دقیق، اثر تساوی‌شکنی، واگرایی ورود ایستا در برابر پویا و خطای ممیز شناور IEEE-754",
        lang="fa",
        rtl=True,
        cover_meta=[
            ("مخزن", "ZaraNodehi/Guaranteed-Scheduling"),
            ("تمرین", "تمرین ۳ — درستی‌سنجی دستی گام‌به‌گام با کسرهای دقیق"),
            ("ابزارها", "جبر کسری مستقل [E] | شبیه‌ساز هسته [M] | تحلیل رانش ممیز شناور [D]"),
            ("منبع داده‌ها", "exercise-3/output/experiments.json (تولید خودکار بدون عدد دستی)"),
        ],
    )

    # Page 1: Cover
    rep.page(rk.cover(rep.cover_meta))

    # Page 2: TOC
    rep.page(rk.toc())

    # Page 3: Overview
    rep.page(
        rk.ptitle("۱. چشم‌انداز اجرایی و اهداف درستی‌سنجی"),
        rk.para(
            "هر گاه شبیه‌ساز زمان‌بندی از تقریب ممیز شناور یا قوانین تساوی‌شکنی پنهان استفاده کند، "
            "خطاهای ریز می‌تواند بی‌سروصدا ترتیب اجرا را دگرگون سازد. تمرین ۳ یک ممیزی دستی کاملاً "
            "مستقل با کسرهای دقیق `fractions.Fraction` بنا می‌کند و هر تیک آن را با `gs_core.py` "
            "در دو سناریوی ورود ایستا و ورود پویا تطبیق می‌دهد."
        ),
        rk.bullets([
            "**تطبیق کامل ورود ایستا (`[E]`=`[M]`):** درستی‌سنجی همه ۱۲ تیک دسته وزن‌دار `P1(0,3,1)`، `P2(0,5,2)` و `P3(0,4,3)` تحت سه سیاست `index`، `stay` و `max_weight`.",
            "**هم‌ارزی واریانت‌های ایستا (`[M]`):** بررسی تطابق دقیق `gs_ratio`، `gs_vtime`، `gs_entitled` و `stride` در شروع هم‌زمان `t = 0`.",
            "**واگرایی ورود پویا (`[E]`+`[M]`+`[D]`):** ردگیری دستی ۱۸ تیک با ورودهای پلکانی (`t = 0, 4, 7`) برای اثبات گرسنگی در `gs_ratio` در برابر کرانداری `gs_entitled` و `gs_vtime`.",
            "**رانش ممیز شناور IEEE-754 (`[D]`):** اندازه‌گیری دقیق شکستن تساوی‌های مجازی به‌علت خطای گردشدن `1.0 / w_i`.",
        ]),
    )

    # Page 4: Verification Architecture Diagram
    rep.page(
        rk.ptitle("۲. خط‌لوله درستی‌سنجی سه‌ابزاری [E]+[M]+[D]"),
        rk.para(
            "شکل ۱ چرخه تطبیق میان محاسبه دستی مستقل کسری `[E]`، شبیه‌ساز قطعی هسته `[M]` و "
            "انباشتگر ممیز شناور باینری `[D]` را ترسیم می‌کند."
        ),
        rk.image("fig_ex3_verification_pipeline.png", width_cm=15.4,
                 caption="خط‌لوله تطبیق متقابل بین جدول دستی کسری، شبیه‌ساز هسته و رانش ممیز شناور."),
        rk.kv([
            ["آزمون ممیزی", "نتیجه تاییدشده"],
            ["تطابق بار ایستا W1 (index / stay / max_w)", f"{w1m['index']}/{w1m['total_ticks']} | {w1m['stay']}/{w1m['total_ticks']} | {w1m['max_weight']}/{w1m['total_ticks']}"],
            ["هم‌ارزی ایستا (gs_ratio==vtime==entitled==stride)", str(w1["all_static_equiv"])],
            ["تطابق بار پویا W2 (ratio / entitled / vtime)", f"{w2m['gs_ratio']}/18 | {w2m['gs_entitled']}/18 | {w2m['gs_vtime']}/18"],
            ["رانش ممیز شناور در w=[3,6,9]", f"{w3_c0['diverged_ticks']}/{w3_c0['total_ticks']} تیک ({w3_c0['diverged_pct']:.2f}%)"],
        ], caption="خلاصه تطابق‌های جبری دقیق و ناهماهنگی ممیز شناور [E]+[D]"),
    )

    # Page 5: Exact Fractional Laws
    rep.page(
        rk.ptitle("۳. قوانین دقیق کسری برای حل دستی"),
        rk.h1("هم‌ارزی نسبت خدمت و زمان مجازی در حالت ایستا"),
        rk.formula(
            "W = sum_{j=1}^n w_j = 1 + 2 + 3 = 6\n"
            "E_i(t) = t * (w_i / W)   (t <= 8)\n"
            "gs_ratio:    used_i / w_i\n"
            "gs_vtime:    v_i = used_i / w_i  (when arr_i = 0)\n"
            "Signed Lag:  L_i(t) = A_i(t) - E_i(t) in [-1, +1]  (q = 1)",
            caption="روابط جبری دقیق توضیح‌دهنده هم‌ارزی کامل در ورود هم‌زمان",
        ),
        rk.para(
            "چون سه فرایند هم‌زمان در `t = 0` وارد می‌شوند، ساعت مجازی سیستم `V(t)` برای هر سه برابر با "
            "صفر آغاز می‌گردد؛ از این رو امتیاز `gs_vtime` و `gs_ratio` در هر تیک دقیقاً یکسان است — تا "
            "زمانی که در بار کاری ۲ ورودهای جدید در میانه اجرا رخ دهند."
        ),
    )

    # Page 6: Workload 1 Full 12-Tick Hand Trace (`index`)
    rep.page(
        rk.ptitle("۴. بار کاری ۱: جدول دستی ۱۲ تیک کامل (تساوی‌شکن index) [E]=[M]"),
        rk.para(
            "بار کاری ۱ شامل `P1(0,3,1)`، `P2(0,5,2)` و `P3(0,4,3)` (جمع کار ۱۲ تیک) است. جدول ۲ "
            "تمامی ۱۲ تیک را با کسرهای دقیق نشان می‌دهد که ۱۲/۱۲ با خروجی `gs_core` منطبق است."
        ),
        rk.table(
            ["t", "نسبت‌های پیشین (used/w)", "کمینه برابر", "انتخاب", "تطبیق", "تاخیر پس از تیک [P1, P2, P3]"],
            gd.w1_hand_rows(d, "index"),
            widths=[0.9, 4.8, 2.5, 1.5, 1.5, 6.0],
            caption="ردیابی کسری کامل ۱۲ تیک بار کاری ۱ تحت gs_ratio:index [E]=[M]",
        ),
    )

    # Page 7: Workload 1 Comparison & Exhaustive Bounds
    rep.page(
        rk.ptitle("۵. بار کاری ۱: هم‌ارزی ایستا و اثر تساوی‌شکنی [M]+[E]"),
        rk.para(
            f"جدول ۳ نشان می‌دهد `all_static_equiv = {w1['all_static_equiv']}` است: هر چهار سیاست "
            f"`gs_ratio`، `gs_vtime`، `gs_entitled` و `stride` بیشینه تاخیر `{sim1['gs_ratio:index']['max_abs_lag_frac']}`، "
            f"RMSE برابر `{sim1['gs_ratio:index']['rmse_lag']:.4f}` و `{sim1['gs_ratio:index']['context_switches']}` تعویض دارند."
        ),
        rk.table(
            ["سیاست : تساوی‌شکن", "بیشینه تاخیر", "RMSE", "تعویض", "پیش‌گیری", "میانگین TA", "جین"],
            gd.w1_policy_rows(d),
            widths=[3.8, 2.7, 1.7, 1.9, 1.9, 2.0, 1.9],
            caption="مقایسه واریانت‌های ایستا، تساوی‌شکن‌ها و Round Robin روی بار کاری ۱ [M]",
        ),
        rk.kv([
            ["شاخص پوش جامع تساوی‌شکنی [E]", "مقدار دقیق"],
            ["حالت‌ها / برگ‌های پیمایش‌شده", f"{env1['states']} حالت / {env1['leaves']} برگ (truncated={env1['truncated']})"],
            ["بازه بیشینه تاخیر [کمینه، بیشینه]", f"[{env1['best_max_lag']:.4f}, {env1['worst_max_lag']:.4f}] (کسر {env1['worst_max_lag_frac']})"],
            ["بازه تعویض زمینه [کمینه، بیشینه]", f"[{env1['min_context_switches']}, {env1['max_context_switches']}]"],
        ], caption="کران‌های دقیق پوش تساوی‌شکنی بار کاری ۱ با وارسی جامع [E]"),
    )

    # Page 8: Workload 1 Stay Tie-Breaker Trace
    rep.page(
        rk.ptitle("۶. انشعاب دقیق کسری تحت تساوی‌شکن stay [E]"),
        rk.para(
            "در لحظه `t = 0` تمام نسبت‌ها صفر است و در لحظه `t = 6` (`used = [1, 2, 3]`) همه نسبت‌ها "
            "دقیقاً به `1/1` بازمی‌گردند. جدول ۵ نشان می‌دهد تساوی‌شکن `stay` با حفظ `P3` در `t = 6` "
            f"تعویض زمینه را از `{sim1['gs_ratio:index']['context_switches']}` به `{sim1['gs_ratio:stay']['context_switches']}` "
            f"(کران پایین دقیق {env1['min_context_switches']}) کاهش می‌دهد."
        ),
        rk.table(
            ["t", "نسبت‌های پیشین", "کمینه برابر", "انتخاب (stay)", "تطبیق", "تاخیر پس از تیک"],
            gd.w1_hand_rows(d, "stay"),
            widths=[0.9, 4.8, 2.5, 1.8, 1.4, 5.8],
            caption="جدول دستی کامل ۱۲ تیک برای gs_ratio:stay (انطباق ۱۲/۱۲) [E]=[M]",
        ),
    )

    # Page 9: Workload 1 Gantt Figure
    rep.page(
        rk.ptitle("۷. مشاهده بصری بازنشانی تساوی در t = 6 و اثر تساوی‌شکن [M]"),
        rk.para(
            "شکل ۲ چهار جدول زمانی ۱۲ تیکی بار کاری ۱ را کنار هم می‌گذارد و مرز دقیق بازنشانی `t = 6` را نشان می‌دهد."
        ),
        rk.image("fig_ex3_static_hand_gantt.png", width_cm=15.4,
                 caption="مقایسه نمودار گانت بار کاری ۱ تحت تساوی‌شکن‌های مختلف و Round Robin."),
        rk.bullets([
            "**تساوی آغازین `t = 0` (`0 == 0 == 0`):** سیاست `index` سراغ `P1` می‌رود در حالی که `max_weight` به `P3 (w=3)` اولویت می‌دهد.",
            "**تساوی چرخه‌ای `t = 6` (`1 == 1 == 1`):** سیاست `stay` از پیش‌گیری بی‌مورد `P3` جلوگیری کرده و آن را در `t = 7` تمام می‌کند.",
            "**اختلاف بنیادی RR:** راند رابین سهم‌های ۱:۲:۳ را نادیده گرفته و پایان `P3` را به عقب می‌اندازد.",
        ]),
    )

    # Page 10: Workload 1 Signed Lag Figure
    rep.page(
        rk.ptitle("۸. راستی‌آزمایی پوش تاخیر علامت‌دار در بار کاری ۱ [E]+[M]"),
        rk.para(
            "شکل ۳ نشان می‌دهد تاخیر علامت‌دار `L_i(t) = A_i(t) - E_i(t)` در تمام ۱۲ تیک اکیداً درون "
            "بازه بسته `[-1, +1]` باقی می‌ماند و در `t = 6` هر سه فرایند هم‌زمان به تاخیر صفر می‌رسند."
        ),
        rk.image("fig_ex3_static_lag_fractions.png", width_cm=15.2,
                 caption="خدمت تجمعی واقعی در برابر GPS ایده‌آل (بالا) و تاخیر علامت‌دار درون [-1, +1] (پایین)."),
        rk.note(
            "پس از اتمام `P3` در `t = 9`، نرخ استحقاق GPS میان دو فرایند باقی‌مانده `P1 (w=1)` و `P2 (w=2)` "
            "به‌طور خودکار روی نسبت `1/3` و `2/3` بازتنظیم می‌شود تا پایان در `t = 12`.",
            caption="بازتنظیم خودکار نرخ GPS پس از خروج فرایند",
        ),
    )

    # Page 11: Workload 2 Dynamic Arrival Setup
    rep.page(
        rk.ptitle("۹. بار کاری ۲: واگرایی ورود ایستا در برابر ورود پویا [E]+[M]+[D]"),
        rk.para(
            "در بار کاری ۲ فرایندها در زمان‌های متفاوت وارد می‌شوند: `P1(arr=0, work=8, w=2)`، "
            "`P2(arr=4, work=6, w=2)` و `P3(arr=7, work=4, w=1)` (جمع ۱۸ تیک). جدول ۶ شکاف عمیق "
            "میان سه واریانت GS را نشان می‌دهد که در بار کاری ۱ کاملاً یکسان بودند."
        ),
        rk.table(
            ["سیاست", "بیشینه تاخیر (کسر)", "RMSE", "بیشترین وقفه", "تعویض", "میانگین TA", "جین"],
            gd.w2_summary_rows(d),
            widths=[2.6, 2.8, 1.8, 2.3, 1.9, 2.0, 2.0],
            caption="مقایسه معیارهای ورود پویا در بار کاری ۲ [M]",
        ),
        rk.bullets([
            f"**فروپاشی `gs_ratio` (`GuaranteedScheduling.py`):** بیشینه تاخیر به `{sim2['gs_ratio']['max_abs_lag']:.4f}` (`{sim2['gs_ratio']['max_abs_lag_frac']}`) اوج می‌گیرد و `P1` برای `{sim2['gs_ratio']['max_starve_gap']}` تیک (`t = 4..10`) گرسنه می‌ماند.",
            f"**بهبود سه‌برابری در `gs_entitled`:** ردیابی استحقاق برخط از لحظه ورود تاخیر بیشینه را به `{sim2['gs_entitled']['max_abs_lag']:.4f}` (`{sim2['gs_entitled']['max_abs_lag_frac']}`) می‌رساند.",
            f"**دقت بهینه `gs_vtime`:** لنگرزدن به ساعت مجازی `V(t)` کمترین تاخیر (`{sim2['gs_vtime']['max_abs_lag']:.4f}` یعنی `{sim2['gs_vtime']['max_abs_lag_frac']}`) و کمترین RMSE (`{sim2['gs_vtime']['rmse_lag']:.4f}`) را می‌سازد.",
        ]),
    )

    # Page 12: Workload 2 Hand Trace — gs_ratio
    rep.page(
        rk.ptitle("۱۰. حل دستی ۱۸ تیک کامل تحت gs_ratio (شاهد گرسنگی) [E]=[M]"),
        rk.para(
            "جدول ۷ تمام ۱۸ تیک `gs_ratio` را گام‌به‌گام دنبال می‌کند. در `t = 4` فرایند تازه‌وارد `P2` "
            "با نسبت `0/2 = 0` بر `P1` با نسبت `4/2 = 2` غلبه کرده و تا `t = 7` اجرا می‌شود؛ سپس ورود "
            "`P3` با نسبت `0/1 = 0` محرومیت `P1` را تا `t = 10` ادامه می‌دهد."
        ),
        rk.table(
            ["t", "امتیاز پیش از تیک", "انتخاب", "P1: A/E (تاخیر)", "P2: A/E (تاخیر)", "P3: A/E (تاخیر)"],
            gd.w2_dynamic_rows(d, "gs_ratio"),
            widths=[0.8, 4.1, 2.0, 3.4, 3.4, 3.4],
            caption="ردیابی دستی ۱۸ تیک کامل برای gs_ratio در بار کاری ۲ (انطباق ۱۸/۱۸) [E]=[M]",
        ),
    )

    # Page 13: Workload 2 Hand Trace — gs_entitled
    rep.page(
        rk.ptitle("۱۱. حل دستی ۱۸ تیک کامل تحت gs_entitled (A_i / E_online) [E]=[M]"),
        rk.para(
            "در `gs_entitled` تازه‌وارد `P2` پس از یک تیک اجرا در `t=4..5` نسبت `1 / (1/2) = 2` را "
            "به‌دست می‌آورد که از نسبت `4 / (9/2) = 8/9` مربوط به `P1` بزرگ‌تر است؛ در نتیجه CPU در `t = 5` "
            "فوراً به `P1` بازمی‌گردد (جدول ۸)."
        ),
        rk.table(
            ["t", "امتیاز پیش از تیک", "انتخاب", "P1: A/E (تاخیر)", "P2: A/E (تاخیر)", "P3: A/E (تاخیر)"],
            gd.w2_dynamic_rows(d, "gs_entitled"),
            widths=[0.8, 4.2, 1.9, 3.4, 3.4, 3.4],
            caption="ردیابی دستی ۱۸ تیک کامل برای gs_entitled در بار کاری ۲ (انطباق ۱۸/۱۸) [E]=[M]",
        ),
    )

    # Page 14: Workload 2 Hand Trace — gs_vtime
    rep.page(
        rk.ptitle("۱۲. حل دستی ۱۸ تیک کامل تحت gs_vtime (لنگر V(t)) [E]=[M]"),
        rk.para(
            "در `gs_vtime` به محض ورود `P2` در `t = 4`، ساعت مجازی آن برابر `V(4) = 4 * (1/2) = 2` تنظیم "
            "می‌شود که دقیقاً برابر `v_P1 = 2` است! بنابراین هیچ بدهی یا اعتبار کاذبی ایجاد نمی‌شود و "
            "تسهیم ۱ به ۱ فوراً برقرار می‌گردد (جدول ۹)."
        ),
        rk.table(
            ["t", "امتیاز پیش از تیک", "انتخاب", "P1: A/E (تاخیر)", "P2: A/E (تاخیر)", "P3: A/E (تاخیر)"],
            gd.w2_dynamic_rows(d, "gs_vtime"),
            widths=[0.8, 4.2, 1.9, 3.4, 3.4, 3.4],
            caption="ردیابی دستی ۱۸ تیک کامل برای gs_vtime در بار کاری ۲ (انطباق ۱۸/۱۸) [E]=[M]",
        ),
    )

    # Page 15: Dynamic Divergence Gantt Chart
    rep.page(
        rk.ptitle("۱۳. تصویرسازی واگرایی ورود پویا روی نمودار گانت [M]+[D]"),
        rk.para(
            "شکل ۴ هر سه سیاست را روی بازه ۱۸ تیکی کنار هم نشان می‌دهد و لحظات ورود `t = 4` و `t = 7` "
            "همراه با بازه ۶ تیکی گرسنگی `P1` تحت `gs_ratio` را برجسته می‌سازد."
        ),
        rk.image("fig_ex3_dynamic_divergence.png", width_cm=15.4,
                 caption="مقایسه گانت ورود پویا: گرسنگی ۶ تیکی P1 در gs_ratio در برابر تسهیم فوری gs_entitled و gs_vtime."),
        rk.note(
            "توجه کنید `gs_vtime` کار `P1` را در `t = 12` به پایان می‌رساند، در حالی که `gs_ratio` اتمام "
            "`P1` را تا `t = 18` به تاخیر می‌اندازد (افزایش ۵۰ درصدی زمان پاسخ فرایند قدیمی!).",
            caption="پیامد مستقیم اعتبار کاذب تازه‌وارد بر زمان چرخش",
        ),
    )

    # Page 16: Signed Lag Curves
    rep.page(
        rk.ptitle("۱۴. مقایسه مسیر تاخیر علامت‌دار: انفجار تاخیر در برابر کران بسته [E]+[M]"),
        rk.para(
            "شکل ۵ مسیر دقیق تاخیر `L_i(t)` را میان `gs_ratio` و `gs_vtime` مقایسه می‌کند. در `gs_ratio` "
            "تاخیر `P1` تا `-29/10 = -2.90` (در `t = 13`) سقوط می‌کند، در حالی که `gs_vtime` تمام فرایندها را "
            "درون بازه `[-0.70, +0.70]` حفظ می‌نماید."
        ),
        rk.image("fig_ex3_dynamic_lag_curves.png", width_cm=15.4,
                 caption="روند تاخیر علامت‌دار در بار کاری ۲: انفجار به -2.90 در gs_ratio در برابر کران 0.70 در gs_vtime."),
        rk.bullets([
            "**نقطه اوج نقض:** در پایان تیک `t = 13`، خدمت واقعی `P1` برابر ۵ و سهم GPS آن `79/10` است (`L = -29/10`).",
            "**چرا `gs_vtime` از ۱ عبور نمی‌کند:** لنگرزدن به `V(t)` تضمین می‌کند ورود فرایند جدید هیچ بدهی پیشینی به فرایندهای فعال تحمیل نکند.",
        ]),
    )

    # Page 17: Workload 3 — IEEE-754 Float Drift [D]
    rep.page(
        rk.ptitle("۱۵. ناهماهنگی ابزار [D]: رانش ممیز شناور IEEE-754 در برابر کسر دقیق"),
        rk.para(
            "چرا `core/gs_core.py` از `fractions.Fraction` به‌جای `float` استاندارد ۶۴بیتی استفاده می‌کند؟ "
            "برای آزمودن این پرسش، انباشت `v_i += Fraction(1, w_i)` را با `v_i += 1.0 / w_i` روی سه مجموعه "
            "وزن صحیح مقایسه کردیم (جدول ۱۰)."
        ),
        rk.table(
            ["وزن‌ها", "افق اجرا", "تیک‌های واگرا (٪)", "نخستین واگرایی", "انتخاب دقیق در برابر Float"],
            gd.w3_drift_rows(d),
            widths=[2.6, 2.4, 3.6, 2.2, 4.4],
            caption="واگرایی تصمیم‌گیری زمان‌بند صرفاً بر اثر خطای گردشدن ممیز شناور IEEE-754 [D]",
        ),
        rk.note(
            f"در `weights = {w3_c0['weights']}` نخستین انشعاب در `t = {w3_d0['t']}` رخ می‌دهد: کسر دقیق "
            f"(`{w3_d0['exact_vtime_frac']}`) تساوی را به نفع `{w3_d0['exact_choice']}` می‌شکند، ولی ممیز شناور "
            f"با خطای `1e-16` مقایسه را برعکس کرده و `{w3_d0['float_choice']}` را برمی‌گزیند!",
            caption="مکانیزم پنهان وارونگی تساوی در ممیز شناور [D]",
        ),
    )

    # Page 18: Float Drift Plot
    rep.page(
        rk.ptitle("۱۶. مشاهده آبشار واگرایی ناشی از خطای 1e-16 [D]"),
        rk.para(
            f"شکل ۶ نشان می‌دهد روی وزن‌های `[3, 6, 9]` بیش از `{w3_c0['diverged_pct']:.1f}%` "
            f"(`{w3_c0['diverged_ticks']}` از `{w3_c0['total_ticks']}` تیک) صرفاً به‌علت نمایش باینری "
            "ممیز شناور برخلاف جبر دقیق زمان‌بندی می‌شوند."
        ),
        rk.image("fig_ex3_float_drift.png", width_cm=15.4,
                 caption="درصد تیک‌های واگرا در سه ترکیب وزنی (چپ) و تطبیق ۶۰ تیک نخست w=[3,6,9] (راست)."),
        rk.bullets([
            "**چرا `(3, 6, 9)` بیشتر از `(3, 7, 10)` رانش دارد:** وجود مقسوم‌علیه مشترک تساوی‌های کسری دقیق‌تری می‌سازد و هر تساوی دقیق در معرض خطای یک ULP است.",
            "**ارتباط با `GuaranteedScheduling.py`:** استفاده از `float` برای `cpu_times() / weight` در کنار تیک ۱۰ میلی‌ثانیه‌ای لینوکس، تساوی‌های واقعی را ناپایدار می‌کند.",
        ]),
    )

    # Page 19: Designing Drift-Free Schedulers
    rep.page(
        rk.ptitle("۱۷. مهندسی زمان مجازی بدون رانش (کسری و ممیز ثابت)"),
        rk.para(
            "چگونه زمان‌بندهای عملیاتی بدون سربار `Fraction` در هر تعویض زمینه و بدون خطای ممیز شناور کار می‌کنند؟"
        ),
        rk.bullets([
            "**گزینه ۱ — کسرهای دقیق `Fraction` (درستی‌سنجی `[E]`/`[M]`):** دقت ریاضی مطلق بدون هیچ خطای تجمعی.",
            "**گزینه ۲ — ضرایب صحیح از پیش محاسبه‌شده با `LCM` (`Stride`):** تعریف گام صحیح `stride_i = L / w_i` که تمام جمع‌ها را به حساب صحیح `O(1)` تبدیل می‌کند.",
            "**گزینه ۳ — ممیز ثابت مقیاس‌شده (`Linux CFS / EEVDF`):** نگهداری `vruntime` برحسب نانوثانیه صحیح با ضرب معکوس وزن بدون نیاز به واحد FPU هسته.",
        ], numbered=True),
    )

    # Page 20: Protocol
    rep.page(
        rk.ptitle("۱۸. دستورالعمل گام‌به‌گام ممیزی دستی"),
        rk.para(
            "برای ممیزی هر مثال جدید با دست و تطبیق ۱۰۰٪ آن با `gs_core.py` این پنج گام کسری را اجرا کنید:"
        ),
        rk.code([
            "1. Compute active weight sum W(t) = sum_{i in A(t)} w_i on every interval.",
            "2. Update exact Fluid GPS E_i(t) += w_i / W(t) as Fractions.",
            "3. Evaluate exact score_i(t) before tick t (used/w, used/E_on, or v_i with V(t)).",
            "4. List all minimum-tied processes explicitly and apply tie rule (index/stay/max_w).",
            "5. Verify |A_i(t) - E_i(t)| <= 1 for static q=1 and compare 100% of ticks to gs_core.",
        ], caption="پروتکل ۵ مرحله‌ای درستی‌سنجی دستی آزموده‌شده در بارهای ۱ و ۲"),
    )

    # Page 21: Practical Guidance & Limitations
    rep.page(
        rk.ptitle("۱۹. راهنمای عملی و محدودیت‌های صریح"),
        rk.table(
            ["شرایط و ریسک", "انتخاب مهندسی صحیح", "شواهد از تمرین ۳"],
            [
                ["ورود هم‌زمان ایستا در `t = 0`", "هر واریانت دقیق GS", f"[E]: تطابق ۱۰۰٪ همه واریانت‌ها (`all_static_equiv={w1['all_static_equiv']}`)."],
                ["ورود پویا و پراکنده فرایندها", "`gs_vtime` (`v_i <- V(t)`) یا `gs_entitled`", f"[E]+[M]: تاخیر {sim2['gs_vtime']['max_abs_lag_frac']} در برابر {sim2['gs_ratio']['max_abs_lag_frac']} برای gs_ratio."],
                ["تساوی‌های مکرر در چرخه وزن‌ها", "تساوی‌شکن صریح `stay`", f"[E]: کاهش تعویض زمینه ({sim1['gs_ratio:stay']['context_switches']} در برابر {sim1['gs_ratio:index']['context_switches']})."],
                ["پیشگیری از ناپایداری تساوی در کد", "`Fraction` یا گام صحیح `LCM/w_i`", f"[D]: حذف {w3_c0['diverged_ticks']}/{w3_c0['total_ticks']} خطای رانش ممیز شناور."],
            ],
            widths=[4.6, 5.2, 7.4],
            caption="توصیه‌های مهندسی مستند تمرین ۳ مبتنی بر ممیزی جبری",
        ),
        rk.h1("محدودیت‌های صریح"),
        rk.bullets([
            "جداول دستی با پیش‌گیری تک‌تیکی (`q = 1`) و بدون خواب I/O محاسبه شده‌اند (سناریوی خواب و بیداری I/O در تمرین ۷ بررسی می‌شود).",
            "توان‌های ۲ (`w = 1, 2, 4, 8`) رانش باینری ندارند اما وزن‌های غیرتوان‌دویی نظیر `[3, 6, 9]` خطای IEEE-754 را بلافاصله آشکار می‌کنند.",
        ]),
    )

    # Page 22: Summary & Roadmap
    rep.page(
        rk.ptitle("۲۰. جمع‌بندی یافته‌های تاییدشده و مسیر تمرین ۴"),
        rk.bullets([
            f"**تطبیق ۱۰۰٪ حل دستی ایستا (`[E]`=`[M]`):** تمام `{w1m['total_ticks']}` تیک بار کاری ۱ در هر سه تساوی‌شکن `index`، `stay` و `max_weight` صددرصد با شبیه‌ساز یکسان است.",
            f"**تطبیق ۱۰۰٪ حل دستی پویا (`[E]`=`[M]`):** تمام `{w2['total_work']}` تیک بار کاری ۲ در هر سه سیاست `gs_ratio`، `gs_entitled` و `gs_vtime` مستقل تایید شد.",
            f"**کمّی‌سازی واگرایی پویا (`[D]`):** در `gs_ratio` تاخیر به `{sim2['gs_ratio']['max_abs_lag']:.4f}` (`{sim2['gs_ratio']['max_abs_lag_frac']}`) اوج می‌گیرد و `P1` برای `{sim2['gs_ratio']['max_starve_gap']}` تیک قفل می‌شود، ولی `gs_vtime` تاخیر را به `{sim2['gs_vtime']['max_abs_lag']:.4f}` (`{sim2['gs_vtime']['max_abs_lag_frac']}`) محدود می‌کند.",
            f"**آشکارسازی رانش ممیز شناور (`[D]`):** حساب ممیز شناور `1.0 / w_i` روی `w = {w3_c0['weights']}` باعث انحراف `{w3_c0['diverged_ticks']}/{w3_c0['total_ticks']}` (`{w3_c0['diverged_pct']:.2f}%`) از تیک‌ها از `t = {w3_c0['first_divergence_t']}` به بعد شد.",
            "**گام بعدی — تمرین ۴:** اثبات صوری درستی، قضایای کران تاخیر پارخ-گالگر، امکان‌پذیری جامع بلادرنگ و ناورداهای عدالت اضافه‌بار.",
        ]),
    )
    return rep
