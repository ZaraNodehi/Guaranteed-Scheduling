from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("guaranteed_scheduler_cli",ROOT/"GuaranteedScheduling.py")
scheduler=importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(scheduler)


def test_waitid_preserves_final_process_cpu_sample():
    child=subprocess.Popen([
        sys.executable,"-c",
        "sum(i*i for i in range(3000000))"
    ])
    try:
        exited,reaped=scheduler._wait_exit_without_reaping(child,timeout=5.0)
        assert exited
        if not (hasattr(os,"waitid") and hasattr(os,"WNOWAIT")):
            pytest.skip("This platform reaps through Popen.wait and has no WNOWAIT support")
        assert not reaped
        rec={
            "monitor":scheduler.psutil.Process(child.pid),
            "cpu_sample":0.0,
            "used":0.0,
        }
        assert scheduler._account_cpu(rec)
        assert rec["used"] > 0.0
    finally:
        try:
            child.wait(timeout=2)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=2)


def test_cli_rejects_non_positive_quantum(monkeypatch):
    answers=iter(["1","0"])
    monkeypatch.setattr("builtins.input",lambda _prompt:next(answers))
    assert scheduler.main()==2


def test_cli_rejects_non_positive_process_count(monkeypatch):
    answers=iter(["0","0.05"])
    monkeypatch.setattr("builtins.input",lambda _prompt:next(answers))
    assert scheduler.main()==2


def test_cli_rejects_invalid_weight_before_launch(monkeypatch):
    answers=iter(["1","0.05","/bin/true","0"])
    monkeypatch.setattr("builtins.input",lambda _prompt:next(answers))
    assert scheduler.main()==2
