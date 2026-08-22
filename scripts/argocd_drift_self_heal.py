#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


APP = "kubepulse-gitops"
ARGO_NS = "argocd"

DEPLOYMENT = "kubepulse-gitops-demo"
APP_NS = "kubepulse-gitops"

MANIFEST = Path(
    "experiments/gitops/app/deployment.yaml"
)

ARTIFACT = Path(
    "artifacts/gitops/argocd_drift_self_heal.json"
)


def run(*args: str) -> str:
    result = subprocess.run(
        list(args),
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def get_json(
    kind: str,
    name: str,
    namespace: str,
) -> dict:
    raw = run(
        "kubectl",
        "get",
        kind,
        name,
        "-n",
        namespace,
        "-o",
        "json",
    )
    return json.loads(raw)


def deployment_state() -> dict:
    data = get_json(
        "deployment",
        DEPLOYMENT,
        APP_NS,
    )

    return {
        "spec_replicas": data[
            "spec"
        ].get("replicas", 0),
        "ready_replicas": data.get(
            "status", {}
        ).get("readyReplicas", 0),
        "available_replicas": data.get(
            "status", {}
        ).get("availableReplicas", 0),
    }


def application_state() -> dict:
    data = get_json(
        "application",
        APP,
        ARGO_NS,
    )

    status = data.get("status", {})

    return {
        "sync": status.get(
            "sync", {}
        ).get("status"),
        "health": status.get(
            "health", {}
        ).get("status"),
        "revision": status.get(
            "sync", {}
        ).get("revision"),
    }


def patch_self_heal(enabled: bool) -> None:
    patch = {
        "spec": {
            "syncPolicy": {
                "automated": {
                    "selfHeal": enabled
                }
            }
        }
    }

    run(
        "kubectl",
        "patch",
        "application",
        APP,
        "-n",
        ARGO_NS,
        "--type",
        "merge",
        "-p",
        json.dumps(patch),
    )


def hard_refresh() -> None:
    run(
        "kubectl",
        "annotate",
        "application",
        APP,
        "-n",
        ARGO_NS,
        "argocd.argoproj.io/refresh=hard",
        "--overwrite",
    )


def wait_until(
    condition,
    description: str,
    timeout: float = 60.0,
    interval: float = 0.25,
):
    started = time.monotonic()

    while time.monotonic() - started < timeout:
        value = condition()

        if value:
            return value

        time.sleep(interval)

    raise RuntimeError(
        f"Timed out waiting for {description}"
    )


def git_desired_replicas() -> int:
    text = MANIFEST.read_text()

    match = re.search(
        r"^\s*replicas:\s*(\d+)\s*$",
        text,
        flags=re.MULTILINE,
    )

    if not match:
        raise RuntimeError(
            "Could not determine replicas from Git manifest"
        )

    return int(match.group(1))


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def main() -> int:
    desired = git_desired_replicas()

    if desired != 2:
        raise RuntimeError(
            f"Expected Git desired replicas=2, got {desired}"
        )

    initial_dep = deployment_state()
    initial_app = application_state()

    print("===== BASELINE =====")
    print("Git desired replicas:", desired)
    print("Deployment:", initial_dep)
    print("Argo:", initial_app)

    if (
        initial_dep["spec_replicas"] != 2
        or initial_dep["ready_replicas"] != 2
    ):
        raise RuntimeError(
            "Baseline deployment is not healthy at 2 replicas"
        )

    print()
    print("===== DISABLE SELF HEAL =====")

    patch_self_heal(False)

    time.sleep(2)

    self_heal_value = run(
        "kubectl",
        "get",
        "application",
        APP,
        "-n",
        ARGO_NS,
        "-o",
        "jsonpath={.spec.syncPolicy.automated.selfHeal}",
    )

    print("selfHeal:", self_heal_value)

    if self_heal_value != "false":
        raise RuntimeError(
            "Could not disable selfHeal"
        )

    print()
    print("===== INJECT DRIFT =====")

    drift_started_at = utc_now()

    run(
        "kubectl",
        "scale",
        "deployment",
        DEPLOYMENT,
        "-n",
        APP_NS,
        "--replicas=1",
    )

    drift_state = wait_until(
        lambda: (
            deployment_state()
            if deployment_state()[
                "spec_replicas"
            ] == 1
            else None
        ),
        "deployment spec replicas=1",
    )

    drift_ready_state = wait_until(
        lambda: (
            deployment_state()
            if deployment_state()[
                "ready_replicas"
            ] == 1
            else None
        ),
        "deployment ready replicas=1",
    )

    print(
        "Verified live drift:",
        drift_ready_state,
    )

    hard_refresh()

    out_of_sync = wait_until(
        lambda: (
            application_state()
            if application_state()[
                "sync"
            ] == "OutOfSync"
            else None
        ),
        "Argo CD OutOfSync state",
        timeout=90.0,
    )

    print(
        "Verified Argo drift detection:",
        out_of_sync,
    )

    print()
    print("===== ENABLE SELF HEAL =====")

    patch_self_heal(True)

    self_heal_enabled_at = utc_now()
    started = time.monotonic()

    observations = []

    workload_restoration_seconds = None
    convergence_seconds = None

    while time.monotonic() - started < 180:
        dep = deployment_state()
        app = application_state()

        elapsed = round(
            time.monotonic() - started,
            3,
        )

        observation = {
            "elapsed_seconds": elapsed,
            "deployment": dep,
            "application": app,
        }

        observations.append(observation)

        print(
            f"{elapsed:7.3f}s "
            f"spec={dep['spec_replicas']} "
            f"ready={dep['ready_replicas']} "
            f"available={dep['available_replicas']} "
            f"sync={app['sync']} "
            f"health={app['health']}"
        )

        workload_restored = (
            dep["spec_replicas"] == 2
            and dep["ready_replicas"] == 2
            and dep["available_replicas"] == 2
        )

        if (
            workload_restored
            and workload_restoration_seconds
            is None
        ):
            workload_restoration_seconds = elapsed

        fully_converged = (
            workload_restored
            and app["sync"] == "Synced"
            and app["health"] == "Healthy"
        )

        if fully_converged:
            convergence_seconds = elapsed
            break

        time.sleep(0.1)

    if convergence_seconds is None:
        patch_self_heal(True)
        raise RuntimeError(
            "Argo CD failed to converge within 180 seconds"
        )

    final_dep = deployment_state()
    final_app = application_state()

    report = {
        "experiment": (
            "argocd_gitops_drift_self_heal"
        ),
        "desired_state": {
            "source": "Git",
            "manifest": str(MANIFEST),
            "replicas": desired,
        },
        "baseline": {
            "deployment": initial_dep,
            "application": initial_app,
        },
        "injected_drift": {
            "started_at": drift_started_at,
            "self_heal_disabled": True,
            "live_spec_replicas": (
                drift_state["spec_replicas"]
            ),
            "live_ready_replicas": (
                drift_ready_state[
                    "ready_replicas"
                ]
            ),
            "argocd_sync_status": (
                out_of_sync["sync"]
            ),
            "git_desired_replicas": desired,
        },
        "self_heal": {
            "enabled_at": (
                self_heal_enabled_at
            ),
            "restored_replicas": (
                final_dep[
                    "spec_replicas"
                ]
            ),
            "workload_restoration_seconds": (
                workload_restoration_seconds
            ),
            "full_argocd_convergence_seconds": (
                convergence_seconds
            ),
        },
        "final_state": {
            "deployment": final_dep,
            "application": final_app,
        },
        "result": "PASS",
        "completed_at": utc_now(),
        "observations": observations,
    }

    ARTIFACT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ARTIFACT.write_text(
        json.dumps(
            report,
            indent=2,
        )
        + "\n"
    )

    print()
    print("===== RESULT =====")
    print(
        "PASS: live state drift was "
        "observed before self-healing"
    )
    print(
        "workload_restoration_seconds:",
        workload_restoration_seconds,
    )
    print(
        "full_argocd_convergence_seconds:",
        convergence_seconds,
    )
    print(
        "artifact:",
        ARTIFACT,
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        try:
            patch_self_heal(True)
        except Exception:
            pass
        raise
