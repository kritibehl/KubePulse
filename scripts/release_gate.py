import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


def http_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return 0


def pod_ready() -> bool:
    command = [
        "kubectl",
        "get",
        "pods",
        "-l",
        "app=kubepulse-demo-api",
        "-o",
        "json",
    ]

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    if not payload.get("items"):
        return False

    conditions = payload["items"][0].get("status", {}).get("conditions", [])

    return any(
        condition.get("type") == "Ready"
        and condition.get("status") == "True"
        for condition in conditions
    )


def dependency_ready(base_url: str) -> bool:
    return http_status(f"{base_url}/dependency") == 200


def build_contract(base_url: str) -> dict:
    health = http_status(f"{base_url}/health")
    ready = pod_ready()
    dependency = dependency_ready(base_url)

    if health != 200:
        decision = "BLOCK"
        reason = "http_health_unavailable"
    elif not ready:
        decision = "BLOCK"
        reason = "pod_not_ready"
    elif not dependency:
        decision = "BLOCK"
        reason = "postgresql_dependency_unavailable"
    else:
        decision = "ALLOW"
        reason = "release_policy_satisfied"

    return {
        "decision": decision,
        "reason": reason,
        "http_health": health,
        "pod_ready": ready,
        "dependency_ready": dependency,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:18080",
    )
    parser.add_argument("--output")
    parser.add_argument(
        "--expected-decision",
        choices=["ALLOW", "BLOCK"],
    )
    args = parser.parse_args()

    contract = build_contract(args.base_url)
    rendered = json.dumps(contract, indent=2)

    print(rendered)

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n")

    if args.expected_decision:
        if contract["decision"] != args.expected_decision:
            print(
                f"Expected {args.expected_decision}, "
                f"received {contract['decision']}",
                file=sys.stderr,
            )
            return 1

        return 0

    return 1 if contract["decision"] == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
