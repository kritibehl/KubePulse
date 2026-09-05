package analysis

type Decision string

const (
	DecisionPass         Decision = "PASS"
	DecisionFail         Decision = "FAIL"
	DecisionInconclusive Decision = "INCONCLUSIVE"
)

type CohortStats struct {
	TotalFlows   int `json:"totalFlows"`
	DNSQueries   int `json:"dnsQueries"`
	DNSFailures  int `json:"dnsFailures"`
	TCPAttempts  int `json:"tcpAttempts"`
	TCPFailures  int `json:"tcpFailures"`
	HTTPRequests int `json:"httpRequests"`
	HTTP5xx      int `json:"http5xx"`
	DroppedFlows int `json:"droppedFlows"`
}

type Thresholds struct {
	MinFlows        int `json:"minFlows"`
	MinDNSQueries   int `json:"minDNSQueries"`
	MinTCPAttempts  int `json:"minTCPAttempts"`
	MinHTTPRequests int `json:"minHTTPRequests"`

	DNSFailureDelta float64 `json:"dnsFailureDelta"`
	DropRateDelta   float64 `json:"dropRateDelta"`
	TCPFailureDelta float64 `json:"tcpFailureDelta"`
	HTTP5xxDelta    float64 `json:"http5xxDelta"`
}

type Rates struct {
	DNSFailureRate float64 `json:"dnsFailureRate"`
	DropRate       float64 `json:"dropRate"`
	TCPFailureRate float64 `json:"tcpFailureRate"`
	HTTP5xxRate    float64 `json:"http5xxRate"`
}

type Deltas struct {
	DNSFailureDelta float64 `json:"dnsFailureDelta"`
	DropRateDelta   float64 `json:"dropRateDelta"`
	TCPFailureDelta float64 `json:"tcpFailureDelta"`
	HTTP5xxDelta    float64 `json:"http5xxDelta"`
}

type Report struct {
	Decision Decision `json:"decision"`

	Stable Rates  `json:"stable"`
	Canary Rates  `json:"canary"`
	Deltas Deltas `json:"deltas"`

	EvaluatedSignals []string `json:"evaluatedSignals"`
	Regressions      []string `json:"regressions"`
	Reasons          []string `json:"reasons"`
}
