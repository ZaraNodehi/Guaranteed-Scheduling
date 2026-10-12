import subprocess
import time
import psutil

processes = []

number = int(input("Number of programs: "))
quantum = float(input("Time quantum (seconds): "))

for i in range(number):
    print(f"\nProgram {i + 1}")

    path = input("Program path: ")
    weight = int(input("CPU share weight: "))

    processes.append({
        "name": f"P{i + 1}",
        "path": path,
        "weight": weight,
        "used": 0.0,
        "start": 0,
        "runtime": 0.0,
        "process": None,
        "monitor": None,
        "finished": False
    })

for p in processes:
    try:
        p["start"] = time.perf_counter()
        p["process"] = subprocess.Popen([p["path"]])
        p["monitor"] = psutil.Process(p["process"].pid)
        p["monitor"].suspend()
    except Exception as error:
        print("Error starting", p["name"], error)
        p["finished"] = True

while any(not p["finished"] for p in processes):
    available = [
        p for p in processes
        if not p["finished"]
    ]

    if not available:
        break

    current = min(
        available,
        key=lambda p: p["used"] / p["weight"]
    )

    process = current["process"]
    monitor = current["monitor"]

    try:
        before = monitor.cpu_times()
        current["start"] = current["start"] or time.perf_counter()

        monitor.resume()

        try:
            process.wait(timeout=quantum)
            current["finished"] = True
            current["runtime"] = time.perf_counter() - current["start"]
            print(current["name"], "finished")
        except subprocess.TimeoutExpired:
            monitor.suspend()

            after = monitor.cpu_times()
            current["used"] += (
                after.user + after.system
                - before.user - before.system
            )

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        if process.poll() is not None:
            current["finished"] = True
            current["runtime"] = time.perf_counter() - current["start"]
        else:
            print("Unable to control", current["name"])
            current["finished"] = True

for p in processes:
    if p["process"] is not None and p["process"].poll() is None:
        try:
            p["monitor"].resume()
            p["process"].terminate()
            p["process"].wait()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

print("\nResults")
print("Program\tCPU Time\tRuntime\tReturn Code")

for p in processes:
    if p["process"] is not None:
        try:
            cpu_time = p["used"]
            print(
                f'{p["name"]}\t{round(cpu_time, 3)}\t\t'
                f'{round(p["runtime"], 3)}\t'
                f'{p["process"].returncode}'
            )
        except Exception:
            print(p["name"], "Result unavailable")
