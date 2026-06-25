import json
from pathlib import Path


def test_reachability_scenarios_have_release_decision():
    expected = {
        "dns_failure.json",
        "port_closed.json",
        "localhost_binding_failure.json",
        "dependency_timeout.json",
        "high_latency.json",
    }
    for path in Path("scenarios").glob("*.json"):
        if path.name in expected:
            data = json.loads(path.read_text())
            assert data["release_decision"] == "block"


def test_network_report_shape():
    data = json.loads(Path("reports/network_reachability_report.json").read_text())
    assert data["incident"] == "Service unreachable"
    assert "root_cause" in data
    assert "suggested_remediation" in data
