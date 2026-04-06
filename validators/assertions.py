from __future__ import annotations

def evaluate_assertions(report: dict, scenario_spec: dict) -> dict:
    must_hold = scenario_spec.get("must_hold_invariants", [])
    must_not = scenario_spec.get("must_not_happen", [])

    failures = []

    if "no full outage" in must_hold and bool(report.get("full_outage", False)):
        failures.append("full outage occurred")
    if "eventual recovery" in must_hold and report.get("status") == "fail":
        failures.append("recovery did not complete")
    if "decision report emitted" in must_hold and not report.get("decision_artifact"):
        failures.append("decision artifact missing")
    if "path diagnosis emitted" in must_hold and not report.get("path_trace_correlation"):
        failures.append("path diagnosis missing")
    if "compare view emitted" in must_hold and not report.get("compare_view"):
        failures.append("compare view missing")

    if "safe_to_operate true during brownout if SLO violated" in must_not:
        if report.get("safe_to_operate") and not report.get("slo_met", False):
            failures.append("safe_to_operate true despite SLO violation")
    if "safe_to_operate true when downstream unresolved" in must_not:
        if report.get("safe_to_operate") and report.get("status") == "fail":
            failures.append("safe_to_operate true while downstream unresolved")
    if "probes stay trusted if dependency unreachable" in must_not:
        if report.get("probes_say_healthy") and report.get("status") == "fail":
            failures.append("probes trusted during unreachable state")

    return {
        "assertions_passed": len(failures) == 0,
        "assertion_failures": failures,
    }
