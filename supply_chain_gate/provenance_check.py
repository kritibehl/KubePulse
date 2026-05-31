import json
from pathlib import Path

artifact = {
    "artifact": "kubepulse:latest",
    "provenance_present": True,
    "signed_artifact": False,
    "dependency_review_passed": True,
    "build_reproducible": True
}

violations = []
if not artifact["provenance_present"]:
    violations.append("missing_provenance")
if not artifact["signed_artifact"]:
    violations.append("unsigned_artifact")
if not artifact["dependency_review_passed"]:
    violations.append("dependency_policy_violation")

decision = {
    **artifact,
    "violations": violations,
    "release_decision": "block" if violations else "continue"
}

Path("supply_chain_gate/build_integrity_result.json").write_text(json.dumps(decision, indent=2))

print(json.dumps(decision, indent=2))
