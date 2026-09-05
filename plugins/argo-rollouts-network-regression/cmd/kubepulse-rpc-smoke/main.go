package main

import (
	"encoding/json"
	"fmt"
	"net"
	"os"
	"os/exec"
	"sync"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"
	kubepulse "github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/plugin"

	flowpb "github.com/cilium/cilium/api/v1/flow"
	observerpb "github.com/cilium/cilium/api/v1/observer"

	rolloutsRPC "github.com/argoproj/argo-rollouts/metricproviders/plugin/rpc"
	"github.com/argoproj/argo-rollouts/pkg/apis/rollouts/v1alpha1"

	goPlugin "github.com/hashicorp/go-plugin"
	"google.golang.org/grpc"
)

var handshakeConfig = goPlugin.HandshakeConfig{
	ProtocolVersion:  1,
	MagicCookieKey:   "ARGO_ROLLOUTS_RPC_PLUGIN",
	MagicCookieValue: "metricprovider",
}

const (
	stableSelector  = "app=checkout,role=stable"
	healthySelector = "app=checkout,role=healthy-canary"
	badSelector     = "app=checkout,role=bad-canary"
	lowSelector     = "app=checkout,role=low-traffic-canary"
	lostSelector    = "app=checkout,role=lost-telemetry-canary"
)

type cohortSpec struct {
	tcpAttempts int
	tcpFailures int

	dnsResponses int
	dnsFailures  int

	httpResponses int
	http5xx       int

	dropped int
	filler  int

	lost uint64
}

type fakeHubbleObserver struct {
	observerpb.UnimplementedObserverServer

	mu    sync.Mutex
	calls map[string]int
}

func newFakeHubbleObserver() *fakeHubbleObserver {
	return &fakeHubbleObserver{
		calls: map[string]int{},
	}
}

func (f *fakeHubbleObserver) GetFlows(
	request *observerpb.GetFlowsRequest,
	stream grpc.ServerStreamingServer[observerpb.GetFlowsResponse],
) error {
	selector := selectorFromRequest(request)

	f.mu.Lock()
	f.calls[selector]++
	f.mu.Unlock()

	spec, ok := cohortForSelector(selector)
	if !ok {
		return fmt.Errorf(
			"unexpected Hubble selector %q",
			selector,
		)
	}

	return emitCohort(
		stream,
		spec,
	)
}

func (f *fakeHubbleObserver) callCount(
	selector string,
) int {
	f.mu.Lock()
	defer f.mu.Unlock()

	return f.calls[selector]
}

func selectorFromRequest(
	request *observerpb.GetFlowsRequest,
) string {
	for _, filter := range request.GetWhitelist() {
		if labels := filter.GetSourceLabel(); len(labels) > 0 {
			return labels[0]
		}

		if labels := filter.GetDestinationLabel(); len(labels) > 0 {
			return labels[0]
		}
	}

	return ""
}

func cohortForSelector(
	selector string,
) (cohortSpec, bool) {
	switch selector {
	case stableSelector:
		return healthySpec(), true

	case healthySelector:
		return healthySpec(), true

	case badSelector:
		return cohortSpec{
			tcpAttempts: 100,
			tcpFailures: 20,

			dnsResponses: 40,
			dnsFailures:  10,

			httpResponses: 40,
			http5xx:       10,

			dropped: 20,
		}, true

	case lowSelector:
		return cohortSpec{
			filler: 3,
		}, true

	case lostSelector:
		spec := healthySpec()
		spec.lost = 5

		return spec, true

	default:
		return cohortSpec{}, false
	}
}

func healthySpec() cohortSpec {
	return cohortSpec{
		tcpAttempts: 100,
		tcpFailures: 1,

		dnsResponses: 40,
		dnsFailures:  1,

		httpResponses: 40,
		http5xx:       1,

		dropped: 1,
		filler:  18,
	}
}

func emitCohort(
	stream grpc.ServerStreamingServer[observerpb.GetFlowsResponse],
	spec cohortSpec,
) error {
	for i := 0; i < spec.tcpAttempts; i++ {
		if err := stream.Send(
			flowResponse(
				tcpSYN(),
			),
		); err != nil {
			return err
		}
	}

	for i := 0; i < spec.tcpFailures; i++ {
		if err := stream.Send(
			flowResponse(
				tcpRST(),
			),
		); err != nil {
			return err
		}
	}

	for i := 0; i < spec.dnsResponses; i++ {
		rcode := uint32(0)

		if i < spec.dnsFailures {
			// NXDOMAIN for deterministic failure
			// classification.
			rcode = 3
		}

		if err := stream.Send(
			flowResponse(
				dnsResponse(rcode),
			),
		); err != nil {
			return err
		}
	}

	for i := 0; i < spec.httpResponses; i++ {
		code := uint32(200)

		if i < spec.http5xx {
			code = 503
		}

		if err := stream.Send(
			flowResponse(
				httpResponse(code),
			),
		); err != nil {
			return err
		}
	}

	for i := 0; i < spec.dropped; i++ {
		if err := stream.Send(
			flowResponse(
				droppedFlow(),
			),
		); err != nil {
			return err
		}
	}

	for i := 0; i < spec.filler; i++ {
		if err := stream.Send(
			flowResponse(
				forwardedFlow(),
			),
		); err != nil {
			return err
		}
	}

	if spec.lost > 0 {
		if err := stream.Send(
			&observerpb.GetFlowsResponse{
				ResponseTypes: &observerpb.GetFlowsResponse_LostEvents{
					LostEvents: &flowpb.LostEvent{
						NumEventsLost: spec.lost,
					},
				},
			},
		); err != nil {
			return err
		}
	}

	return nil
}

func flowResponse(
	flow *flowpb.Flow,
) *observerpb.GetFlowsResponse {
	return &observerpb.GetFlowsResponse{
		ResponseTypes: &observerpb.GetFlowsResponse_Flow{
			Flow: flow,
		},
	}
}

func tcpSYN() *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_FORWARDED,

		L4: &flowpb.Layer4{
			Protocol: &flowpb.Layer4_TCP{
				TCP: &flowpb.TCP{
					Flags: &flowpb.TCPFlags{
						SYN: true,
					},
				},
			},
		},
	}
}

func tcpRST() *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_FORWARDED,

		L4: &flowpb.Layer4{
			Protocol: &flowpb.Layer4_TCP{
				TCP: &flowpb.TCP{
					Flags: &flowpb.TCPFlags{
						RST: true,
						ACK: true,
					},
				},
			},
		},
	}
}

func dnsResponse(
	rcode uint32,
) *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_FORWARDED,

		L7: &flowpb.Layer7{
			Type: flowpb.L7FlowType_RESPONSE,

			Record: &flowpb.Layer7_Dns{
				Dns: &flowpb.DNS{
					Query: "dependency.default.svc.cluster.local.",

					Rcode: rcode,
				},
			},
		},
	}
}

func httpResponse(
	code uint32,
) *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_FORWARDED,

		L7: &flowpb.Layer7{
			Type: flowpb.L7FlowType_RESPONSE,

			Record: &flowpb.Layer7_Http{
				Http: &flowpb.HTTP{
					Code: code,
				},
			},
		},
	}
}

func droppedFlow() *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_DROPPED,
	}
}

func forwardedFlow() *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_FORWARDED,
	}
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

func metricFor(
	topic string,
	hubbleAddress string,
	canarySelector string,
) (v1alpha1.Metric, error) {
	config := kubepulse.Config{
		HubbleRelay: hubbleAddress,

		StableSelector: stableSelector,
		CanarySelector: canarySelector,

		WindowSeconds:       60,
		QueryTimeoutSeconds: 5,
		MaxLostEvents:       0,

		Thresholds: thresholds(),
	}

	raw, err := json.Marshal(config)
	if err != nil {
		return v1alpha1.Metric{}, err
	}

	return v1alpha1.Metric{
		Name: topic,

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

	fmt.Println("========================================")
	fmt.Println("START FAKE HUBBLE OBSERVER")
	fmt.Println("========================================")

	listener, err := net.Listen(
		"tcp",
		"127.0.0.1:0",
	)
	if err != nil {
		fmt.Fprintln(
			os.Stderr,
			"HUBBLE LISTENER ERROR:",
			err,
		)
		os.Exit(1)
	}
	defer listener.Close()

	hubbleObserver := newFakeHubbleObserver()

	hubbleServer := grpc.NewServer()

	observerpb.RegisterObserverServer(
		hubbleServer,
		hubbleObserver,
	)

	go func() {
		if err := hubbleServer.Serve(listener); err != nil {
			fmt.Fprintln(
				os.Stderr,
				"HUBBLE SERVER ERROR:",
				err,
			)
		}
	}()

	defer hubbleServer.Stop()

	hubbleAddress := listener.Addr().String()

	fmt.Println(
		"PASS: fake Hubble listening at",
		hubbleAddress,
	)

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("START ARGO PLUGIN SUBPROCESS")
	fmt.Println("========================================")
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

	fmt.Println(
		"PASS: Type() over RPC = RPCPlugin",
	)

	metadata := provider.GetMetadata(
		v1alpha1.Metric{
			Name: "network-regression",
		},
	)

	if metadata["provider"] != kubepulse.Name ||
		metadata["telemetry"] != "cilium-hubble" {
		fmt.Fprintf(
			os.Stderr,
			"unexpected metadata: %+v\n",
			metadata,
		)
		os.Exit(1)
	}

	fmt.Println(
		"PASS: GetMetadata() telemetry=cilium-hubble",
	)

	tests := []struct {
		name string

		canarySelector string

		expectedPhase v1alpha1.AnalysisPhase
		expected      string
	}{
		{
			name: "healthy-canary",

			canarySelector: healthySelector,

			expectedPhase: v1alpha1.AnalysisPhaseSuccessful,

			expected: "PASS",
		},

		{
			name: "network-regression",

			canarySelector: badSelector,

			expectedPhase: v1alpha1.AnalysisPhaseFailed,

			expected: "FAIL",
		},

		{
			name: "insufficient-traffic",

			canarySelector: lowSelector,

			expectedPhase: v1alpha1.AnalysisPhaseInconclusive,

			expected: "INCONCLUSIVE",
		},

		{
			name: "lost-hubble-telemetry",

			canarySelector: lostSelector,

			expectedPhase: v1alpha1.AnalysisPhaseInconclusive,

			expected: "INCONCLUSIVE",
		},
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("RUN HUBBLE-BACKED ARGO MEASUREMENTS")
	fmt.Println("========================================")

	for _, test := range tests {
		metric, err := metricFor(
			test.name,
			hubbleAddress,
			test.canarySelector,
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

		regressions := ""

		if measurement.Value != "" {
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

			regressions = fmt.Sprint(
				report.Regressions,
			)
		}

		fmt.Printf(
			"PASS: %-22s phase=%-12s decision=%-12s regressions=%s\n",
			test.name,
			measurement.Phase,
			measurement.Metadata["decision"],
			regressions,
		)
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("VERIFY HUBBLE QUERIES")
	fmt.Println("========================================")

	expectedCalls := map[string]int{
		stableSelector: 4,

		healthySelector: 1,
		badSelector:     1,
		lowSelector:     1,
		lostSelector:    1,
	}

	for selector, expected := range expectedCalls {
		got := hubbleObserver.callCount(
			selector,
		)

		if got != expected {
			fmt.Fprintf(
				os.Stderr,
				"selector %q: expected %d Hubble calls, got %d\n",
				selector,
				expected,
				got,
			)
			os.Exit(1)
		}

		fmt.Printf(
			"PASS: selector=%q calls=%d\n",
			selector,
			got,
		)
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("END-TO-END VALIDATION COMPLETE")
	fmt.Println("========================================")

	fmt.Println("PASS: fake Hubble Observer gRPC")
	fmt.Println("PASS: Hubble GetFlows streaming")
	fmt.Println("PASS: stable cohort collection")
	fmt.Println("PASS: canary cohort collection")
	fmt.Println("PASS: Hubble flow classification")
	fmt.Println("PASS: lost-event safety gate")
	fmt.Println("PASS: network regression analysis")
	fmt.Println("PASS: HashiCorp plugin subprocess")
	fmt.Println("PASS: Argo RpcMetricProviderPlugin")
	fmt.Println("PASS: PASS rollout measurement")
	fmt.Println("PASS: FAIL rollout measurement")
	fmt.Println("PASS: INCONCLUSIVE rollout measurement")
}
