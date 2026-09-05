package plugin

import (
	"encoding/json"
	"testing"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"

	"github.com/argoproj/argo-rollouts/pkg/apis/rollouts/v1alpha1"
)

func thresholds() analysis.Thresholds {
	return analysis.Thresholds{
		MinFlows:        100,
		MinDNSQueries:   20,
		MinTCPAttempts:  20,
		MinHTTPRequests: 20,

		DNSFailureDelta: 0.02,
		DropRateDelta:   0.01,
		TCPFailureDelta: 0.02,
		HTTP5xxDelta:    0.02,
	}
}

func stableStats() analysis.CohortStats {
	return analysis.CohortStats{
		TotalFlows:   1000,
		DNSQueries:   200,
		DNSFailures:  1,
		TCPAttempts:  400,
		TCPFailures:  2,
		HTTPRequests: 500,
		HTTP5xx:      2,
		DroppedFlows: 1,
	}
}

func metricFor(
	t *testing.T,
	config Config,
) v1alpha1.Metric {
	t.Helper()

	raw, err := json.Marshal(config)
	if err != nil {
		t.Fatal(err)
	}

	return v1alpha1.Metric{
		Name: "network-regression",
		Provider: v1alpha1.MetricProvider{
			Plugin: map[string]json.RawMessage{
				Name: raw,
			},
		},
	}
}

func TestRunReturnsSuccessfulForHealthyCanary(t *testing.T) {
	p := &RPCPlugin{}

	metric := metricFor(
		t,
		Config{
			Stable: stableStats(),
			Canary: analysis.CohortStats{
				TotalFlows:   300,
				DNSQueries:   100,
				DNSFailures:  1,
				TCPAttempts:  120,
				TCPFailures:  1,
				HTTPRequests: 150,
				HTTP5xx:      1,
				DroppedFlows: 1,
			},
			Thresholds: thresholds(),
		},
	)

	got := p.Run(nil, metric)

	if got.Phase != v1alpha1.AnalysisPhaseSuccessful {
		t.Fatalf(
			"expected Successful, got %s: %s",
			got.Phase,
			got.Message,
		)
	}

	if got.Metadata["decision"] != "PASS" {
		t.Fatalf(
			"expected PASS metadata, got %+v",
			got.Metadata,
		)
	}
}

func TestRunReturnsFailedForNetworkRegression(t *testing.T) {
	p := &RPCPlugin{}

	metric := metricFor(
		t,
		Config{
			Stable: stableStats(),
			Canary: analysis.CohortStats{
				TotalFlows:   300,
				DNSQueries:   100,
				DNSFailures:  12,
				TCPAttempts:  120,
				TCPFailures:  15,
				HTTPRequests: 150,
				HTTP5xx:      12,
				DroppedFlows: 10,
			},
			Thresholds: thresholds(),
		},
	)

	got := p.Run(nil, metric)

	if got.Phase != v1alpha1.AnalysisPhaseFailed {
		t.Fatalf(
			"expected Failed, got %s: %s",
			got.Phase,
			got.Message,
		)
	}

	if got.Metadata["decision"] != "FAIL" {
		t.Fatalf(
			"expected FAIL metadata, got %+v",
			got.Metadata,
		)
	}
}

func TestRunReturnsInconclusiveForTooLittleTraffic(
	t *testing.T,
) {
	p := &RPCPlugin{}

	metric := metricFor(
		t,
		Config{
			Stable: stableStats(),
			Canary: analysis.CohortStats{
				TotalFlows: 3,
			},
			Thresholds: thresholds(),
		},
	)

	got := p.Run(nil, metric)

	if got.Phase != v1alpha1.AnalysisPhaseInconclusive {
		t.Fatalf(
			"expected Inconclusive, got %s: %s",
			got.Phase,
			got.Message,
		)
	}
}

func TestRunReturnsErrorForMissingPluginConfiguration(
	t *testing.T,
) {
	p := &RPCPlugin{}

	got := p.Run(
		nil,
		v1alpha1.Metric{
			Name: "network-regression",
		},
	)

	if got.Phase != v1alpha1.AnalysisPhaseError {
		t.Fatalf(
			"expected Error, got %s",
			got.Phase,
		)
	}
}

func TestPluginType(t *testing.T) {
	p := &RPCPlugin{}

	if got := p.Type(); got != "RPCPlugin" {
		t.Fatalf(
			"expected RPCPlugin, got %q",
			got,
		)
	}
}
