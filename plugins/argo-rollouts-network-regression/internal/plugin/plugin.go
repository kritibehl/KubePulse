package plugin

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"
	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/hubble"

	rolloutsMetricPlugin "github.com/argoproj/argo-rollouts/metricproviders/plugin"
	rolloutsRPC "github.com/argoproj/argo-rollouts/metricproviders/plugin/rpc"
	"github.com/argoproj/argo-rollouts/pkg/apis/rollouts/v1alpha1"
	"github.com/argoproj/argo-rollouts/utils/plugin/types"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

const Name = "kubepulse/network-regression"

var _ rolloutsRPC.MetricProviderPlugin = (*RPCPlugin)(nil)

type Config struct {
	HubbleRelay string `json:"hubbleRelay"`

	StableSelector string `json:"stableSelector"`
	CanarySelector string `json:"canarySelector"`

	WindowSeconds       int `json:"windowSeconds"`
	QueryTimeoutSeconds int `json:"queryTimeoutSeconds"`

	// Conservative default:
	// if omitted, any Hubble event loss makes the
	// measurement inconclusive.
	MaxLostEvents uint64 `json:"maxLostEvents"`

	Thresholds analysis.Thresholds `json:"thresholds"`
}

type CohortCollector interface {
	CollectCohortStats(
		ctx context.Context,
		selector string,
		since time.Time,
		until time.Time,
	) (hubble.Collection, error)

	Close() error
}

type CollectorFactory func(
	ctx context.Context,
	address string,
) (CohortCollector, error)

type RPCPlugin struct {
	// Injection points keep unit tests deterministic.
	NewCollector CollectorFactory
	Now          func() time.Time
}

func (p *RPCPlugin) InitPlugin() types.RpcError {
	return types.RpcError{}
}

func (p *RPCPlugin) Run(
	analysisRun *v1alpha1.AnalysisRun,
	metric v1alpha1.Metric,
) v1alpha1.Measurement {
	startedAt := metav1.Now()

	measurement := v1alpha1.Measurement{
		StartedAt: &startedAt,
	}

	raw, ok := metric.Provider.Plugin[Name]
	if !ok {
		return markError(
			measurement,
			fmt.Errorf(
				"plugin configuration %q not found",
				Name,
			),
		)
	}

	var config Config

	if err := json.Unmarshal(raw, &config); err != nil {
		return markError(
			measurement,
			fmt.Errorf(
				"decode %s configuration: %w",
				Name,
				err,
			),
		)
	}

	if err := validateConfig(config); err != nil {
		return markError(
			measurement,
			err,
		)
	}

	timeoutSeconds := config.QueryTimeoutSeconds
	if timeoutSeconds <= 0 {
		timeoutSeconds = 10
	}

	ctx, cancel := context.WithTimeout(
		context.Background(),
		time.Duration(timeoutSeconds)*time.Second,
	)
	defer cancel()

	collector, err := p.collectorFactory()(
		ctx,
		config.HubbleRelay,
	)
	if err != nil {
		return markError(
			measurement,
			fmt.Errorf(
				"connect to Hubble Relay %q: %w",
				config.HubbleRelay,
				err,
			),
		)
	}
	defer collector.Close()

	until := p.now().UTC()
	since := until.Add(
		-time.Duration(config.WindowSeconds) *
			time.Second,
	)

	stable, err := collector.CollectCohortStats(
		ctx,
		config.StableSelector,
		since,
		until,
	)
	if err != nil {
		return markError(
			measurement,
			fmt.Errorf(
				"collect stable Hubble flows: %w",
				err,
			),
		)
	}

	canary, err := collector.CollectCohortStats(
		ctx,
		config.CanarySelector,
		since,
		until,
	)
	if err != nil {
		return markError(
			measurement,
			fmt.Errorf(
				"collect canary Hubble flows: %w",
				err,
			),
		)
	}

	measurement.Metadata =
		collectionMetadata(
			stable,
			canary,
		)

	measurement.Metadata["provider"] = Name
	measurement.Metadata["hubbleRelay"] =
		config.HubbleRelay
	measurement.Metadata["stableSelector"] =
		config.StableSelector
	measurement.Metadata["canarySelector"] =
		config.CanarySelector
	measurement.Metadata["windowSeconds"] =
		strconv.Itoa(config.WindowSeconds)

	if stable.LostEvents > config.MaxLostEvents ||
		canary.LostEvents > config.MaxLostEvents {
		measurement.Metadata["decision"] =
			string(analysis.DecisionInconclusive)

		return markInconclusive(
			measurement,
			fmt.Sprintf(
				"Hubble telemetry incomplete: stable lost=%d, canary lost=%d, allowed=%d",
				stable.LostEvents,
				canary.LostEvents,
				config.MaxLostEvents,
			),
		)
	}

	report := analysis.Analyze(
		stable.Stats,
		canary.Stats,
		config.Thresholds,
	)

	encoded, err := json.Marshal(report)
	if err != nil {
		return markError(
			measurement,
			fmt.Errorf(
				"encode network regression report: %w",
				err,
			),
		)
	}

	measurement.Value = string(encoded)

	measurement.Metadata["decision"] =
		string(report.Decision)

	measurement.Metadata["evaluatedSignals"] =
		strings.Join(
			report.EvaluatedSignals,
			",",
		)

	measurement.Metadata["regressions"] =
		strings.Join(
			report.Regressions,
			",",
		)

	switch report.Decision {
	case analysis.DecisionPass:
		measurement.Phase =
			v1alpha1.AnalysisPhaseSuccessful

		measurement.Message =
			"canary network behavior is within stable-relative thresholds"

	case analysis.DecisionFail:
		measurement.Phase =
			v1alpha1.AnalysisPhaseFailed

		measurement.Message = fmt.Sprintf(
			"network regression detected: %s",
			strings.Join(
				report.Regressions,
				", ",
			),
		)

	case analysis.DecisionInconclusive:
		return markInconclusive(
			measurement,
			strings.Join(
				report.Reasons,
				"; ",
			),
		)

	default:
		return markError(
			measurement,
			fmt.Errorf(
				"unsupported analysis decision %q",
				report.Decision,
			),
		)
	}

	finishedAt := metav1.Now()
	measurement.FinishedAt = &finishedAt

	return measurement
}

func validateConfig(
	config Config,
) error {
	if strings.TrimSpace(config.HubbleRelay) == "" {
		return fmt.Errorf(
			"hubbleRelay must not be empty",
		)
	}

	if strings.TrimSpace(config.StableSelector) == "" {
		return fmt.Errorf(
			"stableSelector must not be empty",
		)
	}

	if strings.TrimSpace(config.CanarySelector) == "" {
		return fmt.Errorf(
			"canarySelector must not be empty",
		)
	}

	if config.StableSelector ==
		config.CanarySelector {
		return fmt.Errorf(
			"stableSelector and canarySelector must differ",
		)
	}

	if config.WindowSeconds <= 0 {
		return fmt.Errorf(
			"windowSeconds must be greater than zero",
		)
	}

	return nil
}

func (p *RPCPlugin) collectorFactory() CollectorFactory {
	if p.NewCollector != nil {
		return p.NewCollector
	}

	return func(
		ctx context.Context,
		address string,
	) (CohortCollector, error) {
		return hubble.Dial(
			ctx,
			address,
		)
	}
}

func (p *RPCPlugin) now() time.Time {
	if p.Now != nil {
		return p.Now()
	}

	return time.Now()
}

func collectionMetadata(
	stable hubble.Collection,
	canary hubble.Collection,
) map[string]string {
	return map[string]string{
		"stableFlowEvents": strconv.FormatUint(
			stable.FlowEvents,
			10,
		),

		"canaryFlowEvents": strconv.FormatUint(
			canary.FlowEvents,
			10,
		),

		"stableLostEvents": strconv.FormatUint(
			stable.LostEvents,
			10,
		),

		"canaryLostEvents": strconv.FormatUint(
			canary.LostEvents,
			10,
		),
	}
}

func (p *RPCPlugin) Resume(
	analysisRun *v1alpha1.AnalysisRun,
	metric v1alpha1.Metric,
	measurement v1alpha1.Measurement,
) v1alpha1.Measurement {
	return measurement
}

func (p *RPCPlugin) Terminate(
	analysisRun *v1alpha1.AnalysisRun,
	metric v1alpha1.Metric,
	measurement v1alpha1.Measurement,
) v1alpha1.Measurement {
	return measurement
}

func (p *RPCPlugin) GarbageCollect(
	analysisRun *v1alpha1.AnalysisRun,
	metric v1alpha1.Metric,
	limit int,
) types.RpcError {
	return types.RpcError{}
}

func (p *RPCPlugin) Type() string {
	return rolloutsMetricPlugin.ProviderType
}

func (p *RPCPlugin) GetMetadata(
	metric v1alpha1.Metric,
) map[string]string {
	return map[string]string{
		"provider":  Name,
		"analysis":  "stable-vs-canary-network-regression",
		"telemetry": "cilium-hubble",
	}
}

func markInconclusive(
	measurement v1alpha1.Measurement,
	message string,
) v1alpha1.Measurement {
	measurement.Phase =
		v1alpha1.AnalysisPhaseInconclusive

	measurement.Message = message

	finishedAt := metav1.Now()
	measurement.FinishedAt = &finishedAt

	return measurement
}

func markError(
	measurement v1alpha1.Measurement,
	err error,
) v1alpha1.Measurement {
	measurement.Phase =
		v1alpha1.AnalysisPhaseError

	measurement.Message = err.Error()

	finishedAt := metav1.Now()
	measurement.FinishedAt = &finishedAt

	return measurement
}
