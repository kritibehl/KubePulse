#!/usr/bin/env python3

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path


def aws(region, *args):
    cmd = ["aws", *args, "--region", region, "--output", "json"]
    result = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_report(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="eu-north-1")
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    started = time.time()

    while time.time() - started < args.timeout:
        service_data = aws(
            args.region,
            "ecs",
            "describe-services",
            "--cluster",
            args.cluster,
            "--services",
            args.service,
        )

        service = service_data["services"][0]

        deployment = next(
            (
                d
                for d in service.get("deployments", [])
                if d.get("taskDefinition") == args.candidate
            ),
            None,
        )

        if deployment:
            rollout = deployment.get("rolloutState", "UNKNOWN")

            print(
                f'{now()} candidate={args.candidate.split(":")[-1]} '
                f'rollout={rollout} '
                f'running={deployment.get("runningCount", 0)} '
                f'pending={deployment.get("pendingCount", 0)}'
            )

            if rollout == "FAILED":
                report = {
                    "decision": "BLOCK",
                    "reason": "candidate_deployment_failed",
                    "candidate_task_definition": args.candidate,
                    "rollout_state": rollout,
                    "timestamp_utc": now(),
                }
                write_report(args.report, report)
                print(json.dumps(report, indent=2))
                return 1

            task_list = aws(
                args.region,
                "ecs",
                "list-tasks",
                "--cluster",
                args.cluster,
                "--service-name",
                args.service,
                "--desired-status",
                "RUNNING",
            ).get("taskArns", [])

            if task_list:
                task_data = aws(
                    args.region,
                    "ecs",
                    "describe-tasks",
                    "--cluster",
                    args.cluster,
                    "--tasks",
                    *task_list,
                )

                candidate_tasks = [
                    t
                    for t in task_data.get("tasks", [])
                    if t.get("taskDefinitionArn") == args.candidate
                ]

                for task in candidate_tasks:
                    health = task.get("healthStatus", "UNKNOWN")
                    last = task.get("lastStatus", "UNKNOWN")

                    print(
                        f'  task={task["taskArn"].split("/")[-1]} '
                        f'status={last} health={health}'
                    )

                    if health == "UNHEALTHY":
                        report = {
                            "decision": "BLOCK",
                            "reason": "candidate_task_unhealthy",
                            "candidate_task_definition": args.candidate,
                            "task_arn": task["taskArn"],
                            "task_health": health,
                            "timestamp_utc": now(),
                        }
                        write_report(args.report, report)
                        print(json.dumps(report, indent=2))
                        return 1

                    if rollout == "COMPLETED" and health == "HEALTHY":
                        report = {
                            "decision": "ALLOW",
                            "reason": "candidate_healthy",
                            "candidate_task_definition": args.candidate,
                            "task_arn": task["taskArn"],
                            "task_health": health,
                            "timestamp_utc": now(),
                        }
                        write_report(args.report, report)
                        print(json.dumps(report, indent=2))
                        return 0

        time.sleep(5)

    report = {
        "decision": "BLOCK",
        "reason": "candidate_failed_to_become_healthy_before_timeout",
        "candidate_task_definition": args.candidate,
        "timeout_seconds": args.timeout,
        "timestamp_utc": now(),
    }

    write_report(args.report, report)
    print(json.dumps(report, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
