package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"time"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"
	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/hubble"
)

func contains(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}

	return false
}

func main() {
	address := flag.String(
		"address",
		"127.0.0.1:4245",
		"Hubble Relay gRPC address",
	)

	stableSelector := flag.String(
		"stable-selector",
		"k8s:cohort=stable",
		"Hubble stable cohort selector",
	)

	canarySelector := flag.String(
		"canary-selector",
		"k8s:cohort=canary",
		"Hubble canary cohort selector",
	)

	window := flag.Duration(
		"window",
		25*time.Second,
		"Hubble observation window",
	)

	flag.Parse()

	ctx, cancel := context.WithTimeout(
		context.Background(),
		30*time.Second,
	)
	defer cancel()

	client, err := hubble.Dial(ctx, *address)
	if err != nil {
		log.Fatalf("dial Hubble Relay: %v", err)
	}
	defer client.Close()

	status, err := client.ServerStatus(ctx)
	if err != nil {
		log.Fatalf("Hubble ServerStatus: %v", err)
	}

	fmt.Printf(
		"relay_version=%s connected_nodes=%d unavailable_nodes=%d flows_per_second=%.2f\n",
		status.Version,
		status.ConnectedNodes,
		status.UnavailableNodes,
		status.FlowsPerSecond,
	)

	if status.ConnectedNodes == 0 {
		log.Fatal("Hubble Relay has zero connected nodes")
	}

	if status.UnavailableNodes != 0 {
		log.Fatalf(
			"Hubble Relay has unavailable nodes: %d",
			status.UnavailableNodes,
		)
	}

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

	if stable.LostEvents != 0 || canary.LostEvents != 0 {
		log.Fatalf(
			"telemetry loss detected: stable=%d canary=%d",
			stable.LostEvents,
			canary.LostEvents,
		)
	}

	thresholds := analysis.Thresholds{
		MinFlows:        20,
		MinDNSQueries:   1,
		MinTCPAttempts:  10,
		MinHTTPRequests: 1,

		DNSFailureDelta: 0.10,
		DropRateDelta:   0.10,
		TCPFailureDelta: 0.10,
		HTTP5xxDelta:    0.10,
	}

	fmt.Printf(
		"thresholds=%+v\n",
		thresholds,
	)

	report := analysis.Analyze(
		stable.Stats,
		canary.Stats,
		thresholds,
	)

	encoded, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		log.Fatalf("encode analysis report: %v", err)
	}

	fmt.Println("===== KUBEPULSE ANALYSIS REPORT =====")
	fmt.Println(string(encoded))

	if report.Decision != analysis.DecisionFail {
		log.Fatalf(
			"expected FAIL decision, got %s",
			report.Decision,
		)
	}

	if !contains(report.Regressions, "drop_rate") {
		log.Fatalf(
			"expected drop_rate regression, got %v",
			report.Regressions,
		)
	}

	fmt.Println("real_network_regression_decision=FAIL")
	fmt.Println("real_hubble_to_analyzer=PASS")
}
