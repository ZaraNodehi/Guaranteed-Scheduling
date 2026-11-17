"""Pytest invariants for Exercise 5 Monte Carlo, Pareto & live OS trials."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EX5_DIR = os.path.dirname(HERE)
JSON_PATH = os.path.join(EX5_DIR, "output", "experiments.json")


def _load():
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_sweep_a_monte_carlo_ordering():
    d = _load()
    sw_a = d["sweep_a_monte_carlo"]
    assert sw_a["n_workloads"] == 240
    ov = sw_a["overall"]
    assert ov["gs_vtime:stay"]["lag"]["mean"] < ov["gs_ratio:index"]["lag"]["mean"] * 0.35
    assert ov["gs_vtime:stay"]["lag"]["p99"] < ov["rr:index"]["lag"]["p99"] * 0.25


def test_sweep_b_pareto_and_c_scaling():
    d = _load()
    rows = d["sweep_b_quantum_pareto"]["rows"]
    q1 = rows[0]["policies"]["gs_vtime:stay"]
    q2 = rows[1]["policies"]["gs_vtime:stay"]
    assert q2["switches"]["mean"] < q1["switches"]["mean"] * 0.65
    assert d["sweep_c_scaling"]["scaling_rows"][-1]["skew_vtime_lag"]["mean"] < 1.8


def test_sweep_d_live_os_interval_improvement():
    d = _load()
    tr = d["sweep_d_os_intervals"]["interval_trials"]
    assert tr[0]["poll_dt_sec"] == 0.02
    assert tr[2]["poll_dt_sec"] == 0.10
    assert tr[0]["max_share_deviation"] < tr[2]["max_share_deviation"] * 0.5
    assert tr[0]["controller_switches"] > tr[2]["controller_switches"]


def test_reports_and_diagrams_exist():
    for fn in ("REPORT_EN.md", "REPORT_FA.md", "README.md",
               "docs/REPORT_EN.pdf", "docs/REPORT_EN.docx",
               "docs/REPORT_FA.pdf", "docs/REPORT_FA.docx"):
        p = os.path.join(EX5_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 0, f"Missing {p}"
    diags = [f for f in os.listdir(os.path.join(EX5_DIR, "diagrams")) if f.endswith(".png")]
    assert len(diags) == 6
