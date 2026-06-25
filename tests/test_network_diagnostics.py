from network_diagnostics.checks import classify_root_cause, remediation_for
from network_diagnostics.latency_check import run_latency_check


def test_latency_check_fails_when_threshold_exceeded():
    result = run_latency_check(780, 300, "edge-api")
    assert result["status"] == "fail"
    assert result["name"] == "latency"


def test_classifies_tcp_failure_as_binding_or_closed_port():
    results = [
        {"name": "dns_resolution", "status": "pass", "target": "localhost", "evidence": "ok"},
        {"name": "tcp_reachability", "status": "fail", "target": "localhost:5000", "evidence": "connection refused"},
    ]
    assert classify_root_cause(results) == "Host binding failure or closed port"


def test_remediation_for_binding_failure():
    remediation = remediation_for("Host binding failure or closed port")
    assert "bind service to 0.0.0.0 instead of localhost" in remediation
