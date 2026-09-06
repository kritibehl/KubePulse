package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"time"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/hubble"
)

func main() {
	address := flag.String(
		"address",
		"127.0.0.1:4245",
		"Hubble Relay gRPC address",
	)

	stableSelector := flag.String(
		"stable-selector",
		"k8s:cohort=stable",
		"Hubble label selector for stable cohort",
	)

	canarySelector := flag.String(
		"canary-selector",
		"k8s:cohort=canary",
		"Hubble label selector for canary cohort",
	)

	window := flag.Duration(
		"window",
		20*time.Second,
		"historical Hubble collection window",
	)

	flag.Parse()

	ctx, cancel := context.WithTimeout(
		context.Background(),
		20*time.Second,
	)
	defer cancel()

	client, err := hubble.Dial(ctx, *address)
	if err != nil {
		log.Fatalf("dial Hubble Relay: %v", err)
	}
	defer client.Close()

	status, err := client.ServerStatus(ctx)
	if err != nil {
		log.Fatalf("server status: %v", err)
	}

	fmt.Printf(
		"relay_version=%s connected_nodes=%d unavailable_nodes=%d flows_per_second=%.2f\n",
		status.Version,
		status.ConnectedNodes,
		status.UnavailableNodes,
		status.FlowsPerSecond,
	)

	until := time.Now().UTC()
	since := until.Add(-*window)

	fmt.Printf(
		"window_since=%s\nwindow_until=%s\n",
		since.Format(time.RFC3339Nano),
		until.Format(time.RFC3339Nano),
	)

	stable, err := client.CollectCohortStats(
		ctx,
		*stableSelector,
		since,
		until,
	)
	if err != nil {
		log.Fatalf("collect stable cohort: %v", err)
	}

	canary, err := client.CollectCohortStats(
		ctx,
		*canarySelector,
		since,
		until,
	)
	if err != nil {
		log.Fatalf("collect canary cohort: %v", err)
	}

	fmt.Printf(
		"stable selector=%q flow_events=%d lost_events=%d stats=%+v\n",
		*stableSelector,
		stable.FlowEvents,
		stable.LostEvents,
		stable.Stats,
	)

	fmt.Printf(
		"canary selector=%q flow_events=%d lost_events=%d stats=%+v\n",
		*canarySelector,
		canary.FlowEvents,
		canary.LostEvents,
		canary.Stats,
	)

	if stable.FlowEvents == 0 {
		log.Fatal("stable cohort returned zero Hubble flow events")
	}

	if canary.FlowEvents == 0 {
		log.Fatal("canary cohort returned zero Hubble flow events")
	}

	if stable.Stats.TotalFlows == 0 {
		log.Fatal("stable cohort classified zero flows")
	}

	if canary.Stats.TotalFlows == 0 {
		log.Fatal("canary cohort classified zero flows")
	}

	if stable.LostEvents != 0 || canary.LostEvents != 0 {
		log.Fatalf(
			"telemetry loss detected: stable=%d canary=%d",
			stable.LostEvents,
			canary.LostEvents,
		)
	}

	fmt.Println("real_cohort_collection=PASS")
}
