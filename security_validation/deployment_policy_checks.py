from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML required: pip install pyyaml")


def load(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text())


def validate(doc: dict) -> dict:
    annotations = doc.get("metadata", {}).get("annotations", {})
    containers = (
        doc.get("spec", {})
        .get("template", {})
        .get("spec", {})
        .get("containers", [])
    )

    violations = []

    if annotations.get("kubepulse.io/tls") != "enabled":
        violations.append("missing_tls")

    if annotations.get("kubepulse.io/auth") != "required":
        violations.append("missing_auth")

    for c in containers:
        env = {e.get("name"): e.get("value") for e in c.get("env", [])}
        if env.get("DEBUG") == "true" or env.get("ALLOW_INSECURE_HTTP") == "true":
            violations.append("insecure_env_var")

        if "resources" not in c or "limits" not in c.get("resources", {}):
            violations.append("missing_resource_limits")

        if "readinessProbe" not in c or "livenessProbe" not in c:
            violations.append("missing_health_probe")

    decision = "block" if violations else "continue"

    return {
        "violations": sorted(set(violations)),
        "release_decision": decision,
        "safe_to_operate": decision == "continue",
    }


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "security_validation/sample_insecure_deployment.yaml"
    result = validate(load(path))
    print(result)


if __name__ == "__main__":
    main()
