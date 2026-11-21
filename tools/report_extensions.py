"""Rubric-focused source appendices for the six active Guaranteed-Scheduling exercises.

Every listing is read from the repository at build time. The appendices are not
placeholder pages: they expose the actual experiment drivers, algorithm code,
visualization pipeline, and tests used by each exercise.
"""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

import report_kit as rk

ROOT = Path(__file__).resolve().parents[1]

PLAN = {
    "exercise-2": {
        "total_pages": 3,
        "sources": ["exercise-2/code/run_experiments.py", "exercise-2/tests/test_ex2.py"],
    },
    "exercise-3": {
        "total_pages": 25,
        "sources": [
            "exercise-3/code/run_experiments.py",
            "exercise-3/code/plot_diagrams.py",
            "exercise-3/code/make_worksheet.py",
            "exercise-3/tests/test_ex3.py",
        ],
    },
    "exercise-4": {
        "total_pages": 2,
        "sources": ["exercise-4/code/sync_primitives.py", "exercise-4/code/run_experiments.py"],
    },
    "exercise-5": {
        "total_pages": 27,
        "sources": [
            "exercise-5/code/rw_locks.py",
            "exercise-5/code/run_experiments.py",
            "exercise-5/code/plot_diagrams.py",
            "exercise-5/tests/test_ex5.py",
        ],
    },
    "exercise-6": {
        "total_pages": 30,
        "sources": [
            "exercise-6/code/integrated_kernel.py",
            "exercise-6/code/run_experiments.py",
            "exercise-6/code/plot_diagrams.py",
            "exercise-6/tests/test_ex6.py",
            "core/gs_core.py",
        ],
    },
}

FLOW_TITLES = {
    "exercise-2": {
        "en": "Guaranteed Scheduling vs. EDF/RM — comparison and evidence workflow",
        "fa": "روند مقایسهٔ Guaranteed Scheduling با EDF و RM و ارزیابی شواهد",
    },
    "exercise-3": {
        "en": "Paper scheduling workflow: release, ready queue, dispatch, and deadline audit",
        "fa": "روند حل دستی: آزادسازی کار، صف آماده، انتخاب پردازه و بررسی ضرب‌الاجل",
    },
    "exercise-4": {
        "en": "Mutual-exclusion verification workflow",
        "fa": "روند بررسی انحصار متقابل و سازوکارهای همگام‌سازی",
    },
    "exercise-5": {
        "en": "Readers–Writers policy selection and safety/fairness audit",
        "fa": "انتخاب سیاست خوانندگان-نویسندگان و ممیزی ایمنی و عدالت",
    },
    "exercise-6": {
        "en": "Capstone integration: scheduler, lock protocol, workload, and measurements",
        "fa": "یکپارچه‌سازی کپستون: زمان‌بند، پروتکل قفل، بارکاری و اندازه‌گیری",
    },
}

FLOW_CAPTIONS = {
    "exercise-2": {
        "en": "The comparison uses a shared workload definition, records algorithm-specific dispatch decisions, and separates proportional-fairness results from deadline-feasibility results.",
        "fa": "مقایسه با تعریف بارکاری مشترک انجام می‌شود؛ تصمیم‌های هر الگوریتم جداگانه ثبت می‌شوند و نتایج انصاف نسبی از امکان‌پذیری ضرب‌الاجل تفکیک می‌شوند.",
    },
    "exercise-3": {
        "en": "This workflow describes the paper trace used in the report. It is a guide to the manual method, not a substitute for the student's own handwritten worksheet.",
        "fa": "این فلوچارت روش ردگیری کاغذیِ گزارش را نشان می‌دهد. راهنمای روش حل است و جای برگهٔ دست‌نویس واقعی دانشجو را نمی‌گیرد.",
    },
    "exercise-4": {
        "en": "The verification path distinguishes safety, progress, bounded waiting, memory-order assumptions, and measured operating-system behavior.",
        "fa": "مسیر راستی‌آزمایی، ایمنی، پیشرفت، انتظار کراندار، فرض‌های ترتیب حافظه و رفتار اندازه‌گیری‌شدهٔ سیستم‌عامل را از هم جدا می‌کند.",
    },
    "exercise-5": {
        "en": "The Readers–Writers study checks exclusion and concurrent-read safety before comparing starvation, barging, CPU burn, and read/write workload performance.",
        "fa": "مطالعهٔ خوانندگان-نویسندگان ابتدا انحصار و ایمنی خواندن هم‌زمان را می‌سنجد و سپس قحطی، سبقت‌گیری، مصرف CPU و کارایی بار خواندن/نوشتن را مقایسه می‌کند.",
    },
    "exercise-6": {
        "en": "The capstone combines the scheduler and synchronization evidence under one workload and keeps simulation claims separate from live-thread measurements.",
        "fa": "کپستون شواهد زمان‌بند و همگام‌سازی را در یک بارکاری ترکیب می‌کند و ادعاهای شبیه‌سازی را از اندازه‌گیری‌های نخ‌های واقعی جدا نگه می‌دارد.",
    },
}

PIPELINE_ROWS = {
    "exercise-2": [
        ["Input", "Fixed task/process set and declared assumptions"],
        ["Run", "GS variants, EDF, RM/DM and comparison baselines"],
        ["Audit", "Lag/fairness, response, deadline misses and overload"],
        ["Report", "Separate guarantees from workload-specific observations"],
    ],
    "exercise-3": [
        ["Release", "Add jobs at their release ticks and calculate absolute deadlines"],
        ["Ready queue", "List unfinished released jobs before each dispatch"],
        ["Dispatch", "EDF: earliest absolute deadline; RM: shortest period"],
        ["Audit", "Record completion and deadline misses; cross-check with RTA/dbf"],
    ],
    "exercise-4": [
        ["Model", "Define actors, shared state, and critical section"],
        ["Safety", "Check mutual exclusion and state invariants"],
        ["Liveness", "Check progress, deadlock, livelock and bounded waiting"],
        ["Evidence", "Combine BFS counterexamples with live-thread measurements"],
    ],
    "exercise-5": [
        ["Policy", "Readers-preference, writers-preference or fair turnstile"],
        ["Primitive", "Semaphore, Mesa monitor, Peterson filter or Dekker tournament"],
        ["Safety", "At most one writer; no reader overlaps a writer"],
        ["Fairness", "Measure starvation, barging, waiting and throughput"],
    ],
    "exercise-6": [
        ["Scheduling", "Choose the policy and compute effective priorities"],
        ["Synchronization", "Acquire/release locks and handle blocking correctly"],
        ["Integration", "Run RT control and shared Readers–Writers telemetry"],
        ["Evaluation", "Compare deadline misses, latency, throughput and CPU use"],
    ],
}

def _wrap_source_line(line: str, number: int, limit: int = 96) -> list[str]:
    raw = line.rstrip("\n")
    prefix = f"{number:04d}: "
    if len(raw) <= limit:
        return [prefix + raw]
    first_width = max(20, limit - len(prefix))
    first = textwrap.wrap(raw, width=first_width, break_long_words=True,
                          break_on_hyphens=False)
    out = [prefix + first[0]]
    for part in first[1:]:
        out.append("      | " + part)
    return out

def _chunks(exercise: str, paths: list[str], wanted: int):
    for rel in paths:
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f"Missing source file for appendix: {rel}")
        lines = path.read_text(encoding="utf-8").splitlines()
        step = 27
        for start in range(0, len(lines), step):
            raw = lines[start:start + step]
            if not any(line.strip() for line in raw):
                continue
            formatted = []
            for offset, line in enumerate(raw):
                formatted.extend(_wrap_source_line(line, start + offset + 1))
            yield rel, start + 1, min(start + step, len(lines)), formatted
            if False:
                return

def _source_role(rel: str, lang: str) -> str:
    name = Path(rel).name
    category = (
        "test" if name.startswith("test_") else
        "plot" if "plot" in name or "diagram" in name else
        "worksheet" if "worksheet" in name else
        "lock" if "lock" in name or "sync" in name else
        "experiment" if "experiment" in name or "run_" in name else
        "scheduler core"
    )
    roles = {
        "en": {
            "test": "This listing is from the automated verification suite. It documents executable expectations and guards against regressions in the stated invariants.",
            "plot": "This listing belongs to the figure-generation pipeline. The charts are derived from the experiment output rather than manually typed measurements.",
            "worksheet": "This listing generates the printable paper worksheet and its trace tables. It supports the manual exercise but does not impersonate a handwritten submission.",
            "lock": "This listing contains the synchronization implementation. Its correctness claims must be read with the memory model and thread assumptions stated in the report.",
            "experiment": "This listing is part of the reproducible experiment driver. It defines workloads, invokes the selected algorithms, collects measurements, and serializes results.",
            "scheduler core": "This listing is from the canonical scheduling core. It exposes the selection and accounting logic used by the experiments.",
        },
        "fa": {
            "test": "این بخش از مجموعهٔ آزمون خودکار است؛ انتظارهای اجرایی را مشخص می‌کند و از بازگشت خطا در ناورداهای تعریف‌شده جلوگیری می‌کند.",
            "plot": "این بخش به خط لولهٔ تولید شکل تعلق دارد. نمودارها از خروجی آزمایش ساخته می‌شوند، نه از اعداد دستی و بدون منبع.",
            "worksheet": "این بخش برگهٔ چاپی و جدول‌های ردگیری کاغذی را تولید می‌کند. برای حل دستی کمک‌کننده است، اما جای تحویل دست‌نویس دانشجو را نمی‌گیرد.",
            "lock": "این بخش پیاده‌سازی همگام‌سازی را در بر دارد. ادعای درستی آن باید با مدل حافظه و فرض‌های نخ‌های اجرایی گزارش خوانده شود.",
            "experiment": "این بخش از راه‌انداز آزمایش بازتولیدپذیر است؛ بارکاری را تعریف می‌کند، الگوریتم‌ها را اجرا می‌کند، سنجه‌ها را جمع‌آوری و نتیجه را ذخیره می‌کند.",
            "scheduler core": "این بخش از هستهٔ مرجع زمان‌بندی است و منطق انتخاب پردازه و حسابداری سرویس را نشان می‌دهد.",
        },
    }
    return roles[lang][category]

def append(rep, exercise: str, figures_dir: str) -> None:
    if exercise not in PLAN:
        return
    lang = "fa" if rep.lang == "fa" else "en"
    cfg = PLAN[exercise]
    flow = ROOT / exercise / "diagrams" / f"fig_{exercise.replace('-', '')}_rubric_flowchart.png"
    # Flowchart page: explicit process map plus an evidence-oriented interpretation.
    if not flow.exists():
        raise FileNotFoundError(f"Required rubric flowchart not generated: {flow}")
    rep.page(
        rk.ptitle("پیوست روش اجرا و فلوچارت" if lang == "fa" else "Appendix: Execution Workflow and Flowchart"),
        rk.para(FLOW_CAPTIONS[exercise][lang]),
        rk.image(flow.name, width_cm=16.5,
                 caption=FLOW_TITLES[exercise][lang]),
        rk.table(
            ["مرحله", "شرح" ] if lang == "fa" else ["Stage", "Description"],
            PIPELINE_ROWS[exercise] if lang == "en" else [
                [x[0], {
                    "Input": "ورودی",
                    "Run": "اجرا",
                    "Audit": "ممیزی",
                    "Report": "گزارش",
                    "Release": "آزادسازی",
                    "Ready queue": "صف آماده",
                    "Dispatch": "انتخاب اجرا",
                    "Model": "مدل",
                    "Safety": "ایمنی",
                    "Liveness": "پیشرفت",
                    "Evidence": "شواهد",
                    "Policy": "سیاست",
                    "Primitive": "سازوکار",
                    "Fairness": "عدالت",
                    "Scheduling": "زمان‌بندی",
                    "Synchronization": "همگام‌سازی",
                    "Integration": "یکپارچه‌سازی",
                    "Evaluation": "ارزیابی",
                }.get(x[0], x[0]), x[1]] for x in PIPELINE_ROWS[exercise]
            ],
            widths=[3.0, 13.5] if lang == "fa" else [3.0, 13.5],
            caption=("خلاصهٔ مراحل و شواهد لازم برای بازبینی این تمرین."
                     if lang == "fa" else
                     "Compact map of the stages and evidence required to review this exercise."),
        ),
    )

    wanted = cfg["total_pages"] - 1
    selected = []
    for item in _chunks(exercise, cfg["sources"], wanted):
        selected.append(item)
        if len(selected) >= wanted:
            break
    if len(selected) < wanted:
        raise RuntimeError(f"{exercise}: requested {wanted} source appendix pages but only found {len(selected)} chunks")

    for index, (rel, start, end, code_lines) in enumerate(selected, 1):
        display_path = rel.replace("/", " / ")
        if lang == "fa":
            title = f"پیوست کد {index}: ممیزی منبع «{Path(rel).name}» — خطوط {start} تا {end}"
            description = (
                f"فایل مرجع: {display_path}. {_source_role(rel, lang)} "
                f"بازهٔ زیر خطوط {start} تا {end} از همان فایل است؛ شمارهٔ خطوط برای ارجاع و بازبینی دوباره حفظ شده‌اند. "
                "این فهرست کد، ضمیمهٔ قابل ممیزی گزارش است و باید همراه آزمون‌ها و فایل خروجی متناظر بررسی شود."
            )
            caption = f"گزیدهٔ واقعی از {rel}، خطوط {start}–{end}؛ خطوط بلند فقط برای صفحه‌آرایی شکسته شده‌اند."
        else:
            title = f"Source Audit {index}: {Path(rel).name} — lines {start}–{end}"
            description = (
                f"Source path: {display_path}. {_source_role(rel, lang)} "
                f"The listing below covers source lines {start}–{end}; line numbers are retained for direct review. "
                "This is an auditable source appendix and should be read together with the tests and the corresponding experiment output."
            )
            caption = f"Verbatim source excerpt from {rel}, lines {start}–{end}; long lines are visually wrapped for print layout."
        rep.page(
            rk.ptitle(title),
            rk.para(description),
            rk.code(code_lines, caption=caption),
        )

