package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"time"

	observerpb "github.com/cilium/cilium/api/v1/observer"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	address := flag.String(
		"address",
		"127.0.0.1:4245",
		"Hubble Relay gRPC address",
	)

	flag.Parse()

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	conn, err := grpc.NewClient(
		*address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Fatalf("create gRPC client: %v", err)
	}
	defer conn.Close()

	client := observerpb.NewObserverClient(conn)

	status, err := client.ServerStatus(
		ctx,
		&observerpb.ServerStatusRequest{},
	)
	if err != nil {
		log.Fatalf("ServerStatus: %v", err)
	}

	fmt.Printf("server_status=%s\n", status.String())

	nodes, err := client.GetNodes(
		ctx,
		&observerpb.GetNodesRequest{},
	)
	if err != nil {
		log.Fatalf("GetNodes: %v", err)
	}

	fmt.Printf("nodes=%s\n", nodes.String())

	stream, err := client.GetFlows(
		ctx,
		&observerpb.GetFlowsRequest{
			Number: 5,
			Follow: false,
		},
	)
	if err != nil {
		log.Fatalf("GetFlows: %v", err)
	}

	responses := 0

	for {
		resp, err := stream.Recv()

		if err == io.EOF {
			break
		}

		if err != nil {
			log.Fatalf("GetFlows Recv: %v", err)
		}

		responses++

		fmt.Printf(
			"flow_response_%d=%s\n",
			responses,
			resp.String(),
		)
	}

	if responses == 0 {
		log.Fatal("GetFlows returned zero responses")
	}

	fmt.Printf("flow_responses=%d\n", responses)
	fmt.Println("real_hubble_relay_grpc=PASS")
}
