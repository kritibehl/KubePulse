package plugin

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"

	rolloutsMetricPlugin "github.com/argoproj/argo-rollouts/metricproviders/plugin"
	rolloutsRPC "github.com/argoproj/argo-rollouts/metricproviders/plugin/rpc"
	"github.com/argoproj/argo-rollouts/pkg/apis/rollouts/v1alpha1"
	"github.com/argoproj/argo-rollouts/utils/plugin/types"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

const Name = "kubepulse/network-regression"

var _ rolloutsRPC.MetricProviderPlugin = (*RPCPlugin)(nil)

type RPCPlugin struct{}

type Config struct {
	Stable     analysis.CohortStats `json:"stable"`
	Canary     analysis.CohortStats `json:"canary"`
	Thresholds analysis.Thresholds  `json:"thresholds"`
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

	report := analysis.Analyze(
		config.Stable,
		config.Canary,
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

	measurement.Metadata = map[string]string{
		"provider":         Name,
		"decision":         string(report.Decision),
		"evaluatedSignals": strings.Join(report.EvaluatedSignals, ","),
		"regressions":      strings.Join(report.Regressions, ","),
	}

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
			strings.Join(report.Regressions, ", "),
		)

	case analysis.DecisionInconclusive:
		measurement.Phase =
			v1alpha1.AnalysisPhaseInconclusive

		measurement.Message = strings.Join(
			report.Reasons,
			"; ",
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

func (p *RPCPlugin) Resume(
	analysisRun *v1alpha1.AnalysisRun,
	metric v1alpha1.Metric,
	measurement v1alpha1.Measurement,
) v1alpha1.Measurement {
	// V1 analysis is synchronous, so there is nothing to resume.
	return measurement
}

func (p *RPCPlugin) Terminate(
	analysisRun *v1alpha1.AnalysisRun,
	metric v1alpha1.Metric,
	measurement v1alpha1.Measurement,
) v1alpha1.Measurement {
	// V1 analysis completes synchronously.
	return measurement
}

func (p *RPCPlugin) GarbageCollect(
	analysisRun *v1alpha1.AnalysisRun,
	metric v1alpha1.Metric,
	limit int,
) types.RpcError {
	// V1 has no external per-measurement resources.
	return types.RpcError{}
}

func (p *RPCPlugin) Type() string {
	return rolloutsMetricPlugin.ProviderType
}

func (p *RPCPlugin) GetMetadata(
	metric v1alpha1.Metric,
) map[string]string {
	return map[string]string{
		"provider": Name,
		"analysis": "stable-vs-canary-network-regression",
	}
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
