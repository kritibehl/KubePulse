#!/usr/bin/env python3

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

LAB = "kubepulse-netns-lab"
PREFIX = "10.20.2.0/24"
DESTINATION = "10.20.2.10"
PEER = "10.12.0.2"

OUT = Path("artifacts/network_lab/bgp_convergence.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

POLL_INTERVAL_SECONDS = 0.02
TIMEOUT_SECONDS = 8.0


def run(cmd):
    return subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )


def vtysh(pathspace, *commands):
    cmd = [
        "docker", "exec", LAB,
        "vtysh", "-N", pathspace,
    ]

    for command in commands:
        cmd += ["-c", command]

    return run(cmd)


def bgp_route_present():
    result = vtysh(
        "r1",
        f"show ip bgp {PREFIX}",
    )

    return (
        result.returncode == 0
        and "Network not in table" not in result.stdout
        and "BGP routing table entry" in result.stdout
    )


def kernel_route_present():
    result = run([
        "docker", "exec", LAB,
        "ip", "-n", "r1",
        "route", "get", DESTINATION,
    ])

    return (
        result.returncode == 0
        and "via 10.12.0.2" in result.stdout
    )


def ping_success():
    result = run([
        "docker", "exec", LAB,
        "ip", "netns", "exec", "h1",
        "ping",
        "-c", "1",
        "-W", "0.2",
        DESTINATION,
    ])

    return result.returncode == 0


def peer_established():
    result = vtysh(
        "r1",
        f"show bgp neighbors {PEER}",
    )

    return "BGP state = Established" in result.stdout


def ms_since(start_ns):
    return round(
        (time.monotonic_ns() - start_ns) / 1_000_000,
        3,
    )


def observe_withdrawal(start_ns):
    observed = {
        "bgp_route_removed_ms": None,
        "fib_route_removed_ms": None,
        "data_plane_failure_ms": None,
    }

    deadline = time.monotonic() + TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        if (
            observed["bgp_route_removed_ms"] is None
            and not bgp_route_present()
        ):
            observed["bgp_route_removed_ms"] = ms_since(start_ns)

        if (
            observed["fib_route_removed_ms"] is None
            and not kernel_route_present()
        ):
            observed["fib_route_removed_ms"] = ms_since(start_ns)

        if (
            observed["data_plane_failure_ms"] is None
            and not ping_success()
        ):
            observed["data_plane_failure_ms"] = ms_since(start_ns)

        if all(value is not None for value in observed.values()):
            return observed

        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError(
        f"Timed out observing withdrawal: {observed}"
    )


def observe_restore(start_ns):
    observed = {
        "bgp_route_restored_ms": None,
        "fib_route_restored_ms": None,
        "data_plane_recovery_ms": None,
    }

    deadline = time.monotonic() + TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        if (
            observed["bgp_route_restored_ms"] is None
            and bgp_route_present()
        ):
            observed["bgp_route_restored_ms"] = ms_since(start_ns)

        if (
            observed["fib_route_restored_ms"] is None
            and kernel_route_present()
        ):
            observed["fib_route_restored_ms"] = ms_since(start_ns)

        if (
            observed["data_plane_recovery_ms"] is None
            and ping_success()
        ):
            observed["data_plane_recovery_ms"] = ms_since(start_ns)

        if all(value is not None for value in observed.values()):
            return observed

        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError(
        f"Timed out observing restoration: {observed}"
    )


def withdraw():
    return vtysh(
        "r2",
        "configure terminal",
        "router bgp 65002",
        "address-family ipv4 unicast",
        f"no network {PREFIX}",
    )


def restore():
    return vtysh(
        "r2",
        "configure terminal",
        "router bgp 65002",
        "address-family ipv4 unicast",
        f"network {PREFIX}",
    )


def main():
    print("===== BGP CONVERGENCE MEASUREMENT =====")

    baseline = {
        "peer_established": peer_established(),
        "bgp_route_present": bgp_route_present(),
        "fib_route_present": kernel_route_present(),
        "data_plane_reachable": ping_success(),
    }

    print("Baseline:", baseline)

    if not all(baseline.values()):
        raise RuntimeError(
            "Baseline is not healthy; refusing to run failure injection."
        )

    result = {
        "schema_version": 1,
        "experiment": "ebgp_prefix_withdrawal_and_restore",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "topology": {
            "r1_as": 65001,
            "r2_as": 65002,
            "r1_peer": "10.12.0.2",
            "r2_peer": "10.12.0.1",
            "advertised_prefix": PREFIX,
            "probe_destination": DESTINATION,
        },
        "measurement": {
            "clock": "python_time.monotonic_ns",
            "observation_point": "host-driven docker exec polling",
            "requested_poll_interval_ms": (
                POLL_INTERVAL_SECONDS * 1000
            ),
            "note": (
                "Observed latencies include docker exec and command "
                "execution overhead; they are lab-observed convergence "
                "times, not wire-speed protocol processing times."
            ),
        },
        "baseline": baseline,
    }

    restored = False

    try:
        print("\n===== WITHDRAW PREFIX =====")

        withdrawal_start_ns = time.monotonic_ns()

        command_start_ns = withdrawal_start_ns
        withdrawal_cmd = withdraw()
        command_end_ns = time.monotonic_ns()

        if withdrawal_cmd.returncode != 0:
            raise RuntimeError(
                f"Withdrawal command failed:\n"
                f"{withdrawal_cmd.stderr}"
            )

        withdrawal = observe_withdrawal(
            withdrawal_start_ns
        )

        withdrawal["command_duration_ms"] = round(
            (command_end_ns - command_start_ns)
            / 1_000_000,
            3,
        )

        withdrawal["peer_established_after_withdrawal"] = (
            peer_established()
        )

        print("Withdrawal observations:", withdrawal)

        if not withdrawal[
            "peer_established_after_withdrawal"
        ]:
            raise RuntimeError(
                "BGP peer dropped during prefix withdrawal."
            )

        print("\n===== RESTORE PREFIX =====")

        restore_start_ns = time.monotonic_ns()

        command_start_ns = restore_start_ns
        restore_cmd = restore()
        command_end_ns = time.monotonic_ns()

        if restore_cmd.returncode != 0:
            raise RuntimeError(
                f"Restore command failed:\n"
                f"{restore_cmd.stderr}"
            )

        restoration = observe_restore(
            restore_start_ns
        )

        restoration["command_duration_ms"] = round(
            (command_end_ns - command_start_ns)
            / 1_000_000,
            3,
        )

        restoration["peer_established_after_restore"] = (
            peer_established()
        )

        restored = True

        print("Restore observations:", restoration)

        final = {
            "peer_established": peer_established(),
            "bgp_route_present": bgp_route_present(),
            "fib_route_present": kernel_route_present(),
            "data_plane_reachable": ping_success(),
        }

        if not all(final.values()):
            raise RuntimeError(
                f"Final health check failed: {final}"
            )

        result["withdrawal"] = withdrawal
        result["restoration"] = restoration
        result["final"] = final

        result["derived"] = {
            "control_plane_withdrawal_ms": withdrawal[
                "bgp_route_removed_ms"
            ],
            "fib_withdrawal_ms": withdrawal[
                "fib_route_removed_ms"
            ],
            "data_plane_failure_ms": withdrawal[
                "data_plane_failure_ms"
            ],
            "control_plane_restore_ms": restoration[
                "bgp_route_restored_ms"
            ],
            "fib_restore_ms": restoration[
                "fib_route_restored_ms"
            ],
            "data_plane_recovery_ms": restoration[
                "data_plane_recovery_ms"
            ],
        }

        OUT.write_text(
            json.dumps(result, indent=2) + "\n"
        )

        print("\n===== PASS =====")
        print(f"Artifact: {OUT}")

        print(
            "Withdrawal BGP RIB:",
            result["derived"][
                "control_plane_withdrawal_ms"
            ],
            "ms",
        )

        print(
            "Withdrawal Linux FIB:",
            result["derived"][
                "fib_withdrawal_ms"
            ],
            "ms",
        )

        print(
            "Observed data-plane failure:",
            result["derived"][
                "data_plane_failure_ms"
            ],
            "ms",
        )

        print(
            "Restore BGP RIB:",
            result["derived"][
                "control_plane_restore_ms"
            ],
            "ms",
        )

        print(
            "Restore Linux FIB:",
            result["derived"][
                "fib_restore_ms"
            ],
            "ms",
        )

        print(
            "Observed data-plane recovery:",
            result["derived"][
                "data_plane_recovery_ms"
            ],
            "ms",
        )

    finally:
        if not restored:
            # Fail-safe: never intentionally leave the lab withdrawn.
            restore()
            time.sleep(1)


if __name__ == "__main__":
    main()
