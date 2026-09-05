package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"
)

func main() {
	stable := analysis.CohortStats{
		TotalFlows:   1000,
		DNSQueries:   200,
		DNSFailures:  1,
		TCPAttempts:  400,
		TCPFailures:  2,
		HTTPRequests: 500,
		HTTP5xx:      2,
		DroppedFlows: 1,
	}

	canary := analysis.CohortStats{
		TotalFlows:   300,
		DNSQueries:   100,
		DNSFailures:  12,
		TCPAttempts:  120,
		TCPFailures:  15,
		HTTPRequests: 150,
		HTTP5xx:      12,
		DroppedFlows: 10,
	}

	thresholds := analysis.Thresholds{
		MinFlows:        100,
		MinDNSQueries:   20,
		MinTCPAttempts:  20,
		MinHTTPRequests: 20,

		DNSFailureDelta: 0.02,
		DropRateDelta:   0.01,
		TCPFailureDelta: 0.02,
		HTTP5xxDelta:    0.02,
	}

	report := analysis.Analyze(
		stable,
		canary,
		thresholds,
	)

	encoded, err := json.MarshalIndent(
		report,
		"",
		"  ",
	)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	fmt.Println(string(encoded))

	if report.Decision == analysis.DecisionFail {
		os.Exit(2)
	}
}
