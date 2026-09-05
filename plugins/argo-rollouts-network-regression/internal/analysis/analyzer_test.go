package analysis

import "testing"

func defaultThresholds() Thresholds {
	return Thresholds{
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

func healthyStable() CohortStats {
	return CohortStats{
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

func TestHealthyCanaryPasses(t *testing.T) {
	stable := healthyStable()

	canary := CohortStats{
		TotalFlows:   300,
		DNSQueries:   80,
		DNSFailures:  1,
		TCPAttempts:  120,
		TCPFailures:  1,
		HTTPRequests: 150,
		HTTP5xx:      1,
		DroppedFlows: 1,
	}

	report := Analyze(
		stable,
		canary,
		defaultThresholds(),
	)

	if report.Decision != DecisionPass {
		t.Fatalf(
			"expected PASS, got %s: %+v",
			report.Decision,
			report,
		)
	}
}

func TestDNSRegressionFails(t *testing.T) {
	stable := healthyStable()

	canary := CohortStats{
		TotalFlows:   300,
		DNSQueries:   100,
		DNSFailures:  12,
		TCPAttempts:  120,
		TCPFailures:  1,
		HTTPRequests: 150,
		HTTP5xx:      1,
		DroppedFlows: 1,
	}

	report := Analyze(
		stable,
		canary,
		defaultThresholds(),
	)

	if report.Decision != DecisionFail {
		t.Fatalf(
			"expected FAIL, got %s",
			report.Decision,
		)
	}

	if !contains(
		report.Regressions,
		"dns_failure_rate",
	) {
		t.Fatalf(
			"expected DNS regression: %+v",
			report.Regressions,
		)
	}
}

func TestDropRegressionFails(t *testing.T) {
	stable := healthyStable()

	canary := CohortStats{
		TotalFlows:   200,
		DNSQueries:   50,
		DNSFailures:  0,
		TCPAttempts:  80,
		TCPFailures:  0,
		HTTPRequests: 100,
		HTTP5xx:      0,
		DroppedFlows: 10,
	}

	report := Analyze(
		stable,
		canary,
		defaultThresholds(),
	)

	if report.Decision != DecisionFail {
		t.Fatalf(
			"expected FAIL, got %s",
			report.Decision,
		)
	}

	if !contains(
		report.Regressions,
		"drop_rate",
	) {
		t.Fatalf(
			"expected drop regression: %+v",
			report.Regressions,
		)
	}
}

func TestTCPRegressionFails(t *testing.T) {
	stable := healthyStable()

	canary := CohortStats{
		TotalFlows:   300,
		DNSQueries:   50,
		DNSFailures:  0,
		TCPAttempts:  100,
		TCPFailures:  15,
		HTTPRequests: 120,
		HTTP5xx:      0,
		DroppedFlows: 0,
	}

	report := Analyze(
		stable,
		canary,
		defaultThresholds(),
	)

	if report.Decision != DecisionFail {
		t.Fatalf(
			"expected FAIL, got %s",
			report.Decision,
		)
	}

	if !contains(
		report.Regressions,
		"tcp_failure_rate",
	) {
		t.Fatalf(
			"expected TCP regression: %+v",
			report.Regressions,
		)
	}
}

func TestHTTPRegressionFails(t *testing.T) {
	stable := healthyStable()

	canary := CohortStats{
		TotalFlows:   300,
		DNSQueries:   50,
		DNSFailures:  0,
		TCPAttempts:  100,
		TCPFailures:  0,
		HTTPRequests: 100,
		HTTP5xx:      10,
		DroppedFlows: 0,
	}

	report := Analyze(
		stable,
		canary,
		defaultThresholds(),
	)

	if report.Decision != DecisionFail {
		t.Fatalf(
			"expected FAIL, got %s",
			report.Decision,
		)
	}

	if !contains(
		report.Regressions,
		"http_5xx_rate",
	) {
		t.Fatalf(
			"expected HTTP regression: %+v",
			report.Regressions,
		)
	}
}

func TestLowCanaryTrafficIsInconclusive(t *testing.T) {
	stable := healthyStable()

	canary := CohortStats{
		TotalFlows: 3,
	}

	report := Analyze(
		stable,
		canary,
		defaultThresholds(),
	)

	if report.Decision != DecisionInconclusive {
		t.Fatalf(
			"expected INCONCLUSIVE, got %s",
			report.Decision,
		)
	}
}

func TestStableBadCanarySameBadDoesNotFail(t *testing.T) {
	stable := CohortStats{
		TotalFlows:   1000,
		DNSQueries:   200,
		DNSFailures:  20,
		TCPAttempts:  400,
		TCPFailures:  40,
		HTTPRequests: 500,
		HTTP5xx:      50,
		DroppedFlows: 30,
	}

	canary := CohortStats{
		TotalFlows:   300,
		DNSQueries:   100,
		DNSFailures:  10,
		TCPAttempts:  100,
		TCPFailures:  10,
		HTTPRequests: 100,
		HTTP5xx:      10,
		DroppedFlows: 9,
	}

	report := Analyze(
		stable,
		canary,
		defaultThresholds(),
	)

	if report.Decision != DecisionPass {
		t.Fatalf(
			"expected PASS for no regression, got %s: %+v",
			report.Decision,
			report,
		)
	}
}

func contains(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}
