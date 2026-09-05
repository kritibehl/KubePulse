package main

import (
	kubepulse "github.com/kritibehl/KubePulse/plugins/argo-rollouts-network-regression/internal/plugin"

	rolloutsRPC "github.com/argoproj/argo-rollouts/metricproviders/plugin/rpc"
	goPlugin "github.com/hashicorp/go-plugin"
)

var handshakeConfig = goPlugin.HandshakeConfig{
	ProtocolVersion:  1,
	MagicCookieKey:   "ARGO_ROLLOUTS_RPC_PLUGIN",
	MagicCookieValue: "metricprovider",
}

func main() {
	implementation := &kubepulse.RPCPlugin{}

	pluginMap := map[string]goPlugin.Plugin{
		"RpcMetricProviderPlugin": &rolloutsRPC.RpcMetricProviderPlugin{
			Impl: implementation,
		},
	}

	goPlugin.Serve(
		&goPlugin.ServeConfig{
			HandshakeConfig: handshakeConfig,
			Plugins:         pluginMap,
		},
	)
}
