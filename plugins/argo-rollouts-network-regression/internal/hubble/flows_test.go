package hubble

import (
	"context"
	"net"
	"testing"
	"time"

	flowpb "github.com/cilium/cilium/api/v1/flow"
	observerpb "github.com/cilium/cilium/api/v1/observer"
	"google.golang.org/grpc"
)

type flowObserver struct {
	observerpb.UnimplementedObserverServer

	request *observerpb.GetFlowsRequest
}

func (f *flowObserver) GetFlows(
	request *observerpb.GetFlowsRequest,
	stream grpc.ServerStreamingServer[observerpb.GetFlowsResponse],
) error {
	f.request = request

	responses := []*observerpb.GetFlowsResponse{
		flowResponse(
			&flowpb.Flow{
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
			},
		),

		flowResponse(
			&flowpb.Flow{
				Verdict: flowpb.Verdict_DROPPED,
				L4: &flowpb.Layer4{
					Protocol: &flowpb.Layer4_TCP{
						TCP: &flowpb.TCP{
							Flags: &flowpb.TCPFlags{
								SYN: true,
							},
						},
					},
				},
			},
		),

		flowResponse(
			&flowpb.Flow{
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
			},
		),

		flowResponse(
			dnsResponse(0),
		),

		flowResponse(
			dnsResponse(3),
		),

		flowResponse(
			dnsRequest(),
		),

		flowResponse(
			httpResponse(200),
		),

		flowResponse(
			httpResponse(503),
		),

		flowResponse(
			httpRequest(),
		),

		{
			ResponseTypes: &observerpb.GetFlowsResponse_LostEvents{
				LostEvents: &flowpb.LostEvent{
					NumEventsLost: 4,
				},
			},
		},
	}

	for _, response := range responses {
		if err := stream.Send(response); err != nil {
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

func dnsRequest() *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_FORWARDED,
		L7: &flowpb.Layer7{
			Type: flowpb.L7FlowType_REQUEST,
			Record: &flowpb.Layer7_Dns{
				Dns: &flowpb.DNS{
					Query: "dependency.default.svc.cluster.local.",
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

func httpRequest() *flowpb.Flow {
	return &flowpb.Flow{
		Verdict: flowpb.Verdict_FORWARDED,
		L7: &flowpb.Layer7{
			Type: flowpb.L7FlowType_REQUEST,
			Record: &flowpb.Layer7_Http{
				Http: &flowpb.HTTP{
					Method: "GET",
					Url:    "/dependency",
				},
			},
		},
	}
}

func TestCollectCohortStatsOverGRPC(
	t *testing.T,
) {
	listener, err := net.Listen(
		"tcp",
		"127.0.0.1:0",
	)
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()

	observer := &flowObserver{}

	server := grpc.NewServer()

	observerpb.RegisterObserverServer(
		server,
		observer,
	)

	go func() {
		_ = server.Serve(listener)
	}()

	defer server.Stop()

	ctx, cancel := context.WithTimeout(
		context.Background(),
		5*time.Second,
	)
	defer cancel()

	client, err := Dial(
		ctx,
		listener.Addr().String(),
	)
	if err != nil {
		t.Fatal(err)
	}
	defer client.Close()

	until := time.Now().UTC()
	since := until.Add(-60 * time.Second)

	collection, err := client.CollectCohortStats(
		ctx,
		"app=checkout,rollouts-pod-template-hash=stable",
		since,
		until,
	)
	if err != nil {
		t.Fatal(err)
	}

	if observer.request == nil {
		t.Fatal(
			"expected GetFlows request",
		)
	}

	if len(observer.request.GetWhitelist()) != 2 {
		t.Fatalf(
			"expected 2 whitelist filters, got %d",
			len(observer.request.GetWhitelist()),
		)
	}

	source := observer.request.GetWhitelist()[0]
	destination := observer.request.GetWhitelist()[1]

	if len(source.GetSourceLabel()) != 1 {
		t.Fatalf(
			"unexpected source labels: %+v",
			source.GetSourceLabel(),
		)
	}

	if len(destination.GetDestinationLabel()) != 1 {
		t.Fatalf(
			"unexpected destination labels: %+v",
			destination.GetDestinationLabel(),
		)
	}

	if collection.FlowEvents != 9 {
		t.Fatalf(
			"expected 9 flow events, got %d",
			collection.FlowEvents,
		)
	}

	if collection.LostEvents != 4 {
		t.Fatalf(
			"expected 4 lost events, got %d",
			collection.LostEvents,
		)
	}

	stats := collection.Stats

	if stats.TotalFlows != 9 {
		t.Fatalf(
			"expected 9 total flows, got %d",
			stats.TotalFlows,
		)
	}

	if stats.DroppedFlows != 1 {
		t.Fatalf(
			"expected 1 dropped flow, got %d",
			stats.DroppedFlows,
		)
	}

	if stats.TCPAttempts != 2 {
		t.Fatalf(
			"expected 2 TCP attempts, got %d",
			stats.TCPAttempts,
		)
	}

	if stats.TCPFailures != 1 {
		t.Fatalf(
			"expected 1 TCP failure, got %d",
			stats.TCPFailures,
		)
	}

	if stats.DNSQueries != 2 {
		t.Fatalf(
			"expected 2 DNS responses, got %d",
			stats.DNSQueries,
		)
	}

	if stats.DNSFailures != 1 {
		t.Fatalf(
			"expected 1 DNS failure, got %d",
			stats.DNSFailures,
		)
	}

	if stats.HTTPRequests != 2 {
		t.Fatalf(
			"expected 2 HTTP responses, got %d",
			stats.HTTPRequests,
		)
	}

	if stats.HTTP5xx != 1 {
		t.Fatalf(
			"expected 1 HTTP 5xx, got %d",
			stats.HTTP5xx,
		)
	}
}
