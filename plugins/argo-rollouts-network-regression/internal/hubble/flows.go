package hubble

import (
	"context"
	"errors"
	"fmt"
	"io"
	"strings"
	"time"

	"github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/analysis"

	flowpb "github.com/cilium/cilium/api/v1/flow"
	observerpb "github.com/cilium/cilium/api/v1/observer"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type Collection struct {
	Stats      analysis.CohortStats
	FlowEvents uint64
	LostEvents uint64
}

func (c *Client) CollectCohortStats(
	ctx context.Context,
	selector string,
	since time.Time,
	until time.Time,
) (Collection, error) {
	if c == nil || c.observer == nil {
		return Collection{}, fmt.Errorf(
			"hubble client is not initialized",
		)
	}

	selector = strings.TrimSpace(selector)
	if selector == "" {
		return Collection{}, fmt.Errorf(
			"cohort label selector must not be empty",
		)
	}

	if !until.After(since) {
		return Collection{}, fmt.Errorf(
			"until must be after since",
		)
	}

	sinceTimestamp := timestamppb.New(since)
	if err := sinceTimestamp.CheckValid(); err != nil {
		return Collection{}, fmt.Errorf(
			"invalid since timestamp: %w",
			err,
		)
	}

	untilTimestamp := timestamppb.New(until)
	if err := untilTimestamp.CheckValid(); err != nil {
		return Collection{}, fmt.Errorf(
			"invalid until timestamp: %w",
			err,
		)
	}

	request := &observerpb.GetFlowsRequest{
		Since: sinceTimestamp,
		Until: untilTimestamp,
		Whitelist: []*flowpb.FlowFilter{
			{
				SourceLabel: []string{
					selector,
				},
			},
			{
				DestinationLabel: []string{
					selector,
				},
			},
		},
	}

	stream, err := c.observer.GetFlows(
		ctx,
		request,
	)
	if err != nil {
		return Collection{}, fmt.Errorf(
			"hubble get flows: %w",
			err,
		)
	}

	var collection Collection

	for {
		response, err := stream.Recv()

		if errors.Is(err, io.EOF) {
			break
		}

		if err != nil {
			return Collection{}, fmt.Errorf(
				"receive hubble flow: %w",
				err,
			)
		}

		if lost := response.GetLostEvents(); lost != nil {
			collection.LostEvents +=
				lost.GetNumEventsLost()

			continue
		}

		flow := response.GetFlow()
		if flow == nil {
			continue
		}

		collection.FlowEvents++

		classifyFlow(
			&collection.Stats,
			flow,
		)
	}

	return collection, nil
}

func classifyFlow(
	stats *analysis.CohortStats,
	flow *flowpb.Flow,
) {
	if stats == nil || flow == nil {
		return
	}

	stats.TotalFlows++

	if flow.GetVerdict() == flowpb.Verdict_DROPPED {
		stats.DroppedFlows++
	}

	if layer4 := flow.GetL4(); layer4 != nil {
		if tcp := layer4.GetTCP(); tcp != nil {
			if flags := tcp.GetFlags(); flags != nil {
				// Treat SYN without ACK as an observed
				// TCP connection-attempt event.
				if flags.GetSYN() && !flags.GetACK() {
					stats.TCPAttempts++
				}

				// Treat any observed RST as a
				// TCP failure/reset event.
				if flags.GetRST() {
					stats.TCPFailures++
				}
			}
		}
	}

	layer7 := flow.GetL7()
	if layer7 == nil {
		return
	}

	// Count only completed L7 responses so request
	// and response events do not double the denominator.
	if layer7.GetType() !=
		flowpb.L7FlowType_RESPONSE {
		return
	}

	if dns := layer7.GetDns(); dns != nil {
		stats.DNSQueries++

		if dns.GetRcode() != 0 {
			stats.DNSFailures++
		}
	}

	if http := layer7.GetHttp(); http != nil {
		code := http.GetCode()

		if code > 0 {
			stats.HTTPRequests++
		}

		if code >= 500 && code <= 599 {
			stats.HTTP5xx++
		}
	}
}
