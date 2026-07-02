from network_operations_pack.ops_pack import as_dicts


def test_network_ops_pack_has_required_scenarios():
    scenarios = {i["scenario"] for i in as_dicts()}

    assert "dns_resolution_failure" in scenarios
    assert "tcp_connection_timeout" in scenarios
    assert "blocked_port_iptables" in scenarios
    assert "packet_loss_latency_spike" in scenarios
    assert "service_unreachable_health_green" in scenarios


def test_network_ops_pack_has_required_fields():
    required = {
        "incident_severity",
        "detected_symptom",
        "probable_root_cause",
        "commands_used_for_diagnosis",
        "pre_change_verification",
        "post_change_verification",
        "recommended_escalation",
        "operate_decision",
        "release_decision",
    }

    for incident in as_dicts():
        assert required.issubset(incident.keys())


def test_health_green_dependency_failure_blocks_release():
    incident = [
        i for i in as_dicts()
        if i["scenario"] == "service_unreachable_health_green"
    ][0]

    assert incident["incident_severity"] == "critical"
    assert incident["operate_decision"] == "unsafe_to_operate"
    assert incident["release_decision"] == "block"
