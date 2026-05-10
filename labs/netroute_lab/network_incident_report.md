# Network Incident Report

## Scenario
Client requests fail intermittently while connecting to the API service.

## Checks
- DNS resolution
- TCP connectivity
- cURL HTTP status
- traceroute hop inspection
- route failure simulation

## Findings
- DNS check validates host resolution.
- TCP check validates connectivity to service port.
- cURL check validates HTTP reachability.
- Routing simulator shows alternate path behavior after link failure.

## Scope
This lab demonstrates networking troubleshooting fundamentals and routing concepts. It does not implement BGP, OSPF, or production network control planes.
