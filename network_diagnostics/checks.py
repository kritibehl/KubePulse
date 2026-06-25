from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class CheckResult:
    name: str
    status: str
    target: str
    evidence: str
    latency_ms: float = 0.0


def result(name: str, status: str, target: str, evidence: str, latency_ms: float = 0.0) -> Dict[str, Any]:
    return asdict(CheckResult(name, status, target, evidence, latency_ms))


def classify_root_cause(results: List[Dict[str, Any]]) -> str:
    by_name = {r["name"]: r for r in results}

    if by_name.get("dns_resolution", {}).get("status") == "fail":
        return "DNS resolution failure"
    if by_name.get("tcp_reachability", {}).get("status") == "fail":
        return "Host binding failure or closed port"
    if by_name.get("http_health", {}).get("status") == "fail":
        return "HTTP health endpoint failure"
    if by_name.get("latency", {}).get("status") == "fail":
        return "High latency or timeout behavior"
    if by_name.get("dependency_reachability", {}).get("status") == "fail":
        return "Dependency unreachable"

    return "No network reachability failure detected"


def remediation_for(root_cause: str) -> List[str]:
    if root_cause == "DNS resolution failure":
        return [
            "verify DNS record exists",
            "check service discovery configuration",
            "validate resolver configuration",
            "confirm dependency hostname",
        ]
    if root_cause == "Host binding failure or closed port":
        return [
            "bind service to 0.0.0.0 instead of localhost",
            "verify firewall or security group rules",
            "confirm process is listening on expected port",
            "restart service after config fix",
        ]
    if root_cause == "HTTP health endpoint failure":
        return [
            "verify health endpoint path",
            "check upstream dependency health",
            "review application logs",
            "restart unhealthy service instance",
        ]
    if root_cause == "High latency or timeout behavior":
        return [
            "check packet loss and route quality",
            "review p95/p99 latency drift",
            "inspect dependency saturation",
            "increase timeout only after root cause is understood",
        ]
    if root_cause == "Dependency unreachable":
        return [
            "verify dependency host and port",
            "check network route between services",
            "validate DNS and service discovery",
            "fail over or block rollout until dependency recovers",
        ]
    return ["continue monitoring"]
