package plugin

import (
	"context"
	"encoding/json"
	"errors"
	"testing"
	"time"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"
	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/hubble"

	"github.com/argoproj/argo-rollouts/pkg/apis/rollouts/v1alpha1"
)

type fakeCollector struct {
	results map[string]hubble.Collection
	errors  map[string]error

	calls  []string
	closed bool
}

func (f *fakeCollector) CollectCohortStats(
	ctx context.Context,
	selector string,
	since time.Time,
	until time.Time,
) (hubble.Collection, error) {
	f.calls = append(
		f.calls,
		selector,
	)

	if err := f.errors[selector]; err != nil {
		return hubble.Collection{}, err
	}

	return f.results[selector], nil
}

func (f *fakeCollector) Close() error {
	f.closed = true
	return nil
}

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

func stableCollection() hubble.Collection {
	stats := analysis.CohortStats{
		TotalFlows:   1000,
		DNSQueries:   200,
		DNSFailures:  1,
		TCPAttempts:  400,
		TCPFailures:  2,
		HTTPRequests: 500,
		HTTP5xx:      2,
		DroppedFlows: 1,
	}

	return hubble.Collection{
		Stats:      stats,
		FlowEvents: uint64(stats.TotalFlows),
	}
}

func healthyCanaryCollection() hubble.Collection {
	stats := analysis.CohortStats{
		TotalFlows:   300,
		DNSQueries:   100,
		DNSFailures:  1,
		TCPAttempts:  120,
		TCPFailures:  1,
		HTTPRequests: 150,
		HTTP5xx:      1,
		DroppedFlows: 1,
	}

	return hubble.Collection{
		Stats:      stats,
		FlowEvents: uint64(stats.TotalFlows),
	}
}

func badCanaryCollection() hubble.Collection {
	stats := analysis.CohortStats{
		TotalFlows:   300,
		DNSQueries:   100,
		DNSFailures:  12,
		TCPAttempts:  120,
		TCPFailures:  15,
		HTTPRequests: 150,
		HTTP5xx:      12,
		DroppedFlows: 10,
	}

	return hubble.Collection{
		Stats:      stats,
		FlowEvents: uint64(stats.TotalFlows),
	}
}

func baseConfig() Config {
	return Config{
		HubbleRelay: "127.0.0.1:4245",

		StableSelector: "app=checkout,role=stable",

		CanarySelector: "app=checkout,role=canary",

		WindowSeconds:       60,
		QueryTimeoutSeconds: 5,
		MaxLostEvents:       0,

		Thresholds: thresholds(),
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

func pluginWithCollector(
	collector *fakeCollector,
) *RPCPlugin {
	return &RPCPlugin{
		NewCollector: func(
			ctx context.Context,
			address string,
		) (CohortCollector, error) {
			if address != "127.0.0.1:4245" {
				return nil, errors.New(
					"unexpected relay address",
				)
			}

			return collector, nil
		},

		Now: func() time.Time {
			return time.Date(
				2026,
				time.September,
				5,
				21,
				0,
				0,
				0,
				time.UTC,
			)
		},
	}
}

func TestRunCollectsHubbleAndReturnsSuccessful(
	t *testing.T,
) {
	config := baseConfig()

	collector := &fakeCollector{
		results: map[string]hubble.Collection{
			config.StableSelector: stableCollection(),

			config.CanarySelector: healthyCanaryCollection(),
		},
		errors: map[string]error{},
	}

	p := pluginWithCollector(collector)

	got := p.Run(
		nil,
		metricFor(t, config),
	)

	if got.Phase !=
		v1alpha1.AnalysisPhaseSuccessful {
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

	if len(collector.calls) != 2 {
		t.Fatalf(
			"expected 2 Hubble queries, got %d",
			len(collector.calls),
		)
	}

	if !collector.closed {
		t.Fatal(
			"expected Hubble collector to close",
		)
	}
}

func TestRunCollectsHubbleAndReturnsFailed(
	t *testing.T,
) {
	config := baseConfig()

	collector := &fakeCollector{
		results: map[string]hubble.Collection{
			config.StableSelector: stableCollection(),

			config.CanarySelector: badCanaryCollection(),
		},
		errors: map[string]error{},
	}

	got := pluginWithCollector(
		collector,
	).Run(
		nil,
		metricFor(t, config),
	)

	if got.Phase !=
		v1alpha1.AnalysisPhaseFailed {
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

func TestRunReturnsInconclusiveForLowTraffic(
	t *testing.T,
) {
	config := baseConfig()

	collector := &fakeCollector{
		results: map[string]hubble.Collection{
			config.StableSelector: stableCollection(),

			config.CanarySelector: {
				Stats: analysis.CohortStats{
					TotalFlows: 3,
				},
				FlowEvents: 3,
			},
		},
		errors: map[string]error{},
	}

	got := pluginWithCollector(
		collector,
	).Run(
		nil,
		metricFor(t, config),
	)

	if got.Phase !=
		v1alpha1.AnalysisPhaseInconclusive {
		t.Fatalf(
			"expected Inconclusive, got %s: %s",
			got.Phase,
			got.Message,
		)
	}
}

func TestRunReturnsInconclusiveForLostTelemetry(
	t *testing.T,
) {
	config := baseConfig()

	canary := healthyCanaryCollection()
	canary.LostEvents = 7

	collector := &fakeCollector{
		results: map[string]hubble.Collection{
			config.StableSelector: stableCollection(),

			config.CanarySelector: canary,
		},
		errors: map[string]error{},
	}

	got := pluginWithCollector(
		collector,
	).Run(
		nil,
		metricFor(t, config),
	)

	if got.Phase !=
		v1alpha1.AnalysisPhaseInconclusive {
		t.Fatalf(
			"expected Inconclusive, got %s: %s",
			got.Phase,
			got.Message,
		)
	}

	if got.Metadata["canaryLostEvents"] != "7" {
		t.Fatalf(
			"expected lost-event metadata, got %+v",
			got.Metadata,
		)
	}
}

func TestRunReturnsErrorForHubbleFailure(
	t *testing.T,
) {
	config := baseConfig()

	collector := &fakeCollector{
		results: map[string]hubble.Collection{
			config.StableSelector: stableCollection(),
		},

		errors: map[string]error{
			config.CanarySelector: errors.New(
				"relay unavailable",
			),
		},
	}

	got := pluginWithCollector(
		collector,
	).Run(
		nil,
		metricFor(t, config),
	)

	if got.Phase !=
		v1alpha1.AnalysisPhaseError {
		t.Fatalf(
			"expected Error, got %s",
			got.Phase,
		)
	}
}

func TestRunReturnsErrorForInvalidConfiguration(
	t *testing.T,
) {
	config := baseConfig()
	config.HubbleRelay = ""

	collector := &fakeCollector{}

	got := pluginWithCollector(
		collector,
	).Run(
		nil,
		metricFor(t, config),
	)

	if got.Phase !=
		v1alpha1.AnalysisPhaseError {
		t.Fatalf(
			"expected Error, got %s",
			got.Phase,
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

	if got.Phase !=
		v1alpha1.AnalysisPhaseError {
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
