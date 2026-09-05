package analysis

import "fmt"

func rate(numerator, denominator int) float64 {
	if denominator <= 0 {
		return 0
	}
	return float64(numerator) / float64(denominator)
}

func calculateRates(s CohortStats) Rates {
	return Rates{
		DNSFailureRate: rate(s.DNSFailures, s.DNSQueries),
		DropRate:       rate(s.DroppedFlows, s.TotalFlows),
		TCPFailureRate: rate(s.TCPFailures, s.TCPAttempts),
		HTTP5xxRate:    rate(s.HTTP5xx, s.HTTPRequests),
	}
}

func Analyze(
	stable CohortStats,
	canary CohortStats,
	thresholds Thresholds,
) Report {
	stableRates := calculateRates(stable)
	canaryRates := calculateRates(canary)

	report := Report{
		Stable: stableRates,
		Canary: canaryRates,
		Deltas: Deltas{
			DNSFailureDelta: canaryRates.DNSFailureRate - stableRates.DNSFailureRate,
			DropRateDelta:   canaryRates.DropRate - stableRates.DropRate,
			TCPFailureDelta: canaryRates.TCPFailureRate - stableRates.TCPFailureRate,
			HTTP5xxDelta:    canaryRates.HTTP5xxRate - stableRates.HTTP5xxRate,
		},
	}

	if stable.TotalFlows < thresholds.MinFlows {
		report.Decision = DecisionInconclusive
		report.Reasons = append(
			report.Reasons,
			fmt.Sprintf(
				"stable traffic below minimum: %d < %d",
				stable.TotalFlows,
				thresholds.MinFlows,
			),
		)
		return report
	}

	if canary.TotalFlows < thresholds.MinFlows {
		report.Decision = DecisionInconclusive
		report.Reasons = append(
			report.Reasons,
			fmt.Sprintf(
				"canary traffic below minimum: %d < %d",
				canary.TotalFlows,
				thresholds.MinFlows,
			),
		)
		return report
	}

	if stable.DNSQueries >= thresholds.MinDNSQueries &&
		canary.DNSQueries >= thresholds.MinDNSQueries {
		report.EvaluatedSignals = append(
			report.EvaluatedSignals,
			"dns_failure_rate",
		)

		if report.Deltas.DNSFailureDelta >
			thresholds.DNSFailureDelta {
			report.Regressions = append(
				report.Regressions,
				"dns_failure_rate",
			)
		}
	}

	report.EvaluatedSignals = append(
		report.EvaluatedSignals,
		"drop_rate",
	)

	if report.Deltas.DropRateDelta >
		thresholds.DropRateDelta {
		report.Regressions = append(
			report.Regressions,
			"drop_rate",
		)
	}

	if stable.TCPAttempts >= thresholds.MinTCPAttempts &&
		canary.TCPAttempts >= thresholds.MinTCPAttempts {
		report.EvaluatedSignals = append(
			report.EvaluatedSignals,
			"tcp_failure_rate",
		)

		if report.Deltas.TCPFailureDelta >
			thresholds.TCPFailureDelta {
			report.Regressions = append(
				report.Regressions,
				"tcp_failure_rate",
			)
		}
	}

	if stable.HTTPRequests >= thresholds.MinHTTPRequests &&
		canary.HTTPRequests >= thresholds.MinHTTPRequests {
		report.EvaluatedSignals = append(
			report.EvaluatedSignals,
			"http_5xx_rate",
		)

		if report.Deltas.HTTP5xxDelta >
			thresholds.HTTP5xxDelta {
			report.Regressions = append(
				report.Regressions,
				"http_5xx_rate",
			)
		}
	}

	if len(report.EvaluatedSignals) == 0 {
		report.Decision = DecisionInconclusive
		report.Reasons = append(
			report.Reasons,
			"no signals had enough traffic to evaluate",
		)
		return report
	}

	if len(report.Regressions) > 0 {
		report.Decision = DecisionFail
		report.Reasons = append(
			report.Reasons,
			fmt.Sprintf(
				"network regression detected in %d signal(s)",
				len(report.Regressions),
			),
		)
		return report
	}

	report.Decision = DecisionPass
	report.Reasons = append(
		report.Reasons,
		"canary network behavior is within configured deltas",
	)

	return report
}
