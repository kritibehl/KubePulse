VALIDATION_MATRIX = [
    {"scenario": "readiness_false_positive", "failure_class": "topology_failover", "release_action": "reroute"},
    {"scenario": "multi_service_cascade", "failure_class": "dependency_latency_propagation", "release_action": "block"},
    {"scenario": "packet_loss", "failure_class": "transport_degradation", "release_action": "block"},
    {"scenario": "jitter", "failure_class": "latency_variability", "release_action": "reroute"},
]
