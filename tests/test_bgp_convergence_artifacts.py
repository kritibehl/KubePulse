import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BENCHMARK = (
    ROOT
    / "artifacts"
    / "network_lab"
    / "bgp_convergence_benchmark.json"
)

PCAP = (
    ROOT
    / "artifacts"
    / "network_lab"
    / "bgp_withdrawal_manual.pcap"
)


def load_benchmark():
    return json.loads(BENCHMARK.read_text())


def test_bgp_benchmark_has_ten_runs():
    data = load_benchmark()

    assert data["runs"] == 10
    assert len(data["run_results"]) == 10


def test_bgp_benchmark_statistics_are_ordered():
    data = load_benchmark()

    for stats in data["summary"].values():
        assert stats["min_ms"] <= stats["median_ms"]
        assert stats["median_ms"] <= stats["p95_ms"]
        assert stats["p95_ms"] <= stats["max_ms"]


def test_every_bgp_measurement_is_positive():
    data = load_benchmark()

    for run in data["run_results"]:
        for metric, value in run.items():
            if metric == "run":
                continue

            assert value > 0


def test_data_plane_recovery_is_subsecond_in_artifact():
    data = load_benchmark()

    recovery = data["summary"]["data_plane_recovery_ms"]

    assert recovery["median_ms"] < 1000
    assert recovery["p95_ms"] < 1000


def test_manual_bgp_capture_contains_packets():
    assert PCAP.exists()

    # A classic pcap containing only a global header is 24 bytes.
    assert PCAP.stat().st_size > 24
