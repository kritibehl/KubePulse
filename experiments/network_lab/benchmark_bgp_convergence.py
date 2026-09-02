#!/usr/bin/env python3

import json
import statistics
import subprocess
import time
from pathlib import Path

RUNS = 10

MEASURE_SCRIPT = Path(
    "experiments/network_lab/measure_bgp_convergence.py"
)

LATEST = Path(
    "artifacts/network_lab/bgp_convergence.json"
)

OUTPUT = Path(
    "artifacts/network_lab/bgp_convergence_benchmark.json"
)


def percentile(values, p):
    values = sorted(values)

    if len(values) == 1:
        return values[0]

    position = (len(values) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)

    fraction = position - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * fraction
    )


def summary(values):
    return {
        "min_ms": round(min(values), 3),
        "median_ms": round(statistics.median(values), 3),
        "p95_ms": round(percentile(values, 0.95), 3),
        "max_ms": round(max(values), 3),
        "mean_ms": round(statistics.mean(values), 3),
    }


def main():
    results = []

    for run_number in range(1, RUNS + 1):
        print()
        print("=" * 60)
        print(f"RUN {run_number}/{RUNS}")
        print("=" * 60)

        completed = subprocess.run(
            ["python3", str(MEASURE_SCRIPT)],
            text=True,
        )

        if completed.returncode != 0:
            raise SystemExit(
                f"Run {run_number} failed."
            )

        data = json.loads(LATEST.read_text())

        data["benchmark_run"] = run_number
        results.append(data)

        run_file = Path(
            "artifacts/network_lab/"
            f"bgp_convergence_run_{run_number:02d}.json"
        )

        run_file.write_text(
            json.dumps(data, indent=2) + "\n"
        )

        # Allow the restored baseline to settle.
        time.sleep(0.5)

    metrics = {
        "control_plane_withdrawal_ms": [],
        "fib_withdrawal_ms": [],
        "data_plane_failure_ms": [],
        "control_plane_restore_ms": [],
        "fib_restore_ms": [],
        "data_plane_recovery_ms": [],
    }

    for result in results:
        for metric in metrics:
            metrics[metric].append(
                result["derived"][metric]
            )

    report = {
        "schema_version": 1,
        "experiment": (
            "ebgp_prefix_withdrawal_restore_benchmark"
        ),
        "runs": RUNS,
        "measurement_warning": (
            "Measurements are host-observed lab latencies. "
            "Each state probe invokes docker exec and therefore "
            "includes command startup and polling overhead. "
            "Do not interpret differences between BGP, FIB and "
            "data-plane observation timestamps as exact internal "
            "protocol processing order."
        ),
        "summary": {
            metric: summary(values)
            for metric, values in metrics.items()
        },
        "run_results": [
            {
                "run": result["benchmark_run"],
                **result["derived"],
            }
            for result in results
        ],
    }

    OUTPUT.write_text(
        json.dumps(report, indent=2) + "\n"
    )

    print()
    print("=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)

    for metric, stats in report["summary"].items():
        print()
        print(metric)
        print(
            f"  min    = {stats['min_ms']} ms"
        )
        print(
            f"  median = {stats['median_ms']} ms"
        )
        print(
            f"  p95    = {stats['p95_ms']} ms"
        )
        print(
            f"  max    = {stats['max_ms']} ms"
        )

    print()
    print(f"Artifact: {OUTPUT}")


if __name__ == "__main__":
    main()
