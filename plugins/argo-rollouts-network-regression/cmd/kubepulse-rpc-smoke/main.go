package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"
	kubepulse "github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/plugin"

	rolloutsRPC "github.com/argoproj/argo-rollouts/metricproviders/plugin/rpc"
	"github.com/argoproj/argo-rollouts/pkg/apis/rollouts/v1alpha1"
	goPlugin "github.com/hashicorp/go-plugin"
)

var handshakeConfig = goPlugin.HandshakeConfig{
	ProtocolVersion:  1,
	MagicCookieKey:   "ARGO_ROLLOUTS_RPC_PLUGIN",
	MagicCookieValue: "metricprovider",
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

func stable() analysis.CohortStats {
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
	name string,
	canary analysis.CohortStats,
) (v1alpha1.Metric, error) {
	config := kubepulse.Config{
		Stable:     stable(),
		Canary:     canary,
		Thresholds: thresholds(),
	}

	raw, err := json.Marshal(config)
	if err != nil {
		return v1alpha1.Metric{}, err
	}

	return v1alpha1.Metric{
		Name: name,
		Provider: v1alpha1.MetricProvider{
			Plugin: map[string]json.RawMessage{
				kubepulse.Name: raw,
			},
		},
	}, nil
}

func main() {
	pluginPath := "bin/kubepulse-rollouts-plugin"

	if len(os.Args) > 1 {
		pluginPath = os.Args[1]
	}

	fmt.Println("===== START RPC PLUGIN PROCESS =====")
	fmt.Println("binary:", pluginPath)

	client := goPlugin.NewClient(
		&goPlugin.ClientConfig{
			HandshakeConfig: handshakeConfig,

			Plugins: map[string]goPlugin.Plugin{
				"RpcMetricProviderPlugin": &rolloutsRPC.RpcMetricProviderPlugin{},
			},

			Cmd: exec.Command(pluginPath),

			AllowedProtocols: []goPlugin.Protocol{
				goPlugin.ProtocolNetRPC,
			},
		},
	)
	defer client.Kill()

	rpcClient, err := client.Client()
	if err != nil {
		fmt.Fprintln(
			os.Stderr,
			"RPC CLIENT ERROR:",
			err,
		)
		os.Exit(1)
	}

	rawProvider, err := rpcClient.Dispense(
		"RpcMetricProviderPlugin",
	)
	if err != nil {
		fmt.Fprintln(
			os.Stderr,
			"DISPENSE ERROR:",
			err,
		)
		os.Exit(1)
	}

	provider, ok := rawProvider.(rolloutsRPC.MetricProviderPlugin)
	if !ok {
		fmt.Fprintf(
			os.Stderr,
			"unexpected provider type %T\n",
			rawProvider,
		)
		os.Exit(1)
	}

	fmt.Println("PASS: RPC plugin dispensed")

	if rpcErr := provider.InitPlugin(); rpcErr.HasError() {
		fmt.Fprintln(
			os.Stderr,
			"InitPlugin failed:",
			rpcErr.Error(),
		)
		os.Exit(1)
	}

	fmt.Println("PASS: InitPlugin over RPC")

	if got := provider.Type(); got != "RPCPlugin" {
		fmt.Fprintf(
			os.Stderr,
			"unexpected provider type value %q\n",
			got,
		)
		os.Exit(1)
	}

	fmt.Println("PASS: Type() over RPC = RPCPlugin")

	metadata := provider.GetMetadata(
		v1alpha1.Metric{
			Name: "network-regression",
		},
	)

	if metadata["provider"] != kubepulse.Name {
		fmt.Fprintf(
			os.Stderr,
			"unexpected metadata: %+v\n",
			metadata,
		)
		os.Exit(1)
	}

	fmt.Println(
		"PASS: GetMetadata() over RPC provider=" +
			metadata["provider"],
	)

	tests := []struct {
		name          string
		canary        analysis.CohortStats
		expectedPhase v1alpha1.AnalysisPhase
		expected      string
	}{
		{
			name: "healthy-canary",
			canary: analysis.CohortStats{
				TotalFlows:   300,
				DNSQueries:   100,
				DNSFailures:  1,
				TCPAttempts:  120,
				TCPFailures:  1,
				HTTPRequests: 150,
				HTTP5xx:      1,
				DroppedFlows: 1,
			},
			expectedPhase: v1alpha1.AnalysisPhaseSuccessful,
			expected:      "PASS",
		},
		{
			name: "network-regression",
			canary: analysis.CohortStats{
				TotalFlows:   300,
				DNSQueries:   100,
				DNSFailures:  12,
				TCPAttempts:  120,
				TCPFailures:  15,
				HTTPRequests: 150,
				HTTP5xx:      12,
				DroppedFlows: 10,
			},
			expectedPhase: v1alpha1.AnalysisPhaseFailed,
			expected:      "FAIL",
		},
		{
			name: "insufficient-traffic",
			canary: analysis.CohortStats{
				TotalFlows: 3,
			},
			expectedPhase: v1alpha1.AnalysisPhaseInconclusive,
			expected:      "INCONCLUSIVE",
		},
	}

	fmt.Println()
	fmt.Println("===== RUN MEASUREMENTS OVER RPC =====")

	for _, test := range tests {
		metric, err := metricFor(
			test.name,
			test.canary,
		)
		if err != nil {
			fmt.Fprintln(
				os.Stderr,
				"metric construction error:",
				err,
			)
			os.Exit(1)
		}

		measurement := provider.Run(
			nil,
			metric,
		)

		if measurement.Phase != test.expectedPhase {
			fmt.Fprintf(
				os.Stderr,
				"%s: expected phase %s, got %s: %s\n",
				test.name,
				test.expectedPhase,
				measurement.Phase,
				measurement.Message,
			)
			os.Exit(1)
		}

		if measurement.Metadata["decision"] !=
			test.expected {
			fmt.Fprintf(
				os.Stderr,
				"%s: expected decision %s, got %+v\n",
				test.name,
				test.expected,
				measurement.Metadata,
			)
			os.Exit(1)
		}

		var report analysis.Report

		if err := json.Unmarshal(
			[]byte(measurement.Value),
			&report,
		); err != nil {
			fmt.Fprintf(
				os.Stderr,
				"%s: invalid report JSON: %v\n",
				test.name,
				err,
			)
			os.Exit(1)
		}

		fmt.Printf(
			"PASS: %-22s phase=%-12s decision=%s regressions=%v\n",
			test.name,
			measurement.Phase,
			report.Decision,
			report.Regressions,
		)
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("RPC PROCESS-BOUNDARY VALIDATION COMPLETE")
	fmt.Println("========================================")
	fmt.Println("PASS: subprocess launch")
	fmt.Println("PASS: HashiCorp plugin handshake")
	fmt.Println("PASS: Argo metric provider dispense")
	fmt.Println("PASS: InitPlugin RPC")
	fmt.Println("PASS: Type/GetMetadata RPC")
	fmt.Println("PASS: PASS measurement RPC")
	fmt.Println("PASS: FAIL measurement RPC")
	fmt.Println("PASS: INCONCLUSIVE measurement RPC")
}
