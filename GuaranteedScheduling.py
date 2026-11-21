"""Interactive Linux subprocess scheduler using weighted Guaranteed Scheduling."""
from __future__ import annotations

import math
import os
import subprocess
import time

import psutil


def _wait_exit_without_reaping(proc: subprocess.Popen, timeout: float) -> tuple[bool, bool]:
    """Return (exited, already_reaped); WNOWAIT preserves final /proc counters."""
    if not (hasattr(os, "waitid") and hasattr(os, "WNOWAIT") and hasattr(os, "P_PID")):
        try:
            proc.wait(timeout=timeout)
            return True, True
        except subprocess.TimeoutExpired:
            return False, False
    deadline = time.monotonic() + timeout
    while True:
        info = os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
        if info is not None and info.si_pid:
            return True, False
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False, False
        time.sleep(min(0.002, remaining))


def _account_cpu(record: dict) -> bool:
    """Accumulate the delta between successive cumulative psutil CPU samples."""
    monitor = record.get("monitor")
    if monitor is None:
        return False
    try:
        times = monitor.cpu_times()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    total = times.user + times.system
    previous = record.get("cpu_sample", total)
    record["used"] += max(0.0, total - previous)
    record["cpu_sample"] = total
    return True


def _finish(record: dict) -> None:
    child = record.get("process")
    if child is not None:
        try:
            child.wait()
        except (ChildProcessError, OSError):
            pass
    record["finished"] = True
    record["runtime"] = time.perf_counter() - record["start"]


def main() -> int:
    try:
        number = int(input("Number of programs: "))
        quantum = float(input("Time quantum (seconds): "))
    except (ValueError, EOFError) as exc:
        print("Invalid program count or quantum:", exc)
        return 2
    if number <= 0:
        print("Number of programs must be greater than zero.")
        return 2
    if not math.isfinite(quantum) or quantum <= 0:
        print("Time quantum must be a finite positive number.")
        return 2

    processes = []
    for i in range(number):
        print(f"\nProgram {i + 1}")
        path = input("Program path: ").strip()
        try:
            weight = int(input("CPU share weight: "))
        except ValueError:
            print("CPU share weight must be an integer.")
            return 2
        if not path or weight <= 0:
            print("Program path must be non-empty and weight must be positive.")
            return 2
        processes.append({
            "name": f"P{i + 1}", "path": path, "weight": weight,
            "used": 0.0, "start": 0.0, "runtime": 0.0,
            "process": None, "monitor": None, "cpu_sample": 0.0,
            "finished": False, "launch_error": None,
        })

    # Start children suspended so they do not all run before scheduling begins.
    for record in processes:
        try:
            record["start"] = time.perf_counter()
            child = subprocess.Popen([record["path"]])
            record["process"] = child
            monitor = psutil.Process(child.pid)
            record["monitor"] = monitor
            monitor.suspend()
            sample = monitor.cpu_times()
            record["cpu_sample"] = sample.user + sample.system
        except (OSError, psutil.Error, subprocess.SubprocessError) as error:
            child = record.get("process")
            if child is not None:
                try:
                    exited, reaped = _wait_exit_without_reaping(child, 0.0)
                    if exited and not reaped:
                        _account_cpu(record)
                        _finish(record)
                        continue
                    if exited:
                        record["finished"] = True
                        record["runtime"] = time.perf_counter() - record["start"]
                        continue
                except Exception:
                    pass
            record["launch_error"] = str(error)
            record["finished"] = True
            record["runtime"] = time.perf_counter() - record["start"]
            print("Error starting", record["name"], error)

    while any(not record["finished"] for record in processes):
        available = [record for record in processes if not record["finished"]]
        current = min(available, key=lambda item: item["used"] / item["weight"])
        child = current["process"]
        monitor = current["monitor"]
        try:
            # Catch an exit between dispatches before attempting to resume a zombie.
            exited, already_reaped = _wait_exit_without_reaping(child, 0.0)
            if exited:
                if not already_reaped:
                    _account_cpu(current)
                    _finish(current)
                else:
                    current["finished"] = True
                    current["runtime"] = time.perf_counter() - current["start"]
                print(current["name"], "finished")
                continue

            monitor.resume()
            exited, already_reaped = _wait_exit_without_reaping(child, quantum)
            if exited:
                # On POSIX, sample the terminal counters while WNOWAIT keeps the
                # exited child available, then reap it with Popen.wait().
                if not already_reaped:
                    _account_cpu(current)
                    _finish(current)
                else:
                    current["finished"] = True
                    current["runtime"] = time.perf_counter() - current["start"]
                print(current["name"], "finished")
                continue

            # Quantum expired: freeze first, then add the cumulative CPU delta.
            monitor.suspend()
            _account_cpu(current)

            # Close the narrow race where the child exits just after the timeout.
            exited, already_reaped = _wait_exit_without_reaping(child, 0.0)
            if exited:
                if not already_reaped:
                    _account_cpu(current)
                    _finish(current)
                else:
                    current["finished"] = True
                    current["runtime"] = time.perf_counter() - current["start"]
                print(current["name"], "finished")

        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError) as error:
            # The process may have exited during resume/suspend; account it if the
            # zombie is still available before marking the process as finished.
            try:
                exited, reaped = _wait_exit_without_reaping(child, 0.0)
                if exited and not reaped:
                    _account_cpu(current)
                    _finish(current)
                    print(current["name"], "finished")
                    continue
            except Exception:
                pass
            print("Unable to control", current["name"], error)
            current["launch_error"] = str(error)
            current["finished"] = True
            current["runtime"] = time.perf_counter() - current["start"]

    # Safety cleanup: do not leave a child running when scheduling/control failed.
    for record in processes:
        child = record["process"]
        monitor = record["monitor"]
        if child is None or child.poll() is not None:
            continue
        try:
            if monitor is not None:
                monitor.resume()
            child.terminate()
            child.wait(timeout=2)
        except (psutil.Error, subprocess.SubprocessError, OSError):
            try:
                child.kill()
                child.wait(timeout=2)
            except (subprocess.SubprocessError, OSError):
                pass

    print("\nResults")
    print("Program\tCPU Time (s)\tWall Time (s)\tReturn Code\tStatus")
    for record in processes:
        child = record["process"]
        if child is None:
            print(f"{record['name']}\t-\t-\t-\tlaunch failed: {record['launch_error']}")
            continue
        status = "finished" if record["launch_error"] is None else record["launch_error"]
        print(
            f"{record['name']}\t{record['used']:.6f}\t"
            f"{record['runtime']:.6f}\t{child.returncode}\t{status}"
        )
    if not (hasattr(os, "waitid") and hasattr(os, "WNOWAIT")):
        print("Note: this platform lacks waitid(WNOWAIT); a very short terminal CPU slice may not be sampled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
